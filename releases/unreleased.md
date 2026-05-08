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
- `scripts/relatorio.py` — relatório completo de qualidade com score estimado
- `scripts/diff_original.py` — comparação EN original vs PT, gera fila de trabalho
- `scripts/translate_batch.py` — pipeline de tradução com IA (Ollama → Groq → Google Translate) com checkpoint de progresso
- `scripts/build_from_original.py` — reconstrução limpa do enGB.json a partir do original EN
- `.github/copilot-instructions.md` — instruções permanentes para o Copilot com regras de tradução
- `.github/agents/` — 3 agentes Copilot especializados (Tradutor WH40K, Revisor de Qualidade, Corretor Automático)
- `.github/prompts/` — 5 prompts reutilizáveis para tradução, revisão e correção
- `.github/workflows/ci.yml` — CI que valida JSON e gera relatório em todo PR
- `CONTRIBUTING.md` — guia completo para contribuidores
- `README.md` — documentação pública com instalação, estado e guia de ambiente
- `.env.example` — template de configuração para provedores de IA

### Corrigido
- 67 strings obsoletas identificadas (existem na tradução mas não no original 1.5.0.320)
- Estrutura do projeto originalmente sem controle de versão ou padrões

### Conhecido / Pendente
- **193 strings** com tags `{g|..}{/g}` desbalanceadas (herança da tradução automática original)
- **~525 strings** ainda em inglês (não traduzidas)
- **~112 casos** de concordância de gênero incorreta (`o nave`, `uma alvo`)
- **67 strings** obsoletas ainda presentes no enGB.json (serão removidas em `build_from_original`)
