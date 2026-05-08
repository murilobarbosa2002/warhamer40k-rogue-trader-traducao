---
description: "Traduz todas as strings ainda em inglês no enGB.json. Use quando quiser traduzir as strings não traduzidas encontradas na análise."
name: "Traduzir Strings Não Traduzidas"
agent: "tradutor"
tools: [read, edit, search]
argument-hint: "Deixe vazio para traduzir todas, ou informe um UUID específico"
---
Abra o arquivo [enGB.json](../enGB.json) e identifique todas as strings que ainda estão em inglês — ou seja, o campo `"Text"` contém texto em inglês estrutural (palavras como "the", "and", "is", "are", "was", "were", "this", "that", "with", "from", "they", "their", "you", "your", "when", "where") e **não** contém palavras estruturais em português.

Para cada string encontrada:
1. Leia o texto original em inglês.
2. Identifique o contexto (fala de personagem? enciclopédia? UI? habilidade?).
3. Aplique o [glossario.json](../glossario.json) para terminologia técnica.
4. Produza uma tradução PT-BR de qualidade, respeitando:
   - Tom grimdark e sério do universo WH40K
   - Preservação integral de todas as tags `{g|..}`, `{d|..}`, `{n}..{/n}`, `{uip|..}`, `<b>`, `<i>`, `<br>`, `\n`
   - Termos canônicos obrigatórios do glossário
5. Edite o campo `"Text"` diretamente no arquivo.

Após concluir, apresente um resumo:
- Total de strings traduzidas
- Lista com UUID e primeiras palavras de cada tradução feita
- Strings que precisam de atenção especial (termos de lore incertos, contexto ambíguo)
