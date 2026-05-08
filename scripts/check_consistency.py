#!/usr/bin/env python3
"""
check_consistency.py — Detector de traduções inconsistentes via sentence-transformers

Encontra strings em inglês que são semanticamente idênticas (ou muito similares)
mas foram traduzidas de formas diferentes — o que causa inconsistência no jogo.

Exemplo:
  "Take cover!" → "Tome cobertura!" em alguns lugares e "Busque cobertura!" em outros.

Usa embeddings semânticos (multilingual-MiniLM) para medir similaridade entre strings
EN originais, depois compara as traduções PT de pares similares.

REQUER: pip install sentence-transformers torch
        arquivo-original-1.5.0.320.json presente na raiz

Uso:
    python3 scripts/check_consistency.py                 # analisa tudo
    python3 scripts/check_consistency.py --limite 2000   # amostra de 2000 strings
    python3 scripts/check_consistency.py --threshold 0.92
    python3 scripts/check_consistency.py --output inconsistencias.json
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ENDB_PATH = ROOT / "enGB.json"
ORIG_PATH = ROOT / "arquivo-original-1.5.0.320.json"
TAG_RE = re.compile(r"\{[^}]+\}|<[^>]+>|\n")

# Modelo multilingual leve (~90MB) — entende PT e EN no mesmo espaço vetorial
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# Limiar: strings com similaridade EN > threshold são candidatas a inconsistência
DEFAULT_THRESHOLD = 0.92
# Limiar mínimo de diferença PT para considerar inconsistente
PT_DIFF_THRESHOLD = 0.70


def strip_tags(text: str) -> str:
    return TAG_RE.sub(" ", text).strip()


def load_data() -> tuple[dict, dict]:
    with open(ENDB_PATH, encoding="utf-8") as f:
        pt_data = json.load(f)
    with open(ORIG_PATH, encoding="utf-8") as f:
        en_data = json.load(f)
    return pt_data["strings"], en_data["strings"]


def compute_embeddings(texts: list[str], model) -> "list":
    """Calcula embeddings em lotes para eficiência."""
    return model.encode(texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)


def find_inconsistencies(
    pt_strings: dict,
    en_strings: dict,
    limite: int,
    en_threshold: float,
    pt_threshold: float,
) -> list[dict]:
    try:
        from sentence_transformers import SentenceTransformer, util
        import torch
    except ImportError:
        print("ERRO: sentence-transformers não instalado: pip install sentence-transformers torch")
        sys.exit(1)

    # Montar lista de pares (uuid, texto_en_limpo, texto_pt_limpo)
    pairs = []
    for uuid, en_entry in en_strings.items():
        if uuid not in pt_strings:
            continue
        en_clean = strip_tags(en_entry["Text"])
        pt_clean = strip_tags(pt_strings[uuid]["Text"])

        # Ignorar strings muito curtas ou puramente de interface
        if len(en_clean) < 15 or len(pt_clean) < 5:
            continue
        # Ignorar strings que não foram traduzidas (EN == PT)
        if en_clean.lower() == pt_clean.lower():
            continue

        pairs.append((uuid, en_clean, pt_clean))

    if limite > 0:
        pairs = pairs[:limite]

    print(f"Analisando {len(pairs):,} pares EN/PT com sentence-transformers...")
    print(f"Modelo: {EMBEDDING_MODEL}\n")

    model = SentenceTransformer(EMBEDDING_MODEL)

    uuids = [p[0] for p in pairs]
    en_texts = [p[1] for p in pairs]
    pt_texts = [p[2] for p in pairs]

    print("Calculando embeddings EN...")
    en_embeddings = compute_embeddings(en_texts, model)
    print("Calculando embeddings PT...")
    pt_embeddings = compute_embeddings(pt_texts, model)

    print("\nComparando similaridades...")
    en_tensor = __import__("torch").tensor(en_embeddings)
    pt_tensor = __import__("torch").tensor(pt_embeddings)

    # Calcular matriz de similaridade EN x EN (find duplicates)
    # Para eficiência, usar util.semantic_search ao invés de produto completo
    from sentence_transformers import util as st_util

    # Encontrar para cada string suas vizinhas mais próximas em EN
    top_k = min(5, len(pairs))
    hits = st_util.semantic_search(en_tensor, en_tensor, top_k=top_k + 1)

    inconsistencies = []
    seen_pairs = set()

    for i, neighbors in enumerate(hits):
        for hit in neighbors:
            j = hit["corpus_id"]
            score_en = hit["score"]

            if j <= i:  # evitar duplicatas e autocomparação
                continue
            if score_en < en_threshold:
                continue

            pair_key = (min(i, j), max(i, j))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            # Medir similaridade das traduções PT
            pt_i = pt_tensor[i].unsqueeze(0)
            pt_j = pt_tensor[j].unsqueeze(0)
            score_pt = float(st_util.cos_sim(pt_i, pt_j)[0][0])

            # Inconsistência: EN muito similar, PT bem diferente
            if score_pt < pt_threshold:
                inconsistencies.append({
                    "uuid_a": uuids[i],
                    "uuid_b": uuids[j],
                    "en_a": en_texts[i][:120],
                    "en_b": en_texts[j][:120],
                    "pt_a": pt_texts[i][:120],
                    "pt_b": pt_texts[j][:120],
                    "sim_en": round(float(score_en), 3),
                    "sim_pt": round(score_pt, 3),
                    "divergencia": round(float(score_en) - score_pt, 3),
                })

    # Ordenar pelas mais divergentes primeiro
    inconsistencies.sort(key=lambda x: -x["divergencia"])
    return inconsistencies


def render_report(inconsistencies: list[dict], output_path: Path | None):
    print("\n" + "=" * 60)
    print("  RELATÓRIO DE CONSISTÊNCIA — check_consistency.py")
    print("=" * 60)
    print(f"  Pares inconsistentes encontrados: {len(inconsistencies)}")
    print()

    for item in inconsistencies[:30]:
        print(f"  EN similar ({item['sim_en']:.2f}) | PT divergente ({item['sim_pt']:.2f}) | delta={item['divergencia']:.2f}")
        print(f"    EN-A [{item['uuid_a'][:8]}]: {item['en_a']}")
        print(f"    EN-B [{item['uuid_b'][:8]}]: {item['en_b']}")
        print(f"    PT-A: {item['pt_a']}")
        print(f"    PT-B: {item['pt_b']}")
        print()

    if len(inconsistencies) > 30:
        print(f"  ... e mais {len(inconsistencies) - 30} pares. Use --output para ver todos.")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(inconsistencies, f, ensure_ascii=False, indent=2)
        print(f"\nResultados completos salvos em: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Detecta strings EN similares com traduções PT inconsistentes"
    )
    parser.add_argument("--limite", type=int, default=0,
                        help="Máximo de strings a analisar (0 = todas, pode ser lento)")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                        help=f"Limiar de similaridade EN (padrão: {DEFAULT_THRESHOLD})")
    parser.add_argument("--pt-threshold", type=float, default=PT_DIFF_THRESHOLD,
                        help=f"Limiar máximo de similaridade PT (padrão: {PT_DIFF_THRESHOLD})")
    parser.add_argument("--output", type=str, default=None,
                        help="Salvar resultados em JSON")
    args = parser.parse_args()

    if not ORIG_PATH.exists():
        print(f"ERRO: {ORIG_PATH.name} não encontrado.")
        print("Necessário para comparar os textos EN originais.")
        return 1

    pt_strings, en_strings = load_data()
    print(f"PT: {len(pt_strings):,} strings | EN: {len(en_strings):,} strings")

    inconsistencies = find_inconsistencies(
        pt_strings, en_strings,
        limite=args.limite,
        en_threshold=args.threshold,
        pt_threshold=args.pt_threshold,
    )

    output_path = Path(args.output) if args.output else None
    render_report(inconsistencies, output_path)

    return 0 if not inconsistencies else 1


if __name__ == "__main__":
    sys.exit(main())
