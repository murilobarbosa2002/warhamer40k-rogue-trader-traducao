---
description: "Atualiza o CHANGELOG.md e releases/unreleased.md após concluir um conjunto de mudanças, ou prepara e empacota uma nova release pública. Use após uma sessão de trabalho ou quando for publicar uma versão."
name: "Registrar Mudanças e Release"
agent: "DevOps"
tools: [read, edit, run_in_terminal]
argument-hint: "Descrição do que foi feito, ou 'release X.Y.Z-ptbr-vN' para empacotar"
---

Registre o trabalho realizado na documentação do projeto e/ou empacote uma release.

## Modo 1 — Atualizar unreleased.md (após cada sessão de trabalho)

Leia [releases/unreleased.md](../../releases/unreleased.md) e adicione na seção adequada:

### Seções disponíveis

```markdown
### Adicionado
- `scripts/novo_script.py` — descrição do que faz e flags principais

### Corrigido
- N strings com [tipo de problema] corrigidas por [script]
- Bug em [script]: descrição da causa e da solução

### Melhorado
- [script]: melhoria específica (ex: 30% mais rápido, novo fallback)

### Conhecido / Pendente
- [N strings] ainda com [problema] — corrigíveis com [script]
```

### Regras de estilo

- Cada item começa com `` `script` `` em backtick ou número de strings
- Não usar emojis
- Ser específico: "136 tags reparadas" em vez de "tags corrigidas"
- Versão do jogo sempre destacada: **1.5.0.320**

---

## Modo 2 — Empacotar release pública

### Pré-requisitos

```bash
# 1. Verificar se está tudo OK
make validar && make status

# 2. Confirmar que não há pendências críticas
.venv/bin/python scripts/validate.py  # deve retornar 0 erros
```

### Executar release

```bash
.venv/bin/python scripts/release.py --versao 1.5.0.320-ptbr-v2
```

O script cria:
- `releases/1.5.0.320-ptbr-v2/enGB.json`
- `releases/1.5.0.320-ptbr-v2/LEIAME.txt`
- `releases/1.5.0.320-ptbr-v2/1.5.0.320-ptbr-v2.md`
- Atualiza `CHANGELOG.md` com a nova entrada

### Após a release

```bash
# Commit
git add releases/ CHANGELOG.md releases/unreleased.md
git commit -m "release: 1.5.0.320-ptbr-v2"

# Tag
git tag v1.5.0.320-ptbr-v2
git push origin main --tags
```

### Atualizar unreleased.md após release

Mover o conteúdo de `releases/unreleased.md` para o arquivo de notas da release criado, e limpar o unreleased.md mantendo apenas o cabeçalho:

```markdown
# Unreleased — Em desenvolvimento

> Mudanças que ainda não foram empacotadas em uma release oficial.

---

## [Unreleased] — base: 1.5.0.320

### Adicionado

### Corrigido

### Conhecido / Pendente
```

---

## Formato de entrada no CHANGELOG.md

```markdown
| 1.5.0.320-ptbr-v2 | 2026-05-08 | [1.5.0.320-ptbr-v2.md](releases/1.5.0.320-ptbr-v2/1.5.0.320-ptbr-v2.md) | Estável |
```
