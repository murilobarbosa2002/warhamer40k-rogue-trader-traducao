---
description: "Melhora a qualidade literária de falas de personagens no enGB.json: remove tom robótico, adiciona personalidade, ajusta registro adequado ao personagem WH40K. Use para refinar diálogos depois da tradução inicial."
name: "Melhorar Qualidade Literária"
agent: "Tradutor WH40K"
tools: [read, edit, search]
argument-hint: "UUID da string ou nome do personagem/área a melhorar"
---
Abra o arquivo [enGB.json](../../enGB.json) e melhore a qualidade literária das strings solicitadas.

## Passo 1 — Identificar o perfil do personagem

Antes de qualquer edição, determine quem fala e qual é o seu registro canônico:

| Perfil | Tom | Exemplo |  
|--------|-----|---------|  
| Nobre/Rogue Trader | Altivo, vocabulário rico, formal | "Não se atreva a questionar minha autoridade." |
| Militar/Soldado | Seco, direto, objetivo | "Ordem cumprida. Próximo objetivo." |
| Tech-Priest | Jargão mecânico, referências ao Omnissiah | "O binário sagrado revela a verdade." |
| Inquisidor | Ameaçador, formal, implacável | "A heresia será extirpada pela raiz." |
| Cultista/Herege | Fanático, perturbado, fragmentado | "Ele nos chama... todos nós..." |
| Comum/Servo | Simples, direto, sem ornamentação | "Sim, senhor. Como ordenar." |

## Passo 2 — Revisar o texto

Com o perfil definido, reescreva o texto aplicando as regras do perfil, mantendo **obrigatoriamente**:
- O **significado e todas as informações** do original — não omita nem acrescente fatos
- Todas as **tags intactas**: `{g|..}`, `{n}..{/n}`, `{uip|..}`, `<b>`, `<i>`, `<br>`, `\n`
- Os **nomes próprios** do universo WH40K sem tradução (consulte [glossario.json](../../glossario.json))

O que pode e deve ser ajustado:
- Substituir construções literais de tradução automática ("certifique-se de que" → "garanta que", "você pode ser capaz de" → "você pode")
- Usar o vocabulário típico do perfil identificado (formal/técnico/seco/fragmentado)
- Corrigir frases que soam artificiais em PT-BR

> **Nota sobre registro**: personagens de perfil Comum/Servo podem usar linguagem mais simples que outros perfis. O objetivo é adequação ao personagem, não elevar artificialmente o tom de todos.

## Passo 3 — Apresentar resultado

Para cada string alterada:
```
UUID: <uuid>
Perfil: <tipo de personagem>
Original : <texto antes>
Melhorado: <texto depois>
Justificativa: <o que foi mudado e por quê>
```
