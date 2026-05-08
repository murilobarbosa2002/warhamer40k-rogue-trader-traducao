---
description: "Gera relatório completo de qualidade da tradução: strings em inglês, termos incorretos, erros gramaticais, inconsistências de terminologia. Use para ter uma visão geral do estado atual da tradução."
name: "Relatório de Qualidade"
tools: [read, execute, search]
argument-hint: "Deixe vazio para relatório completo. Informe 'resumido' para ver apenas estatísticas gerais e problemas críticos (strings em inglês + erros de terminologia), sem detalhamento de avisos de qualidade."
---
Execute a análise de qualidade do arquivo [enGB.json](../../enGB.json).

```bash
python3 scripts/relatorio.py
```

Se o argumento for `resumido`, execute:
```bash
python3 scripts/relatorio.py 2>&1 | grep -E '(CRITICO|ERRO|TOTAL|Score|strings)'
```

Se o script não existir, execute a análise manualmente em quatro etapas independentes:

**Etapa 1 — Strings não traduzidas** (CRÍTICO)
Identifique strings onde o texto está majoritariamente em inglês e não contém palavras estruturais em português.

**Etapa 2 — Termos proibidos** (ERRO)
Contabilize ocorrências de: `damage`, `target`, `range`, `cooldown`, `buff`, `debuff`, `skill`, `MP`, `AP`, `HP`, `NPC`, `talent`, `trait` fora de tags `{..}`.

**Etapa 3 — Erros gramaticais** (ERRO)
Procure por: artigos duplicados (`o o`, `um um`, `a a`), preposições duplicadas (`de de`, `para para`) e concordância de gênero errada (`o nave`, `o habilidade`, `a efeito`).

**Etapa 4 — Qualidade** (AVISO)
Contabilize: `certifique-se de que` (→ garanta que) e `você pode ser capaz de` (→ você pode).

Apresente o relatório no formato:

```
╔══════════════════════════════════════════╗
║   RELATÓRIO DE QUALIDADE - WH40K PT-BR   ║
╚══════════════════════════════════════════╝

📊 ESTATÍSTICAS GERAIS
  Total de strings: X
  Strings com conteúdo: X
  Caracteres totais: X

🔴 PROBLEMAS CRÍTICOS (precisam de ação imediata)
  Strings 100% em inglês: X
  → Lista das primeiras 10 com UUID

❌ ERROS (terminologia incorreta)
  "MP" no lugar de "PM": X ocorrências
  "AP" no lugar de "PA": X ocorrências
  "cooldown" no lugar de "recarga": X
  outros termos em inglês: X total
  → Detalhamento por termo

⚠️ AVISOS (qualidade)
  Artigos duplicados: X
  Preposições duplicadas: X
  Concordância de gênero suspeita: X
  Construções literais: X

✅ PROGRESSO GERAL
  Score estimado de qualidade: X/10
  Strings sem problemas detectados: X (X%)

📋 PRÓXIMOS PASSOS RECOMENDADOS
  1. ...
  2. ...
```
