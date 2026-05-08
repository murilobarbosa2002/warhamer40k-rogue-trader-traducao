---
description: "Referência rápida de todas as bibliotecas Python usadas no projeto: o que fazem, como usar, exemplos práticos, limites e armadilhas. Use quando precisar usar ou entender qualquer biblioteca do requirements.txt."
name: "referencia-bibliotecas"
tools: [read]
---

Leia [.github/copilot-instructions.md](../copilot-instructions.md) — seção "Stack de Bibliotecas" para a referência completa.

## Resumo rápido por caso de uso

### Quero traduzir texto EN→PT offline

```python
from transformers import pipeline
modelo = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-en-pt", device=-1)
resultado = modelo("The warrior charges forward", max_length=512)
print(resultado[0]["translation_text"])
```

### Quero medir se dois textos são semanticamente similares

```python
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
emb = model.encode(["texto em PT", "texto em EN"], normalize_embeddings=True)
score = float(util.cos_sim(emb[0], emb[1])[0][0])  # 0.0 a 1.0
```

### Quero analisar morfologia PT-BR (gênero, número, POS)

```python
import spacy
nlp = spacy.load("pt_core_news_sm")
doc = nlp("o nave estava danificado")
for token in doc:
    print(token.text, token.pos_, token.morph.get("Gender"))
# o    DET  ['Masc']
# nave NOUN ['Fem']   ← inconsistência detectável!
```

### Quero verificar gramática PT-BR com LanguageTool

```python
import language_tool_python
tool = language_tool_python.LanguageTool("pt-BR")
erros = tool.check("O nave estava danificado")
for e in erros:
    print(e.message, e.replacements[:2])
tool.close()
# Requer Java 8+: java -version
```

### Quero chamar Ollama local

```python
import requests
resp = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama3.1:8b",
    "prompt": "Traduza: The warrior cannot move",
    "stream": False,
    "options": {"temperature": 0.3}
}, timeout=60)
print(resp.json()["response"])
```

### Quero chamar Groq (cloud gratuito)

```python
from groq import Groq
import os
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
resp = client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages=[{"role": "user", "content": "Traduza: The warrior cannot move"}],
    temperature=0.3
)
print(resp.choices[0].message.content)
```

### Quero Google Translate sem API key

```python
from deep_translator import GoogleTranslator
result = GoogleTranslator(source="en", target="pt").translate("The warrior cannot move")
# Limite: ~5000 chars por chamada
```

### Quero detectar se texto está em inglês ou português

```python
from langdetect import detect
lang = detect("The warrior cannot move")  # "en"
lang = detect("O guerreiro não pode se mover")  # "pt"
```

### Quero mostrar barra de progresso

```python
from tqdm import tqdm
for item in tqdm(lista, unit="str", desc="Processando"):
    processar(item)
```

### Quero carregar variáveis do .env

```python
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("GROQ_API_KEY", "")
```

## Limites e armadilhas

| Biblioteca | Limite | Armadilha |
|------------|--------|-----------|
| `Helsinki-NLP` | ~512 tokens | Trunca silenciosamente strings longas |
| `deep-translator` | ~5000 chars | Pode falhar com muitas tags protegidas |
| `spacy` | Velocidade | `nlp(texto)` é lento — processar em batch: `nlp.pipe(textos)` |
| `language-tool-python` | Requer Java 8+ | Falha silenciosamente se Java não estiver no PATH |
| `sentence-transformers` | RAM | Modelo ocupa ~400MB na RAM — instanciar uma vez só |
| `groq` | 14.400 req/dia | Sem retry automático no rate limit — implementar manualmente |
| `Ollama` | Requer servidor rodando | `requests.ConnectionError` se `ollama serve` não estiver ativo |
