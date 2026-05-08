# Warhammer 40,000: Rogue Trader — Tradução PT-BR

[![Validação CI](https://github.com/murilobarbosa2002/warhamer40k-rogue-trader-traducao/actions/workflows/ci.yml/badge.svg)](https://github.com/murilobarbosa2002/warhamer40k-rogue-trader-traducao/actions/workflows/ci.yml)
[![Contribuições bem-vindas](https://img.shields.io/badge/contribuições-bem--vindas-brightgreen)](CONTRIBUTING.md)
[![Versão do jogo](https://img.shields.io/badge/jogo-1.5.0.320-blue)](https://store.steampowered.com/app/2186680/Warhammer_40000_Rogue_Trader/)

Mod de tradução não oficial para o português brasileiro do jogo **Warhammer 40,000: Rogue Trader** (Owlcat Games).

> **Status:** ~99% traduzido — 69.377+ de 69.795 strings. Arquitetura de fontes `src/strings/` implementada. Score de qualidade: 9.7/10.

---

## Origem e objetivo do projeto

Este projeto parte da tradução publicada no Nexus Mods por [fabiobassini](https://www.nexusmods.com/warhammer40kroguetrader/mods/5), que cobria a versão **1.4.1.229** do jogo e foi gerada **100% automaticamente com Google Translate, sem revisão humana**. O resultado é funcional, mas com qualidade inconsistente — termos de jogo em inglês no meio do texto, tom robótico em falas de personagens, erros de concordância de gênero e terminologia fora do padrão WH40K.

**O que este projeto está fazendo:**

- Atualizar a compatibilidade para a versão **1.5.0.320**
- Estruturar um projeto público para receber contribuições da comunidade
- Melhorar progressivamente a qualidade da tradução (terminologia, tom, revisão)
- Manter compatibilidade com futuras atualizações e DLCs

**Sobre o mantenedor:** Não sou tradutor, não falo inglês e não tenho experiência com localização de jogos — sou apenas um desenvolvedor brasileiro que queria que outros brasileiros pudessem jogar com tradução. Por isso este projeto é aberto: ele depende da comunidade para melhorar. Se você fala inglês, entende o universo WH40K ou simplesmente jogou o jogo e achou algo estranho na tradução, sua contribuição é muito bem-vinda.

---

## Instalação do mod

1. Baixe o arquivo `enGB.json` da [última release](https://github.com/murilobarbosa2002/warhamer40k-rogue-trader-traducao/releases)
2. Navegue até a pasta de localização do jogo:
   ```
   <Steam>/steamapps/common/Warhammer 40000 Rogue Trader/Bundles/localization/
   ```
3. Faça backup do `enGB.json` original
4. Substitua pelo arquivo baixado
5. Inicie o jogo — a tradução será carregada automaticamente

> O jogo precisa estar na versão **1.5.0.320** para compatibilidade total.

---

## Estado da tradução

| Métrica | Valor |
|---------|-------|
| Strings traduzidas | ~69.377 (~99%) |
| Strings ainda em inglês | ~418 (em tradução automática) |
| Strings simbólicas/tags | ~4.981 (7,1%) |
| Erros de tag | 0 |
| Score de qualidade | 9.7/10 |

Para ver o relatório completo atualizado:
```bash
python3 scripts/relatorio.py
```

---

## Contribuindo

Toda ajuda é bem-vinda! Veja o guia completo em [CONTRIBUTING.md](./CONTRIBUTING.md).

**Formas de contribuir:**
- Traduzir strings ainda em inglês
- Corrigir o tom de falas de personagens (muito robotizado pela tradução automática original)
- Corrigir erros de concordância de gênero (`o nave` → `a nave`)
- Revisar terminologia do glossário
- Reportar erros abrindo uma [Issue](https://github.com/murilobarbosa2002/warhamer40k-rogue-trader-traducao/issues)

---

## Ambiente de desenvolvimento

**Requisitos:** Python 3.10+, Git

```bash
git clone https://github.com/murilobarbosa2002/warhamer40k-rogue-trader-traducao.git
cd warhamer40k-rogue-trader-traducao

# Criar ambiente virtual e instalar dependências
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Baixar modelo de linguagem PT para gramática (opcional)
.venv/bin/python -m spacy download pt_core_news_sm

# Configurar provedores de IA (opcional — só para tradução automática)
cp .env.example .env
```

### Arquitetura de fontes

As traduções são mantidas em `src/strings/<categoria>.json` e compiladas para `enGB.json`:

```bash
# Ver estatísticas por categoria
make split-stats

# Após editar src/strings/, reconstruir enGB.json
make compile

# Validar o resultado
make validar
```

### Tradução automática com IA

O projeto usa uma pipeline de IA com fallback automático:
**Translation Memory** → **Helsinki-NLP (local, offline)** → **Ollama (local)** → **Groq (cloud gratuito)** → **Google Translate**

```bash
# Traduzir strings pendentes com Helsinki-NLP (sem internet, ~465MB)
python3 scripts/translate_batch.py --provider helsinki

# Traduzir com Ollama local (requer ollama pull llama3.1:8b)
python3 scripts/translate_batch.py --provider ollama

# Traduzir apenas 50 strings para testar
python3 scripts/translate_batch.py --limite 50

# Retomar de onde parou (checkpoint automático)
python3 scripts/translate_batch.py
```

### Scripts disponíveis

| Script | Descrição |
|--------|-----------|
| `scripts/split.py` | Migra enGB.json para `src/strings/` por categoria (1x) |
| `scripts/compile.py` | Reconstrói enGB.json a partir de `src/strings/` |
| `scripts/translate_batch.py` | Traduz strings com IA (Helsinki/Ollama/Groq/Google) |
| `scripts/fix_auto.py` | Correções automáticas de terminologia (MP→PM, etc.) |
| `scripts/fix_tags.py` | Repara tags `{g|..}{/g}` desbalanceadas |
| `scripts/fix_gender.py` | Corrige concordância de gênero |
| `scripts/validate.py` | Valida estrutura JSON e balanço de tags |
| `scripts/relatorio.py` | Relatório completo de qualidade |
| `scripts/check_grammar.py` | Verificação gramatical com spaCy + LanguageTool |
| `scripts/check_consistency.py` | Detecta traduções inconsistentes para strings similares |

```bash
make help  # lista todos os comandos disponíveis
```

### Agentes Copilot (VS Code)

Se você usa VS Code com GitHub Copilot, há agentes especializados disponíveis:

| Agente | Função |
|--------|--------|
| **Tradutor WH40K** | Traduz strings com terminologia WH40K correta |
| **Revisor de Qualidade** | Revisa tom, terminologia e gramática |
| **Corretor Automático** | Aplica correções em massa via scripts |
| **Desenvolvedor** | Escreve e modifica scripts Python do projeto |
| **Arquiteto** | Revisa decisões de design e trade-offs |
| **DevOps** | CI/CD, releases, pre-commit e troubleshooting |

---

## Glossário canônico

Os termos principais obrigatórios:

| Inglês | PT-BR |
|--------|-------|
| Action Points / AP | Pontos de Ação / PA |
| Movement Points / MP | Pontos de Movimento / PM |
| Wounds / HP | Ferimentos |
| Damage | Dano |
| Cooldown | Recarga |
| Skill | Perícia |
| Talent | Talento |
| NPC | PNJ |
| The Warp | O Imaterium / A Distorção |
| Lord Captain | Capitão-Comandante |

Termos que **nunca** se traduzem (nomes próprios do universo WH40K):

- **Facções:** `Rogue Trader`, `Astartes`, `Adeptus Mechanicus`, `Adepta Sororitas`, `Inquisition`, `Astra Militarum`, `Space Wolves`, `Grey Knights`, `Drukhari`, `Leagues of Votann`
- **Entidades:** `Chaos`, `Warp`, `Immaterium`, `Omnissiah`, `Eldar`, `Ork`, `Necron`, `Tyranid`, `Daemon`, `Nurgle`, `Tzeentch`, `Khorne`, `Slaanesh`
- **Armas:** `Bolter`, `Lasgun`, `Plasma Gun`, `Meltagun`, `Chainsword`, `Power Sword`, `Thunder Hammer`
- **Personagens:** `Abelard Werserian`, `Cassia Orsellio`, `Argenta`, `Idira Tlass`, `Pasqal Haneumann`, `Yrliet Lanaevyss`, `Ulfar`, `Heinrix van Calox`, `Marazhai`, `Jae Heydari`
- **Locais:** `Port Wander`, `Footfall`, `The Maw`, `Koronus Expanse`

Lista completa (150+ termos) em [`glossario.json`](./glossario.json).

---

## Licença

Este é um projeto de fãs sem fins lucrativos. Warhammer 40,000: Rogue Trader é propriedade da Owlcat Games e Games Workshop. Este mod não é afiliado nem endossado por nenhuma dessas empresas.
