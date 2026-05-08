#!/usr/bin/env python3
"""
relatorio.py — Gera relatório completo de qualidade da tradução.
Uso: python3 scripts/relatorio.py
     python3 scripts/relatorio.py --output relatorio.txt
"""
import json
import re
import sys
import argparse
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
ENDB_PATH = ROOT / "enGB.json"

PT_WORDS = re.compile(
    r'\b(de|da|do|das|dos|em|para|uma|um|com|que|não|são|foi|ser|tem|ter|'
    r'pelo|pela|nos|nas|seu|sua|você|este|esta|esse|essa|quando|como|mais|'
    r'muito|pode|deve|após|antes|durante|sobre|entre|também|ainda|já|apenas|'
    r'sempre|nunca|cada|todos|todas)\b', re.IGNORECASE
)
EN_WORDS = re.compile(
    r'\b(the|and|or|is|are|was|were|will|would|can|could|should|have|has|'
    r'had|this|that|these|those|with|from|they|their|you|your|when|where|'
    r'what|which|who)\b', re.IGNORECASE
)

FORBIDDEN = {
    r'\bMP\b':       ("MP → PM",        "PM"),
    r'\bAP\b':       ("AP → PA",        "PA"),
    r'\bcooldowns?\b': ("cooldown → recarga", "recarga"),
    r'\bdebuffs?\b': ("debuff → penalidade de efeito", "penalidade de efeito"),
    r'\bbuff\b(?!er|et)': ("buff → aprimoramento", "aprimoramento"),
    r'\btalents?\b': ("talent → talento", "talento"),
    r'\bNPCs?\b':    ("NPC → PNJ",      "PNJ"),
    r'\bskills?\b':  ("skill → habilidade/perícia", "habilidade"),
    r'\btargets?\b': ("target → alvo",  "alvo"),
    r'\bdamage\b':   ("damage → dano",  "dano"),
    r'\btraits?\b':  ("trait → característica", "característica"),
    r'\bfeats?\b':   ("feat → habilidade", "habilidade"),
}

DUPS = {
    r'\bde de\b':    "preposição duplicada \"de de\"",
    r'\bque que\b':  "conjunção duplicada \"que que\"",
    r'\bpara para\b':"preposição duplicada \"para para\"",
    r'\bo o\b':      "artigo duplicado \"o o\"",
    r'\bum um\b':    "artigo duplicado \"um um\"",
    r'\ba a\b':      "artigo duplicado \"a a\"",
}

GENERO_MASC_FEM = re.compile(
    r'\b(o|um|do|ao|pelo|no|todo|este|esse|aquele)\s+'
    r'(habilidade|arma|rodada|missão|nave|ação|criatura|unidade|batalha)\b',
    re.IGNORECASE
)
GENERO_FEM_MASC = re.compile(
    r'\b(a|uma|da|pela|na|toda|esta|essa|aquela)\s+'
    r'(efeito|ataque|dano|bônus|teste|turno|combate|poder|alvo)\b',
    re.IGNORECASE
)


def inside_tag(text, start):
    before = text[:start]
    return before.count('{') > before.count('}')


def run(output_file=None):
    out = []

    def p(line=""):
        out.append(line)
        print(line)

    p("Carregando enGB.json...")
    with open(ENDB_PATH, encoding="utf-8") as f:
        data = json.load(f)
    strings = data["strings"]
    all_texts = [(k, v["Text"]) for k, v in strings.items()]

    p()
    p("=" * 62)
    p("  RELATORIO DE QUALIDADE — WH40K: ROGUE TRADER PT-BR")
    p("=" * 62)

    # ── 1. Estatísticas gerais ────────────────────────────────────────────
    total = len(strings)
    nonempty = sum(1 for _, t in all_texts if len(t.strip()) > 5)
    total_chars = sum(len(t) for _, t in all_texts)
    p()
    p("ESTATISTICAS GERAIS")
    p(f"  Total de strings    : {total:,}")
    p(f"  Com conteudo real   : {nonempty:,}")
    p(f"  Total de caracteres : {total_chars:,}")

    # ── 2. Strings não traduzidas ─────────────────────────────────────────
    untranslated = []
    for uuid, text in all_texts:
        clean = re.sub(r'\{[^}]+\}|<[^>]+>|\[[^\]]+\]', '', text).strip()
        if len(clean) < 30:
            continue
        if EN_WORDS.search(clean) and not PT_WORDS.search(clean):
            untranslated.append((uuid, text))

    p()
    p(f"[CRITICO] STRINGS NAO TRADUZIDAS: {len(untranslated)}")
    for uuid, text in untranslated[:10]:
        p(f"  [{uuid[:8]}] {text[:100]}")
    if len(untranslated) > 10:
        p(f"  ... e mais {len(untranslated) - 10}")

    # ── 3. Termos proibidos ───────────────────────────────────────────────
    p()
    p("[ERRO] TERMOS EM INGLES NO TEXTO PT:")
    total_forbidden = 0
    for pat, (desc, _) in FORBIDDEN.items():
        matches = []
        for uuid, text in all_texts:
            for m in re.finditer(pat, text, re.IGNORECASE):
                if not inside_tag(text, m.start()):
                    matches.append((uuid, text[:80]))
                    break
        if matches:
            total_forbidden += len(matches)
            p(f"  {len(matches):4d}x  {desc}")
    p(f"  TOTAL: {total_forbidden}")

    # ── 4. Duplicações gramaticais ────────────────────────────────────────
    p()
    p("[ERRO] DUPLICACOES GRAMATICAIS:")
    total_dups = 0
    for pat, desc in DUPS.items():
        c = sum(1 for _, t in all_texts if re.search(pat, t, re.IGNORECASE))
        if c:
            total_dups += c
            p(f"  {c:4d}x  {desc}")
    if total_dups == 0:
        p("  Nenhuma encontrada.")

    # ── 5. Gênero ─────────────────────────────────────────────────────────
    p()
    masc_fem = sum(1 for _, t in all_texts if GENERO_MASC_FEM.search(t))
    fem_masc = sum(1 for _, t in all_texts if GENERO_FEM_MASC.search(t))
    p(f"[AVISO] CONCORDANCIA DE GENERO SUSPEITA: {masc_fem + fem_masc} casos")
    p(f"  Artigo masc. + subst. feminino : {masc_fem}")
    p(f"  Artigo fem.  + subst. masculino: {fem_masc}")
    for _, t in all_texts:
        m = GENERO_MASC_FEM.search(t)
        if m:
            p(f"  ex: ...{t[max(0,m.start()-20):m.end()+20]}...")
            break

    # ── 6. Score ──────────────────────────────────────────────────────────
    problems = len(untranslated) * 3 + total_forbidden + total_dups + (masc_fem + fem_masc) // 5
    score = max(0, 10 - (problems / nonempty * 100))
    score = round(min(10, score), 1)

    p()
    p("=" * 62)
    p(f"  SCORE ESTIMADO DE QUALIDADE: {score}/10")
    p(f"  Strings sem problemas detectados: ~{nonempty - len(untranslated) - total_forbidden:,}")
    p()
    p("PROXIMOS PASSOS RECOMENDADOS:")
    p("  1. python3 scripts/fix_auto.py         — corrigir termos automaticos")
    p("  2. /traduzir-nao-traduzidas             — traduzir strings em ingles")
    p("  3. /revisar-lote                        — revisar qualidade em lotes")
    p("  4. /melhorar-literario                  — refinar falas de personagens")
    p("=" * 62)

    if output_file:
        Path(output_file).write_text('\n'.join(out), encoding="utf-8")
        print(f"\nRelatorio salvo em: {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Relatorio de qualidade WH40K PT-BR")
    parser.add_argument("--output", help="Salvar relatorio em arquivo texto")
    args = parser.parse_args()
    run(output_file=args.output)


if __name__ == "__main__":
    main()
