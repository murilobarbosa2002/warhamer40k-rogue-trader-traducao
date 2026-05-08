---
description: "Depura um script que está falhando, produzindo saída errada, ou corrompendo o enGB.json. Use quando um script retorna erro, produz resultado inesperado ou o validate.py falha após rodá-lo."
name: "Debugar Script"
agent: "Desenvolvedor"
tools: [read, edit, search, run_in_terminal]
argument-hint: "Nome do script e descrição do problema ou mensagem de erro"
---

Investigue e corrija o problema reportado no script.

## Passo 1 — Coletar contexto

1. Leia o script completo: `read_file scripts/<nome>.py`
2. Leia o erro ou comportamento inesperado descrito
3. Verifique o estado atual do enGB.json:
   ```bash
   .venv/bin/python scripts/validate.py
   ```

## Passo 2 — Diagnóstico por categoria de problema

### O script abortou com exceção

Verificar:
- [ ] `FileNotFoundError` — o script assume que `arquivo-original-1.5.0.320.json` existe?
  ```python
  if not ORIG_PATH.exists():
      print(f"ERRO: {ORIG_PATH.name} não encontrado.")
      return 1
  ```
- [ ] `KeyError` em `strings[uuid]` — uuid pode não existir no PT se veio do EN original
- [ ] `UnicodeDecodeError` — falta `encoding="utf-8"` no `open()`
- [ ] `json.JSONDecodeError` — enGB.json foi corrompido por escrita parcial

### O validate.py falha após rodar o script

Indica que o script corrompeu o enGB.json. Verificar:
- [ ] O script escreveu `json.dump(data, ...)` com o `data` completo?
- [ ] Algum `strings[uuid]["Text"]` recebeu `None` em vez de string?
- [ ] Tags foram desbalanceadas pelo script?

Restaurar enGB.json do git:
```bash
git checkout -- enGB.json
```

### O script produziu resultado diferente do esperado

- [ ] O `--dry-run` foi testado primeiro?
- [ ] O regex está escapado corretamente? Testar isolado:
  ```python
  import re
  pattern = r"\bMP\b"
  print(re.findall(pattern, "O personagem tem 5 MP de movimento"))
  ```
- [ ] A função `replace_outside_tags()` está sendo usada onde deveria?

### O script é muito lento

- [ ] O modelo ML está sendo recarregado a cada iteração? → usar singleton global
- [ ] O arquivo JSON está sendo aberto dentro do loop? → abrir uma vez antes
- [ ] Está processando strings que já foram processadas? → verificar filtro

## Passo 3 — Corrigir

Faça a menor alteração possível para corrigir o problema. Não refatore código não relacionado.

## Passo 4 — Verificar

```bash
# Testar com dry-run
.venv/bin/python scripts/<nome>.py --dry-run

# Testar com limite pequeno
.venv/bin/python scripts/<nome>.py --limite 5

# Confirmar integridade do JSON
.venv/bin/python scripts/validate.py
```

## Checklist de emergência — enGB.json corrompido

Se o enGB.json foi corrompido e o script não tem `--dry-run`:

```bash
# 1. Verificar se há backup no git
git diff --stat enGB.json

# 2. Restaurar do último commit
git checkout -- enGB.json

# 3. Verificar se restaurou OK
.venv/bin/python scripts/validate.py

# 4. Aplicar correção no script antes de rodar de novo
```
