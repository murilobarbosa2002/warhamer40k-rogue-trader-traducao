# Unreleased — Em desenvolvimento

> Mudanças que ainda não foram empacotadas em uma release oficial.
> Quando uma release for publicada, mova o conteúdo daqui para um novo arquivo `releases/X.Y.Z.md`.

---

## [Unreleased] — base: 1.5.0.320

### Adicionado

**Infraestrutura do projeto**
- Compatibilidade com a versão **1.5.0.320** do jogo (base era 1.4.1.229)
- Projeto público com infraestrutura para contribuições colaborativas
- `glossario.json` v1.1.0 — terminologia canônica expandida: mecânicas de jogo, personagens do Rogue Trader, locais, instituições imperiais, armas/equipamentos, títulos e patentes WH40K
- `translation-memory.json` — memória de tradução para pares EN→PT aprovados por humanos
- `requirements.txt` — dependências Python fixas (transformers, sentence-transformers, spacy, language-tool-python, groq, etc.)
- `.env.example` — template de configuração para todos os provedores de IA
- `.pre-commit-config.yaml` — roda `validate.py` automaticamente antes de cada commit
- `Makefile` — atalhos completos para todos os comandos (25+ targets)

**Arquitetura de fontes `src/strings/`**
- `scripts/split.py` — migra enGB.json monolítico para 9 arquivos por categoria (`ui`, `tutorial`, `combate`, `enciclopedia`, `itens`, `missoes`, `personagens`, `dialogo`, `outros`) com campos `en` (referência), `pt` (tradução) e `status` (`approved|machine|pending`)
- `scripts/compile.py` — reconstrói enGB.json a partir dos arquivos `src/strings/`, preservando Offset e UUID intactos
- `src/strings/` criado: 69.795 strings distribuídas em 9 categorias

**Scripts de tradução**
- `scripts/translate_batch.py` — pipeline de tradução com IA: Translation Memory → Helsinki-NLP → Ollama → Groq → Google Translate, com checkpoint automático a cada 10 strings; atualiza `src/strings/` e `enGB.json` em paralelo
- `scripts/build_from_original.py` — reconstrução limpa do enGB.json a partir do original EN
- `scripts/diff_original.py` — comparação EN original vs PT, gera fila de trabalho
- Helsinki-NLP corrigido para usar `MarianMTModel` diretamente (versões novas do `transformers` removeram o task `"translation"` do pipeline); tradução por segmentos garante preservação de tags sem fallback

**Scripts de correção**
- `scripts/fix_auto.py` — correções automáticas (MP→PM, AP→PA, cooldown→recarga, artigos duplicados)
- `scripts/fix_tags.py` — repara tags `{g|..}{/g}` desbalanceadas
- `scripts/fix_gender.py` — corrige erros de concordância de gênero

**Scripts de qualidade e análise**
- `scripts/validate.py` — validação estrutural do JSON e balanço de tags
- `scripts/relatorio.py` — relatório completo de qualidade com score estimado
- `scripts/check_grammar.py` — verifica gramática PT-BR real com spaCy (POS tagging) + LanguageTool
- `scripts/check_consistency.py` — detecta strings EN similares com traduções PT inconsistentes via sentence-transformers
- `scripts/categorizar.py` — agrupa strings por área temática para facilitar revisão humana
- `scripts/release.py` — empacota enGB.json em release versionada com LEIAME.txt

**Ecossistema Copilot**
- `.github/copilot-instructions.md` v2 — expandido com: mapa completo do projeto, stack de bibliotecas, padrões de código, referência do Makefile, regras de tradução com glossário completo de nomes próprios WH40K
- `.github/agents/` — 6 agentes Copilot: `Tradutor WH40K`, `Revisor de Qualidade`, `Corretor Automático`, `Desenvolvedor`, `Arquiteto`, `DevOps`
- `.github/prompts/` — 10 prompts reutilizáveis: 5 de tradução/revisão + 5 de engenharia
- `.github/skills/` — 3 skills de contexto: `estado-do-projeto`, `arquitetura-do-projeto`, `referencia-bibliotecas`

**CI/CD**
- `.github/workflows/ci.yml` — 5 jobs: `validar-json`, `score-pr` (comenta score antes/depois em PRs), `relatorio-qualidade`, `verificar-termos`, `atualizar-stats`
- `.github/ISSUE_TEMPLATE/` — 3 templates de issue (erro de tradução, terminologia, compatibilidade)
- `.github/pull_request_template.md` — template de PR com checklist

**Documentação**
- `CONTRIBUTING.md` — guia completo para contribuidores com fluxo de trabalho atualizado
- `README.md` — documentação pública com estado atual, instalação, scripts e glossário
- `CHANGELOG.md` — índice de releases

### Corrigido
- Helsinki-NLP: singleton corrigido (usava `pipeline("translation")` removido em versões novas do transformers; migrado para `MarianMTModel` + `MarianTokenizer` direto)
- Helsinki-NLP: eliminado bug de recarga do modelo a cada string com fallback para Google Translate; substituído por tradução por segmentos
- `translate_batch.py`: nomes próprios do glossário agora carregados das 5 seções `termos_nao_traduzir_*` (personagens, locais, instituições, armas, títulos)
- `glossario.json`: expandido de ~60 para 150+ termos — adicionados personagens do Rogue Trader, locais, subfações, armas, equipamentos, títulos imperiais
- `copilot-instructions.md`: seção de termos não-traduzíveis expandida de uma linha para 6 categorias com 100+ nomes próprios
- Estrutura do projeto originalmente sem controle de versão ou padrões
- `split.py`: `detect_status()` corrigido — 1.125 strings marcadas como `pending` incorretamente (eram nomes próprios intraduzíveis como `Rogue Trader`, `Bolter`, `Melta`, código binário do Pasqal, créditos de empresas); agora marcadas como `approved`
- `{g|Encyclopedia:Skills}skills{/g}` corrigido para `perícias` (único termo EN real encontrado em texto visível)
- `relatorio.py`: detectava 23 falsos positivos em "termos EN no PT" — a maioria eram: `skill` dentro de tags de enciclopédia (identificadores intraduzíveis), `damage` na EULA em inglês (intencional), `a a` em expressões PT corretas ("de A a Z", "levando-a a se arrepender")
- Revisão por IA (diálogos, 100 strings): detectou e corrigiu `demônios`→`Daemons`, `voz`→`Vox`, `dobra`→`Warp`, `segurança`→`executor` (no contexto correto), negação em fala de personagem Eldar

**Revisão por IA (`scripts/review_ai.py`)**
- Novo script de revisão de qualidade por IA (Groq / Ollama / Gemini)
  - Processa uma string por vez com prompt especializado WH40K (terminologia, tom grimdark, preservação de tags)
  - Modelo padrão: `llama-3.3-70b-versatile` (Groq) — segue instruções com precisão
  - Checkpoint automático a cada 20 strings — retomável sem perder progresso
  - `--aplicar <relatório>` aplica correções validadas no `enGB.json` e `src/strings/`
  - `--dry-run` mostra correções sem alterar arquivos
  - Retry automático com espera exata indicada pelo rate limit do Groq
  - Suporte a Gemini 2.0 Flash como alternativa

### Estado atual
- Score de qualidade: **9.9/10**
- Strings traduzidas: **100%** (69.795/69.795 — nomes próprios corretos incluídos)
- `src/strings/`: 11.454 `approved` + 58.341 `machine` + 0 `pending`
- Tags desbalanceadas: **0**
- Erros de gênero: **0**
- Revisão por IA em andamento: 100/474 diálogos revisados, 8 correções aplicadas
