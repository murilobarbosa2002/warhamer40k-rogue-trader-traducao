---
description: "Melhora a qualidade literária de falas de personagens no enGB.json: remove tom robótico, adiciona personalidade, ajusta registro formal/informal adequado ao personagem WH40K. Use para refinar diálogos depois da tradução inicial."
name: "Melhorar Qualidade Literária"
agent: "tradutor"
tools: [read, edit, search]
argument-hint: "UUID da string ou nome do personagem/área a melhorar"
---
Abra o arquivo [enGB.json](../enGB.json) e melhore a qualidade literária das strings solicitadas.

## Critérios de melhoria

**Identifique o perfil do personagem que fala:**
- **Nobre/Rogue Trader**: voz altiva, vocabulário rico, frases complexas. "Não se atreva a questionar minha autoridade."
- **Militar/Soldado**: seco, direto, sem floreios. "Ordem cumprida. Próximo objetivo."
- **Tech-Priest**: jargão mecânico, referências ao Omnissiah, mistura termos técnicos. "O binário sagrado revela a verdade."
- **Inquisidor**: ameaçador, formal, implacável. "A heresia será extirpada pela raiz."
- **Cultista/Herege**: fanático, perturbado, fragmentado. "Ele nos chama... todos nós... o Vazio nos abraça."
- **Comerciante/Mercador**: pragmático, persuasivo, calculista.
- **Comum/Servo**: submisso, simples, temeroso.

## O que NÃO fazer
- Não mudar o significado original
- Não remover nem alterar tags
- Não adicionar informações que não estavam no original
- Não deixar mais casual do que o original
- Não traduzir nomes próprios do glossário

## Processo
1. Leia o texto atual.
2. Identifique: quem fala? qual contexto?
3. Reescreva mantendo o conteúdo mas melhorando:
   - Eliminar construções literais ("certifique-se de que" → "garanta que")
   - Adicionar peso dramático quando apropriado
   - Ajustar o registro ao perfil do personagem
   - Corrigir frases que soam como tradução automática
4. Apresente: texto original → texto melhorado + justificativa
