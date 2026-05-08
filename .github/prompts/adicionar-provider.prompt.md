---
description: "Adiciona um novo provedor de tradução ao translate_batch.py. Use quando quiser integrar uma nova API de IA (ex: OpenAI, Anthropic, DeepL, Mistral) ou um novo modelo local."
name: "Adicionar Provider de Tradução"
agent: "Desenvolvedor"
tools: [read, edit, search]
argument-hint: "Nome do provedor e detalhes da API (URL, autenticação, formato de resposta)"
---

Integre um novo provedor de tradução ao pipeline do `translate_batch.py`.

## Ler primeiro

Leia [scripts/translate_batch.py](../../scripts/translate_batch.py) completo para entender a arquitetura atual antes de modificar.

## Padrão de um provedor

Todo provedor é uma função independente que:
1. Levanta `ImportError` se a lib não estiver instalada (com mensagem de como instalar)
2. Levanta `RuntimeError` se a configuração estiver faltando (chave API vazia)
3. Protege tags com placeholders antes de traduzir
4. Restaura tags após traduzir
5. Retorna apenas o texto traduzido (string limpa)

```python
def translate_NOME(text: str) -> str:
    """Traduz usando NOME (descrição breve)."""
    try:
        from biblioteca_necessaria import Cliente
    except ImportError:
        raise RuntimeError("biblioteca_necessaria não instalado: pip install biblioteca_necessaria")

    api_key = os.getenv("NOME_API_KEY", "")
    if not api_key:
        raise RuntimeError("NOME_API_KEY não configurado no .env")

    # Proteger tags
    tags = TAG_RE.findall(text)
    protected = text
    placeholders = {}
    for i, tag in enumerate(tags):
        ph = f"XTAG{i}X"
        placeholders[ph] = tag
        protected = protected.replace(tag, ph, 1)

    # Chamar API
    client = Cliente(api_key=api_key)
    result = client.translate(protected, source="en", target="pt")
    translated = result.text  # ajustar conforme a API

    # Restaurar tags
    for ph, tag in placeholders.items():
        translated = translated.replace(ph, tag)

    return translated
```

## Integrar no fallback chain

No `translate_with_fallback()`, adicionar o novo provider na ordem correta:

```python
providers = [provider]
if provider != "groq" and GROQ_API_KEY:
    providers.append("groq")
if provider not in ("helsinki", "deep_translator", "NOME"):
    providers.append("helsinki")
if provider != "deep_translator":
    providers.append("deep_translator")
```

## Registrar no argparse

```python
parser.add_argument(
    "--provider",
    choices=["ollama", "groq", "helsinki", "deep_translator", "NOME"],
    ...
)
```

## Atualizar configuração

Em [.env.example](../../.env.example), adicionar:
```bash
# --- NOME (descrição) ---
NOME_API_KEY=
NOME_MODEL=modelo-recomendado
```

Em [requirements.txt](../../requirements.txt), adicionar:
```
# NOME — descrição breve
biblioteca_necessaria>=x.y.z
```

No [Makefile](../../Makefile), adicionar:
```makefile
.PHONY: traduzir-NOME
traduzir-NOME: ## Traduzir usando NOME
	$(PYTHON) scripts/translate_batch.py --provider NOME
```

## Testar

```bash
# Dry-run para confirmar o provider aparece
.venv/bin/python scripts/translate_batch.py --provider NOME --dry-run

# Traduzir 5 strings para testar qualidade
.venv/bin/python scripts/translate_batch.py --provider NOME --limite 5

# Confirmar que o JSON está OK
.venv/bin/python scripts/validate.py
```
