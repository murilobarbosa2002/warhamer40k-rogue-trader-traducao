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

# ─── Releases ────────────────────────────────────────────────────────────────

.PHONY: release
release: validar ## Empacotar enGB.json para uma nova release
	$(PYTHON) scripts/release.py

# ─── Git ─────────────────────────────────────────────────────────────────────

.PHONY: commit-traducao
commit-traducao: validar ## Commit e push das traduções após validação
	git add enGB.json
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
