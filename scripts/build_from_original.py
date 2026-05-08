#!/usr/bin/env python3
"""
build_from_original.py — Constrói a tradução do ZERO a partir do original EN.

Ao contrário de translate_batch.py (que traduz apenas as strings faltando),
este script reconstrói enGB.json inteiro a partir de arquivo-original-1.5.0.320.json,
eliminando as 67 strings obsoletas e garantindo que a estrutura seja limpa.

ATENÇÃO: Este script NÃO sobrescreve enGB.json diretamente.
Gera um arquivo 'enGB-rebuilt.json' que você pode revisar antes de adotar.

Uso:
    python3 scripts/build_from_original.py --stats         # ver o que mudaria
    python3 scripts/build_from_original.py --dry-run       # simular sem salvar
    python3 scripts/build_from_original.py                 # gerar enGB-rebuilt.json
    python3 scripts/build_from_original.py --apply         # substituir enGB.json (CUIDADO!)
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ORIGINAL_PATH = ROOT / "arquivo-original-1.5.0.320.json"
TRADUCAO_PATH = ROOT / "enGB.json"
OUTPUT_PATH = ROOT / "enGB-rebuilt.json"

TAG_RE = re.compile(r"\{[^}]+\}|<[^>]+>")
PT_MARKERS = re.compile(
    r"\b(de|da|do|das|dos|em|para|uma|um|com|que|não|são|foi|ser|tem"
    r"|ter|você|este|essa|quando|mais|pode|deve|sobre|entre|também|já)\b",
    re.IGNORECASE,
)
EN_MARKERS = re.compile(
    r"\b(the|and|or|is|are|was|were|will|would|can|could|should|have"
    r"|has|had|this|that|these|those|with|from|they|their|you|your)\b",
    re.IGNORECASE,
)


def is_translated(en_text: str, pt_text: str) -> bool:
    """Retorna True se o texto parece ter sido traduzido."""
    clean_en = TAG_RE.sub("", en_text).strip()
    clean_pt = TAG_RE.sub("", pt_text).strip()

    if len(clean_en) < 5:
        return True  # Texto curto: aceitar como está

    if clean_en.lower() == clean_pt.lower():
        return False  # Idêntico ao original = não traduzido

    if EN_MARKERS.search(clean_pt) and not PT_MARKERS.search(clean_pt):
        return False  # Só marcadores EN, sem PT = não traduzido

    return True


def run(dry_run: bool, apply: bool, stats_only: bool) -> int:
    if not ORIGINAL_PATH.exists():
        print(f"ERRO: {ORIGINAL_PATH.name} não encontrado na raiz do projeto.")
        return 1

    if not TRADUCAO_PATH.exists():
        print(f"ERRO: {TRADUCAO_PATH.name} não encontrado.")
        return 1

    print("Carregando arquivos...")
    with open(ORIGINAL_PATH, encoding="utf-8") as f:
        orig_data = json.load(f)
    with open(TRADUCAO_PATH, encoding="utf-8") as f:
        trad_data = json.load(f)

    orig_strings = orig_data["strings"]
    trad_strings = trad_data["strings"]

    print(f"  Original EN:  {len(orig_strings):,} strings")
    print(f"  Tradução PT:  {len(trad_strings):,} strings")

    # Construir o novo enGB a partir do original
    new_strings = {}
    stats = {
        "mantidas_pt": 0,
        "mantidas_en_sem_traducao": 0,
        "mantidas_curtas": 0,
        "obsoletas_removidas": len(trad_strings) - len(orig_strings),
    }

    for key, orig_entry in orig_strings.items():
        en_text = orig_entry["Text"]
        offset = orig_entry.get("Offset", 0)

        # Se existe tradução para esta chave
        if key in trad_strings:
            pt_text = trad_strings[key]["Text"]
            clean_en = TAG_RE.sub("", en_text).strip()

            if len(clean_en) < 5:
                # Texto muito curto: manter o que existe (pode ser só símbolo)
                new_strings[key] = {"Offset": offset, "Text": pt_text}
                stats["mantidas_curtas"] += 1
            elif is_translated(en_text, pt_text):
                # Tem tradução: usar a existente
                new_strings[key] = {"Offset": offset, "Text": pt_text}
                stats["mantidas_pt"] += 1
            else:
                # Sem tradução: manter inglês por enquanto (será traduzido depois)
                new_strings[key] = {"Offset": offset, "Text": en_text}
                stats["mantidas_en_sem_traducao"] += 1
        else:
            # String no original mas não na tradução: usar inglês
            new_strings[key] = {"Offset": offset, "Text": en_text}
            stats["mantidas_en_sem_traducao"] += 1

    total = len(orig_strings)
    print()
    print("=" * 60)
    print("  RELATÓRIO DE RECONSTRUÇÃO")
    print("=" * 60)
    print(f"  Strings com tradução PT mantidas:  {stats['mantidas_pt']:>7,}  ({stats['mantidas_pt']/total*100:.1f}%)")
    print(f"  Strings curtas/simbólicas:         {stats['mantidas_curtas']:>7,}  ({stats['mantidas_curtas']/total*100:.1f}%)")
    print(f"  Strings sem tradução (inglês):     {stats['mantidas_en_sem_traducao']:>7,}  ({stats['mantidas_en_sem_traducao']/total*100:.1f}%)")
    print(f"  Strings obsoletas REMOVIDAS:       {max(0, stats['obsoletas_removidas']):>7,}")
    print(f"  Total no arquivo reconstruído:     {len(new_strings):>7,}")
    print("=" * 60)

    if stats_only or dry_run:
        if dry_run:
            print(f"\n[DRY-RUN] Seria gerado: {OUTPUT_PATH.name}")
            print("Use sem --dry-run para gerar o arquivo.")
        return 0

    # Salvar arquivo reconstruído
    new_data = {"strings": new_strings}

    if apply:
        backup = TRADUCAO_PATH.with_suffix(".json.bak")
        shutil.copy2(TRADUCAO_PATH, backup)
        print(f"\nBackup salvo em: {backup.name}")
        out_path = TRADUCAO_PATH
        print(f"Substituindo {TRADUCAO_PATH.name}...")
    else:
        out_path = OUTPUT_PATH
        print(f"\nSalvando em {OUTPUT_PATH.name}...")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print(f"Arquivo salvo: {out_path.name} ({out_path.stat().st_size / 1024 / 1024:.1f} MB)")
    print()
    if not apply:
        print("Para adotar o arquivo reconstruído:")
        print(f"  cp {OUTPUT_PATH.name} {TRADUCAO_PATH.name}")
        print("  python3 scripts/validate.py")
        print("  python3 scripts/relatorio.py")
    else:
        print("Próximos passos:")
        print("  python3 scripts/translate_batch.py   — traduzir as strings em inglês")
        print("  python3 scripts/validate.py          — validar integridade")
        print("  python3 scripts/relatorio.py         — ver qualidade")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Reconstrói enGB.json do zero a partir do original EN"
    )
    parser.add_argument("--dry-run", action="store_true", help="Simular sem salvar")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Substituir enGB.json diretamente (faz backup automático)",
    )
    parser.add_argument("--stats", action="store_true", help="Mostrar apenas estatísticas")
    args = parser.parse_args()
    sys.exit(run(dry_run=args.dry_run, apply=args.apply, stats_only=args.stats))


if __name__ == "__main__":
    main()
