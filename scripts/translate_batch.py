#!/usr/bin/env python3
"""
translate_batch.py — Pipeline de tradução com IA (Helsinki-NLP → Ollama → Groq → Google Translate)

Traduz as strings não traduzidas do enGB.json usando IA com fallback automático.
Suporta checkpoint para retomar do ponto onde parou.

Uso:
    python3 scripts/translate_batch.py                      # traduzir tudo
    python3 scripts/translate_batch.py --dry-run            # simular sem salvar
    python3 scripts/translate_batch.py --limite 100         # traduzir apenas 100 strings
    python3 scripts/translate_batch.py --provider helsinki  # modelo local offline EN→PT
    python3 scripts/translate_batch.py --provider ollama    # forçar Ollama
    python3 scripts/translate_batch.py --reset              # limpar checkpoint e recomeçar
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# Carregar .env se existir
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ROOT = Path(__file__).parent.parent
ENDB_PATH = ROOT / "enGB.json"
CHECKPOINT_PATH = ROOT / Path(os.getenv("CHECKPOINT_FILE", ".translation_checkpoint.json"))
GLOSSARIO_PATH = ROOT / "glossario.json"
TRANSLATION_MEMORY_PATH = ROOT / "translation-memory.json"

# ─── Configurações do .env ──────────────────────────────────────────────────
PROVIDER = os.getenv("TRANSLATION_PROVIDER", "ollama")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "10"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
DELAY = float(os.getenv("DELAY_BETWEEN_BATCHES", "0.5"))

# ─── Tags que devem ser preservadas nas traduções ────────────────────────────
TAG_RE = re.compile(r"\{[^}]+\}|<[^>]+>")

# ─── System prompt para o modelo de IA ──────────────────────────────────────
SYSTEM_PROMPT = """Você é um tradutor especializado no universo Warhammer 40,000 para português brasileiro.

REGRAS OBRIGATÓRIAS:
1. Preserve TODAS as tags exatamente como estão: {g|...}texto{/g}, {n}texto{/n}, {uip|..}, {unit_stat|..}, <b>, <i>, <br>, \\n
2. O identificador dentro de {g|Encyclopedia:NomeDaCoisa} NUNCA é traduzido — apenas o texto entre as tags
3. Tom: grimdark, épico, sério. Sem linguagem casual ou moderna
4. Use "você" como tratamento padrão (não "vós" ou "tu")

GLOSSÁRIO OBRIGATÓRIO (não desviar):
- AP / Action Points → PA / Pontos de Ação
- MP / Movement Points → PM / Pontos de Movimento
- Wounds / HP → Ferimentos
- Damage → Dano
- Target → Alvo
- Range → Alcance
- Cooldown → Recarga
- Buff → Aprimoramento
- Debuff → Penalidade de efeito
- Skill → Perícia
- Talent → Talento
- Trait → Característica
- Round → Rodada
- Turn → Turno
- Cover → Cobertura
- Dodge → Esquiva
- Charge → Investida
- NPC → PNJ

TERMOS QUE NUNCA TRADUZIR (nomes próprios):
Rogue Trader, Astartes, Space Marine, Adeptus Mechanicus, Adepta Sororitas,
Chaos (nome próprio), Eldar, Aeldari, Ork, Necron, Tyranid, Bolter, Boltgun,
Lasgun, Laspistol, Vox, Mechadendrite, Servo-skull, Warp (nome próprio),
Immaterium, Webway, Omnissiah

Responda SOMENTE com o texto traduzido, sem explicações, notas ou aspas extras."""


def extract_tags(text: str) -> list:
    """Extrai todas as tags do texto para verificação."""
    return TAG_RE.findall(text)


def tags_preserved(original: str, translated: str) -> bool:
    """Verifica se as tags foram preservadas na tradução."""
    orig_tags = sorted(extract_tags(original))
    trad_tags = sorted(extract_tags(translated))
    return orig_tags == trad_tags


def apply_glossary_fixes(text: str) -> str:
    """Aplica correções do glossário no texto traduzido."""
    # Não mexe dentro de tags
    def replace_outside_tags(pattern, replacement, text):
        result = []
        last = 0
        for m in TAG_RE.finditer(text):
            segment = text[last:m.start()]
            segment = re.sub(pattern, replacement, segment, flags=re.IGNORECASE)
            result.append(segment)
            result.append(m.group())
            last = m.end()
        result.append(re.sub(pattern, replacement, text[last:], flags=re.IGNORECASE))
        return "".join(result)

    text = replace_outside_tags(r"\bAP\b", "PA", text)
    text = replace_outside_tags(r"\bMP\b", "PM", text)
    text = replace_outside_tags(r"\bcooldowns?\b", lambda m: "recargas" if m.group().endswith("s") else "recarga", text)
    return text


# ─── Provedores de tradução ──────────────────────────────────────────────────

def translate_ollama(text: str) -> str:
    """Traduz usando Ollama local."""
    import urllib.request
    import urllib.error

    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": f"{SYSTEM_PROMPT}\n\nTexto para traduzir:\n{text}",
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 1024},
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
    return result["response"].strip()


def translate_groq(text: str) -> str:
    """Traduz usando Groq API (cloud gratuito)."""
    try:
        from groq import Groq
    except ImportError:
        raise RuntimeError("groq não instalado: pip install groq")

    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY não configurado no .env")

    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Traduza para português brasileiro:\n\n{text}"},
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


def translate_google(text: str) -> str:
    """Traduz usando Google Translate via deep-translator (sem API key)."""
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        raise RuntimeError("deep-translator não instalado: pip install deep-translator")

    # Protege as tags substituindo por placeholders
    tags = TAG_RE.findall(text)
    protected = text
    placeholders = {}
    for i, tag in enumerate(tags):
        ph = f"XTAG{i}X"
        placeholders[ph] = tag
        protected = protected.replace(tag, ph, 1)

    translated = GoogleTranslator(source="en", target="pt").translate(protected)

    # Restaura as tags
    for ph, tag in placeholders.items():
        translated = translated.replace(ph, tag)

    return translated


# Cache global do pipeline Helsinki para não recarregar a cada chamada
_helsinki_pipeline = None


def translate_helsinki(text: str) -> str:
    """Traduz usando Helsinki-NLP/opus-mt-tc-big-en-pt (modelo local offline, ~300MB)."""
    global _helsinki_pipeline
    try:
        from transformers import pipeline as hf_pipeline
    except ImportError:
        raise RuntimeError("transformers não instalado: pip install transformers sentencepiece")

    if _helsinki_pipeline is None:
        print("  [Helsinki] Carregando modelo opus-mt-tc-big-en-pt (primeira vez, ~300MB)...")
        _helsinki_pipeline = hf_pipeline(
            "translation",
            model="Helsinki-NLP/opus-mt-tc-big-en-pt",
            device=-1,  # CPU
        )

    # Protege as tags substituindo por placeholders
    tags = TAG_RE.findall(text)
    protected = text
    placeholders = {}
    for i, tag in enumerate(tags):
        ph = f"XTAG{i}X"
        placeholders[ph] = tag
        protected = protected.replace(tag, ph, 1)

    # O modelo tem limite de ~512 tokens; trunca se necessário
    result = _helsinki_pipeline(protected, max_length=512)
    translated = result[0]["translation_text"]

    # Restaura as tags
    for ph, tag in placeholders.items():
        translated = translated.replace(ph, tag)

    return translated


def translate_with_fallback(text: str, provider: str) -> tuple[str, str]:
    """
    Tenta traduzir com o provedor principal, caindo para fallback se falhar.
    Retorna (texto_traduzido, provedor_usado).
    """
    providers = [provider]
    if provider != "groq" and GROQ_API_KEY:
        providers.append("groq")
    if provider not in ("helsinki", "deep_translator"):
        providers.append("helsinki")
    if provider != "deep_translator":
        providers.append("deep_translator")

    last_error = None
    for prov in providers:
        for attempt in range(MAX_RETRIES):
            try:
                if prov == "ollama":
                    result = translate_ollama(text)
                elif prov == "groq":
                    result = translate_groq(text)
                elif prov == "helsinki":
                    result = translate_helsinki(text)
                elif prov == "deep_translator":
                    result = translate_google(text)
                else:
                    continue

                if result and len(result) > 2:
                    return result, prov

            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    time.sleep(1 * (attempt + 1))

    raise RuntimeError(f"Todos os provedores falharam. Último erro: {last_error}")


# ─── Checkpoint ─────────────────────────────────────────────────────────────

def load_checkpoint() -> dict:
    if CHECKPOINT_PATH.exists():
        with open(CHECKPOINT_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {"traduzidas": {}, "falhas": {}}


def save_checkpoint(checkpoint: dict):
    with open(CHECKPOINT_PATH, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, ensure_ascii=False, indent=2)


# ─── Pipeline principal ──────────────────────────────────────────────────────

def run(provider: str, limite: int, dry_run: bool, reset: bool, quiet: bool) -> int:
    try:
        from tqdm import tqdm
        use_tqdm = True
    except ImportError:
        use_tqdm = False

    # Carregar dados
    print(f"Carregando enGB.json...")
    with open(ENDB_PATH, encoding="utf-8") as f:
        data = json.load(f)
    strings = data["strings"]

    # Carregar original para ter o texto EN
    orig_path = ROOT / "arquivo-original-1.5.0.320.json"
    if not orig_path.exists():
        print("ERRO: arquivo-original-1.5.0.320.json não encontrado.")
        print("Necessário para identificar as strings não traduzidas.")
        return 1

    print("Carregando original EN...")
    with open(orig_path, encoding="utf-8") as f:
        orig_data = json.load(f)
    orig_strings = orig_data["strings"]

    # Checkpoint
    if reset and CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()
        print("Checkpoint removido. Recomeçando do zero.")

    checkpoint = load_checkpoint()
    ja_traduzidas = set(checkpoint["traduzidas"].keys())

    # Carregar translation memory (traduções revisadas por humanos)
    tm = {}
    if TRANSLATION_MEMORY_PATH.exists():
        with open(TRANSLATION_MEMORY_PATH, encoding="utf-8") as f:
            tm_data = json.load(f)
        tm = tm_data.get("pairs", {})
        if tm:
            print(f"Translation memory: {len(tm):,} pares aprovados carregados")

    # Identificar strings não traduzidas
    TAG_ONLY = re.compile(r"^[\s\{<\[%\-\d\.\*,/\|]+$")
    PT_RE = re.compile(
        r"\b(de|da|do|das|dos|em|para|uma|um|com|que|não|são|foi|ser|tem"
        r"|ter|você|este|essa|quando|mais|pode|deve|sobre|entre|também|já)\b",
        re.IGNORECASE,
    )
    EN_RE = re.compile(
        r"\b(the|and|or|is|are|was|were|will|would|can|could|should|have"
        r"|has|had|this|that|these|those|with|from|they|their|you|your)\b",
        re.IGNORECASE,
    )

    fila = []
    for key, orig_entry in orig_strings.items():
        if key in ja_traduzidas:
            continue
        orig_text = orig_entry["Text"]
        if key not in strings:
            fila.append((key, orig_text))
            continue

        trad_text = strings[key]["Text"]
        clean_orig = TAG_RE.sub("", orig_text).strip()
        clean_trad = TAG_RE.sub("", trad_text).strip()

        if len(clean_orig) < 10 or TAG_ONLY.match(clean_orig):
            continue

        if not re.search(r"[a-zA-Z]{3}", clean_orig):
            continue

        if clean_orig.lower() == clean_trad.lower():
            fila.append((key, orig_text))
        elif EN_RE.search(clean_trad) and not PT_RE.search(clean_trad):
            fila.append((key, orig_text))

    if limite > 0:
        fila = fila[:limite]

    print(f"\nProvedor: {provider.upper()}")
    print(f"Strings para traduzir: {len(fila):,}")
    print(f"Já traduzidas (checkpoint): {len(ja_traduzidas):,}")

    if dry_run:
        print("\n[DRY-RUN] Simulando primeiras 3 traduções...")
        sample = fila[:3]
        for key, text in sample:
            print(f"\n  [{key[:8]}] EN: {text[:100]}")
            print(f"  Seria enviado para {provider.upper()} com batch_size={BATCH_SIZE}")
        print("\nPara executar de verdade, remova --dry-run")
        return 0

    if not fila:
        print("\nNada a traduzir! Tudo já está traduzido ou no checkpoint.")
        return 0

    # Executar traduções
    print(f"\nIniciando tradução (batch_size={BATCH_SIZE}, delay={DELAY}s)...")
    print("Use Ctrl+C para pausar — o progresso é salvo no checkpoint.\n")

    success = 0
    failures = 0

    iterator = tqdm(fila, unit="str") if use_tqdm else fila

    try:
        for key, en_text in iterator:
            if not use_tqdm and not quiet:
                print(f"  [{success+failures+1}/{len(fila)}] {key[:8]}...", end="\r")

            try:
                # 1. Verificar translation memory primeiro
                if key in tm:
                    translated = tm[key]["pt"]
                    used_provider = "translation-memory"
                elif key in ja_traduzidas:
                    continue
                else:
                    translated, used_provider = translate_with_fallback(en_text, provider)
                translated = apply_glossary_fixes(translated)

                # Verificar integridade das tags
                if not tags_preserved(en_text, translated):
                    # Tentar reparar: usar o texto original para strings curtas
                    if not quiet:
                        print(f"\n  AVISO [{key[:8]}]: tags alteradas — usando fallback Google")
                    translated, used_provider = translate_with_fallback(en_text, "deep_translator")
                    translated = apply_glossary_fixes(translated)

                # Salvar no checkpoint
                checkpoint["traduzidas"][key] = {
                    "en": en_text,
                    "pt": translated,
                    "provider": used_provider,
                }
                success += 1

                # Salvar checkpoint a cada 10 traduções
                if success % 10 == 0:
                    save_checkpoint(checkpoint)
                    # Aplicar ao enGB.json incrementalmente
                    _apply_checkpoint_to_json(data, checkpoint)

                # Delay para evitar rate limit
                if DELAY > 0:
                    time.sleep(DELAY)

            except Exception as e:
                checkpoint["falhas"][key] = str(e)
                failures += 1
                if not quiet:
                    print(f"\n  FALHA [{key[:8]}]: {e}")

    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário. Salvando progresso...")

    # Salvar checkpoint final
    save_checkpoint(checkpoint)

    # Aplicar todas as traduções ao enGB.json
    print("\nAplicando traduções ao enGB.json...")
    n_aplicadas = _apply_checkpoint_to_json(data, checkpoint)

    print(f"\nSalvando enGB.json...")
    with open(ENDB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 50)
    print(f"  RESULTADO")
    print("=" * 50)
    print(f"  Traduzidas com sucesso: {success:,}")
    print(f"  Falhas:                 {failures:,}")
    print(f"  Aplicadas ao JSON:      {n_aplicadas:,}")
    print(f"  Checkpoint em:          {CHECKPOINT_PATH.name}")
    print()
    print("Próximos passos:")
    print("  python3 scripts/validate.py")
    print("  python3 scripts/relatorio.py")
    print('  git add enGB.json && git commit -m "feat(tradução): batch de traduções via IA"')
    return 0


def _apply_checkpoint_to_json(data: dict, checkpoint: dict) -> int:
    """Aplica as traduções do checkpoint ao dict do enGB.json em memória."""
    strings = data["strings"]
    count = 0
    for key, entry in checkpoint["traduzidas"].items():
        if key in strings:
            strings[key]["Text"] = entry["pt"]
            count += 1
        else:
            # String nova: adicionar com offset 0
            strings[key] = {"Offset": 0, "Text": entry["pt"]}
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(
        description="Traduz strings não traduzidas usando IA com fallback"
    )
    parser.add_argument(
        "--provider",
        default=PROVIDER,
        choices=["ollama", "groq", "helsinki", "deep_translator"],
        help=f"Provedor de tradução (padrão: {PROVIDER} do .env)",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=0,
        help="Número máximo de strings a traduzir (0 = sem limite)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simular sem salvar",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Limpar checkpoint e recomeçar do zero",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suprimir output detalhado",
    )
    args = parser.parse_args()
    sys.exit(run(
        provider=args.provider,
        limite=args.limite,
        dry_run=args.dry_run,
        reset=args.reset,
        quiet=args.quiet,
    ))


if __name__ == "__main__":
    main()
