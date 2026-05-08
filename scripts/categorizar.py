#!/usr/bin/env python3
"""
categorizar.py — Agrupa strings do enGB.json por área temática

Facilita revisão humana por tema (combate, diálogos, UI, enciclopédia, etc.)
em vez de revisar 69.000 strings de forma linear.

Uso:
    python3 scripts/categorizar.py                    # gerar relatório de categorias
    python3 scripts/categorizar.py --exportar         # criar arquivos por categoria em revisao/
    python3 scripts/categorizar.py --categoria combate --limite 50  # listar 50 strings de combate
    python3 scripts/categorizar.py --nao-traduzidas   # strings não traduzidas por categoria
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ENDB_PATH = ROOT / "enGB.json"
ORIG_PATH = ROOT / "arquivo-original-1.5.0.320.json"
REVISAO_DIR = ROOT / "revisao"

TAG_RE = re.compile(r"\{[^}]+\}|<[^>]+>|\n")

# ─── Definições de categorias ────────────────────────────────────────────────
# Cada categoria tem prioridade: a primeira que casar é usada.
# Ordem importa — mais específico primeiro.

CATEGORIES = [
    ("ui", "Interface de Usuário", re.compile(
        r"\b(botão|clique|menu|tela|painel|ícone|interface|cursor|janela"
        r"|configuração|opção|salvar|carregar|confirmar|cancelar)\b", re.I
    )),
    ("tutorial", "Tutorial e Ajuda", re.compile(
        r"\b(dica|tutorial|aprenda|como|passo a passo|ajuda|hint|tip)\b", re.I
    )),
    ("combate", "Combate e Mecânicas", re.compile(
        r"\b(dano|ataque|defesa|rodada|turno|alcance|recarga|cobertura"
        r"|esquiva|investida|tiro|acerto|crítico|ferimento|pontos de ação"
        r"|pontos de movimento|habilidade|passivo|talento|perícia)\b", re.I
    )),
    ("enciclopedia", "Enciclopédia e Lore", re.compile(
        r"\b(característica|origem|facção|história|lore|conhecimento"
        r"|crença|dogma|ritual|texto de enciclopédia)\b", re.I
    )),
    ("dialogo", "Diálogos e Narrativa", re.compile(
        r"\b(disse|respondeu|perguntou|ordenou|sussurrou|gritou"
        r"|narração|fala|resposta|opção de diálogo)\b", re.I
    )),
    ("personagens", "Personagens e NPCs", re.compile(
        r"\b(rogue trader|capitão|comissário|tech-priest|sister"
        r"|explorador|mercenário|herege|inquisidor|navio|tripulação)\b", re.I
    )),
    ("itens", "Itens e Equipamento", re.compile(
        r"\b(arma|armadura|implante|modificação|munição|engrenagem"
        r"|item|equipamento|relíquia|mechadendrite)\b", re.I
    )),
    ("missoes", "Missões e Objetivos", re.compile(
        r"\b(missão|objetivo|tarefa|recompensa|falha|sucesso"
        r"|colônia|planeta|sistema|setor|exploração)\b", re.I
    )),
    ("outros", "Outros", re.compile(r".*")),  # Catch-all
]


def strip_tags(text: str) -> str:
    return TAG_RE.sub(" ", text).strip()


def categorize(text: str) -> str:
    clean = strip_tags(text)
    for cat_id, _, pattern in CATEGORIES:
        if pattern.search(clean):
            return cat_id
    return "outros"


def is_untranslated(en_text: str, pt_text: str) -> bool:
    """Retorna True se a string parece não traduzida (EN == PT ou maioria EN)."""
    en_clean = strip_tags(en_text).lower()
    pt_clean = strip_tags(pt_text).lower()
    if en_clean == pt_clean:
        return True
    en_words = re.compile(r"\b(the|and|or|is|are|was|were|will|have|has|this|that|with)\b", re.I)
    pt_words = re.compile(r"\b(de|da|do|em|para|um|uma|com|que|não|são|você)\b", re.I)
    if en_words.search(pt_clean) and not pt_words.search(pt_clean):
        return True
    return False


def load_data(need_orig: bool = False) -> tuple[dict, dict | None]:
    with open(ENDB_PATH, encoding="utf-8") as f:
        pt_data = json.load(f)
    orig = None
    if need_orig and ORIG_PATH.exists():
        with open(ORIG_PATH, encoding="utf-8") as f:
            orig = json.load(f)
    return pt_data["strings"], (orig["strings"] if orig else None)


def cmd_relatorio(args):
    """Mostra distribuição de strings por categoria."""
    pt_strings, en_strings = load_data(need_orig=bool(args.nao_traduzidas))

    # Contar por categoria
    contagem: dict[str, dict] = {cat_id: {"total": 0, "nao_trad": 0, "label": label}
                                  for cat_id, label, _ in CATEGORIES}

    for uuid, entry in pt_strings.items():
        pt_text = entry["Text"]
        cat = categorize(pt_text)
        contagem[cat]["total"] += 1

        if en_strings and uuid in en_strings:
            en_text = en_strings[uuid]["Text"]
            if is_untranslated(en_text, pt_text):
                contagem[cat]["nao_trad"] += 1

    print("=" * 60)
    print("  DISTRIBUIÇÃO POR CATEGORIA — categorizar.py")
    print("=" * 60)
    print(f"  {'Categoria':<20} {'Total':>8} {'Não trad':>10} {'%':>6}")
    print(f"  {'-'*20} {'-'*8} {'-'*10} {'-'*6}")

    grand_total = sum(v["total"] for v in contagem.values())
    grand_nao_trad = sum(v["nao_trad"] for v in contagem.values())

    for cat_id, _, _ in CATEGORIES:
        c = contagem[cat_id]
        pct = round(c["nao_trad"] / c["total"] * 100, 1) if c["total"] else 0
        label = c["label"]
        print(f"  {label:<20} {c['total']:>8,} {c['nao_trad']:>10,} {pct:>5.1f}%")

    print(f"  {'─'*46}")
    grand_pct = round(grand_nao_trad / grand_total * 100, 1) if grand_total else 0
    print(f"  {'TOTAL':<20} {grand_total:>8,} {grand_nao_trad:>10,} {grand_pct:>5.1f}%")
    print()


def cmd_listar(args):
    """Lista strings de uma categoria específica."""
    pt_strings, en_strings = load_data(need_orig=True)

    count = 0
    for uuid, entry in pt_strings.items():
        pt_text = entry["Text"]
        cat = categorize(pt_text)
        if cat != args.categoria:
            continue

        if args.nao_traduzidas and en_strings:
            en_text = en_strings.get(uuid, {}).get("Text", "")
            if not is_untranslated(en_text, pt_text):
                continue

        print(f"[{uuid[:8]}] {pt_text[:120]}")
        count += 1

        if args.limite > 0 and count >= args.limite:
            print(f"\n... limitado a {args.limite} strings. Use --limite 0 para ver tudo.")
            break

    print(f"\nTotal listado: {count:,} strings da categoria '{args.categoria}'")


def cmd_exportar(args):
    """Exporta strings por categoria para arquivos JSON em revisao/."""
    pt_strings, en_strings = load_data(need_orig=True)

    REVISAO_DIR.mkdir(exist_ok=True)

    buckets: dict[str, list] = {cat_id: [] for cat_id, _, _ in CATEGORIES}

    for uuid, entry in pt_strings.items():
        pt_text = entry["Text"]
        cat = categorize(pt_text)

        item = {"uuid": uuid, "pt": pt_text}
        if en_strings and uuid in en_strings:
            item["en"] = en_strings[uuid]["Text"]
            item["nao_traduzida"] = is_untranslated(item["en"], pt_text)
        buckets[cat].append(item)

    for cat_id, label, _ in CATEGORIES:
        out_path = REVISAO_DIR / f"{cat_id}.json"
        payload = {
            "categoria": label,
            "total": len(buckets[cat_id]),
            "strings": buckets[cat_id],
        }
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"  {label:<25} → revisao/{cat_id}.json ({len(buckets[cat_id]):,} strings)")

    print(f"\nArquivos exportados para: {REVISAO_DIR}/")
    print("Para revisar: abra o arquivo JSON de uma categoria e edite o campo 'pt'.")


def main():
    parser = argparse.ArgumentParser(
        description="Agrupa strings do enGB.json por área temática para revisão"
    )
    sub = parser.add_subparsers(dest="cmd")

    # Subcomandos
    p_rel = sub.add_parser("relatorio", help="Distribuição por categoria (padrão)")
    p_rel.add_argument("--nao-traduzidas", action="store_true",
                       help="Mostrar contagem de não traduzidas por categoria")

    p_list = sub.add_parser("listar", help="Listar strings de uma categoria")
    p_list.add_argument("--categoria", required=True, choices=[c[0] for c in CATEGORIES[:-1]])
    p_list.add_argument("--limite", type=int, default=20)
    p_list.add_argument("--nao-traduzidas", action="store_true")

    p_exp = sub.add_parser("exportar", help="Exportar categorias para revisao/")

    # Compat: argumentos legados sem subcomando
    parser.add_argument("--categoria", type=str, default=None)
    parser.add_argument("--limite", type=int, default=20)
    parser.add_argument("--exportar", action="store_true")
    parser.add_argument("--nao-traduzidas", action="store_true")

    args = parser.parse_args()

    # Roteamento
    if args.cmd == "listar" or (not args.cmd and args.categoria):
        if not args.cmd:
            # modo legado
            args.cmd = "listar"
        cmd_listar(args)
    elif args.cmd == "exportar" or (not args.cmd and args.exportar):
        cmd_exportar(args)
    else:
        # padrão: relatório
        cmd_relatorio(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
