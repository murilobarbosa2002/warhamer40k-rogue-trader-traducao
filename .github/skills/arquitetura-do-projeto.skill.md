---
description: "Explica a arquitetura completa do projeto: como os scripts se conectam, quais bibliotecas fazem o quê, o pipeline de tradução, o CI/CD e as convenções de código. Use quando precisar entender como o projeto funciona ou planejar uma mudança."
name: "arquitetura-do-projeto"
tools: [read]
---

Leia os seguintes arquivos para construir um entendimento completo da arquitetura:

## Documentação principal

1. [.github/copilot-instructions.md](../copilot-instructions.md) — mapa completo do projeto, padrões, bibliotecas e convenções
2. [.github/agents/arquiteto.agent.md](../agents/arquiteto.agent.md) — decisões arquiteturais, mapa de dependências, trade-offs

## Scripts principais a entender

3. [scripts/translate_batch.py](../../scripts/translate_batch.py) — pipeline de tradução com fallback chain
4. [scripts/validate.py](../../scripts/validate.py) — validação estrutural (o que é considerado erro)
5. [scripts/fix_auto.py](../../scripts/fix_auto.py) — padrão de script de correção com replace_outside_tags

## Infraestrutura

6. [Makefile](../../Makefile) — todos os comandos disponíveis
7. [.github/workflows/ci.yml](../workflows/ci.yml) — jobs de CI e quando rodam
8. [requirements.txt](../../requirements.txt) — dependências com comentários explicativos

## Após ler, apresente

1. Mapa visual de dependências entre scripts (ASCII art ou texto estruturado)
2. Fluxo de uma tradução do início ao fim
3. Fluxo de uma correção do início ao fim
4. Pontos de extensão: onde adicionar novos providers, novas correções, novos jobs de CI
