# Warhammer 40,000: Rogue Trader — Tradução PT-BR

Mod de tradução não oficial para o português brasileiro do jogo **Warhammer 40,000: Rogue Trader** (Owlcat Games).

> **Status:** 92,1% traduzido — 64.289 de 69.795 strings. ~510 strings ainda em inglês.

---

## Origem e objetivo do projeto

Este projeto parte da tradução publicada no Nexus Mods por [fabiobassini](https://www.nexusmods.com/warhammer40kroguetrader/mods/5), que cobria a versão **1.4.1.229** do jogo e foi gerada **100% automaticamente com Google Translate, sem revisão humana**. O resultado é funcional, mas com qualidade inconsistente — termos de jogo em inglês no meio do texto, tom robótico em falas de personagens, erros de concordância de gênero e terminologia fora do padrão WH40K.

**O que este projeto está fazendo:**

- ✅ Atualizar a compatibilidade para a versão **1.5.0.320**
- ✅ Estruturar um projeto público para receber contribuições da comunidade
- 🔄 Melhorar progressivamente a qualidade da tradução (terminologia, tom, revisão)
- 🔄 Manter compatibilidade com futuras atualizações e DLCs

**Aviso:** Eu não sou tradutor profissional. Este projeto é colaborativo — quanto mais pessoas contribuírem, melhor ficará a tradução para todos. Se você encontrou um erro, [abra uma Issue](https://github.com/murilobarbosa2002/warhamer40k-rogue-trader-traducao/issues) ou envie um Pull Request.

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
| Strings traduzidas | ~64.289 (92,1%) |
| Strings ainda em inglês | ~510 (0,7%) |
| Strings simbólicas/tags | ~4.981 (7,1%) |
| Erros de tag conhecidos | ~193 (herança da tradução automática original) |

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
pip install tqdm rich groq python-dotenv deep-translator

# Configurar provedores de IA (opcional)
cp .env.example .env
# Edite .env com suas chaves de API
```

### Tradução automática com IA

O projeto usa uma pipeline de IA com fallback automático:
**Ollama (local)** → **Groq (cloud gratuito)** → **Google Translate**

```bash
# Ver quantas strings precisam de tradução
python3 scripts/diff_original.py --stats

# Traduzir com IA local (Ollama)
# Instale primeiro: curl -fsSL https://ollama.com/install.sh | sudo sh
# Depois: ollama pull llama3.1:8b
python3 scripts/translate_batch.py

# Traduzir apenas 50 strings para testar
python3 scripts/translate_batch.py --limite 50

# Usar Google Translate (sem instalar nada)
python3 scripts/translate_batch.py --provider deep_translator
```

### Scripts disponíveis

| Script | Descrição |
|--------|-----------|
| `scripts/diff_original.py` | Compara EN original vs PT, gera fila de trabalho |
| `scripts/translate_batch.py` | Traduz strings com IA (Ollama/Groq/Google) |
| `scripts/build_from_original.py` | Reconstrói enGB.json limpo a partir do original |
| `scripts/fix_auto.py` | Correções automáticas de terminologia (MP→PM, etc.) |
| `scripts/validate.py` | Valida estrutura JSON e balanço de tags |
| `scripts/relatorio.py` | Relatório completo de qualidade |

### Agentes Copilot (VS Code)

Se você usa VS Code com GitHub Copilot, há agentes especializados disponíveis:

| Agente | Função |
|--------|--------|
| **Tradutor WH40K** | Traduz strings com terminologia WH40K correta |
| **Revisor de Qualidade** | Revisa tom, terminologia e gramática |
| **Corretor Automático** | Aplica correções em massa via scripts |

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

Termos que **nunca** se traduzem: `Rogue Trader`, `Astartes`, `Space Marine`, `Bolter`, `Warp`, `Immaterium`, `Chaos`, `Ork`, `Eldar`, `Necron`, `Mechanicus`, `Omnissiah`, `Inquisition`, `Vox`, `Mechadendrite`, `Servo-skull`, `Webway`.

Glossário completo em [`glossario.json`](./glossario.json).

---

## Licença

Este é um projeto de fãs sem fins lucrativos. Warhammer 40,000: Rogue Trader é propriedade da Owlcat Games e Games Workshop. Este mod não é afiliado nem endossado por nenhuma dessas empresas.
