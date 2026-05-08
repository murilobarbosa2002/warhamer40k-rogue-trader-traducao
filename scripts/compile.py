#!/usr/bin/env python3
"""
compile.py — Reconstrói enGB.json a partir dos arquivos src/strings/<categoria>.json

Lê todos os arquivos de src/strings/, mescla as traduções PT e reconstrói
o enGB.json preservando a estrutura original (Offset e UUID intactos).

O enGB.json gerado é o artefato final para o mod do jogo.

Uso:
    python3 scripts/compile.py              # reconstruir enGB.json
    python3 scripts/compile.py --dry-run    # simular sem salvar
    python3 scripts/compile.py --stats      # apenas exibir estatísticas
    python3 scripts/compile.py --validar    # compilar e validar em seguida
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ENDB_PATH = ROOT / "enGB.json"
ORIG_PATH = ROOT / "arquivo-original-1.5.0.320.json"
SRC_DIR = ROOT / "src" / "strings"

CATEGORY_ORDER = [
    "ui", "tutorial", "combate", "enciclopedia", "itens",
    "missoes", "personagens", "dialogo", "outros"
]


def run(dry_run: bool, stats_only: bool, validar: bool) -> int:
    # Verificar que src/strings/ existe
    if not SRC_DIR.exists():
        print(f"ERRO: {SRC_DIR} não encontrado.")
        print("Rode primeiro: python3 scripts/split.py")
        return 1

    # Carregar arquivo original para preservar Offset e ordem
    if not ORIG_PATH.exists():
        print(f"ERRO: {ORIG_PATH.name} não encontrado.")
        return 1
    print(f"Carregando {ORIG_PATH.name}...")
    with open(ORIG_PATH, encoding="utf-8") as f:
        orig_data = json.load(f)
    en_strings = orig_data["strings"]

    # Carregar todos os arquivos src/strings/*.json
    print(f"Carregando src/strings/...")
    src_entries: dict[str, dict] = {}
    stats = {"approved": 0, "machine": 0, "pending": 0, "sem_status": 0}

    for cat in CATEGORY_ORDER:
        cat_path = SRC_DIR / f"{cat}.json"
        if not cat_path.exists():
            continue
        with open(cat_path, encoding="utf-8") as f:
            cat_data = json.load(f)
        for uuid, entry in cat_data.items():
            src_entries[uuid] = entry
            status = entry.get("status", "sem_status")
            if status in stats:
                stats[status] += 1
            else:
                stats["sem_status"] += 1

    total_src = len(src_entries)
    print(f"  {total_src:,} strings carregadas dos arquivos src/")

    # Estatísticas
    total_traduzidas = stats["approved"] + stats["machine"]
    pct = round(total_traduzidas / total_src * 100, 1) if total_src > 0 else 0
    print()
    print("=" * 50)
    print("  ESTATÍSTICAS")
    print("=" * 50)
    print(f"  Aprovadas:    {stats['approved']:6,}")
    print(f"  Máquina:      {stats['machine']:6,}")
    print(f"  Pendentes:    {stats['pending']:6,}")
    print(f"  Progresso:    {pct}%")
    print()

    if stats_only:
        return 0

    # Montar enGB.json mantendo estrutura original (Offset intacto)
    print("Construindo enGB.json...")
    new_strings = {}
    n_pt = 0
    n_en_fallback = 0

    for uuid, en_entry in en_strings.items():
        offset = en_entry["Offset"]
        if uuid in src_entries:
            src = src_entries[uuid]
            pt_text = src.get("pt", en_entry["Text"])
            # Se pendente, usar EN como fallback (não inserir tradução errada)
            if src.get("status") == "pending":
                pt_text = en_entry["Text"]
                n_en_fallback += 1
            else:
                n_pt += 1
        else:
            # UUID não está nos src/ (não deveria acontecer) — usar EN
            pt_text = en_entry["Text"]
            n_en_fallback += 1

        new_strings[uuid] = {
            "Offset": offset,
            "Text": pt_text,
        }

    new_data = {"strings": new_strings}

    if dry_run:
        print(f"[DRY-RUN] Seriam escritas {n_pt:,} strings PT, {n_en_fallback:,} fallback EN")
        return 0

    # Salvar
    print(f"Salvando {ENDB_PATH.name}...")
    with open(ENDB_PATH, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 50)
    print(f"  RESULTADO")
    print("=" * 50)
    print(f"  Strings PT aplicadas:  {n_pt:,}")
    print(f"  Fallback EN (pendente):{n_en_fallback:,}")
    print(f"  Total no enGB.json:    {len(new_strings):,}")
    print()

    if validar:
        print("Validando resultado...")
        import subprocess
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate.py")],
            cwd=ROOT
        )
        return result.returncode

    print("OK — enGB.json reconstruído.")
    print("Para validar: python3 scripts/validate.py")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Reconstrói enGB.json a partir de src/strings/")
    parser.add_argument("--dry-run", action="store_true", help="Simular sem salvar")
    parser.add_argument("--stats", action="store_true", help="Apenas exibir estatísticas")
    parser.add_argument("--validar", action="store_true", help="Validar após compilar")
    args = parser.parse_args()
    sys.exit(run(dry_run=args.dry_run, stats_only=args.stats, validar=args.validar))


if __name__ == "__main__":
    main()
