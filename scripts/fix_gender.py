#!/usr/bin/env python3
"""
fix_gender.py — Corrige erros de concordância de gênero herdados da tradução automática.

A tradução com Google Translate gerou ~112 casos de concordância de gênero errada.
Os mais comuns:
  - "o nave" → "a nave"   (nave é feminino)
  - "um nave" → "uma nave"
  - "no nave" → "na nave"
  - "do nave" → "da nave"
  - "ao nave" → "à nave"

Este script aplica substituições seguras e contextuais,
apenas fora de tags {..} e sem alterar nomes próprios.

Uso:
    python3 scripts/fix_gender.py --dry-run    # simular
    python3 scripts/fix_gender.py              # aplicar
    python3 scripts/fix_gender.py --stats      # mostrar apenas contagens
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ENDB_PATH = ROOT / "enGB.json"

TAG_RE = re.compile(r"\{[^}]+\}|<[^>]+>")


def replace_outside_tags(pattern: str, replacement: str, text: str, flags=re.IGNORECASE) -> str:
    """Aplica substituição apenas fora de tags {..} e <..>."""
    result = []
    last = 0
    for m in TAG_RE.finditer(text):
        segment = text[last:m.start()]
        segment = re.sub(pattern, replacement, segment, flags=flags)
        result.append(segment)
        result.append(m.group())
        last = m.end()
    result.append(re.sub(pattern, replacement, text[last:], flags=flags))
    return "".join(result)


# Cada regra: (padrão, substituição, descrição)
# IMPORTANTE: substituições conservadoras, apenas casos inequívocos
REGRAS = [
    # "nave" é feminino
    (r"\bo nave\b", "a nave", '"o nave" → "a nave"'),
    (r"\bum nave\b", "uma nave", '"um nave" → "uma nave"'),
    (r"\bno nave\b", "na nave", '"no nave" → "na nave"'),
    (r"\bdo nave\b", "da nave", '"do nave" → "da nave"'),
    (r"\bpelo nave\b", "pela nave", '"pelo nave" → "pela nave"'),
    (r"\bao nave\b", "à nave", '"ao nave" → "à nave"'),
    (r"\bdesse nave\b", "dessa nave", '"desse nave" → "dessa nave"'),
    (r"\bneste nave\b", "nesta nave", '"neste nave" → "nesta nave"'),
    # "missão" é feminino
    (r"\bo missão\b", "a missão", '"o missão" → "a missão"'),
    (r"\bum missão\b", "uma missão", '"um missão" → "uma missão"'),
    (r"\bno missão\b", "na missão", '"no missão" → "na missão"'),
    (r"\bdo missão\b", "da missão", '"do missão" → "da missão"'),
    # "habilidade" é feminino
    (r"\bo habilidade\b", "a habilidade", '"o habilidade" → "a habilidade"'),
    (r"\bum habilidade\b", "uma habilidade", '"um habilidade" → "uma habilidade"'),
    (r"\bdo habilidade\b", "da habilidade", '"do habilidade" → "da habilidade"'),
    (r"\bno habilidade\b", "na habilidade", '"no habilidade" → "na habilidade"'),
    # "ação" é feminino
    (r"\bo ação\b", "a ação", '"o ação" → "a ação"'),
    (r"\bdo ação\b", "da ação", '"do ação" → "da ação"'),
    (r"\bno ação\b", "na ação", '"no ação" → "na ação"'),
    # "rodada" é feminino
    (r"\bo rodada\b", "a rodada", '"o rodada" → "a rodada"'),
    (r"\bum rodada\b", "uma rodada", '"um rodada" → "uma rodada"'),
    (r"\bdo rodada\b", "da rodada", '"do rodada" → "da rodada"'),
    # "escolha uma alvo" — alvo é masculino
    (r"\buma alvo\b", "um alvo", '"uma alvo" → "um alvo"'),
    (r"\bessa alvo\b", "esse alvo", '"essa alvo" → "esse alvo"'),
    (r"\bnessa alvo\b", "nesse alvo", '"nessa alvo" → "nesse alvo"'),
    # artigos duplicados óbvios (gerados por tradução literal)
    (r"\bpara para\b", "para", '"para para" → "para"'),
    (r"\bem em\b", "em", '"em em" → "em"'),
    (r"\bde de\b", "de", '"de de" → "de"'),
    (r"\bda da\b", "da", '"da da" → "da"'),
    (r"\bdo do\b", "do", '"do do" → "do"'),
]


def run(dry_run: bool, stats_only: bool) -> int:
    print("Carregando enGB.json...")
    with open(ENDB_PATH, encoding="utf-8") as f:
        data = json.load(f)
    strings = data["strings"]

    # Contar ocorrências por regra
    counts = {desc: 0 for _, _, desc in REGRAS}
    total_afetadas = 0

    for key, entry in strings.items():
        text = entry["Text"]
        modified = text
        afetada = False
        for pattern, replacement, desc in REGRAS:
            new = replace_outside_tags(pattern, replacement, modified)
            if new != modified:
                n = len(re.findall(pattern, TAG_RE.sub("", modified), re.IGNORECASE))
                counts[desc] += n
                modified = new
                afetada = True
        if afetada:
            total_afetadas += 1
            if not dry_run and not stats_only:
                strings[key]["Text"] = modified

    # Relatório
    print()
    print("=" * 58)
    print("  CORREÇÕES DE CONCORDÂNCIA DE GÊNERO")
    if dry_run:
        print("  [DRY-RUN] nenhuma alteração será salva")
    print("=" * 58)
    total_correcoes = sum(counts.values())
    for desc, count in counts.items():
        if count > 0:
            print(f"  {count:>4}x  {desc}")
    print()
    print(f"  Total de correções:   {total_correcoes:>4}")
    print(f"  Strings afetadas:     {total_afetadas:>4}")
    print("=" * 58)

    if stats_only or dry_run:
        if dry_run:
            print("\nPara aplicar, execute sem --dry-run")
        return 0

    if total_correcoes == 0:
        print("\nNenhuma correção necessária.")
        return 0

    print(f"\nSalvando enGB.json ({total_correcoes} correções em {total_afetadas} strings)...")
    with open(ENDB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Salvo.")
    print()
    print("Próximos passos:")
    print("  python3 scripts/validate.py")
    print('  git add enGB.json && git commit -m "fix(gênero): corrige concordância de gênero automática"')
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Corrige erros de concordância de gênero no enGB.json"
    )
    parser.add_argument("--dry-run", action="store_true", help="Simular sem salvar")
    parser.add_argument("--stats", action="store_true", help="Mostrar apenas contagens")
    args = parser.parse_args()
    sys.exit(run(dry_run=args.dry_run, stats_only=args.stats))


if __name__ == "__main__":
    main()
