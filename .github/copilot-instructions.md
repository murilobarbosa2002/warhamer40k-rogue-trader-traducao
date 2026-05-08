# Warhammer 40K: Rogue Trader — Projeto de Tradução PT-BR

Este é um projeto colaborativo de tradução do jogo **Warhammer 40,000: Rogue Trader** para o português brasileiro. O arquivo principal de tradução é `enGB.json`, com ~69.862 strings.

## Contexto do Universo

Warhammer 40K é um universo de ficção científica **grimdark** (sombrio e brutal). O tom é sério, formal, épico e às vezes litúrgico. Personagens nobres falam com altivez, militares falam com autoridade, cultistas e hereges com fanatismo. Evite tom casual ou moderno.

O jogador interpreta um **Rogue Trader** (Comerciante Desonesto/Explorador Imperialista) — um nobre com Carta de Marca Imperial que tem autoridade quase absoluta nos espaços não conquistados. Trate o personagem jogador com pronomes masculinos por padrão, a menos que o contexto indique o contrário.

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

## Princípios de Tradução

1. **Tom grimdark**: As falas devem soar épicas, sérias ou brutais. Evite "você pode" → prefira "podes" quando o personagem tem estatura. Mas mantenha consistência — o jogo usa "você" majoritariamente.
2. **Sem traduções literais robóticas**: "certifique-se de que" → "garanta que". "você pode ser capaz de" → "pode ser possível" ou simplesmente reescreva.
3. **Gênero dos substantivos**: A nave é feminina ("a nave"). O personagem é "o personagem". Verifique concordância.
4. **Textos de interface (UI)**: Podem ser mais diretos e concisos. "Pick up item" → "Pegar item" (não "Por favor, pegue o item").
5. **Textos de enciclopédia/habilidades**: Tom técnico-formal. Use terminologia do glossário.
6. **Falas de personagens**: Preservar a voz e personalidade. Um Tech-Priest fala com jargão mecânico; um Soldado fala direto; um Noble fala com altivez.

## O que NÃO fazer

- Não traduzir UUIDs, chaves, identificadores dentro de tags
- Não remover ou reordenar tags `{g|...}`, `{n}...{/n}`, `{uip|...}`
- Não usar "damage", "target", "range", "cooldown", "buff", "skill" em texto PT-BR
- Não misturar "MP" com "PM" ou "AP" com "PA" na mesma string
- Não usar Google Translate literalmente sem revisão
- Não traduzir nomes próprios listados acima
