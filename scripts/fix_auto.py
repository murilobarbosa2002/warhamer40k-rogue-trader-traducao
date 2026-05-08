#!/usr/bin/env python3
"""
fix_auto.py — Aplica correções automáticas e seguras no enGB.json.

Uso:
    python3 scripts/fix_auto.py              # aplica tudo
    python3 scripts/fix_auto.py --dry-run    # mostra sem alterar
    python3 scripts/fix_auto.py --modo terminologia
    python3 scripts/fix_auto.py --modo artigos
    python3 scripts/fix_auto.py --modo mp-pm
    python3 scripts/fix_auto.py --modo ap-pa
"""

import json
import re
import argparse
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
ENDB_PATH = ROOT / "enGB.json"

# ──────────────────────────────────────────────────────────────────────────────
# Regras: (grupo, pattern, replacement, description)
# callable replacement: recebe o match, retorna string
# ──────────────────────────────────────────────────────────────────────────────
def _cooldown_rep(m):
    return "recargas" if m.group().lower().endswith('s') else "recarga"

RULES = [
    # grupo mp-pm
    ("mp-pm",        r'\bMP\b',             "PM",                    "MP → PM (Pontos de Movimento)"),
    # grupo ap-pa
    ("ap-pa",        r'\bAP\b',             "PA",                    "AP → PA (Pontos de Ação)"),
    # grupo terminologia
    ("terminologia", r'\bcooldowns?\b',     _cooldown_rep,           "cooldown(s) → recarga(s)"),
    ("terminologia", r'\bdebuffs?\b',       "penalidade de efeito",  "debuff(s) → penalidade de efeito"),
    ("terminologia", r'\bbuff\b(?!er|et)',  "aprimoramento",         "buff → aprimoramento"),
    ("terminologia", r'\btalents\b',        "talentos",              "talents → talentos"),
    ("terminologia", r'\btalent\b',         "talento",               "talent → talento"),
    ("terminologia", r'\bNPCs\b',           "PNJs",                  "NPCs → PNJs"),
    ("terminologia", r'\bNPC\b',            "PNJ",                   "NPC → PNJ"),
    # grupo artigos
    ("artigos",      r'\bde de\b',          "de",                    '"de de" duplicado'),
    ("artigos",      r'\bque que\b',        "que",                   '"que que" duplicado'),
    ("artigos",      r'\bpara para\b',      "para",                  '"para para" duplicado'),
    ("artigos",      r'\bo o\b',            "o",                     '"o o" duplicado'),
    ("artigos",      r'\bum um\b',          "um",                    '"um um" duplicado'),
]

GRUPOS = {
    "tudo":         None,
    "mp-pm":        ["mp-pm"],
    "ap-pa":        ["ap-pa"],
    "terminologia": ["terminologia"],
    "artigos":      ["artigos"],
}


def inside_tag(text, start):
    before = text[:start]
    return before.count('{') > before.count('}')


def apply_rule(text, pattern, replacement):
    count = 0
    parts = []
    last = 0
    for m in re.finditer(pattern, text, re.IGNORECASE):
        parts.append(text[last:m.start()])
        if inside_tag(text, m.start()):
            parts.append(m.group())
        else:
            rep = replacement(m) if callable(replacement) else replacement
            parts.append(rep)
            count += 1
        last = m.end()
    parts.append(text[last:])
    return ''.join(parts), count


def run(dry_run, modo, verbose):
    if not ENDB_PATH.exists():
        print(f"Arquivo nao encontrado: {ENDB_PATH}", file=sys.stderr)
        return 1

    size_mb = ENDB_PATH.stat().st_size // 1024 // 1024
    print(f"Carregando enGB.json ({size_mb} MB)...")
    with open(ENDB_PATH, encoding="utf-8") as f:
        data = json.load(f)

    strings = data["strings"]
    allowed = GRUPOS.get(modo)
    active = [(g, p, r, d) for g, p, r, d in RULES if allowed is None or g in allowed]

    total = 0
    counts = defaultdict(int)
    examples = defaultdict(list)

    for uuid, entry in strings.items():
        original = entry["Text"]
        current = original
        for grupo, pattern, replacement, desc in active:
            new_text, n = apply_rule(current, pattern, replacement)
            if n:
                counts[desc] += n
                if len(examples[desc]) < 3:
                    examples[desc].append((uuid, original[:80]))
                current = new_text
                total += n
        if not dry_run and current != original:
            strings[uuid]["Text"] = current

    print()
    print("=" * 62)
    print("  RELATORIO DE CORRECOES AUTOMATICAS")
    if dry_run:
        print("  [DRY-RUN] nenhuma alteracao foi salva")
    print("=" * 62)

    if total == 0:
        print("Nenhuma correcao necessaria. Arquivo ja esta consistente.")
        return 0

    for desc, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"\n  {n:4d}x  {desc}")
        if verbose:
            for uuid, preview in examples[desc]:
                print(f"           [{uuid[:8]}] {preview}")

    print(f"\n  TOTAL: {total} substituicoes")

    if dry_run:
        print("\nPara aplicar, execute sem --dry-run")
        return 0

    print("\nSalvando enGB.json...")
    with open(ENDB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Arquivo salvo com sucesso.")
    print("\nProximos passos:")
    print("  python3 scripts/validate.py")
    print("  git add enGB.json")
    print('  git commit -m "fix(auto): correcoes automaticas de terminologia PT-BR"')
    return 0


def main():
    parser = argparse.ArgumentParser(description="Correcoes automaticas WH40K PT-BR")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--modo", default="tudo", choices=list(GRUPOS.keys()))
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    sys.exit(run(dry_run=args.dry_run, modo=args.modo, verbose=not args.quiet))


if __name__ == "__main__":
    main()
