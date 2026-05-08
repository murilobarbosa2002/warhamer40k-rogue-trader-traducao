---
description: "Revisa o código de um script existente em scripts/. Verifica padrões arquiteturais, segurança, performance e legibilidade. Use após escrever ou modificar um script."
name: "Revisar Código"
agent: "Desenvolvedor"
tools: [read, search]
argument-hint: "Caminho do script a revisar, ex: scripts/fix_auto.py"
---

Faça uma revisão completa do script informado seguindo os padrões deste projeto.

## Ler antes de revisar

- [copilot-instructions.md](../copilot-instructions.md) — seções de arquitetura e convenções

## Checklist de revisão

### Segurança do enGB.json (crítico)

- [ ] O script nunca altera UUID nem o campo `Offset`
- [ ] A escrita é feita via `json.dump(data, ...)` com o `data` completo
- [ ] `--dry-run` existe e funciona corretamente (não salva nada)
- [ ] Não reconstrói o dict do zero (perderia a ordem e os Offsets)

### Manipulação de tags

- [ ] Não usa `str.replace()` diretamente em texto que pode conter tags
- [ ] Usa `replace_outside_tags()` ou equivalente para substituições em texto
- [ ] `TAG_RE = re.compile(r"\{[^}]+\}|<[^>]+>")` é usado para detectar tags

### Robustez

- [ ] Erros individuais de string não abortam o loop principal
- [ ] Erros são coletados e reportados no final
- [ ] Não assume que o arquivo original existe (verifica com `.exists()`)
- [ ] Encoding `utf-8` explícito em todos os `open()`

### Padrões de código

- [ ] `ROOT = Path(__file__).parent.parent` presente
- [ ] Paths construídos com `Path` (não concatenação de strings)
- [ ] Contadores com `{n:,}` na saída
- [ ] Separadores `"=" * 50` ou `"-" * 50` na saída de resumo
- [ ] `sys.exit(run(...))` no `if __name__ == "__main__"`

### Performance

- [ ] Arquivos grandes abertos uma vez só (não em loop)
- [ ] Modelos ML (Helsinki, sentence-transformers) instanciados uma vez (global ou singleton)
- [ ] Checkpoint implementado se o script processa >100 strings com operações lentas

### Documentação

- [ ] Docstring no topo com descrição e exemplos de Uso:
- [ ] Comentários em lógica não óbvia (regex complexo, lógica de tag)
- [ ] `help=` em todos os argumentos do argparse

## Formato do relatório de revisão

Para cada problema encontrado, apresentar:
```
[CRÍTICO/AVISO/SUGESTÃO] Linha X — Descrição do problema
  Código atual:    <trecho problemático>
  Código correto:  <sugestão de correção>
```

Ao final: resumo com contagem por severidade e veredicto (aprovado / reprovado com pendências).
