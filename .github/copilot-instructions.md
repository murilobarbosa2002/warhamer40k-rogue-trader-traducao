# Warhammer 40K: Rogue Trader — Projeto de Tradução PT-BR

Este é um projeto colaborativo de tradução do jogo **Warhammer 40,000: Rogue Trader** para o português brasileiro. O arquivo principal de tradução é `enGB.json`, com ~69.862 strings.

## Arquivos e Scripts do Projeto

| Arquivo | Descrição |
|---------|-----------|
| `enGB.json` | Arquivo de tradução PT-BR (mod para o jogo) |
| `arquivo-original-1.5.0.320.json` | Original EN versão 1.5.0.320 — fonte da verdade |
| `glossario.json` | Terminologia canônica obrigatória |
| `scripts/translate_batch.py` | Tradução automática com IA (Ollama → Groq → Google) |
| `scripts/build_from_original.py` | Reconstrói enGB.json limpo a partir do original |
| `scripts/diff_original.py` | Gera fila de trabalho com strings não traduzidas |
| `scripts/fix_auto.py` | Correções automáticas de terminologia (MP→PM, etc.) |
| `scripts/validate.py` | Valida estrutura JSON e balanço de tags |
| `scripts/relatorio.py` | Relatório completo de qualidade |
| `.env` / `.env.example` | Config: provedor de IA, chaves API, tamanho de lote |

### Comandos rápidos

```bash
# Ver quantas strings ainda precisam de tradução
python3 scripts/diff_original.py --stats

# Traduzir strings faltando com IA local (Ollama)
python3 scripts/translate_batch.py

# Traduzir apenas 50 strings para testar
python3 scripts/translate_batch.py --limite 50

# Correções automáticas de terminologia
python3 scripts/fix_auto.py

# Validar e gerar relatório
python3 scripts/validate.py && python3 scripts/relatorio.py
```

## Contexto do Universo

Warhammer 40K é um universo de ficção científica **grimdark** (sombrio e brutal). O tom é sério, formal, épico e às vezes litúrgico. Personagens nobres falam com altivez, militares falam com autoridade, cultistas e hereges com fanatismo. Evite tom casual ou moderno.

O jogador interpreta um **Rogue Trader** (Comerciante Desonesto/Explorador Imperialista) — um nobre com Carta de Marca Imperial que tem autoridade quase absoluta nos espaços não conquistados. Use pronomes masculinos para o personagem jogador, exceto quando o próprio texto fonte usar explicitamente pronomes femininos (she/her) ou neutros para esse personagem.

## Estrutura do Arquivo

`enGB.json` tem o seguinte formato — **NUNCA altere as chaves UUID nem o campo `Offset`**:

```json
{
  "strings": {
    "uuid-da-string": {
      "Offset": 0,
      "Text": "Texto traduzido aqui"
    }
  }
}
```

### Tags que DEVEM ser preservadas intactas

| Tag | Exemplo | Descrição |
|-----|---------|-----------|
| `{g|..}..{/g}` | `{g|Encyclopedia:Damage}dano{/g}` | Link de enciclopédia — traduz só o texto interno |
| `{d|..}..{/d}` | `{d|Encyclopedia:Ch1_Foo}texto{/d}` | Link de diálogo — traduz só o texto interno |
| `{n}..{/n}` | `{n}Narração{/n}` | Bloco de narração |
| `{uip|..}` | `{uip|MP|uuid}` | Variável de UI — NÃO traduzir |
| `{unit_stat|..}` | `{unit_stat|WP|stat}` | Stat de unidade — NÃO traduzir |
| `<b>`, `<i>`, `<br>` | `<b>negrito</b>` | HTML de formatação — preservar |
| `\n` | — | Quebra de linha — preservar |

**Atenção:** O identificador dentro de `{g|Encyclopedia:NomeDaCoisa}` nunca é traduzido. Apenas o texto entre as tags é traduzido.

## Glossário Canônico

Consulte sempre `glossario.json` na raiz do projeto. Os termos abaixo são obrigatórios:

| Inglês | PT-BR Canônico | Notas |
|--------|----------------|-------|
| Action Points / AP | Pontos de Ação / **PA** | Nunca usar "AP" em texto PT |
| Movement Points / MP | Pontos de Movimento / **PM** | Nunca usar "MP" em texto PT |
| Wounds / HP | **Ferimentos** | Terminologia do tabletop WH40K |
| Damage | **Dano** | |
| Target | **Alvo** | |
| Range | **Alcance** | |
| Cooldown | **Recarga** | |
| Buff | **Aprimoramento** | Ou "bônus de efeito" quando como substantivo |
| Debuff | **Penalidade de efeito** | |
| Skill (perícia de personagem) | **Perícia** | |
| Ability / Feat | **Habilidade** | |
| Talent | **Talento** | |
| Trait | **Característica** | |
| Passive | **Passivo** | |
| Round | **Rodada** | |
| Turn | **Turno** | |
| Resistance Test | **Teste de Resistência** | |
| Cover | **Cobertura** | |
| Dodge | **Esquiva** | |
| Charge | **Investida** | |
| Spawn (creature created) | **Criatura gerada** | Exceto "Spawn do Caos" (nome próprio) |
| NPC | **PNJ** | Personagem Não-Jogador |
| The Void / Void | **O Vazio** | Espaço sideral em WH40K |
| The Warp | **O Imaterium** ou **A Distorção** | Usar "Imaterium" para o lugar, "Distorção" para efeitos |
| Lord Captain | **Capitão-Comandante** | Título do Rogue Trader |
| Lore (skill category) | **Conhecimento** | Ex: "Lore (Warp)" → "Conhecimento (Distorção)" |

### Termos que NUNCA são traduzidos (nomes próprios do universo WH40K)

`Rogue Trader`, `Astartes`, `Space Marine`, `Adeptus Mechanicus`, `Adepta Sororitas`, `Inquisition`, `Mechanicus`, `Omnissiah`, `Immaterium`, `Chaos` (quando nome próprio), `Eldar`, `Aeldari`, `Tau`, `Ork`, `Necron`, `Tyranid`, `Bolter`, `Boltgun`, `Lasgun`, `Laspistol`, `Longlas`, `Vox`, `Mechadendrite`, `Servo-skull`, `Throne` (quando "Golden Throne"), `Webway`, `Warp` (quando nome próprio), `Ferrum Sanctum`, `Omnissias`.

## Regras de Tradução

### 1. Formatação e Tags

- **Preservar todas as tags** exatamente como estão: `{g|..}texto{/g}`, `{n}texto{/n}`, `{uip|..}`, `{unit_stat|..}`, `<b>`, `<i>`, `<br>`, `\n`
- O identificador dentro de `{g|Encyclopedia:NomeDaCoisa}` **nunca é traduzido** — apenas o texto entre as tags
- Não remover, reordenar ou modificar tags `{g|...}`, `{n}...{/n}`, `{uip|...}`
- Não traduzir UUIDs, chaves ou identificadores

### 2. Terminologia

- Usar sempre o glossário canônico (seção acima): AP→PA, MP→PM, Cooldown→Recarga, etc.
- Não usar termos em inglês em texto PT-BR: "damage", "target", "range", "cooldown", "buff", "skill"
- Não misturar "MP" com "PM" ou "AP" com "PA" na mesma string
- Não traduzir nomes próprios do universo WH40K listados na seção de glossário

### 3. Tom e Estilo

- **Tom grimdark**: falas épicas, sérias ou brutais — sem linguagem casual ou moderna
- O jogo usa "você" majoritariamente; manter esse padrão salvo exceções de personagens com estatura formal
- Evitar traduções literais robóticas: "certifique-se de que" → "garanta que"; "você pode ser capaz de" → reescrever livremente
- Verificar concordância de gênero dos substantivos (ex: "a nave" é feminina)

### 4. Tipos de Texto

| Tipo | Orientação |
|------|------------|
| Interface (UI) | Direto e conciso. "Pick up item" → "Pegar item" |
| Enciclopédia/Habilidades | Tom técnico-formal. Usar glossário estritamente |
| Falas de personagens | Preservar voz e personalidade: Tech-Priest usa jargão mecânico; Soldado fala direto; Noble fala com altivez |
