---
description: "Retorna o estado atual completo do projeto: % traduzido, erros pendentes, strings por categoria, últimas releases e próximas prioridades."
name: "estado-do-projeto"
tools: [run_in_terminal, read]
---

Execute os seguintes comandos e compile um resumo completo do estado do projeto:

## 1. Status de tradução

```bash
cd /home/ubuntu/Projetos/warhammer40k-rogue-trader-ptbr
.venv/bin/python scripts/diff_original.py --stats
```

## 2. Erros estruturais

```bash
.venv/bin/python scripts/validate.py 2>&1 | tail -5
```

## 3. Distribuição por categoria

```bash
.venv/bin/python scripts/categorizar.py relatorio --nao-traduzidas 2>&1
```

## 4. Últimas releases

```bash
git log --oneline -5
ls releases/ 2>/dev/null || echo "(sem releases publicadas ainda)"
```

## 5. Leia o unreleased.md

Leia [releases/unreleased.md](../../releases/unreleased.md) para ver o trabalho em andamento.

## Formato do relatório final

Apresente em formato de briefing:

```
ESTADO DO PROJETO — WH40K Rogue Trader PT-BR
Data: <hoje>
Versão base: 1.5.0.320

TRADUÇÃO
  Total de strings: X
  Traduzidas: X (X%)
  Pendentes: X strings

QUALIDADE
  Erros de tag: X
  Concordância de gênero: X
  Termos EN no texto PT: X

PRIORIDADES IMEDIATAS
  1. <ação mais urgente>
  2. <segunda ação>
  3. <terceira ação>
```
