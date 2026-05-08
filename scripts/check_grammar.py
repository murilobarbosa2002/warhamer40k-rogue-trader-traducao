#!/usr/bin/env python3
"""
check_grammar.py — Verificador gramatical para o PT-BR usando LanguageTool + spaCy

Detecta erros reais de gramática, concordância de gênero e acentuação
que os scripts de regex (fix_gender.py) não conseguem pegar.

REQUER: Java 8+ instalado no sistema (LanguageTool roda na JVM)
        pip install language-tool-python spacy
        python -m spacy download pt_core_news_sm

Uso:
    python3 scripts/check_grammar.py                   # analisar tudo
    python3 scripts/check_grammar.py --limite 500      # amostrar 500 strings
    python3 scripts/check_grammar.py --output erros.txt
    python3 scripts/check_grammar.py --spacy-only      # só spaCy (sem Java)
    python3 scripts/check_grammar.py --categoria combate
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ENDB_PATH = ROOT / "enGB.json"
TAG_RE = re.compile(r"\{[^}]+\}|<[^>]+>|\n")

# ─── Categorias por prefixo de UUID / padrão no texto ───────────────────────
# (mesma lógica do categorizar.py)
CATEGORY_PATTERNS = {
    "ui":       re.compile(r"\b(botão|clique|menu|tela|painel|ícone|interface)\b", re.I),
    "combate":  re.compile(r"\b(dano|ataque|defesa|rodada|turno|alcance|recarga|perícia)\b", re.I),
    "dialogo":  re.compile(r"\b(disse|respondeu|perguntou|ordenou|sussurrou|gritou)\b", re.I),
    "enciclopedia": re.compile(r"\b(característica|habilidade|talento|passivo|aprimoramento)\b", re.I),
}


def strip_tags(text: str) -> str:
    return TAG_RE.sub(" ", text).strip()


# ─── Backend: spaCy (sem Java) ───────────────────────────────────────────────

def check_with_spacy(texts: list[tuple[str, str]]) -> list[dict]:
    """
    Detecta erros de concordância de gênero usando POS tagging do spaCy.
    Mais inteligente que regex: analisa o contexto morfológico real.

    Retorna lista de dicts com: uuid, text, tipo, descricao, trecho
    """
    try:
        import spacy
    except ImportError:
        print("ERRO: spacy não instalado. Execute: pip install spacy && python -m spacy download pt_core_news_sm")
        return []

    try:
        nlp = spacy.load("pt_core_news_sm")
    except OSError:
        print("ERRO: modelo pt_core_news_sm não baixado. Execute: python -m spacy download pt_core_news_sm")
        return []

    issues = []
    total = len(texts)

    for i, (uuid, raw_text) in enumerate(texts):
        if i % 100 == 0:
            print(f"  spaCy: {i}/{total}...", end="\r")

        text = strip_tags(raw_text)
        if len(text) < 5:
            continue

        doc = nlp(text)

        for token in doc:
            # Detectar artigo determinado + substantivo com gênero conflitante
            if token.pos_ == "DET" and token.i + 1 < len(doc):
                next_tok = doc[token.i + 1]
                if next_tok.pos_ in ("NOUN", "PROPN"):
                    det_gender = token.morph.get("Gender")
                    noun_gender = next_tok.morph.get("Gender")
                    if det_gender and noun_gender and det_gender != noun_gender:
                        issues.append({
                            "uuid": uuid,
                            "text": raw_text[:120],
                            "tipo": "concordancia_genero_spacy",
                            "descricao": (
                                f"artigo '{token.text}' ({det_gender[0]}) + "
                                f"substantivo '{next_tok.text}' ({noun_gender[0]})"
                            ),
                            "trecho": f"{token.text} {next_tok.text}",
                        })

    print(f"  spaCy: {total}/{total} strings analisadas.")
    return issues


# ─── Backend: LanguageTool (requer Java) ────────────────────────────────────

def check_with_languagetool(texts: list[tuple[str, str]], limite_lt: int = 200) -> list[dict]:
    """
    Verifica gramática real usando LanguageTool (PT-BR).
    Mais lento — analisa até `limite_lt` strings para não demorar demais.
    Requer Java 8+ no sistema.
    """
    try:
        import language_tool_python
    except ImportError:
        print("ERRO: language-tool-python não instalado: pip install language-tool-python")
        return []

    print(f"  LanguageTool: inicializando (requer Java)...")
    try:
        tool = language_tool_python.LanguageTool("pt-BR")
    except Exception as e:
        print(f"  LanguageTool: falhou ao inicializar ({e})")
        print("  Certifique-se que Java 8+ está instalado: java -version")
        return []

    issues = []
    sample = texts[:limite_lt]
    total = len(sample)

    # Categorias de regras ignoradas (muito ruidosas para texto de jogo)
    IGNORE_RULES = {
        "WHITESPACE_RULE",
        "UPPERCASE_SENTENCE_START",
        "COMMA_PARENTHESIS_WHITESPACE",
        "PT_UNPAIRED_BRACKETS",
    }

    for i, (uuid, raw_text) in enumerate(sample):
        if i % 20 == 0:
            print(f"  LanguageTool: {i}/{total}...", end="\r")

        text = strip_tags(raw_text)
        if len(text) < 10:
            continue

        matches = tool.check(text)
        for match in matches:
            if match.ruleId in IGNORE_RULES:
                continue
            issues.append({
                "uuid": uuid,
                "text": raw_text[:120],
                "tipo": f"lt:{match.ruleId}",
                "descricao": match.message,
                "trecho": text[match.offset: match.offset + match.errorLength],
                "sugestao": match.replacements[:3] if match.replacements else [],
            })

    print(f"  LanguageTool: {total}/{total} strings analisadas.")
    tool.close()
    return issues


# ─── Relatório ───────────────────────────────────────────────────────────────

def render_report(issues: list[dict], output_path: Path | None):
    lines = []
    lines.append("=" * 60)
    lines.append("  RELATÓRIO DE GRAMÁTICA — check_grammar.py")
    lines.append("=" * 60)
    lines.append(f"  Total de problemas encontrados: {len(issues)}")
    lines.append("")

    # Agrupar por tipo
    by_type: dict[str, list] = {}
    for issue in issues:
        by_type.setdefault(issue["tipo"], []).append(issue)

    for tipo, grupo in sorted(by_type.items(), key=lambda x: -len(x[1])):
        lines.append(f"[ {tipo} ] — {len(grupo)} ocorrências")
        for item in grupo[:5]:
            lines.append(f"  [{item['uuid'][:8]}] {item['descricao']}")
            lines.append(f"    Trecho: «{item.get('trecho', '')}»")
            if item.get("sugestao"):
                lines.append(f"    Sugestão: {', '.join(item['sugestao'])}")
        if len(grupo) > 5:
            lines.append(f"  ... e mais {len(grupo) - 5} ocorrências")
        lines.append("")

    report = "\n".join(lines)
    print(report)

    if output_path:
        output_path.write_text(report, encoding="utf-8")
        print(f"\nRelatório salvo em: {output_path}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Verifica gramática das traduções PT-BR usando LanguageTool e spaCy"
    )
    parser.add_argument("--limite", type=int, default=0,
                        help="Máximo de strings a analisar (0 = todas)")
    parser.add_argument("--output", type=str, default=None,
                        help="Salvar relatório em arquivo")
    parser.add_argument("--spacy-only", action="store_true",
                        help="Usar apenas spaCy (não requer Java)")
    parser.add_argument("--lt-only", action="store_true",
                        help="Usar apenas LanguageTool")
    parser.add_argument("--categoria", type=str, default=None,
                        choices=list(CATEGORY_PATTERNS.keys()),
                        help="Filtrar por categoria de string")
    args = parser.parse_args()

    print("Carregando enGB.json...")
    with open(ENDB_PATH, encoding="utf-8") as f:
        data = json.load(f)

    strings = data["strings"]
    texts = [(k, v["Text"]) for k, v in strings.items()]

    # Filtrar por categoria se pedido
    if args.categoria:
        pat = CATEGORY_PATTERNS[args.categoria]
        texts = [(k, t) for k, t in texts if pat.search(strip_tags(t))]
        print(f"Filtrado para categoria '{args.categoria}': {len(texts)} strings")

    if args.limite > 0:
        texts = texts[:args.limite]

    print(f"Analisando {len(texts):,} strings...\n")

    issues = []

    if not args.lt_only:
        print("[1/2] Analisando com spaCy (concordância morfológica)...")
        issues += check_with_spacy(texts)

    if not args.spacy_only:
        print("[2/2] Analisando com LanguageTool (gramática completa)...")
        issues += check_with_languagetool(texts)

    output_path = Path(args.output) if args.output else None
    render_report(issues, output_path)

    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())
