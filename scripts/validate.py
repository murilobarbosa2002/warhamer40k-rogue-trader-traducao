#!/usr/bin/env python3
"""
validate.py — Valida a integridade estrutural do enGB.json.
Uso: python3 scripts/validate.py
Retorna exit code 0 se válido, 1 se inválido.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENDB_PATH = ROOT / "enGB.json"

ERRORS = []
WARNINGS = []


def error(msg):
    ERRORS.append(msg)


def warn(msg):
    WARNINGS.append(msg)


def validate():
    print(f"Validando {ENDB_PATH.name}...")

    # 1. JSON válido
    try:
        with open(ENDB_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        error(f"JSON INVALIDO: {e}")
        return

    # 2. Estrutura raiz
    if "strings" not in data:
        error("Chave 'strings' ausente na raiz do JSON")
        return

    strings = data["strings"]
    print(f"  Total de strings: {len(strings)}")

    tag_open = re.compile(r'\{g\|[^}]+\}')
    tag_close = re.compile(r'\{/g\}')
    uip_tag = re.compile(r'\{uip\|[^}]+\}')
    unit_stat_tag = re.compile(r'\{unit_stat\|[^}]+\}')

    for uuid, entry in strings.items():
        # 3. Campos obrigatórios
        if "Offset" not in entry:
            error(f"[{uuid[:8]}] Campo 'Offset' ausente")
        if "Text" not in entry:
            error(f"[{uuid[:8]}] Campo 'Text' ausente")
            continue

        text = entry["Text"]

        # 4. Tags g balanceadas
        opens = len(tag_open.findall(text))
        closes = len(tag_close.findall(text))
        if opens != closes:
            error(f"[{uuid[:8]}] Tags {{g|..}} desbalanceadas ({opens} abertas, {closes} fechadas): {text[:80]}")

        # 5. Tags n balanceadas
        n_opens = text.count("{n}")
        n_closes = text.count("{/n}")
        if n_opens != n_closes:
            error(f"[{uuid[:8]}] Tags {{n}} desbalanceadas: {text[:80]}")

        # 6. Tags d balanceadas
        d_opens = len(re.findall(r'\{d\|[^}]+\}', text))
        d_closes = text.count("{/d}")
        if d_opens != d_closes:
            error(f"[{uuid[:8]}] Tags {{d|..}} desbalanceadas: {text[:80]}")

        # 7. Texto não deve ser None ou ter tipo errado
        if not isinstance(text, str):
            error(f"[{uuid[:8]}] Campo 'Text' não é string: {type(text)}")

    total = len(strings)
    erros = len(ERRORS)
    avisos = len(WARNINGS)

    print()
    print("=" * 50)
    print("  RESULTADO DA VALIDACAO")
    print("=" * 50)

    if ERRORS:
        print(f"\nERROS ({erros}):")
        for e in ERRORS[:20]:
            print(f"  [ERRO] {e}")
        if erros > 20:
            print(f"  ... e mais {erros - 20} erros")

    if WARNINGS:
        print(f"\nAVISOS ({avisos}):")
        for w in WARNINGS[:10]:
            print(f"  [AVISO] {w}")

    if not ERRORS:
        print(f"\n  OK — {total} strings validadas sem erros estruturais")
    else:
        print(f"\n  FALHOU — {erros} erro(s) encontrado(s)")

    return len(ERRORS) == 0


if __name__ == "__main__":
    ok = validate()
    sys.exit(0 if ok else 1)
