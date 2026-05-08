#!/usr/bin/env python3
"""
diff_original.py — Compara arquivo original EN com a tradução PT-BR
e gera uma fila de trabalho JSON com strings que precisam de tradução.

Uso:
    python3 scripts/diff_original.py
    python3 scripts/diff_original.py --output fila.json
    python3 scripts/diff_original.py --modo nao-traduzidas
    python3 scripts/diff_original.py --modo todas
    python3 scripts/diff_original.py --stats
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ORIGINAL_PATH = ROOT / "arquivo-original-1.5.0.320.json"
TRADUCAO_PATH = ROOT / "enGB.json"
DEFAULT_OUTPUT = ROOT / "fila-traducao.json"

# Regex para detectar se o texto tem conteúdo real além de tags/símbolos
TAG_RE = re.compile(r"\{[^}]+\}|<[^>]+>|\[[^\]]+\]")
PT_MARKERS = re.compile(
    r"\b(de|da|do|das|dos|em|para|uma|um|com|que|não|são|foi|ser|tem"
    r"|ter|pelo|pela|nos|nas|você|este|esta|esse|essa|quando|como|mais"
    r"|muito|pode|deve|após|antes|durante|sobre|entre|também|ainda|já"
    r"|apenas|sempre|nunca|cada|todos|todas)\b",
    re.IGNORECASE,
)
EN_MARKERS = re.compile(
    r"\b(the|and|or|is|are|was|were|will|would|can|could|should|have|has"
    r"|had|this|that|these|those|with|from|they|their|you|your|when|where"
    r"|what|which|who|it|its)\b",
    re.IGNORECASE,
)


def has_real_text(text: str) -> bool:
    """Retorna True se o texto tem conteúdo translatable (não só tags/símbolos)."""
    clean = TAG_RE.sub("", text).strip()
    if len(clean) < 10:
        return False
    return bool(re.search(r"[a-zA-Z]{3}", clean))


def classify(key: str, orig_text: str, trad_text: str) -> str:
    """
    Classifica o status de tradução de uma string.
    Retorna: 'nao-traduzida' | 'identica' | 'traduzida' | 'sem-conteudo'
    """
    if not has_real_text(orig_text):
        return "sem-conteudo"

    orig_clean = TAG_RE.sub("", orig_text).strip()
    trad_clean = TAG_RE.sub("", trad_text).strip()

    # Texto idêntico ao original = não foi traduzido
    if orig_clean.lower() == trad_clean.lower():
        return "nao-traduzida"

    # Texto em inglês detectado (sem marcadores PT)
    if EN_MARKERS.search(trad_clean) and not PT_MARKERS.search(trad_clean):
        return "nao-traduzida"

    return "traduzida"


def run(modo: str, output_file: Path, stats_only: bool) -> int:
    if not ORIGINAL_PATH.exists():
        print(f"ERRO: arquivo original não encontrado: {ORIGINAL_PATH}")
        print("Certifique-se de que 'arquivo-original-1.5.0.320.json' está na raiz do projeto.")
        return 1

    if not TRADUCAO_PATH.exists():
        print(f"ERRO: arquivo de tradução não encontrado: {TRADUCAO_PATH}")
        return 1

    print("Carregando arquivos...")
    with open(ORIGINAL_PATH, encoding="utf-8") as f:
        orig_data = json.load(f)
    with open(TRADUCAO_PATH, encoding="utf-8") as f:
        trad_data = json.load(f)

    orig_strings = orig_data["strings"]
    trad_strings = trad_data["strings"]

    print(f"  Original EN: {len(orig_strings):,} strings")
    print(f"  Tradução PT: {len(trad_strings):,} strings")

    # Classificar todas as strings do original
    fila = {
        "nao-traduzida": {},
        "identica": {},
        "sem-conteudo": {},
        "traduzida": {},
        "apenas-no-original": {},  # strings que não estão na tradução
    }

    for key, orig_entry in orig_strings.items():
        orig_text = orig_entry["Text"]

        if key not in trad_strings:
            fila["apenas-no-original"][key] = {
                "en": orig_text,
                "pt": "",
                "offset": orig_entry.get("Offset", 0),
            }
            continue

        trad_text = trad_strings[key]["Text"]
        status = classify(key, orig_text, trad_text)

        fila[status][key] = {
            "en": orig_text,
            "pt": trad_text,
            "offset": orig_entry.get("Offset", 0),
        }

    # Estatísticas
    total = len(orig_strings)
    n_nao = len(fila["nao-traduzida"])
    n_sem = len(fila["sem-conteudo"])
    n_trad = len(fila["traduzida"])
    n_orig = len(fila["apenas-no-original"])

    print()
    print("=" * 60)
    print("  RELATÓRIO DE STATUS DE TRADUÇÃO")
    print("=" * 60)
    print(f"  Total de strings no original:    {total:>7,}")
    print(f"  ✓ Traduzidas:                    {n_trad:>7,}  ({n_trad/total*100:.1f}%)")
    print(f"  ✗ Não traduzidas (em inglês):    {n_nao:>7,}  ({n_nao/total*100:.1f}%)")
    print(f"  ~ Sem conteúdo real (tags/ids):  {n_sem:>7,}  ({n_sem/total*100:.1f}%)")
    print(f"  + Apenas no original (faltando): {n_orig:>7,}")
    extras = len(trad_strings) - len(orig_strings)
    if extras > 0:
        print(f"  - Extras na tradução (obsoletas): {extras:>6,}")
    print("=" * 60)

    if stats_only:
        return 0

    # Montar fila de saída conforme modo
    if modo == "nao-traduzidas":
        output_queue = {**fila["nao-traduzida"], **fila["apenas-no-original"]}
        descricao = "strings não traduzidas"
    elif modo == "todas":
        # Inclui tudo exceto sem-conteudo
        output_queue = {
            **fila["nao-traduzida"],
            **fila["apenas-no-original"],
            **fila["traduzida"],
        }
        descricao = "todas as strings com conteúdo"
    else:
        output_queue = {**fila["nao-traduzida"], **fila["apenas-no-original"]}
        descricao = "strings não traduzidas"

    print()
    print(f"Gerando fila: {len(output_queue):,} {descricao}")

    # Ordenar por offset para processar em ordem de aparecimento no jogo
    sorted_queue = dict(
        sorted(output_queue.items(), key=lambda x: x[1].get("offset", 0))
    )

    output = {
        "meta": {
            "total_original": total,
            "total_fila": len(sorted_queue),
            "modo": modo,
            "status": {
                "traduzidas": n_trad,
                "nao_traduzidas": n_nao,
                "sem_conteudo": n_sem,
            },
        },
        "strings": sorted_queue,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Fila salva em: {output_file}")
    print()
    print("Próximos passos:")
    print("  python3 scripts/translate_batch.py            — traduzir com IA")
    print("  python3 scripts/translate_batch.py --dry-run  — simular sem salvar")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Gera fila de tradução comparando EN original com PT-BR"
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Arquivo de saída (padrão: {DEFAULT_OUTPUT.name})",
    )
    parser.add_argument(
        "--modo",
        default="nao-traduzidas",
        choices=["nao-traduzidas", "todas"],
        help="'nao-traduzidas': apenas não traduzidas | 'todas': todas com conteúdo",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Mostrar apenas estatísticas, sem gerar fila",
    )
    args = parser.parse_args()
    sys.exit(run(modo=args.modo, output_file=Path(args.output), stats_only=args.stats))


if __name__ == "__main__":
    main()
