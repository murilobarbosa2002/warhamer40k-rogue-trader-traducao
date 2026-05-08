# Unreleased — Em desenvolvimento

> Mudanças que ainda não foram empacotadas em uma release oficial.
> Quando uma release for publicada, mova o conteúdo daqui para um novo arquivo `releases/X.Y.Z.md`.

---

## [Unreleased] — base: 1.5.0.320

### Adicionado
- Compatibilidade com a versão **1.5.0.320** do jogo (base era 1.4.1.229)
- Projeto público com infraestrutura para contribuições colaborativas
- `glossario.json` — terminologia canônica com ~60 termos obrigatórios
- `scripts/validate.py` — validação estrutural do JSON e balanço de tags
- `scripts/fix_auto.py` — correções automáticas (MP→PM, AP→PA, cooldown→recarga, artigos duplicados)
- `scripts/fix_tags.py` — repara automaticamente as 136 tags `{g|..}{/g}` desbalanceadas herdadas da tradução original
- `scripts/fix_gender.py` — corrige 120 erros de concordância de gênero (`o nave`→`a nave`, etc.)
- `scripts/check_grammar.py` — verifica gramática PT-BR real com spaCy (POS tagging) + LanguageTool (requer Java)
- `scripts/check_consistency.py` — detecta strings EN similares com traduções PT inconsistentes via sentence-transformers
- `scripts/categorizar.py` — agrupa strings por área temática (combate, diálogos, UI, enciclopédia, etc.) para facilitar revisão humana
- `scripts/relatorio.py` — relatório completo de qualidade com score estimado
- `scripts/diff_original.py` — comparação EN original vs PT, gera fila de trabalho
- `scripts/translate_batch.py` — pipeline de tradução com IA (Helsinki-NLP → Ollama → Groq → Google Translate) com checkpoint e translation memory
- `scripts/build_from_original.py` — reconstrução limpa do enGB.json a partir do original EN
- `scripts/release.py` — empacota enGB.json em release versionada com LEIAME.txt
- `.github/copilot-instructions.md` — instruções permanentes para o Copilot com regras de tradução
- `.github/agents/` — 3 agentes Copilot especializados (Tradutor WH40K, Revisor de Qualidade, Corretor Automático)
- `.github/prompts/` — 5 prompts reutilizáveis para tradução, revisão e correção
- `.github/workflows/ci.yml` — CI que valida JSON, gera relatório em todo PR, comenta score de qualidade (antes/depois) em PRs e atualiza progresso no README automaticamente
- `.github/ISSUE_TEMPLATE/` — 3 templates de issue (erro, terminologia, compatibilidade)
- `.github/pull_request_template.md` — template de PR com checklist
- `CONTRIBUTING.md` — guia completo para contribuidores
- `README.md` — documentação pública com instalação, estado, guia de ambiente e badges
- `CHANGELOG.md` — índice de releases
- `Makefile` — atalhos para todos os comandos do projeto (incluindo `check-grammar`, `check-consistency`, `categorias`, `traduzir-helsinki`)
- `requirements.txt` — dependências Python com versões fixas (inclui transformers, sentence-transformers, spacy, language-tool-python)
- `.env.example` — template de configuração para provedores de IA (incluindo opção `helsinki`)
- `.pre-commit-config.yaml` — roda validate.py automaticamente antes de cada commit
- `translation-memory.json` — memória de tradução para pares EN→PT aprovados por humanos

### Corrigido
- 67 strings obsoletas identificadas (existem na tradução mas não no original 1.5.0.320)
- Estrutura do projeto originalmente sem controle de versão ou padrões
- Nomes dos agentes Copilot padronizados com os `.agent.md` correspondentes
- Regras do `copilot-instructions.md` reorganizadas em 4 seções categorizadas
- Pronomes do personagem jogador explicitados (masculino por padrão, feminino/neutro apenas quando o texto fonte usa explicitamente)

### Conhecido / Pendente
- **193 strings** com tags `{g|..}{/g}` desbalanceadas (136 corrigíveis por `fix_tags.py`, 57 requerem revisão)
- **~525 strings** ainda em inglês (não traduzidas, resolvíveis com `translate_batch.py`)
- **~120 casos** de concordância de gênero incorreta (corrigíveis com `fix_gender.py`)
- **67 strings** obsoletas ainda presentes no enGB.json (removíveis com `build_from_original.py`)
