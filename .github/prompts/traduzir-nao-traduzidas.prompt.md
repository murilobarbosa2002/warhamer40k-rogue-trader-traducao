---
description: "Traduz todas as strings ainda em inglês no enGB.json. Use quando quiser traduzir as strings não traduzidas encontradas na análise."
name: "Traduzir Strings Não Traduzidas"
agent: "Tradutor WH40K"
tools: [read, edit, search]
argument-hint: "Deixe vazio para traduzir todas, ou informe um UUID específico"
---
Abra o arquivo [enGB.json](../../enGB.json) e identifique as strings não traduzidas.

Uma string está **não traduzida** quando o campo `"Text"` contém a maioria do texto em inglês E não contém nenhuma palavra estrutural em português (de, da, do, em, para, uma, um, com, que, não, você, este, esse, quando, como, pode). Strings mistas (inglês + português) devem ser incluídas apenas se a frase principal estiver em inglês.

## Passo 1 — Identificar
Leia o arquivo e liste as strings não traduzidas com seus UUIDs.

## Passo 2 — Traduzir cada string
Para cada string identificada, execute em sequência:
1. **Preserve todas as tags intactas**: `{g|..}{/g}`, `{d|..}{/d}`, `{n}..{/n}`, `{uip|..}`, `{unit_stat|..}`, `<b>`, `<i>`, `<br>`, `\n` — nunca remova nem altere.
2. **Traduza apenas o texto** entre as tags, nunca os identificadores dentro delas.
3. **Consulte o glossário** [glossario.json](../../glossario.json) para cada termo técnico (PA, PM, Ferimentos, Dano, Alvo, Alcance, Recarga, Talento, etc.).
4. **Ajuste o tom** ao tipo de texto: épico para falas de nobres/militares, técnico para enciclopédia/habilidades, direto para UI.
5. **Edite o campo `"Text"`** diretamente no arquivo.

## Passo 3 — Resumo final
Após traduzir todas as strings, apresente:
- Total de strings traduzidas
- Lista com UUID e primeiras palavras de cada tradução
- Strings com decisões não óbvias (termos de lore incertos, contexto ambíguo)
