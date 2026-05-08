# Como Contribuir — WH40K: Rogue Trader PT-BR

Bem-vindo! Este é um projeto colaborativo de tradução para o português brasileiro. Toda ajuda é bem-vinda — seja corrigindo uma linha, traduzindo blocos inteiros ou revisando o tom das falas.

## Estado atual da tradução

> Execute `python3 scripts/relatorio.py` para ver o estado mais recente.

Problemas conhecidos que precisam de atenção:
- **~57 strings ainda em inglês** (não traduzidas)
- **~193 strings com tags HTML/game desbalanceadas** (herança da tradução automática original)
- **~289 termos em inglês** no meio de texto PT (target, range, talent, cooldown...)
- **~97 "MP"** onde deveria ser "PM" e **~60 "AP"** onde deveria ser "PA"

---

## Pré-requisitos

- Git
- Python 3.10+
- VS Code com extensão GitHub Copilot (para usar os agentes)

```bash
git clone https://github.com/murilobarbosa2002/warhamer40k-rogue-trader-traducao.git
cd warhamer40k-rogue-trader-traducao
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

### 2. Edite o arquivo `enGB.json`

**NUNCA altere:**
- UUIDs (as chaves do JSON)
- O campo `"Offset"`
- Identificadores dentro de tags: `{g|Encyclopedia:NomeDaCoisa}` — só o texto entre as tags

**SEMPRE consulte:**
- [`glossario.json`](./glossario.json) — terminologia canônica
- [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) — regras completas

### 3. Valide suas alterações

```bash
python3 scripts/validate.py
```

O CI também roda isso automaticamente no PR. PRs com erros estruturais não serão aceitos.

### 4. Abra o Pull Request

- Título: `[fix] Corrige X strings com termo "cooldown"` ou `[trad] Traduz strings do Capítulo 3`
- Descreva quais UUIDs ou áreas foram alterados
- Se alterou muitas strings, mostre 2-3 exemplos de antes/depois

---

## Usando os Agentes Copilot

Se você usa VS Code com Copilot, os agentes estão disponíveis via `@` no chat:

| Agente | Como usar |
|--------|-----------|
| `@tradutor` | Traduz strings individuais ou em lote com terminologia correta |
| `@revisor` | Revisa qualidade, detecta erros de terminologia e gramática |
| `@corretor` | Aplica correções automáticas seguras em massa |

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
# Ver estado atual da tradução
python3 scripts/relatorio.py

# Aplicar correções automáticas (simulação)
python3 scripts/fix_auto.py --dry-run

# Aplicar correções automáticas (de verdade)
python3 scripts/fix_auto.py

# Validar integridade do JSON
python3 scripts/validate.py
```

---

## Dúvidas?

Abra uma [Issue](https://github.com/murilobarbosa2002/warhamer40k-rogue-trader-traducao/issues) descrevendo sua dúvida ou sugestão de terminologia.
