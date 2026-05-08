#!/usr/bin/env python3
"""
split.py — Migra enGB.json para a arquitetura src/strings/<categoria>.json

Lê enGB.json (PT-BR atual) e arquivo-original-1.5.0.320.json (EN fonte),
e cria um arquivo JSON por categoria em src/strings/.

Formato de cada arquivo gerado:
  {
    "uuid": {
      "en": "texto original em inglês",
      "pt": "texto traduzido em português",
      "status": "approved|machine|pending"
    }
  }

Status atribuídos:
  - "approved"  → texto PT é diferente do EN e parece português
  - "machine"   → traduzido por IA (texto PT difere do EN mas pode ter erros)
  - "pending"   → string ainda não traduzida (PT == EN ou vazia)

Uso:
    python3 scripts/split.py              # migra e cria src/strings/
    python3 scripts/split.py --dry-run    # mostra estatísticas sem criar arquivos
    python3 scripts/split.py --stats      # apenas exibe estatísticas por categoria
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ENDB_PATH = ROOT / "enGB.json"
ORIG_PATH = ROOT / "arquivo-original-1.5.0.320.json"
SRC_DIR = ROOT / "src" / "strings"
GLOSSARIO_PATH = ROOT / "glossario.json"

TAG_RE = re.compile(r"\{[^}]+\}|<[^>]+>")

PT_RE = re.compile(
    r"\b(de|da|do|das|dos|em|para|uma|um|com|que|não|são|foi|ser|tem"
    r"|ter|você|este|essa|quando|mais|pode|deve|sobre|entre|também|já"
    r"|pelo|pela|pelos|pelas|numa|num|ao|aos|à|às|se|ou|e|mas|pois)\b",
    re.IGNORECASE,
)
EN_RE = re.compile(
    r"\b(the|and|or|is|are|was|were|will|would|can|could|should|have"
    r"|has|had|this|that|these|those|with|from|they|their|you|your)\b",
    re.IGNORECASE,
)

CATEGORIES = [
    ("ui", re.compile(
        r"\b(button|click|menu|screen|panel|icon|interface|cursor|window"
        r"|settings|option|save|load|confirm|cancel|toggle|slider"
        r"|botão|clique|tela|painel|ícone|janela|configuração|salvar|carregar)\b", re.I
    )),
    ("tutorial", re.compile(
        r"\b(tip|hint|tutorial|learn|how to|step|guide"
        r"|dica|tutorial|aprenda|como|ajuda)\b", re.I
    )),
    ("combate", re.compile(
        r"\b(damage|attack|defense|round|turn|range|cooldown|cover|dodge|charge"
        r"|wound|action point|movement point|ability|passive|talent|skill"
        r"|dano|ataque|rodada|turno|alcance|recarga|cobertura|esquiva|investida"
        r"|ferimento|habilidade|passivo|talento|perícia)\b", re.I
    )),
    ("enciclopedia", re.compile(
        r"\b(trait|origin|faction|history|lore|knowledge|belief|dogma|ritual"
        r"|característica|origem|facção|história|conhecimento|crença|dogma)\b", re.I
    )),
    ("itens", re.compile(
        r"\b(weapon|armor|implant|modification|ammunition|gear|item|equipment"
        r"|relic|bolter|lasgun|plasma|melta|flamer|chainsword|power sword"
        r"|arma|armadura|implante|modificação|munição|equipamento|relíquia)\b", re.I
    )),
    ("missoes", re.compile(
        r"\b(mission|objective|task|reward|failure|success|colony|planet"
        r"|system|sector|exploration|quest"
        r"|missão|objetivo|tarefa|recompensa|falha|sucesso|colônia|planeta)\b", re.I
    )),
    ("personagens", re.compile(
        r"\b(rogue trader|captain|commissar|tech-priest|sister|explorer"
        r"|mercenary|heretic|inquisitor|ship|crew|companion|npc"
        r"|capitão|comissário|explorador|mercenário|herege|inquisidor|tripulação)\b", re.I
    )),
    ("dialogo", re.compile(
        r"\b(said|replied|asked|ordered|whispered|shouted|narrator|dialogue"
        r"|disse|respondeu|perguntou|ordenou|sussurrou|gritou|narração)\b", re.I
    )),
    ("outros", re.compile(r".*")),
]


def strip_tags(text: str) -> str:
    return TAG_RE.sub(" ", text).strip()


def categorize(text: str) -> str:
    clean = strip_tags(text)
    for cat_id, pattern in CATEGORIES:
        if pattern.search(clean):
            return cat_id
    return "outros"


def _load_nao_traduzir() -> set:
    """Carrega todos os termos que não devem ser traduzidos do glossário."""
    nao_traduzir = set()
    if not GLOSSARIO_PATH.exists():
        return nao_traduzir
    glossario = json.load(open(GLOSSARIO_PATH, encoding="utf-8"))
    # Lista plana
    for t in glossario.get("termos_nao_traduzir", []):
        nao_traduzir.add(t.lower())
    # Grupos estruturados
    for key in ["termos_nao_traduzir_personagens", "termos_nao_traduzir_locais",
                "termos_nao_traduzir_instituicoes", "termos_nao_traduzir_armas_e_equipamentos",
                "termos_nao_traduzir_titulos"]:
        group = glossario.get(key, {})
        for v in group.values():
            if isinstance(v, list):
                nao_traduzir.update(t.lower() for t in v)
    return nao_traduzir


# Padrões de créditos/marcas que nunca são traduzidos
CREDITOS_RE = re.compile(
    r"\b(Inc|Ltd|Pty|Corp|LLC|GmbH|S\.A|Games|Software|Studios|Entertainment"
    r"|Interactive|Technologies|Systems|Solutions|Group|Holdings)\b\.?", re.I
)


def detect_status(en_text: str, pt_text: str, nao_traduzir: set) -> str:
    """Detecta o status de tradução de uma string."""
    clean_en = strip_tags(en_text).strip()
    clean_pt = strip_tags(pt_text).strip()

    # Sem conteúdo real
    if len(clean_en) < 3:
        return "approved"

    # Texto PT é idêntico ao EN → verificar se é nome próprio (não traduzir)
    if clean_en.lower() == clean_pt.lower():
        # Nome próprio do glossário → correto, marcar como approved
        if clean_en.lower() in nao_traduzir:
            return "approved"
        # Créditos/marcas → approved
        if CREDITOS_RE.search(clean_en):
            return "approved"
        # String curta (≤ 3 palavras) com palavra do glossário → approved
        words = clean_en.split()
        if len(words) <= 3 and any(w.lower() in nao_traduzir for w in words):
            return "approved"
        # Genuinamente não traduzido
        return "pending"

    # Texto PT parece inglês → não traduzido
    if EN_RE.search(clean_pt) and not PT_RE.search(clean_pt):
        return "pending"

    # Tem marcadores de português → traduzido por máquina ou humano
    if PT_RE.search(clean_pt):
        return "machine"

    # Difere do EN sem marcadores claros (nomes próprios, siglas, etc.)
    return "approved"


def run(dry_run: bool, stats_only: bool) -> int:
    # Carregar enGB.json
    if not ENDB_PATH.exists():
        print(f"ERRO: {ENDB_PATH} não encontrado.")
        return 1
    print(f"Carregando {ENDB_PATH.name}...")
    with open(ENDB_PATH, encoding="utf-8") as f:
        data = json.load(f)
    pt_strings = data["strings"]

    # Carregar original EN
    if not ORIG_PATH.exists():
        print(f"ERRO: {ORIG_PATH.name} não encontrado.")
        print("Necessário para ter o texto EN de referência.")
        return 1
    print(f"Carregando {ORIG_PATH.name}...")
    with open(ORIG_PATH, encoding="utf-8") as f:
        orig_data = json.load(f)
    en_strings = orig_data["strings"]

    # Carregar nomes próprios do glossário
    print("Carregando glossário de nomes próprios...")
    nao_traduzir = _load_nao_traduzir()

    # Categorizar e separar
    print("Categorizando strings...")
    categories: dict[str, dict] = {cat: {} for cat, _ in CATEGORIES}
    stats: dict[str, dict[str, int]] = {cat: {"approved": 0, "machine": 0, "pending": 0} for cat, _ in CATEGORIES}

    for uuid, en_entry in en_strings.items():
        en_text = en_entry["Text"]
        pt_entry = pt_strings.get(uuid, {})
        pt_text = pt_entry.get("Text", en_text)

        cat = categorize(en_text)
        status = detect_status(en_text, pt_text, nao_traduzir)

        categories[cat][uuid] = {
            "en": en_text,
            "pt": pt_text,
            "status": status,
        }
        stats[cat][status] += 1

    # Exibir estatísticas
    print()
    print("=" * 60)
    print(f"  ESTATÍSTICAS POR CATEGORIA")
    print("=" * 60)
    total_pending = 0
    for cat, _ in CATEGORIES:
        s = stats[cat]
        total = s["approved"] + s["machine"] + s["pending"]
        if total == 0:
            continue
        pct = round((s["approved"] + s["machine"]) / total * 100, 1) if total > 0 else 0
        print(f"  {cat:15} {total:6,} strings | {pct:5.1f}% traduzidas | {s['pending']:4} pendentes")
        total_pending += s["pending"]
    print("-" * 60)
    total_all = sum(sum(s.values()) for s in stats.values())
    print(f"  {'TOTAL':15} {total_all:6,} strings | {total_pending:4} pendentes")
    print()

    if stats_only:
        return 0

    if dry_run:
        print("[DRY-RUN] Nenhum arquivo criado.")
        print(f"Seriam criados em: {SRC_DIR}/")
        return 0

    # Criar diretório e salvar arquivos
    SRC_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Salvando em {SRC_DIR}/...")
    for cat, _ in CATEGORIES:
        if not categories[cat]:
            continue
        out_path = SRC_DIR / f"{cat}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(categories[cat], f, ensure_ascii=False, indent=2)
        print(f"  {out_path.name}: {len(categories[cat]):,} strings")

    print()
    print(f"OK — src/strings/ criado com {len(CATEGORIES)} arquivos.")
    print()
    print("Próximos passos:")
    print("  python3 scripts/compile.py   # reconstruir enGB.json a partir dos src/")
    print("  python3 scripts/validate.py  # validar resultado")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Migra enGB.json para src/strings/<categoria>.json")
    parser.add_argument("--dry-run", action="store_true", help="Simular sem criar arquivos")
    parser.add_argument("--stats", action="store_true", help="Apenas exibir estatísticas por categoria")
    args = parser.parse_args()
    sys.exit(run(dry_run=args.dry_run, stats_only=args.stats))


if __name__ == "__main__":
    main()
