---
description: "Revisa um lote de strings no enGB.json e gera relatório de qualidade com problemas encontrados e sugestões de correção. Use para auditar a tradução antes de publicar."
name: "Revisar Lote de Strings"
agent: "Revisor de Qualidade"
tools: [read, search]
argument-hint: "UUID inicial e quantidade (ex: 'a partir do UUID xxx, 50 strings') ou 'aleatoriamente 30 strings do arquivo'"
---
Abra o arquivo [enGB.json](../../enGB.json) e revise o lote de strings solicitado. Consulte [glossario.json](../../glossario.json) como referência de terminologia.

Para cada string, execute as verificações em três passagens separadas:

## Passagem 1 — Verificações técnicas (estruturais)
- O campo `"Text"` não foi perdido ou corrompido
- Todas as tags estão intactas: `{g|..}{/g}`, `{d|..}{/d}`, `{n}..{/n}`, `{uip|..}`, `{unit_stat|..}`, `<b>`, `<i>`, `<br>`, `\n`
- O texto não está 100% em inglês (string não traduzida)

## Passagem 2 — Verificações de terminologia
- Nenhum termo proibido presente em texto PT: `cooldown`, `damage`, `target`, `range`, `buff`, `debuff`, `skill`, `MP`, `AP`, `HP`, `NPC`, `talent`, `trait`
- Abreviações corretas: `PA` (não AP), `PM` (não MP), `Ferimentos` (não HP ou Vida)
- Concordância de gênero: `a nave` / `o efeito` / `a habilidade` / `o dano` / `o ataque`
- Sem duplicações: `de de`, `o o`, `um um`, `que que`, `para para`

## Passagem 3 — Verificações de qualidade
- Tom adequado ao tipo: épico para falas nobres/militares, técnico para habilidades, direto para UI
- Sem construções literais de tradução automática: `"certifique-se de que"` → `"garanta que"`, `"você pode ser capaz de"` → `"você pode"`

**Classifique cada problema encontrado como:**
- 🔴 CRÍTICO — texto ilegível, string em inglês, tags corrompidas
- ❌ ERRO — termo proibido, duplicação, gênero errado
- ⚠️ AVISO — tom inadequado, construção literal, pode ser melhorado
- ✅ OK — string aprovada

**Relatório final:**
```
RELATÓRIO DE QUALIDADE
======================
Total revisado: X
✅ OK: X (X%)
⚠️ AVISO: X
❌ ERRO: X
🔴 CRÍTICO: X

TOP 5 PROBLEMAS MAIS COMUNS:
1. ...

STRINGS COM CORREÇÃO URGENTE:
- [UUID] Problema: ...
```
