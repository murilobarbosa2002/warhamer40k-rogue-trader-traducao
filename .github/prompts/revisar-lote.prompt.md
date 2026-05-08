---
description: "Revisa um lote de strings no enGB.json e gera relatório de qualidade com problemas encontrados e sugestões de correção. Use para auditar a tradução antes de publicar."
name: "Revisar Lote de Strings"
agent: "revisor"
tools: [read, search]
argument-hint: "UUID inicial e quantidade (ex: 'a partir do UUID xxx, 50 strings') ou 'aleatório 30'"
---
Abra o arquivo [enGB.json](../enGB.json) e revise o lote de strings solicitado.

Para cada string, verifique os seguintes critérios usando o [glossario.json](../glossario.json) como referência:

**Checklist de revisão:**
- [ ] Texto está em PT-BR (não em inglês)
- [ ] Terminologia canônica do glossário respeitada (PA/PM/Ferimentos/Dano/Alvo/etc.)
- [ ] Nenhum termo proibido presente (cooldown, damage, target, range, buff, skill, MP, AP, HP)
- [ ] Todas as tags preservadas intactas
- [ ] Concordância de gênero correta ("a nave", "o efeito", "a habilidade"...)
- [ ] Sem palavras duplicadas (de de, o o, um um, que que)
- [ ] Tom adequado ao tipo de texto (épico para falas, técnico para habilidades, direto para UI)
- [ ] Sem construções literais robóticas ("certifique-se de que", "você pode ser capaz de")

**Classifique cada problema como:**
- 🔴 CRÍTICO — quebra o jogo ou torna o texto incompreensível
- ❌ ERRO — problema claro que deve ser corrigido
- ⚠️ AVISO — pode ser melhorado mas não é urgente
- ✅ OK — string aprovada

**Ao final, gere o relatório:**
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
2. ...

STRINGS QUE PRECISAM DE CORREÇÃO URGENTE:
- [UUID] Problema: ...
```
