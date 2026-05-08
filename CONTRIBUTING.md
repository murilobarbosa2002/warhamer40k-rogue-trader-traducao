# Como Contribuir — WH40K: Rogue Trader PT-BR

Bem-vindo! Este é um projeto colaborativo de tradução para o português brasileiro. Toda ajuda é bem-vinda — seja corrigindo uma linha, traduzindo blocos inteiros ou revisando o tom das falas.

## Estado atual da tradução

> Execute `python3 scripts/relatorio.py` para ver o estado mais recente.

Estado após a refatoração da arquitetura:
- **~99% das strings traduzidas** (automaticamente via Helsinki-NLP)
- **0 erros de tag** (corrigidos pelos scripts de fix)
- **Score de qualidade: 9.7/10**
- Foco atual: **revisão humana da qualidade** — o conteúdo está traduzido, mas partes ainda precisam de revisão de tom e terminologia WH40K

---

## Pré-requisitos

- Git
- Python 3.10+
- VS Code com extensão GitHub Copilot (para usar os agentes, opcional)

```bash
git clone https://github.com/murilobarbosa2002/warhamer40k-rogue-trader-traducao.git
cd warhamer40k-rogue-trader-traducao

# Criar ambiente virtual e instalar dependências
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Baixar modelo de linguagem PT (para check_grammar.py)
.venv/bin/python -m spacy download pt_core_news_sm

# Copiar configuração de IA (opcional — só necessário para tradução automática)
cp .env.example .env
```

---

## Fluxo de contribuição

### 1. Crie uma branch para sua contribuição

```bash
git checkout -b fix/corrige-strings-combate
# ou
git checkout -b traducao/strings-capitulo-2
```

**Convenção de nome de branch:**
- `fix/` — corrige erros existentes
- `traducao/` — traduz strings novas
- `revisao/` — revisão de qualidade de strings já traduzidas
- `glossario/` — atualiza o glossário canônico

### 2. Edite os arquivos `src/strings/<categoria>.json`

O projeto usa uma arquitetura de fontes por categoria. **Não edite `enGB.json` diretamente** — ele é gerado automaticamente.

```
src/strings/
  ui.json          ← Interface (botões, menus)
  tutorial.json    ← Dicas e tutoriais
  combate.json     ← Combate e mecânicas
  enciclopedia.json← Enciclopédia e lore
  itens.json       ← Itens e equipamentos
  missoes.json     ← Missões e objetivos
  personagens.json ← Personagens e NPCs
  dialogo.json     ← Diálogos e narrativa
  outros.json      ← Strings não categorizadas
```

Cada entrada tem o formato:
```json
"uuid-da-string": {
  "en": "texto original em inglês (referência, nunca alterar)",
  "pt": "texto traduzido em português",
  "status": "approved"
}
```

Ao revisar uma string, altere o campo `"pt"` e mude `"status"` para `"approved"`.

Após editar, reconstrua o `enGB.json`:
```bash
python3 scripts/compile.py --validar
```

**NUNCA altere:**
- UUIDs (as chaves do JSON)
- O campo `"en"` (texto de referência)
- Identificadores dentro de tags: `{g|Encyclopedia:NomeDaCoisa}` — só o texto entre as tags

**SEMPRE consulte:**
- [`glossario.json`](./glossario.json) — terminologia canônica
- [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) — regras completas

### 3. Valide suas alterações

```bash
# Reconstruir enGB.json a partir dos src/ e validar
python3 scripts/compile.py --validar

# Ou só validar o enGB.json atual
python3 scripts/validate.py
```

O CI também roda isso automaticamente no PR. PRs com erros estruturais não serão aceitos.

### 4. Abra o Pull Request

- Título: `[fix] Corrige X strings com termo "cooldown"` ou `[trad] Traduz strings do Capítulo 3` ou `[revisao] Melhora tom das falas do Argenta`
- Descreva quais arquivos/categorias foram alterados
- Se alterou muitas strings, mostre 2-3 exemplos de antes/depois

---

## Usando os Agentes Copilot

Se você usa VS Code com Copilot, os agentes estão disponíveis via `@` no chat:

| Agente | Como usar |
|--------|-----------|
| **Tradutor WH40K** | Traduz strings individuais ou em lote com terminologia correta |
| **Revisor de Qualidade** | Revisa qualidade, detecta erros de terminologia e gramática |
| **Corretor Automático** | Aplica correções automáticas seguras em massa |

**Prompts disponíveis** (digite `/` no chat Copilot):

| Prompt | O que faz |
|--------|-----------|
| `/traduzir-nao-traduzidas` | Encontra e traduz todas as strings ainda em inglês |
| `/revisar-lote` | Revisa um lote de strings e gera relatório |
| `/aplicar-correcoes` | Aplica correções automáticas de terminologia |
| `/relatorio-qualidade` | Gera relatório completo de qualidade |
| `/melhorar-literario` | Melhora o tom e estilo de falas de personagens |

---

## Glossário rápido

| Inglês | PT-BR correto | Proibido |
|--------|--------------|---------|
| Action Points / AP | Pontos de Ação / **PA** | AP |
| Movement Points / MP | Pontos de Movimento / **PM** | MP |
| Wounds / HP | **Ferimentos** | HP, Vida |
| Damage | **Dano** | damage |
| Target | **Alvo** | target |
| Range | **Alcance** | range |
| Cooldown | **Recarga** | cooldown |
| Buff | **Aprimoramento** | buff |
| Debuff | **Penalidade de efeito** | debuff |
| Skill | **Perícia** | skill |
| Talent | **Talento** | talent |
| NPC | **PNJ** | NPC |

Termos que **nunca** se traduzem: `Rogue Trader`, `Astartes`, `Space Marine`, `Bolter`, `Warp`, `Immaterium`, `Chaos`, `Ork`, `Eldar`, `Necron`, `Tyranid`, `Mechanicus`, `Omnissiah`, `Inquisition`, `Psyker`, `Vox`, `Mechadendrite`, `Servo-skull`, `Webway`.

---

## Tags do jogo — preserve-as!

```
{g|Encyclopedia:NomeDaCoisa}texto traduzido{/g}   ← traduz só o texto interno
{d|Encyclopedia:NomeDaCoisa}texto traduzido{/d}   ← idem
{n}texto de narração{/n}                          ← traduz o texto
{uip|MP|uuid}                                      ← NÃO traduzir
{unit_stat|WP|stat}                                ← NÃO traduzir
<b>negrito</b>  <i>itálico</i>  <br>  \n          ← preservar
```

---

## Scripts disponíveis

```bash
# Ver estatísticas de tradução por categoria
python3 scripts/split.py --stats

# Após editar src/strings/, reconstruir enGB.json
python3 scripts/compile.py --validar

# Traduzir strings pendentes com IA (Helsinki-NLP, sem internet após download)
python3 scripts/translate_batch.py --provider helsinki

# Traduzir apenas 50 strings para testar
python3 scripts/translate_batch.py --limite 50

# Aplicar correções automáticas de terminologia
python3 scripts/fix_auto.py

# Validar integridade do JSON
python3 scripts/validate.py

# Ver relatório completo de qualidade
python3 scripts/relatorio.py

# Verificar gramática PT-BR
python3 scripts/check_grammar.py --spacy-only

# Todos os comandos disponíveis
make help
```

| Script | Descrição |
|--------|-----------|
| `split.py` | Migra enGB.json para `src/strings/` por categoria |
| `compile.py` | Reconstrói enGB.json a partir de `src/strings/` |
| `translate_batch.py` | Traduz com IA — Translation Memory → Helsinki → Ollama → Groq → Google |
| `fix_auto.py` | Correções automáticas seguras (MP→PM, AP→PA, cooldown→recarga) |
| `fix_tags.py` | Repara tags `{g|..}{/g}` desbalanceadas |
| `fix_gender.py` | Corrige concordância de gênero |
| `validate.py` | Valida estrutura JSON e balanço de tags |
| `relatorio.py` | Relatório completo: score, erros, estatísticas |
| `check_grammar.py` | Verifica gramática PT-BR com spaCy + LanguageTool |
| `check_consistency.py` | Detecta strings EN similares com traduções PT inconsistentes |

---

## Dúvidas?

Abra uma [Issue](https://github.com/murilobarbosa2002/warhamer40k-rogue-trader-traducao/issues) descrevendo sua dúvida ou sugestão de terminologia.
