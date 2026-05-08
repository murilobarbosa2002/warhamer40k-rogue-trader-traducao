# Makefile — Atalhos para o projeto WH40K PT-BR
# Uso: make <comando>
# Exemplo: make status   make traduzir-10   make validar

PYTHON = .venv/bin/python

# ─── Setup ──────────────────────────────────────────────────────────────────

.PHONY: setup
setup: ## Cria o ambiente virtual e instala dependências
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt
	.venv/bin/python -m spacy download pt_core_news_sm
	@echo ""
	@echo "Ambiente pronto. Configure o .env:"
	@echo "  cp .env.example .env"

# ─── Estado ─────────────────────────────────────────────────────────────────

.PHONY: status
status: ## Ver quantas strings precisam de tradução
	$(PYTHON) scripts/diff_original.py --stats

.PHONY: relatorio
relatorio: ## Relatório completo de qualidade
	$(PYTHON) scripts/relatorio.py

.PHONY: validar
validar: ## Validar integridade do JSON e tags
	$(PYTHON) scripts/validate.py

# ─── Correções automáticas ───────────────────────────────────────────────────

.PHONY: fix
fix: ## Aplicar todas as correções automáticas (simulação primeiro)
	@echo "=== Simulando correções ==="
	$(PYTHON) scripts/fix_auto.py --dry-run
	@echo ""
	@read -p "Aplicar? [s/N] " r; [ "$$r" = "s" ] && $(PYTHON) scripts/fix_auto.py || echo "Cancelado."

.PHONY: fix-tags
fix-tags: ## Reparar tags {g|..}{/g} desbalanceadas
	@echo "=== Simulando correção de tags ==="
	$(PYTHON) scripts/fix_tags.py --dry-run
	@echo ""
	@read -p "Aplicar? [s/N] " r; [ "$$r" = "s" ] && $(PYTHON) scripts/fix_tags.py || echo "Cancelado."

.PHONY: fix-gender
fix-gender: ## Corrigir concordância de gênero (o nave → a nave)
	@echo "=== Simulando correção de gênero ==="
	$(PYTHON) scripts/fix_gender.py --dry-run
	@echo ""
	@read -p "Aplicar? [s/N] " r; [ "$$r" = "s" ] && $(PYTHON) scripts/fix_gender.py || echo "Cancelado."

.PHONY: fix-all
fix-all: ## Aplicar TODAS as correções automáticas sem confirmação
	$(PYTHON) scripts/fix_tags.py
	$(PYTHON) scripts/fix_auto.py
	$(PYTHON) scripts/fix_gender.py
	$(PYTHON) scripts/validate.py

# ─── Tradução ────────────────────────────────────────────────────────────────

.PHONY: traduzir
traduzir: ## Traduzir todas as strings não traduzidas com IA (Ollama)
	$(PYTHON) scripts/translate_batch.py

.PHONY: traduzir-10
traduzir-10: ## Testar tradução com 10 strings
	$(PYTHON) scripts/translate_batch.py --limite 10

traduzir-%: ## Traduzir N strings: make traduzir-50
	$(PYTHON) scripts/translate_batch.py --limite $*

.PHONY: traduzir-google
traduzir-google: ## Traduzir usando Google Translate (sem API key)
	$(PYTHON) scripts/translate_batch.py --provider deep_translator

.PHONY: traduzir-helsinki
traduzir-helsinki: ## Traduzir offline com Helsinki-NLP opus-mt (~300MB no primeiro uso)
	$(PYTHON) scripts/translate_batch.py --provider helsinki

# ─── Qualidade e análise ─────────────────────────────────────────────────────

.PHONY: check-grammar
check-grammar: ## Verificar gramática PT-BR com spaCy + LanguageTool (requer Java)
	$(PYTHON) scripts/check_grammar.py --spacy-only

.PHONY: check-grammar-full
check-grammar-full: ## Verificar gramática completa incluindo LanguageTool (mais lento)
	$(PYTHON) scripts/check_grammar.py

.PHONY: check-consistency
check-consistency: ## Detectar strings EN similares com traduções PT inconsistentes
	$(PYTHON) scripts/check_consistency.py --limite 3000

.PHONY: categorias
categorias: ## Ver distribuição de strings por categoria temática
	$(PYTHON) scripts/categorizar.py --nao-traduzidas

.PHONY: exportar-categorias
exportar-categorias: ## Exportar strings por categoria para revisao/
	$(PYTHON) scripts/categorizar.py --exportar

# ─── Arquitetura src/strings/ ─────────────────────────────────────────────────

.PHONY: split
split: ## Migrar enGB.json para src/strings/<categoria>.json (rodar 1x)
	$(PYTHON) scripts/split.py

.PHONY: compile
compile: ## Reconstruir enGB.json a partir de src/strings/ + validar
	$(PYTHON) scripts/compile.py --validar

.PHONY: split-stats
split-stats: ## Ver estatísticas de tradução por categoria
	$(PYTHON) scripts/split.py --stats

# ─── Releases ────────────────────────────────────────────────────────────────

.PHONY: release
release: validar ## Empacotar enGB.json para uma nova release
	$(PYTHON) scripts/release.py

# ─── Git ─────────────────────────────────────────────────────────────────────

.PHONY: commit-traducao
commit-traducao: validar ## Commit e push das traduções após validação
	git add enGB.json src/strings/ glossario.json
	git commit -m "feat(tradução): atualiza traduções via pipeline de IA"
	git push

# ─── Help ─────────────────────────────────────────────────────────────────────

.PHONY: help
help: ## Mostra esta ajuda
	@echo ""
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_%-]+:.*##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""

.DEFAULT_GOAL := help
