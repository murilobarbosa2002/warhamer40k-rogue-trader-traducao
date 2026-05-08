# Warhammer 40K: Rogue Trader — Projeto de Tradução PT-BR

Este é um projeto colaborativo de tradução do jogo **Warhammer 40,000: Rogue Trader** para o português brasileiro. O arquivo principal de tradução é `enGB.json`, com ~69.862 strings.

---

## Mapa Completo do Projeto

### Arquivos de dados

| Arquivo | Descrição |
|---------|-----------|
| `enGB.json` | Arquivo de tradução PT-BR (mod para o jogo, ~69.862 strings) |
| `arquivo-original-1.5.0.320.json` | Original EN versão 1.5.0.320 — fonte da verdade (no .gitignore) |
| `glossario.json` | Terminologia canônica obrigatória (~60 termos) |
| `translation-memory.json` | Pares EN→PT aprovados por humanos (prioridade sobre IA) |

### Scripts de tradução

| Script | Função | Principais flags |
|--------|--------|-----------------|
| `scripts/translate_batch.py` | Pipeline de tradução com IA | `--provider`, `--limite`, `--dry-run`, `--reset` |
| `scripts/build_from_original.py` | Reconstrói enGB.json limpo | `--stats`, `--dry-run` |
| `scripts/diff_original.py` | Gera fila de trabalho | `--stats`, `--output` |

### Scripts de correção

| Script | Função | Principais flags |
|--------|--------|-----------------|
| `scripts/fix_auto.py` | Correções de terminologia (MP→PM, AP→PA, cooldown) | `--dry-run` |
| `scripts/fix_tags.py` | Repara tags `{g|..}{/g}` desbalanceadas | `--dry-run` |
| `scripts/fix_gender.py` | Corrige concordância de gênero | `--dry-run` |

### Scripts de qualidade e análise

| Script | Função | Principais flags |
|--------|--------|-----------------|
| `scripts/validate.py` | Valida estrutura JSON e tags | — |
| `scripts/relatorio.py` | Relatório completo de qualidade | `--output` |
| `scripts/check_grammar.py` | Verifica gramática com spaCy + LanguageTool | `--spacy-only`, `--limite`, `--categoria` |
| `scripts/check_consistency.py` | Detecta inconsistências via sentence-transformers | `--limite`, `--threshold`, `--output` |
| `scripts/categorizar.py` | Agrupa strings por área temática | subcomandos: `relatorio`, `listar`, `exportar` |
| `scripts/release.py` | Empacota release versionada | `--versao` |

### Infraestrutura

| Arquivo | Descrição |
|---------|-----------|
| `Makefile` | Atalhos para todos os comandos (`make help` para listar) |
| `requirements.txt` | Dependências Python com versões fixas |
| `.env` / `.env.example` | Configuração de provedores de IA e parâmetros |
| `.pre-commit-config.yaml` | Roda `validate.py` antes de cada commit |
| `.github/workflows/ci.yml` | CI: valida JSON, score por PR, atualiza % no README |
| `CHANGELOG.md` | Índice de releases |
| `releases/unreleased.md` | Log de trabalho em andamento |

---

## Arquitetura dos Scripts

### Padrões obrigatórios em todos os scripts

```python
ROOT = Path(__file__).parent.parent   # raiz do projeto
ENDB_PATH = ROOT / "enGB.json"        # sempre via ROOT
TAG_RE = re.compile(r"\{[^}]+\}|<[^>]+>")  # regex padrão de tags
```

### Padrão de argparse

```python
parser = argparse.ArgumentParser(description="...")
parser.add_argument("--dry-run", action="store_true", help="Simular sem salvar")
parser.add_argument("--limite", type=int, default=0, help="0 = sem limite")
args = parser.parse_args()
sys.exit(run(...))
```

### Padrão de leitura/escrita do enGB.json

```python
# Leitura
with open(ENDB_PATH, encoding="utf-8") as f:
    data = json.load(f)
strings = data["strings"]   # dict[uuid, {"Offset": int, "Text": str}]

# Escrita — sempre preserve Offset
strings[uuid]["Text"] = novo_texto

with open(ENDB_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

### Regra crítica: nunca alterar Offset ou UUID

O jogo usa o campo `Offset` para indexação binária. Alterar ou reordenar strings quebra o mod. Sempre escrever de volta o `data` completo, nunca reconstruir o JSON do zero.

---

## Stack de Bibliotecas

### Tradução e IA

| Biblioteca | Versão | Uso no projeto |
|------------|--------|----------------|
| `transformers` | ≥4.40 | Helsinki-NLP `opus-mt-tc-big-en-pt` — modelo local offline EN→PT |
| `sentencepiece` | ≥0.2 | Tokenizador do Helsinki-NLP (dependência obrigatória) |
| `sentence-transformers` | ≥3.0 | `paraphrase-multilingual-MiniLM-L12-v2` — embeddings semânticos EN+PT |
| `torch` | ≥2.0 | Backend CPU para transformers e sentence-transformers |
| `groq` | ≥1.2 | API Groq cloud (llama-3.1-8b-instant, 14.400 req/dia gratuitos) |
| `deep-translator` | ≥1.11 | Google Translate sem API key (fallback final) |
| `langdetect` | ≥1.0.9 | Detecta se string traduzida voltou em inglês |

### NLP e Gramática

| Biblioteca | Uso no projeto |
|------------|----------------|
| `spacy` + `pt_core_news_sm` | POS tagging e morfologia PT-BR em `check_grammar.py` |
| `language-tool-python` | Verificação gramatical PT-BR (requer Java 8+ no sistema) |

### Infra e CLI

| Biblioteca | Uso no projeto |
|------------|----------------|
| `rich` | Saída formatada no terminal (tabelas, cores) |
| `tqdm` | Barra de progresso em loops longos |
| `python-dotenv` | Carrega `.env` com `load_dotenv()` |
| `requests` | HTTP para Ollama e outras APIs |

### Ollama (IA local)

- **URL padrão**: `http://localhost:11434`
- **Modelo**: `llama3.1:8b` (4.7GB, CPU-only)
- **API**: `POST /api/generate` com payload `{"model", "prompt", "stream": false, "options": {"temperature": 0.3}}`
- **Setup**: `curl -fsSL https://ollama.com/install.sh | sudo sh && ollama pull llama3.1:8b`

### Helsinki-NLP

- **Modelo**: `Helsinki-NLP/opus-mt-tc-big-en-pt`
- **Baixado automaticamente** do HuggingFace no primeiro uso (~300MB, em `~/.cache/huggingface/`)
- **Uso**: `pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-en-pt", device=-1)`
- **Limite**: ~512 tokens por chamada; trunca automaticamente

### Sentence-Transformers

- **Modelo**: `paraphrase-multilingual-MiniLM-L12-v2` (~90MB)
- **Uso**: embeddings normalizados + `util.cos_sim()` para similaridade
- **Cache**: `~/.cache/torch/sentence_transformers/`
- **Primeira execução**: baixa automaticamente

### spaCy

- **Modelo PT**: `pt_core_news_sm` (43MB)
- **Setup**: `python -m spacy download pt_core_news_sm`
- **Uso**: `spacy.load("pt_core_news_sm")` → `doc.token.morph.get("Gender")`

---

## Pipeline de Tradução

### Ordem de fallback em `translate_batch.py`

```
Translation Memory (pares humanos aprovados)
    ↓ (se não encontrado)
Provedor principal (TRANSLATION_PROVIDER no .env)
    ↓ (se falhar)
Groq API (se GROQ_API_KEY configurado)
    ↓ (se falhar)
Helsinki-NLP (modelo local offline)
    ↓ (se falhar)
Google Translate (deep-translator, sem API key)
```

### Checkpoint

O arquivo `.translation_checkpoint.json` salva o progresso automaticamente a cada 10 strings. Para retomar: basta rodar o script de novo. Para recomeçar: `--reset`.

### Translation Memory (`translation-memory.json`)

```json
{
  "_meta": {"total_pairs": 0},
  "pairs": {
    "uuid": {"en": "...", "pt": "...", "revisor": "github_user", "data": "YYYY-MM-DD"}
  }
}
```

Pares aqui têm **prioridade absoluta** sobre qualquer IA. Editar diretamente para adicionar traduções humanas revisadas.

---

## CI/CD — `.github/workflows/ci.yml`

### Jobs e quando rodam

| Job | Trigger | Função |
|-----|---------|--------|
| `validar-json` | push + PR | Valida JSON e tags |
| `score-pr` | PR only | Comenta tabela de qualidade antes/depois |
| `relatorio-qualidade` | PR only | Gera relatório completo, sobe como artefato |
| `verificar-termos` | PR only | Detecta AP, MP, cooldown em texto PT |
| `atualizar-stats` | push to main | Atualiza % no README automaticamente |

### Permissões necessárias

`score-pr` precisa de `permissions: pull-requests: write` no job. O token `GITHUB_TOKEN` é automático.

---

## Makefile — Referência completa

```bash
make setup              # cria .venv, instala requirements.txt, baixa spacy pt_core_news_sm
make status             # diff_original.py --stats
make validar            # validate.py
make relatorio          # relatorio.py
make categorias         # categorizar.py --nao-traduzidas
make exportar-categorias  # categorizar.py --exportar → revisao/

make fix                # fix_auto.py (com confirmação)
make fix-tags           # fix_tags.py (com confirmação)
make fix-gender         # fix_gender.py (com confirmação)
make fix-all            # fix_tags + fix_auto + fix_gender + validate (sem confirmação)

make traduzir           # translate_batch.py (Ollama)
make traduzir-10        # translate_batch.py --limite 10
make traduzir-N         # translate_batch.py --limite N (ex: make traduzir-50)
make traduzir-google    # translate_batch.py --provider deep_translator
make traduzir-helsinki  # translate_batch.py --provider helsinki

make check-grammar      # check_grammar.py --spacy-only
make check-grammar-full # check_grammar.py (spaCy + LanguageTool, requer Java)
make check-consistency  # check_consistency.py --limite 3000

make release            # release.py (pede versão interativamente)
make commit-traducao    # git add enGB.json + commit padronizado + push
```

---

## Convenções de Código

### Nomes de arquivo e variáveis

- Scripts em `snake_case`, ex: `fix_auto.py`, `check_grammar.py`
- Constantes em `UPPER_SNAKE_CASE` no topo do arquivo
- Paths sempre como `Path` (não `str`), construídos via `ROOT / "subpasta" / "arquivo"`

### Saída para o usuário

- Usar `print()` simples (não `rich`) em scripts de uso diário — compatível com CI
- Usar `rich` apenas em relatórios visuais (`relatorio.py`)
- Sempre mostrar contadores: `{n:,}` para números grandes
- Separadores: `"=" * 50` ou `"-" * 50`

### Manipulação de tags

Nunca usar `str.replace()` dentro de texto com tags. Sempre usar o padrão:

```python
TAG_RE = re.compile(r"\{[^}]+\}|<[^>]+>")

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
```

### Dry-run obrigatório

Todo script que modifica `enGB.json` DEVE implementar `--dry-run` que executa a lógica completa mas não salva. Mostrar contadores de o que seria alterado.

### Tratamento de erros

Scripts de correção nunca devem abortar por erro em uma string individual. Coletar erros numa lista `ERRORS` e reportar no final. Retornar `exit(1)` apenas se houver erros críticos de estrutura.

---

## Configuração do Ambiente

```bash
# Setup completo
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m spacy download pt_core_news_sm
cp .env.example .env   # editar com suas chaves

# Verificar se tudo está OK
make validar && make status

# IA local (opcional mas recomendado)
curl -fsSL https://ollama.com/install.sh | sudo sh
ollama pull llama3.1:8b

# Java para LanguageTool (opcional)
sudo apt-get install default-jre
```

### Variáveis do `.env`

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `TRANSLATION_PROVIDER` | `ollama` | Provedor principal: `ollama`, `groq`, `helsinki`, `deep_translator` |
| `OLLAMA_URL` | `http://localhost:11434` | URL do servidor Ollama |
| `OLLAMA_MODEL` | `llama3.1:8b` | Modelo Ollama |
| `GROQ_API_KEY` | — | Chave Groq (14.400 req/dia gratuitos) |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Modelo Groq |
| `BATCH_SIZE` | `10` | Strings por lote |
| `MAX_RETRIES` | `3` | Tentativas por provedor |
| `DELAY_BETWEEN_BATCHES` | `0.5` | Segundos entre lotes |
| `CHECKPOINT_FILE` | `.translation_checkpoint.json` | Arquivo de checkpoint |

---

## Estrutura de Releases

```
releases/
  unreleased.md          ← trabalho em andamento
  1.5.0.320-ptbr-v1/     ← criado por release.py
    enGB.json
    LEIAME.txt
    1.5.0.320-ptbr-v1.md  ← notas da release
```

`release.py --versao X.Y.Z-ptbr-vN` cria a pasta, copia o enGB.json, gera LEIAME.txt e atualiza CHANGELOG.md.

---



Warhammer 40K é um universo de ficção científica **grimdark** (sombrio e brutal). O tom é sério, formal, épico e às vezes litúrgico. Personagens nobres falam com altivez, militares falam com autoridade, cultistas e hereges com fanatismo. Evite tom casual ou moderno.

O jogador interpreta um **Rogue Trader** (Comerciante Desonesto/Explorador Imperialista) — um nobre com Carta de Marca Imperial que tem autoridade quase absoluta nos espaços não conquistados. Use pronomes masculinos para o personagem jogador, exceto quando o próprio texto fonte usar explicitamente pronomes femininos (she/her) ou neutros para esse personagem.

## Estrutura do Arquivo

`enGB.json` tem o seguinte formato — **NUNCA altere as chaves UUID nem o campo `Offset`**:

```json
{
  "strings": {
    "uuid-da-string": {
      "Offset": 0,
      "Text": "Texto traduzido aqui"
    }
  }
}
```

### Tags que DEVEM ser preservadas intactas

| Tag | Exemplo | Descrição |
|-----|---------|-----------|
| `{g|..}..{/g}` | `{g|Encyclopedia:Damage}dano{/g}` | Link de enciclopédia — traduz só o texto interno |
| `{d|..}..{/d}` | `{d|Encyclopedia:Ch1_Foo}texto{/d}` | Link de diálogo — traduz só o texto interno |
| `{n}..{/n}` | `{n}Narração{/n}` | Bloco de narração |
| `{uip|..}` | `{uip|MP|uuid}` | Variável de UI — NÃO traduzir |
| `{unit_stat|..}` | `{unit_stat|WP|stat}` | Stat de unidade — NÃO traduzir |
| `<b>`, `<i>`, `<br>` | `<b>negrito</b>` | HTML de formatação — preservar |
| `\n` | — | Quebra de linha — preservar |

**Atenção:** O identificador dentro de `{g|Encyclopedia:NomeDaCoisa}` nunca é traduzido. Apenas o texto entre as tags é traduzido.

## Glossário Canônico

Consulte sempre `glossario.json` na raiz do projeto. Os termos abaixo são obrigatórios:

| Inglês | PT-BR Canônico | Notas |
|--------|----------------|-------|
| Action Points / AP | Pontos de Ação / **PA** | Nunca usar "AP" em texto PT |
| Movement Points / MP | Pontos de Movimento / **PM** | Nunca usar "MP" em texto PT |
| Wounds / HP | **Ferimentos** | Terminologia do tabletop WH40K |
| Damage | **Dano** | |
| Target | **Alvo** | |
| Range | **Alcance** | |
| Cooldown | **Recarga** | |
| Buff | **Aprimoramento** | Ou "bônus de efeito" quando como substantivo |
| Debuff | **Penalidade de efeito** | |
| Skill (perícia de personagem) | **Perícia** | |
| Ability / Feat | **Habilidade** | |
| Talent | **Talento** | |
| Trait | **Característica** | |
| Passive | **Passivo** | |
| Round | **Rodada** | |
| Turn | **Turno** | |
| Resistance Test | **Teste de Resistência** | |
| Cover | **Cobertura** | |
| Dodge | **Esquiva** | |
| Charge | **Investida** | |
| Spawn (creature created) | **Criatura gerada** | Exceto "Spawn do Caos" (nome próprio) |
| NPC | **PNJ** | Personagem Não-Jogador |
| The Void / Void | **O Vazio** | Espaço sideral em WH40K |
| The Warp | **O Imaterium** ou **A Distorção** | Usar "Imaterium" para o lugar, "Distorção" para efeitos |
| Lord Captain | **Capitão-Comandante** | Título do Rogue Trader |
| Lore (skill category) | **Conhecimento** | Ex: "Lore (Warp)" → "Conhecimento (Distorção)" |

### Termos que NUNCA são traduzidos (nomes próprios do universo WH40K)

`Rogue Trader`, `Astartes`, `Space Marine`, `Adeptus Mechanicus`, `Adepta Sororitas`, `Inquisition`, `Mechanicus`, `Omnissiah`, `Immaterium`, `Chaos` (quando nome próprio), `Eldar`, `Aeldari`, `Tau`, `Ork`, `Necron`, `Tyranid`, `Bolter`, `Boltgun`, `Lasgun`, `Laspistol`, `Longlas`, `Vox`, `Mechadendrite`, `Servo-skull`, `Throne` (quando "Golden Throne"), `Webway`, `Warp` (quando nome próprio), `Ferrum Sanctum`, `Omnissias`.

## Regras de Tradução

### 1. Formatação e Tags

- **Preservar todas as tags** exatamente como estão: `{g|..}texto{/g}`, `{n}texto{/n}`, `{uip|..}`, `{unit_stat|..}`, `<b>`, `<i>`, `<br>`, `\n`
- O identificador dentro de `{g|Encyclopedia:NomeDaCoisa}` **nunca é traduzido** — apenas o texto entre as tags
- Não remover, reordenar ou modificar tags `{g|...}`, `{n}...{/n}`, `{uip|...}`
- Não traduzir UUIDs, chaves ou identificadores

### 2. Terminologia

- Usar sempre o glossário canônico (seção acima): AP→PA, MP→PM, Cooldown→Recarga, etc.
- Não usar termos em inglês em texto PT-BR: "damage", "target", "range", "cooldown", "buff", "skill"
- Não misturar "MP" com "PM" ou "AP" com "PA" na mesma string
- Não traduzir nomes próprios do universo WH40K listados na seção de glossário

### 3. Tom e Estilo

- **Tom grimdark**: falas épicas, sérias ou brutais — sem linguagem casual ou moderna
- O jogo usa "você" majoritariamente; manter esse padrão salvo exceções de personagens com estatura formal
- Evitar traduções literais robóticas: "certifique-se de que" → "garanta que"; "você pode ser capaz de" → reescrever livremente
- Verificar concordância de gênero dos substantivos (ex: "a nave" é feminina)

### 4. Tipos de Texto

| Tipo | Orientação |
|------|------------|
| Interface (UI) | Direto e conciso. "Pick up item" → "Pegar item" |
| Enciclopédia/Habilidades | Tom técnico-formal. Usar glossário estritamente |
| Falas de personagens | Preservar voz e personalidade: Tech-Priest usa jargão mecânico; Soldado fala direto; Noble fala com altivez |
