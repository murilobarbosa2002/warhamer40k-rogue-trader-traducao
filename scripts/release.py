#!/usr/bin/env python3
"""
release.py — Empacota o enGB.json em uma release versionada.

Cria uma pasta releases/<versao>/ com:
  - enGB.json   (o arquivo do mod, pronto para instalar)
  - LEIAME.txt  (instruções de instalação em PT-BR)

Também atualiza CHANGELOG.md com a nova release.

Uso:
    python3 scripts/release.py                         # release interativa
    python3 scripts/release.py --versao 1.5.0.320-v1  # versão específica
    python3 scripts/release.py --dry-run               # simular
"""

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
ENDB_PATH = ROOT / "enGB.json"
RELEASES_DIR = ROOT / "releases"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
ORIGINAL_PATH = ROOT / "arquivo-original-1.5.0.320.json"

LEIAME_TEMPLATE = """WH40K: Rogue Trader — Tradução PT-BR
Versão: {versao}
Data: {data}
Repositório: https://github.com/murilobarbosa2002/warhamer40k-rogue-trader-traducao

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMO INSTALAR
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Localize a pasta de localização do jogo:
   Steam: <SteamLibrary>/steamapps/common/Warhammer 40000 Rogue Trader/Bundles/localization/

2. Faça backup do arquivo original:
   Renomeie  enGB.json  para  enGB.json.backup

3. Copie o arquivo enGB.json desta pasta para o diretório de localização.

4. Inicie o jogo. A tradução será carregada automaticamente.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPATIBILIDADE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Compatível com a versão {versao_jogo} do jogo.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESTADO DA TRADUÇÃO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{stats}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REPORTAR ERROS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Encontrou um erro de tradução? Abra uma issue em:
https://github.com/murilobarbosa2002/warhamer40k-rogue-trader-traducao/issues

Quer contribuir? Veja o CONTRIBUTING.md no repositório.
"""


def get_stats() -> str:
    """Retorna estatísticas básicas de tradução."""
    try:
        with open(ENDB_PATH, encoding="utf-8") as f:
            trad = json.load(f)
        total = len(trad["strings"])

        orig_total = total
        if ORIGINAL_PATH.exists():
            with open(ORIGINAL_PATH, encoding="utf-8") as f:
                orig = json.load(f)
            orig_total = len(orig["strings"])

            # Contar traduzidas (texto diferente do EN)
            TAG_RE = re.compile(r"\{[^}]+\}|<[^>]+>")
            traduzidas = 0
            for k, v in orig["strings"].items():
                if k in trad["strings"]:
                    en = TAG_RE.sub("", v["Text"]).strip()
                    pt = TAG_RE.sub("", trad["strings"][k]["Text"]).strip()
                    if en.lower() != pt.lower() and len(en) > 5:
                        traduzidas += 1
                    elif len(en) <= 5:
                        traduzidas += 1  # curtas: contar como traduzidas
            pct = traduzidas / orig_total * 100 if orig_total > 0 else 0
            return (
                f"Total de strings: {orig_total:,}\n"
                f"Traduzidas: ~{traduzidas:,} ({pct:.1f}%)\n"
                f"Ainda em inglês: ~{orig_total - traduzidas:,} ({100-pct:.1f}%)"
            )
        return f"Total de strings: {total:,}"
    except Exception:
        return "Estatísticas indisponíveis."


def update_changelog(versao: str, data_str: str) -> None:
    """Adiciona a nova release à tabela do CHANGELOG.md."""
    if not CHANGELOG_PATH.exists():
        return
    content = CHANGELOG_PATH.read_text(encoding="utf-8")
    release_file = f"releases/{versao}.md"
    nova_linha = f"| {versao} | {data_str} | [{release_file}]({release_file}) | ✅ Released |\n"
    # Inserir após o cabeçalho da tabela
    content = content.replace(
        "| Em desenvolvimento | — | [releases/unreleased.md](releases/unreleased.md) | 🔄 Unreleased |\n",
        nova_linha
        + "| Em desenvolvimento | — | [releases/unreleased.md](releases/unreleased.md) | 🔄 Unreleased |\n",
    )
    CHANGELOG_PATH.write_text(content, encoding="utf-8")


def run(versao: str, dry_run: bool) -> int:
    if not ENDB_PATH.exists():
        print(f"ERRO: {ENDB_PATH.name} não encontrado.")
        return 1

    today = date.today()
    data_str = today.strftime("%Y-%m-%d")

    # Versão padrão baseada na data se não informada
    if not versao:
        versao = f"1.5.0.320-ptbr-{today.strftime('%Y%m%d')}"

    release_dir = RELEASES_DIR / versao

    print(f"Release: {versao}")
    print(f"Pasta:   {release_dir}")
    print()

    if release_dir.exists() and not dry_run:
        print(f"AVISO: A pasta {release_dir} já existe.")
        resp = input("Sobrescrever? [s/N] ").strip().lower()
        if resp != "s":
            print("Cancelado.")
            return 0

    stats = get_stats()
    print("Estatísticas da release:")
    for linha in stats.splitlines():
        print(f"  {linha}")
    print()

    if dry_run:
        print("[DRY-RUN] Seria criado:")
        print(f"  {release_dir}/enGB.json")
        print(f"  {release_dir}/LEIAME.txt")
        print(f"  {release_dir}/{versao}.md")
        print(f"  CHANGELOG.md atualizado")
        return 0

    # Criar pasta da release
    release_dir.mkdir(parents=True, exist_ok=True)

    # Copiar enGB.json
    shutil.copy2(ENDB_PATH, release_dir / "enGB.json")
    print(f"✓ {release_dir}/enGB.json")

    # Gerar LEIAME.txt
    # Extrair versão do jogo da versão da release
    versao_jogo = versao.split("-ptbr")[0] if "-ptbr" in versao else "1.5.0.320"
    leiame = LEIAME_TEMPLATE.format(
        versao=versao,
        data=data_str,
        versao_jogo=versao_jogo,
        stats=stats,
    )
    (release_dir / "LEIAME.txt").write_text(leiame, encoding="utf-8")
    print(f"✓ {release_dir}/LEIAME.txt")

    # Gerar arquivo de notas da release
    notas_path = release_dir / f"{versao}.md"
    notas = f"# Release {versao}\n\n**Data:** {data_str}\n\n## Estado da tradução\n\n{stats}\n\n## Mudanças\n\n> Descreva as mudanças desta release aqui.\n\n## Instalação\n\nVeja o [README.md](../../README.md#instalação-do-mod).\n"
    notas_path.write_text(notas, encoding="utf-8")
    print(f"✓ {notas_path}")

    # Atualizar CHANGELOG
    update_changelog(versao, data_str)
    print(f"✓ CHANGELOG.md atualizado")

    print()
    print(f"Release {versao} criada em {release_dir}")
    print()
    print("Próximos passos:")
    print(f"  git add releases/{versao}/ CHANGELOG.md")
    print(f'  git commit -m "release: {versao}"')
    print(f"  git tag {versao}")
    print(f"  git push && git push --tags")
    print()
    print("Para publicar no GitHub Releases:")
    print(f"  gh release create {versao} releases/{versao}/enGB.json --title 'PT-BR {versao}' --notes-file releases/{versao}/{versao}.md")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Empacota uma release do mod")
    parser.add_argument("--versao", default="", help="Nome da versão (ex: 1.5.0.320-ptbr-v1)")
    parser.add_argument("--dry-run", action="store_true", help="Simular sem criar arquivos")
    args = parser.parse_args()
    sys.exit(run(versao=args.versao, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
