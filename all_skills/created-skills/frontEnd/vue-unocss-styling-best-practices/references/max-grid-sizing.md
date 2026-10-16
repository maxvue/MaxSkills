# Contrato Canônico de Dimensionamento Fluido e MaxGrid

Este documento estabelece a especificação canônica da família de regras de dimensionamento `sN`/`s-N` do `presetMaxUno` e sua integração com o componente `MaxGrid` e o ecossistema `@maxvue/max-components-ui`.

---

## 1. Gramática e Fórmulas da Família `s`

A família de utilitários `s` (ou `s-`) do `presetMaxUno` substitui a antiga convenção baseada em porcentagens por um modelo de **dimensionamento fluido com limites em pixels e crescimento flexbox**.

### 1.1 Expressão Regular Canônica

No arquivo `presetMaxUno.ts`, a regra é declarada pela seguinte regex:

```text
^s-?(\d+)(?:-(full|max|\d+))?(?:-(start|end)(?:-(desktop|mobile|tablet))?|-(desktop|mobile|tablet)(?:-(start|end))?)?$
```

### 1.2 Regras de Formação e Declarações CSS

- **Prefixo:** `s` ou `s-` (ex.: `s7` e `s-7` são aliases idênticos).
- **Mínimo obrigatório (`N`):** número inteiro não negativo. Não há limite fixo de 1 a 100. Valores decimais, negativos ou unidades (`px`, `%`) **não** pertencem à gramática.
  - Emite: `min-width: N × 20px`.
  - Emite: `flex: 1 1 0%`.
- **Máximo padrão (quando omitido):**
  - Emite: `max-width: N × 24px`.
- **Máximo numérico explícito (`M`):**
  - Emite: `max-width: M × 20px`.
- **Máximo relativo (`full` ou `max`):**
  - Emite: `max-width: 100%`.
  - **Atenção:** `full` ou `max` afeta apenas o `max-width`; **não** altera o `min-width` e **não** força `width: 100%`.
- **Modificadores de quebra (`start` e `end`):**
  - `start`: emite `break-before: always`.
  - `end`: emite `break-after: always`.
- **Modificadores de dispositivo (`mobile`, `tablet`, `desktop`):**
  - `mobile`: encapsula todas as declarações em `@media (max-width: 767.98px)`.
  - `tablet`: encapsula todas as declarações em `@media (max-width: 1000.98px)`.
  - `desktop`: encapsula todas as declarações em `@media (min-width: 1001px)`.
  - **Nota de sobreposição:** `tablet` inclui `mobile` (não é faixa exclusiva de 768px a 1000px). O intervalo fracionário entre 1000.98px e 1001px não é coberto por tablet nem desktop.
- **Ordem dos modificadores:** Uma posição e um dispositivo podem ser declarados em qualquer ordem após o máximo opcional: `s7-10-end-mobile` e `s7-10-mobile-end` produzem o mesmo CSS.

> [!WARNING]
> **Alerta contra o mito das porcentagens:** O token **não** emite `width: N%` nem `flex-basis: N%`.
> `s50` **não** significa 50%: compila para `min-width: 1000px; max-width: 1200px`.
> `s100` **não** significa 100%: compila para `min-width: 2000px; max-width: 2400px`.

---

## 2. Tabela de Referência Numérica e Efeitos

| Token | Mínimo (`min-width`) | Máximo (`max-width`) | Flex | Quebra / Mídia / Efeito |
|---|---:|---:|:---:|---|
| `s1` / `s-1` | 20px | 24px | `1 1 0%` | Padrão |
| `s7` / `s-7` | 140px | 168px | `1 1 0%` | Padrão |
| `s3-10-start` | 60px | 200px | `1 1 0%` | `break-before: always` (inicia segmento no MaxGrid) |
| `s7-full` / `s7-max` | 140px | 100% | `1 1 0%` | Pode crescer até 100% do contêiner |
| `s7-end-mobile` / `s7-mobile-end` | 140px | 168px | `1 1 0%` | Regra e quebra aplicadas apenas em mobile (`<= 767.98px`) |
| `s12-20` | 240px | 400px | `1 1 0%` | Faixa útil para campos médios de formulário |
| `s50` | 1000px | 1200px | `1 1 0%` | **Não usar para 50%!** Força mínimo de 1.000px |
| `s100` | 2000px | 2400px | `1 1 0%` | **Não usar para 100%!** Força mínimo de 2.000px |

### 2.1 Casos Extremos e Boas Práticas

1. **Overflow por Mínimo Excessivo:** Se o `min-width` (`N × 20px`) for maior que a largura do contêiner disponível, ocorrerá transbordamento horizontal, mesmo quando sufixado com `-full` (ex.: `s50-full` ainda impõe 1.000px de largura mínima).
2. **Máximo Conflitante:** Um token como `s10-5` é aceito pelo regex e emite `min-width: 200px; max-width: 100px`. No modelo CSS de caixas, `min-width` prevalece sobre `max-width`, tornando a declaração redundante e confusa. Evite valores onde `M × 20px < N × 20px`.
3. **Largura Total: `w-full` vs. `sN-full`:**
   - Para garantir que um bloco ocupe 100% da largura em sua própria linha (ex.: wrapper de seções), utilize a classe utilitária `w-full`.
   - `s12-full` significa "largura mínima de 240px, podendo crescer até 100% se houver espaço, compartilhando a linha com outros elementos irmãos se couberem".

---

## 3. CSS Gerado × Linhas Coordenadas pelo MaxGrid

Existe uma separação arquitetural crítica entre o CSS puro emitido pelo UnoCSS e a coordenação de layout executada pelo componente `MaxGrid`:

```text
Token literal no template ──→ UnoCSS/presetMaxUno ──→ flex + min/max + @media + break-*
Filhos do slot MaxGrid    ──→ GridSlotRows        ──→ marcadores ativos ──→ div.max-grid-row
MaxInputText + attrs      ──→ InputBase/rootAttrs ──→ caixa externa dimensionada
```

### 3.1 MaxGrid e o Organizador `GridSlotRows`

O componente `MaxGrid.vue` (`.max-grid`) opera com:
- `display: flex; flex-wrap: wrap; gap: 13px 8px; padding-top: 14px; position: relative;`.
- Atributos `no-message` ou `no-messages`: colapsam o espaçador de mensagem em todos os inputs filhos (`.max-input-main-div`).
- Propriedades públicas: `label?: string | null` e `labelCenter?: boolean`.

Internamente, `MaxGrid` utiliza o componente funcional `GridSlotRows` (`gridSlotRows.ts`):
1. **Sem Marcadores Ativos:** Se nenhum nó filho contiver marcadores de quebra ativos, os VNodes do slot são renderizados diretamente, sem criar nenhuma div intermediária.
2. **Com Marcadores Ativos:** Os nós são agrupados em segmentos envelopados por `<div class="max-grid-row">`, que recebem `flex: 0 0 100%; width: 100%; display: flex; flex-wrap: wrap; gap: inherit;`.
3. **Achatamento de Fragments:** `flattenFragments` desempacota recursivamente nós `Fragment` (como `<template>` e `v-for`) e compõe as `keys` para preservar a reconciliação do Vue.
4. **Escopo Lógico:** O organizador inspeciona **apenas os filhos lógicos diretos** recebidos no slot. Marcadores colocados dentro de subcomponentes arbitrários ou wrappers sem marcadores não ativam a quebra.
5. **Atributos Ativos:** Marcadores são reconhecidos tanto no atributo `class` quanto em atributos booleanos/valueless (`attrs` com valor `''`, `true` ou `'true'`). Valores como `false`, `null` ou `undefined` **não** ativam o marcador.

### 3.2 Matriz de Suporte a Quebras Coordenadas

Nem todos os tokens com `start` ou `end` aceitos pelo `presetMaxUno` são coordenados como novas linhas pelo `MaxGrid`:

| Token / Modificador | CSS emitido pelo preset | Linha coordenada pelo MaxGrid | Contexto de aplicação |
|---|:---:|:---:|---|
| `*-start` (sem dispositivo) | Sim (`break-before`) | **Sim** | Inicia nova linha em qualquer resolução |
| `*-end` (sem dispositivo) | Sim (`break-after`) | **Sim** | Encerra a linha atual em qualquer resolução |
| `*-end-mobile` / `*-mobile-end` | Sim (`break-after`) | **Sim (somente mobile)** | Ativo apenas se `useMediaQuery('(max-width: 767.98px)')` for verdadeiro |
| `*-start-mobile` / `*-mobile-start` | Sim (`break-before`) | **Não** | Emite CSS, mas MaxGrid não segmenta linha |
| `*-start-tablet` / `*-tablet-start` | Sim (`break-before`) | **Não** | Emite CSS, mas MaxGrid não segmenta linha |
| `*-end-tablet` / `*-tablet-end` | Sim (`break-after`) | **Não** | Emite CSS, mas MaxGrid não segmenta linha |
| `*-start-desktop` / `*-desktop-start` | Sim (`break-before`) | **Não** | Emite CSS, mas MaxGrid não segmenta linha |
| `*-end-desktop` / `*-desktop-end` | Sim (`break-after`) | **Não** | Emite CSS, mas MaxGrid não segmenta linha |

> [!NOTE]
> Em flexbox comum, declarações CSS `break-before: always` e `break-after: always` não realizam quebra de linha. No ecossistema Max, a quebra de linha coordenada depende da divisão em `.max-grid-row` operada por `GridSlotRows`.

### 3.3 MaxGrid vs. MaxGridCols

- **`MaxGrid` (`MaxGrid.vue`):** Container flexbox fluido com gap padronizado de formulários e suporte a segmentação por linhas coordenadas (`GridSlotRows`). É o padrão obrigatório para formulários.
- **`MaxGridCols` (`MaxGridCols.vue`):** Container de CSS Grid puro com 24 colunas fixas (`grid-template-columns: repeat(24, 1fr)`), classe `.max-grid-cols` e gap `15px 10px`. **Não** utiliza `GridSlotRows` e não reconhece a família `sN` para quebra de linhas.

### 3.4 Encaminhamento de Atributos em `InputBase`

Nos componentes de formulário (como `MaxInputText`), os atributos de layout e estilos são repassados ao wrapper `InputBase.vue`:
- `rootAttrs`: recebe classes, estilos e atributos de layout (como `s7`, `s12-full`), aplicando-os na `div` externa (`.max-input-base.max-input-main-div`).
- `inputAttrs`: encaminha atributos específicos de controle (`type`, `placeholder`, `disabled`, `readonly`, `aria-*`) diretamente para o elemento de input interno.

---

## 4. Guia de Migração de Exemplos Antigos

Ao atualizar códigos e documentações que usavam a convenção antiga baseada em porcentagem:

1. **Substituir `s100` por `w-full` ou `sN-full`:**
   - Se o objetivo for um bloco ocupar a linha inteira sozinho: use `w-full`.
   - Se for um campo flexível que deve ocupar toda a largura disponível: use `s12-full` ou `s8-full`.
2. **Substituir `s50` por faixas mínimas realistas:**
   - Dois campos lado a lado em telas médias/largas: use `s12-full` em ambos (mínimo de 240px cada; se o contêiner tiver mais de 480px + gap, dividem a linha igualmente em 50%; se a tela for menor, quebram fluidamente).
3. **Substituir `s-70 w-max-400` por `s12-20`:**
   - O token `s12-20` já estabelece `min-width: 240px; max-width: 400px; flex: 1 1 0%`, tornando classes adicionais de `w-max-*` redundantes.
4. **Preservar Literais Estáticos:** Nunca construa classes `sN` dinamicamente via concatenação de strings (ex.: `'s' + tamanho`). Declare tokens literais completos para detecção estática pelo UnoCSS.

---

## 5. Exemplo Completo em Vue 3

```vue
<template>
    <MaxGrid label="Dados do Cadastro">
        <!-- Linha 1: Dois campos flexíveis que dividem a linha e quebram em telas pequenas -->
        <MaxInputText s12-full label="Nome Completo" v-model="form.nome" required />
        <MaxInputText s12-full-end label="E-mail Corporativo" v-model="form.email" required />

        <!-- Linha 2: Três campos com mínimos ajustados; o último fecha a linha -->
        <MaxInputText s8-full label="Documento / CPF" v-model="form.documento" />
        <MaxInputText s8-full label="Telefone de Contato" v-model="form.telefone" />
        <MaxInputText s6-full-end label="Código Postal" v-model="form.cep" />

        <!-- Linha 3: Campo largo e ações; encerramento mobile explícito -->
        <MaxInputText s14-full label="Endereço de Entrega" v-model="form.endereco" />
        <MaxButton s7-end-mobile confirm label="Salvar Alterações" @click="salvar" />
    </MaxGrid>
</template>

<script setup lang="ts">
    import { reactive } from 'vue';

    const form = reactive({
        nome: '',
        email: '',
        documento: '',
        telefone: '',
        cep: '',
        endereco: ''
    });

    function salvar(): void {
        // Fluxo de persistência do formulário
    }
</script>
```
