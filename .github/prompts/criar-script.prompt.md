---
description: "Cria um novo script Python seguindo todos os padrões do projeto. Use quando precisar de um novo utilitário de tradução, análise ou correção."
name: "Criar Novo Script"
agent: "Desenvolvedor"
tools: [read, edit, search]
argument-hint: "Nome do script e o que ele deve fazer"
---

Crie um novo script Python em `scripts/` seguindo **exatamente** os padrões arquiteturais deste projeto.

## Contexto obrigatório para ler antes de escrever

1. Leia [copilot-instructions.md](../copilot-instructions.md) — seções "Arquitetura dos Scripts" e "Convenções de Código"
2. Leia um script existente similar como referência:
   - Para scripts de correção: [scripts/fix_auto.py](../../scripts/fix_auto.py)
   - Para scripts de análise: [scripts/check_grammar.py](../../scripts/check_grammar.py)
   - Para scripts de tradução: [scripts/translate_batch.py](../../scripts/translate_batch.py)

## Checklist obrigatório para o script

- [ ] Shebang `#!/usr/bin/env python3` e docstring com Uso: no topo
- [ ] `ROOT = Path(__file__).parent.parent` e `ENDB_PATH = ROOT / "enGB.json"`
- [ ] `TAG_RE = re.compile(r"\{[^}]+\}|<[^>]+>")` se mexer com tags
- [ ] `--dry-run` implementado se o script modifica `enGB.json`
- [ ] `--limite` implementado se o script itera sobre strings
- [ ] Erros individuais coletados em lista, não abortam o loop
- [ ] Saída com contadores formatados (`{n:,}`)
- [ ] `sys.exit(run(...))` no `if __name__ == "__main__"`

## Após criar o script

1. Adicionar target no [Makefile](../../Makefile):
   ```makefile
   .PHONY: nome-script
   nome-script: ## Descrição curta
       $(PYTHON) scripts/nome_script.py
   ```

2. Adicionar em [releases/unreleased.md](../../releases/unreleased.md) em `### Adicionado`

3. Adicionar na tabela de scripts em [copilot-instructions.md](../copilot-instructions.md)

4. Adicionar dependência nova (se houver) em [requirements.txt](../../requirements.txt)

## Teste o script criado

```bash
# Sempre testar com dry-run primeiro
.venv/bin/python scripts/nome_script.py --dry-run

# Testar com amostra pequena
.venv/bin/python scripts/nome_script.py --limite 10

# Confirmar que o JSON não foi corrompido
.venv/bin/python scripts/validate.py
```
