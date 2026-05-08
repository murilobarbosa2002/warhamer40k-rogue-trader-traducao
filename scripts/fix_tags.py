#!/usr/bin/env python3
"""
fix_tags.py — Repara tags {g|..}{/g} desbalanceadas comparando com o original EN.

O enGB.json herdado tem 193 strings com tags desbalanceadas (abertas ≠ fechadas).
Este script tenta reparar automaticamente cada caso comparando a estrutura de tags
do texto PT-BR com a do original EN, e adicionando ou removendo {/g} onde necessário.

Estratégia:
  - Se PT tem mais {g| que {/g} (falta fechar): adiciona {/g} no fim
  - Se PT tem mais {/g} que {g| (tag extra): remove o {/g} excedente
  - Casos ambíguos (diferença > 1): exporta para revisão manual

Uso:
    python3 scripts/fix_tags.py --dry-run      # simular, não salvar
    python3 scripts/fix_tags.py                # aplicar correções automáticas
    python3 scripts/fix_tags.py --export       # exportar casos ambíguos para revisão
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
TRADUCAO_PATH = ROOT / "enGB.json"
ORIGINAL_PATH = ROOT / "arquivo-original-1.5.0.320.json"
EXPORT_PATH = ROOT / "revisao-tags-manuais.json"

OPEN_TAG = re.compile(r"\{g\|[^}]+\}")
CLOSE_TAG = re.compile(r"\{/g\}")


def count_tags(text: str) -> tuple[int, int]:
    """Retorna (abertas, fechadas)."""
    return len(OPEN_TAG.findall(text)), len(CLOSE_TAG.findall(text))


def is_balanced(text: str) -> bool:
    a, f = count_tags(text)
    return a == f


def try_fix(pt_text: str, en_text: str) -> tuple[str | None, str]:
    """
    Tenta reparar as tags do pt_text comparando com en_text.
    Retorna (texto_corrigido | None, motivo).
    None = não foi possível reparar automaticamente.
    """
    pt_open, pt_close = count_tags(pt_text)
    diff = pt_open - pt_close

    if diff == 0:
        return pt_text, "já balanceado"

    if abs(diff) > 2:
        return None, f"diferença muito grande ({diff:+d}), requer revisão manual"

    if diff > 0:
        # Faltam {/g} — adicionar no final (após o último texto visível)
        fixed = pt_text
        for _ in range(diff):
            # Adicionar {/g} antes de qualquer tag de fechamento de bloco,
            # ou simplesmente no fim do texto se não houver ponto óbvio
            # Estratégia: inserir antes de {/n} ou {/d} se existirem, senão no fim
            if "{/n}" in fixed:
                fixed = fixed.replace("{/n}", "{/g}{/n}", 1)
            elif "{/d}" in fixed:
                fixed = fixed.replace("{/d}", "{/g}{/d}", 1)
            else:
                fixed = fixed + "{/g}"
        return fixed, f"adicionou {diff}x {{/g}}"

    else:
        # Tem {/g} a mais — remover os excedentes do fim
        fixed = pt_text
        excess = abs(diff)
        # Remove {/g} extras do final (última ocorrência primeiro)
        for _ in range(excess):
            pos = fixed.rfind("{/g}")
            if pos == -1:
                break
            fixed = fixed[:pos] + fixed[pos + 4:]
        return fixed, f"removeu {excess}x {{/g}} excedente"


def run(dry_run: bool, export_ambiguous: bool) -> int:
    if not TRADUCAO_PATH.exists():
        print(f"ERRO: {TRADUCAO_PATH.name} não encontrado.")
        return 1

    orig_strings = {}
    if ORIGINAL_PATH.exists():
        with open(ORIGINAL_PATH, encoding="utf-8") as f:
            orig_strings = json.load(f)["strings"]

    print("Carregando enGB.json...")
    with open(TRADUCAO_PATH, encoding="utf-8") as f:
        data = json.load(f)
    strings = data["strings"]

    # Encontrar strings desbalanceadas
    broken = {
        k: v for k, v in strings.items()
        if not is_balanced(v["Text"])
    }

    print(f"Strings com tags desbalanceadas: {len(broken)}")

    fixed_count = 0
    skipped_count = 0
    ambiguous = {}

    for key, entry in broken.items():
        pt_text = entry["Text"]
        en_text = orig_strings.get(key, {}).get("Text", "")
        pt_open, pt_close = count_tags(pt_text)

        result, reason = try_fix(pt_text, en_text)

        if result is None:
            skipped_count += 1
            ambiguous[key] = {
                "pt": pt_text,
                "en": en_text,
                "pt_open": pt_open,
                "pt_close": pt_close,
                "motivo": reason,
            }
        else:
            a2, f2 = count_tags(result)
            if a2 == f2:
                if not dry_run:
                    strings[key]["Text"] = result
                fixed_count += 1
            else:
                # Correção não resultou em balanço — tratar como ambíguo
                skipped_count += 1
                ambiguous[key] = {
                    "pt": pt_text,
                    "en": en_text,
                    "pt_open": pt_open,
                    "pt_close": pt_close,
                    "motivo": f"tentativa falhou ({reason})",
                }

    print()
    print("=" * 55)
    print("  RESULTADO")
    print("=" * 55)
    print(f"  Reparadas automaticamente:  {fixed_count:>4}")
    print(f"  Requerem revisão manual:    {skipped_count:>4}")
    print("=" * 55)

    if export_ambiguous and ambiguous:
        with open(EXPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(ambiguous, f, ensure_ascii=False, indent=2)
        print(f"\nExportados {len(ambiguous)} casos para: {EXPORT_PATH.name}")
        print("Revise manualmente e depois atualize enGB.json.")

    if dry_run:
        print("\n[DRY-RUN] Nenhuma alteração foi salva.")
        print("Remova --dry-run para aplicar.")
        return 0

    if fixed_count > 0:
        print(f"\nSalvando enGB.json ({fixed_count} correções)...")
        with open(TRADUCAO_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Salvo.")
        print()
        print("Próximos passos:")
        print("  python3 scripts/validate.py")
        print('  git add enGB.json && git commit -m "fix(tags): repara tags desbalanceadas herdadas"')
    else:
        print("\nNenhuma correção automática possível.")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Repara tags {g|..}{/g} desbalanceadas no enGB.json"
    )
    parser.add_argument("--dry-run", action="store_true", help="Simular sem salvar")
    parser.add_argument(
        "--export",
        action="store_true",
        help=f"Exportar casos ambíguos para {EXPORT_PATH.name}",
    )
    args = parser.parse_args()
    sys.exit(run(dry_run=args.dry_run, export_ambiguous=args.export))


if __name__ == "__main__":
    main()
