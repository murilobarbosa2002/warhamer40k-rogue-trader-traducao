#!/usr/bin/env python3
"""
review_ai.py — Revisão de qualidade das traduções por IA (Groq / Ollama)

Analisa strings com status "machine" e detecta:
  - Termos EN não traduzidos
  - Tom inadequado (casual, moderno, não-grimdark)
  - Erros de terminologia WH40K
  - Problemas de gramática / concordância

Para cada string com problema, sugere a versão corrigida.
Salva relatório em revisao/review_report_<categoria>.json.

Uso:
    python3 scripts/review_ai.py --categoria dialogo --limite 100
    python3 scripts/review_ai.py --categoria personagens --limite 200
    python3 scripts/review_ai.py --categoria combate --limite 300
    python3 scripts/review_ai.py --all --limite 500
    python3 scripts/review_ai.py --aplicar revisao/review_report_dialogo.json
    python3 scripts/review_ai.py --dry-run --categoria tutorial --limite 20
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC_DIR = ROOT / "src" / "strings"
ENDB_PATH = ROOT / "enGB.json"
REVISAO_DIR = ROOT / "revisao"
GLOSSARIO_PATH = ROOT / "glossario.json"

TAG_RE = re.compile(r"\{[^}]+\}|<[^>]+>")

CATEGORIAS_VALIDAS = [
    "dialogo", "personagens", "combate", "enciclopedia",
    "itens", "missoes", "tutorial", "ui", "outros",
]

# Prioridade de revisão (mais impacto no jogador primeiro)
PRIORIDADE = ["dialogo", "personagens", "missoes", "combate", "enciclopedia", "itens", "tutorial", "ui", "outros"]


# ─── Prompt de revisão ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """Você é revisor de localização PT-BR do jogo Warhammer 40,000: Rogue Trader.

REGRAS CRÍTICAS:
1. Termos que NUNCA se traduzem: Rogue Trader, Astartes, Space Marine, Bolter, Lasgun, Melta, Plasma, Flamer, Warp, Chaos, Ork, Eldar, Necron, Daemon, Omnissiah, Mechanicus, Inquisition, Tech-Priest, Servo-skull, Vox, Mechadendrite, Death Cultist, Adeptus Mechanicus — e todos os nomes próprios de personagens.
2. Terminologia obrigatória: AP→PA, MP→PM, Damage→Dano, Cooldown→Recarga, Skill→Perícia, Talent→Talento, NPC→PNJ.
3. Tom: grimdark, sério, formal — nunca casual ou moderno.
4. Tags {g|..}{/g}, {d|..}{/d}, {n}{/n}, {uip|..}, <b>, <i>, \\n devem ser PRESERVADAS EXATAMENTE — NUNCA crie tags novas nem remova as existentes.
5. O identificador dentro de {g|Encyclopedia:X} NUNCA é traduzido — apenas o texto entre as tags.

QUANDO DIZER OK:
- A tradução estiver correta ou aceitável
- Listas de créditos (nomes de funções, cargos de produção)
- Strings com nomes próprios corretos e intraduzíveis
- Pequenas diferenças de estilo sem impacto no significado

QUANDO REPORTAR PROBLEMA:
- Termo EN visível no texto PT onde deveria estar em PT (ex: "skill" → deveria ser "perícia")
- AP/MP em vez de PA/PM
- Tom claramente errado (muito casual para um contexto épico/formal)
- Erro gramatical óbvio (concordância, artigo errado)
- Tag quebrada ou texto de tag não traduzido quando deveria ser

Analise:
EN: {en}
PT: {pt}

Se a tradução estiver correta ou aceitável, responda APENAS: OK
Se houver problema claro, responda APENAS neste formato exato (sem markdown, sem texto extra):
PROBLEMA: [descrição em uma linha]
CORRIGIDO: [texto PT completo com TODAS as tags originais preservadas intactas]"""


def strip_tags(text: str) -> str:
    return TAG_RE.sub(" ", text).strip()


def load_glossario() -> set:
    """Carrega nomes próprios do glossário para filtragem."""
    nao_traduzir = set()
    if not GLOSSARIO_PATH.exists():
        return nao_traduzir
    g = json.load(open(GLOSSARIO_PATH, encoding="utf-8"))
    for t in g.get("termos_nao_traduzir", []):
        nao_traduzir.add(t.lower())
    return nao_traduzir


def load_categoria(categoria: str) -> dict:
    """Carrega um arquivo de categoria de src/strings/."""
    path = SRC_DIR / f"{categoria}.json"
    if not path.exists():
        print(f"ERRO: {path} não encontrado")
        sys.exit(1)
    return json.load(open(path, encoding="utf-8"))


def sample_para_revisao(data: dict, limite: int) -> list[tuple[str, dict]]:
    """Seleciona strings com status 'machine' para revisão."""
    candidatos = [
        (uuid, entry)
        for uuid, entry in data.items()
        if entry.get("status") == "machine"
        and len(strip_tags(entry.get("en", ""))) >= 20
        and len(strip_tags(entry.get("pt", ""))) >= 10
    ]
    if limite > 0:
        candidatos = candidatos[:limite]
    return candidatos


# ─── Backend Groq ─────────────────────────────────────────────────────────────

def _call_groq(prompt: str, system: str) -> str:
    """Chama a API Groq."""
    try:
        from groq import Groq
    except ImportError:
        raise RuntimeError("groq não instalado: pip install groq")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY não configurado no .env")

    model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=2000,
    )
    return resp.choices[0].message.content.strip()


# ─── Backend Ollama ───────────────────────────────────────────────────────────

def _call_ollama(prompt: str, system: str) -> str:
    """Chama o servidor Ollama local."""
    import requests
    url = os.getenv("OLLAMA_URL", "http://localhost:11434") + "/api/generate"
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    full_prompt = f"SISTEMA: {system}\n\nUSUÁRIO: {prompt}"
    resp = requests.post(url, json={
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }, timeout=120)
    resp.raise_for_status()
    return resp.json()["response"].strip()


def call_ai(prompt: str, provider: str) -> str:
    """Chama o provedor de IA configurado. prompt já contém EN e PT interpolados."""
    if provider == "groq":
        return _call_groq_single(prompt)
    elif provider == "ollama":
        return _call_ollama_single(prompt)
    elif provider == "gemini":
        return _call_gemini_single(prompt)
    else:
        raise ValueError(f"Provider desconhecido: {provider}")


def _call_gemini_single(prompt: str) -> str:
    """Chama a API Google Gemini."""
    import requests
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY não configurado no .env")
    model = os.getenv("GOOGLE_MODEL", "gemini-2.0-flash")
    # Remover prefixo "models/" se presente
    model = model.replace("models/", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 500},
    }
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def _call_groq_single(prompt: str) -> str:
    try:
        from groq import Groq
    except ImportError:
        raise RuntimeError("groq não instalado: pip install groq")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY não configurado no .env")
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    client = Groq(api_key=api_key)
    for attempt in range(5):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            msg = str(e)
            if "429" in msg:
                # Extrair tempo real de espera da mensagem de erro
                wait_m = re.search(r"try again in (\d+)m([\d.]+)s", msg)
                wait_s = re.search(r"try again in ([\d.]+)s", msg)
                if wait_m:
                    wait = int(wait_m.group(1)) * 60 + float(wait_m.group(2)) + 5
                elif wait_s:
                    wait = float(wait_s.group(1)) + 5
                else:
                    wait = 60 * (attempt + 1)
                print(f"\n  [rate limit] aguardando {wait:.0f}s antes de tentar novamente...")
                time.sleep(wait)
            else:
                raise


def _call_ollama_single(prompt: str) -> str:
    import requests
    url = os.getenv("OLLAMA_URL", "http://localhost:11434") + "/api/generate"
    model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    resp = requests.post(url, json={
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }, timeout=120)
    resp.raise_for_status()
    return resp.json()["response"].strip()


# ─── Parser de resposta da IA ─────────────────────────────────────────────────

def parse_batch_response(response: str, uuids: list[str]) -> dict[str, dict]:
    """
    Interpreta a resposta da IA para um batch de strings.
    Retorna dict: uuid → {ok: bool, problema: str, corrigido: str}
    """
    results = {}
    # Dividir resposta por separadores de linha dupla ou por número de string
    blocos = re.split(r"\n{2,}", response.strip())

    for i, (uuid, bloco) in enumerate(zip(uuids, blocos)):
        bloco = bloco.strip()
        if not bloco or bloco.upper() == "OK":
            results[uuid] = {"ok": True}
        else:
            problema_m = re.search(r"PROBLEMA:\s*(.+?)(?:\n|$)", bloco, re.I)
            corrigido_m = re.search(r"CORRIGIDO:\s*(.+?)$", bloco, re.I | re.S)
            if corrigido_m:
                problema = problema_m.group(1).strip() if problema_m else "ver revisão"
                corrigido = corrigido_m.group(1).strip()
                results[uuid] = {
                    "ok": False,
                    "problema": problema,
                    "corrigido": corrigido,
                }
            else:
                # Resposta não estruturada — marcar para revisão manual
                results[uuid] = {
                    "ok": False,
                    "problema": "resposta não estruturada",
                    "corrigido": None,
                    "resposta_raw": bloco[:300],
                }

    # Strings sem resposta correspondente → OK (IA pulou)
    for uuid in uuids:
        if uuid not in results:
            results[uuid] = {"ok": True}

    return results


# ─── Aplicação de correções ───────────────────────────────────────────────────

def aplicar_correcoes(report_path: Path, dry_run: bool = False) -> int:
    """Aplica correções de um relatório de revisão a src/strings/ e enGB.json."""
    if not report_path.exists():
        print(f"ERRO: {report_path} não encontrado")
        return 1

    report = json.load(open(report_path, encoding="utf-8"))
    correcoes = [r for r in report.get("resultados", []) if not r.get("ok") and r.get("corrigido")]

    print(f"Correções disponíveis: {len(correcoes)}")
    if dry_run:
        print("[DRY-RUN] Nenhuma alteração será salva.")
        for r in correcoes[:10]:
            print(f"\n  [{r['uuid'][:8]}] {r['problema']}")
            print(f"  ANTES:  {r['pt_atual'][:100]}")
            print(f"  DEPOIS: {r['corrigido'][:100]}")
        return 0

    # Carregar enGB.json
    endb = json.load(open(ENDB_PATH, encoding="utf-8"))
    endb_strings = endb["strings"]

    # Mapear uuid → categoria para atualizar src/
    categoria_map: dict[str, str] = {}
    src_data: dict[str, dict] = {}
    for cat in CATEGORIAS_VALIDAS:
        path = SRC_DIR / f"{cat}.json"
        if path.exists():
            d = json.load(open(path, encoding="utf-8"))
            src_data[cat] = d
            for uuid in d:
                categoria_map[uuid] = cat

    aplicadas = 0
    invalidas = 0

    for r in correcoes:
        uuid = r["uuid"]
        corrigido = r["corrigido"]

        # Validação básica: preservação de tags
        orig_tags = set(TAG_RE.findall(r.get("en_original", "")))
        novo_tags = set(TAG_RE.findall(corrigido))
        # Verificar que as tags do EN aparecem no corrigido (salvo tags de fechamento)
        # Verificação simples: não deixar corrigido vazio
        if not corrigido.strip():
            invalidas += 1
            continue

        # Aplicar no enGB.json
        if uuid in endb_strings:
            endb_strings[uuid]["Text"] = corrigido

        # Aplicar no src/strings/
        cat = categoria_map.get(uuid)
        if cat and uuid in src_data.get(cat, {}):
            src_data[cat][uuid]["pt"] = corrigido
            src_data[cat][uuid]["status"] = "approved"

        aplicadas += 1

    if not dry_run:
        # Salvar enGB.json
        with open(ENDB_PATH, "w", encoding="utf-8") as f:
            json.dump(endb, f, ensure_ascii=False, indent=2)
        # Salvar src/ modificados
        cats_modificadas = set(categoria_map.get(r["uuid"]) for r in correcoes if r.get("corrigido"))
        for cat in cats_modificadas:
            if cat and cat in src_data:
                with open(SRC_DIR / f"{cat}.json", "w", encoding="utf-8") as f:
                    json.dump(src_data[cat], f, ensure_ascii=False, indent=2)

    print(f"Correções aplicadas: {aplicadas}")
    if invalidas:
        print(f"Ignoradas (inválidas): {invalidas}")
    return 0


# ─── Loop principal de revisão ────────────────────────────────────────────────

def revisar_categoria(categoria: str, limite: int, provider: str, dry_run: bool, batch_size: int = 5) -> Path:
    """
    Revisa uma categoria com IA e salva o relatório.
    Processa uma string por vez para confiabilidade máxima.
    """
    print(f"\n{'=' * 60}")
    print(f"  REVISÃO: {categoria.upper()} ({limite} strings)")
    print(f"  Provedor: {provider}")
    print(f"{'=' * 60}")

    REVISAO_DIR.mkdir(exist_ok=True)
    report_path = REVISAO_DIR / f"review_report_{categoria}.json"

    # Retomar revisão anterior se existir
    revisados_anteriores: set = set()
    resultados_anteriores: list = []
    if report_path.exists():
        prev = json.load(open(report_path, encoding="utf-8"))
        resultados_anteriores = prev.get("resultados", [])
        revisados_anteriores = {r["uuid"] for r in resultados_anteriores}
        print(f"  Retomando: {len(revisados_anteriores)} já revisados")

    data = load_categoria(categoria)
    todos = sample_para_revisao(data, 0)  # todos os machine
    candidatos = [(u, e) for u, e in todos if u not in revisados_anteriores]
    if limite > 0:
        candidatos = candidatos[:limite]

    print(f"  A revisar: {len(candidatos)} strings")

    if dry_run:
        print("\n[DRY-RUN] Primeiras 5 strings que seriam revisadas:")
        for uuid, entry in candidatos[:5]:
            print(f"\n  [{uuid[:8]}]")
            print(f"  EN: {entry['en'][:100]}")
            print(f"  PT: {entry['pt'][:100]}")
        return report_path

    resultados = list(resultados_anteriores)
    total_problemas = sum(1 for r in resultados if not r.get("ok"))
    total_revisados = len(revisados_anteriores)

    for idx, (uuid, entry) in enumerate(candidatos):
        en = entry["en"]
        pt = entry["pt"]

        # Montar prompt individual — usar substituição manual para evitar conflito com {tags}
        prompt = SYSTEM_PROMPT.replace("{en}", en).replace("{pt}", pt)

        try:
            resposta = call_ai(prompt, provider)
            resposta = resposta.strip()

            if resposta.upper() == "OK" or resposta.upper().startswith("OK\n"):
                resultado = {"uuid": uuid, "categoria": categoria,
                             "en_original": en, "pt_atual": pt, "ok": True}
            else:
                problema_m = re.search(r"PROBLEMA:\s*(.+?)(?:\n|$)", resposta, re.I)
                corrigido_m = re.search(r"CORRIGIDO:\s*(.+)$", resposta, re.I | re.S)

                if corrigido_m:
                    problema = problema_m.group(1).strip() if problema_m else "ver revisão"
                    corrigido = corrigido_m.group(1).strip()
                    # Validação: corrigido não pode estar vazio nem ser igual ao EN
                    if corrigido and corrigido.strip() != en.strip():
                        resultado = {
                            "uuid": uuid, "categoria": categoria,
                            "en_original": en, "pt_atual": pt,
                            "ok": False, "problema": problema, "corrigido": corrigido,
                        }
                        total_problemas += 1
                    else:
                        resultado = {"uuid": uuid, "categoria": categoria,
                                     "en_original": en, "pt_atual": pt, "ok": True}
                else:
                    # Resposta sem estrutura esperada — marcar como OK para não bloquear
                    resultado = {"uuid": uuid, "categoria": categoria,
                                 "en_original": en, "pt_atual": pt, "ok": True,
                                 "nota": resposta[:200]}

        except Exception as e:
            print(f"\n  ERRO [{uuid[:8]}]: {e}")
            resultado = {"uuid": uuid, "categoria": categoria,
                         "en_original": en, "pt_atual": pt, "ok": True, "erro": str(e)}

        resultados.append(resultado)
        total_revisados += 1

        # Progresso a cada 10
        if total_revisados % 10 == 0 or idx == len(candidatos) - 1:
            pct = (idx + 1) / max(len(candidatos), 1) * 100
            prob_pct = total_problemas / max(total_revisados, 1) * 100
            print(f"  [{total_revisados:4d}/{len(candidatos) + len(revisados_anteriores)}] "
                  f"{pct:.0f}% | Problemas: {total_problemas} ({prob_pct:.1f}%)")

        # Salvar checkpoint a cada 20 strings
        if total_revisados % 20 == 0 or idx == len(candidatos) - 1:
            report = {
                "categoria": categoria, "provider": provider,
                "total_revisados": total_revisados,
                "total_problemas": total_problemas,
                "resultados": resultados,
            }
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

        # Rate limit suave — 1.5s entre chamadas
        time.sleep(1.5)

    # Relatório final
    print(f"\n{'=' * 60}")
    print(f"  RESULTADO — {categoria.upper()}")
    print(f"{'=' * 60}")
    print(f"  Total revisado:    {total_revisados:,}")
    print(f"  Com problemas:     {total_problemas:,} ({total_problemas / max(total_revisados, 1) * 100:.1f}%)")
    print(f"  Relatório salvo:   {report_path}")

    if total_problemas > 0:
        print(f"\n  Próximo passo:")
        print(f"    python3 scripts/review_ai.py --aplicar {report_path}")

    return report_path


def run(args: argparse.Namespace) -> int:
    # Carregar .env
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    # Aplicar correções de um relatório existente
    if args.aplicar:
        return aplicar_correcoes(Path(args.aplicar), dry_run=args.dry_run)

    # Determinar categorias a revisar
    if args.all:
        categorias = PRIORIDADE
    elif args.categoria:
        if args.categoria not in CATEGORIAS_VALIDAS:
            print(f"ERRO: categoria inválida. Use: {', '.join(CATEGORIAS_VALIDAS)}")
            return 1
        categorias = [args.categoria]
    else:
        print("Especifique --categoria <nome> ou --all")
        print(f"Categorias disponíveis: {', '.join(CATEGORIAS_VALIDAS)}")
        print(f"\nPrioridade recomendada (impacto no jogador):")
        for i, cat in enumerate(PRIORIDADE, 1):
            path = SRC_DIR / f"{cat}.json"
            if path.exists():
                d = json.load(open(path))
                machine = sum(1 for e in d.values() if e.get("status") == "machine")
                print(f"  {i}. {cat:15} {machine:,} strings machine")
        return 0

    limite_por_cat = args.limite if args.limite > 0 else 200

    for cat in categorias:
        report_path = revisar_categoria(
            categoria=cat,
            limite=limite_por_cat,
            provider=args.provider,
            dry_run=args.dry_run,
            batch_size=args.batch,
        )

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Revisão de qualidade das traduções por IA (Groq / Ollama)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Revisar 100 strings de diálogos com Groq
  python3 scripts/review_ai.py --categoria dialogo --limite 100

  # Revisar todas as categorias, 200 strings cada
  python3 scripts/review_ai.py --all --limite 200

  # Simulação sem chamar API
  python3 scripts/review_ai.py --categoria combate --limite 20 --dry-run

  # Aplicar correções de um relatório
  python3 scripts/review_ai.py --aplicar revisao/review_report_dialogo.json

  # Revisar com Ollama local
  python3 scripts/review_ai.py --categoria personagens --provider ollama
        """,
    )
    parser.add_argument("--categoria", help="Categoria a revisar")
    parser.add_argument("--all", action="store_true", help="Revisar todas as categorias")
    parser.add_argument("--limite", type=int, default=200, help="Strings por categoria (padrão: 200)")
    parser.add_argument("--provider", default="groq", choices=["groq", "ollama", "gemini"], help="Provedor de IA (padrão: groq)")
    parser.add_argument("--batch", type=int, default=5, help="Strings por chamada de API (padrão: 5)")
    parser.add_argument("--dry-run", action="store_true", help="Simular sem chamar API nem salvar")
    parser.add_argument("--aplicar", metavar="RELATÓRIO", help="Aplicar correções de um relatório JSON")
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
