---
description: "Aplica todas as correções automáticas seguras no enGB.json: MP→PM, AP→PA, cooldown→recarga, termos em inglês→PT-BR, artigos duplicados. Use antes de um release ou commit de qualidade."
name: "Aplicar Correções Automáticas"
agent: "Corretor Automático"
tools: [read, edit, execute, search]
---
Execute o processo completo de correção automática no arquivo [enGB.json](../../enGB.json) seguindo os passos abaixo em ordem. **Interrompa imediatamente se qualquer passo falhar** e informe o usuário antes de continuar.

## Passo 1 — Verificar pré-condições
```bash
git status
```
Se houver arquivos modificados não commitados, **pare aqui** e informe: "O git tem alterações não salvas. Faça commit ou stash antes de continuar."

## Passo 2 — Validar integridade do JSON
```bash
python3 scripts/validate.py
```
Se retornar erros, **pare aqui** e informe os erros encontrados. Não aplique correções em arquivo com estrutura corrompida.

## Passo 3 — Executar correções (dry-run primeiro)
```bash
python3 scripts/fix_auto.py --dry-run
```
Apresente o resumo de quantas substituições serão feitas por categoria. Aguarde confirmação do usuário.

## Passo 4 — Aplicar correções
Após confirmação:
```bash
python3 scripts/fix_auto.py --modo tudo
```

## Passo 5 — Validar resultado
```bash
python3 scripts/validate.py
git diff --stat enGB.json
```

## Passo 6 — Relatório e commit
Apresente:
- Total de substituições feitas por categoria
- 2-3 exemplos de antes/depois para cada categoria
- Lista de termos que o script **não corrigiu automaticamente** por serem ambíguos (ex: `range` quando pode ser nome de personagem, `target` em contexto de UI não padronizado) — estes precisam de revisão manual

Após confirmação do usuário:
```bash
git add enGB.json
git commit -m "fix(auto): corrige terminologia e erros gramaticais automáticos"
git push
```
