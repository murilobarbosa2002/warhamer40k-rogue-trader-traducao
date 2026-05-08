---
description: "Aplica todas as correções automáticas seguras no enGB.json: MP→PM, AP→PA, cooldown→recarga, termos em inglês→PT-BR, artigos duplicados. Use antes de um release ou commit de qualidade."
name: "Aplicar Correções Automáticas"
agent: "corretor"
tools: [read, edit, execute, search]
---
Execute o processo completo de correção automática no arquivo [enGB.json](../enGB.json).

## Passo 1 — Validação pré-execução
```bash
cd /home/ubuntu/Projetos/warhammer40k-rogue-trader-ptbr
git status
python3 scripts/validate.py
```
Se o JSON estiver inválido ou o git não estiver limpo, **pare e informe o usuário**.

## Passo 2 — Executar o script de correções
```bash
python3 scripts/fix_auto.py --modo tudo
```

## Passo 3 — Validar resultado
```bash
python3 scripts/validate.py
git diff --stat enGB.json
```

## Passo 4 — Relatório e commit
Apresente o relatório de correções com:
- Quantas substituições foram feitas por categoria
- Exemplos de antes/depois para cada tipo de correção
- Avisos sobre termos que foram marcados para revisão humana mas não corrigidos automaticamente

Após confirmação do usuário, execute:
```bash
git add enGB.json
git commit -m "fix(auto): corrige terminologia e erros gramaticais automáticos"
git push
```
