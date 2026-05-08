---
description: "Gera relatório completo de qualidade da tradução: strings em inglês, termos incorretos, erros gramaticais, inconsistências de terminologia. Use para ter uma visão geral do estado atual da tradução."
name: "Relatório de Qualidade"
tools: [read, execute, search]
argument-hint: "Deixe vazio para relatório completo ou informe 'resumido'"
---
Execute a análise completa de qualidade do arquivo [enGB.json](../enGB.json) e gere um relatório detalhado.

```bash
cd /home/ubuntu/Projetos/warhammer40k-rogue-trader-ptbr
python3 scripts/relatorio.py
```

Se o script não existir, execute a análise manualmente lendo o arquivo e verificando:

1. **Strings não traduzidas** — texto estrutural em inglês
2. **Termos proibidos** — damage, target, range, cooldown, buff, debuff, skill, MP, AP, HP, NPC, talent, trait, spawn solto
3. **Inconsistências** — PM vs MP, PA vs AP, Ferimentos vs HP
4. **Erros gramaticais** — artigos duplicados, preposições duplicadas, concordância de gênero
5. **Construções literais** — "certifique-se de que", "você pode ser capaz de"

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
