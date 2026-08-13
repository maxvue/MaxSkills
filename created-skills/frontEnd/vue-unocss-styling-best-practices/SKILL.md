---
name: vue-unocss-styling-best-practices
description: "Use when styling templates, styles, and layouts in Vue 3 with UnoCSS + presetMaxUno: attributify classes/attributes, color shortcuts, transformerVariantGroup, params.scss, SCSS scoped blocks, and dark mode via useDark. Covers objectives and core workflows."
---
# Melhores Práticas de Estilização com Vue 3 e UnoCSS

## Objetivo
Estabelecer diretrizes claras, sólidas e padrões consistentes para estilizar componentes do Vue 3 usando o UnoCSS no ecossistema Engeapp, garantindo a conformidade visual com o tema oficial Aura/Max (`presetMaxUno`), otimização de performance e estruturas de visualização de fácil manutenção.

## Instruções

### 1. Integração do UnoCSS e Preset de Tema
- O Engeapp utiliza um preset customizado chamado `presetMaxUno` (importado de `@maxvue/max-components-ui/preset`), juntamente com `presetWind3()`, `presetAttributify()` e `presetIcons()`.
- O `presetMaxUno` compila as variáveis do tema (como `--pink-X`, `--red-X`, `--blue-X`, `--emerald-X`, etc.) no elemento raiz (:root) do documento.
- Não insira cores hexadecimais ou variáveis CSS manualmente no HTML. Use as classes utilitárias que o `presetMaxUno` mapeia para as `var(--...)` do tema. Atenção às duas famílias distintas de regra (confira em `presetMaxUno.ts`):
  - **Cor de texto:** escreva o token **sem** o prefixo `text-` — a regra `^(red|green|blue|emerald|orange|amber|cyan|pink|yellow|gray|background)-?(\d+)$` casa `blue-600`, `red-700`, e também `blue600` (hífen opcional) e emite `color: var(--blue-600)`. `text-blue-600` **não** casa essa regra e cai no `presetWind3` (paleta Tailwind, não o tema); evite-o para cores do tema.
  - **Cor de fundo:** o shortcut `^bg-(.+)$` aceita qualquer token do tema, incluindo os semânticos — `bg-emerald-700`, `bg-primary-600`, `bg-background-0` compilam para `background-color: var(--emerald-700)` etc.
  - Atalhos personalizados como `fs-1.2` ou `font-size-1.2` para definir o tamanho da fonte (compila para `font-size: 1.2rem !important`)
  - Atalhos utilitários para altura/largura como `h-full`, `h-flex`, `w-full`, `w-flex` (compila para `100% !important`)
  - Atalhos personalizados de margem e preenchimento (ex: `p-10`, `m-20`) processados pelo `presetMaxUno`.

### 2. Atributos Semânticos do Tema (params.scss) vs. presetAttributify
- Distinga duas coisas que parecem iguais no template mas têm origens diferentes:
  - **Atributos semânticos do tema:** seletores de atributo CSS puros escritos à mão em `@maxvue/max-components-ui` (`src/themes/params.scss`), injetados no CSS pelo preflight do `presetMaxUno`, e que funcionam mesmo sem o `presetAttributify`:
    - `danger`, `cancel`, `confirm`, `transparent` para estilização de tipos de botões.
    - `white` — resolve para `color: var(--primary-0)` (token do tema, dark-mode aware).
    - `noborder` para remover rapidamente bordas e contornos.
    - `no-padding`, `no-gap`, `no-row-gap`, `no-column-gap` para redefinição de espaçamento.
    - `grid-center` ou atributos de alinhamento como `left`, `right`, `center`, `start`, `end`, `center-start`, `center-end`, etc.
    - `pointer` para `cursor: pointer !important`; `denied` para `cursor: not-allowed !important`.
    - `absolute`, `relative` para posicionamento.
    - `upper`, `lower` para transformações de texto.
    - `full`, `flex` para largura e altura de `100%`.
  - **presetAttributify:** permite **escrever utilitários UnoCSS em forma de atributo** (ex.: `bg-red-500`, `p-4`). Não é ele que define os atributos semânticos acima, mas alguns nomes colidem: com `presetAttributify` ativo, `flex`, `absolute` e `relative` **sem valor** também são utilitários valueless reconhecidos por ele (`display:flex`, `position:absolute`, `position:relative`) — ou seja, `<div flex>` recebe `display:flex` do `presetAttributify` **além de** `width/height:100% !important` do `params.scss` (regra `[full],[flex] {width:100% !important;height:100% !important;}`), e `absolute`/`relative` recebem a mesma `position` por duas origens sobrepostas. O efeito visual final costuma ser o mesmo, mas são duas regras CSS concorrentes, não uma só.

### 3. Agrupamento de Variantes (transformerVariantGroup)
- O agrupamento de variantes está ativo por meio do `transformerVariantGroup()`. Use parênteses para aplicar múltiplos modificadores de hover, focus, modo escuro, estados responsivos ou filhos para melhorar a legibilidade.
- **Bom:** `hover:(bg-primary-600 shadow-md)` — para texto branco, use o atributo semântico `white` do tema (`[white] {color: var(--primary-0) !important}`, dark-mode aware) em vez de `text-white` (classe crua do `presetWind3`/Tailwind, fixa em `#fff`, não participa do dark mode).
- **Ruim:** `hover:bg-primary-600 hover:text-white hover:shadow-md`

### 4. Estilização Dinâmica e Condicional
- Para classes condicionais, prefira a sintaxe padrão de binding do Vue com notação de objeto ou array.
- Agrupe classes estáticas em um atributo `class` comum e declare as classes dinâmicas/condicionais dentro do `:class`.
- Mantenha a declaração limpa e reativa.
  - **Bom:** `<div class="p-4 rounded-md border" :class="{ 'bg-emerald-700': isActive, 'bg-background-200': !isActive }">` — `border-*` não é uma família de regras do `presetMaxUno` (apenas cor de texto e `bg-`); para cor de fundo use o shortcut `bg-(.+)` (ex.: `bg-background-200`).

### 5. Classes Utilitárias vs. SCSS Localizado `<style lang="scss">`
- Dê preferência total às classes utilitárias do UnoCSS para 90% das tarefas de estilo (layout, cores, espaçamento, bordas e tipografia).
- A convenção dominante do engeapp é `<style lang="scss">` **sem** `scoped`. Reserve `scoped` apenas para os cenários excepcionais abaixo:
  - Sobrescrita de estilos de componentes de terceiros complexos (ex.: ajustes finos em componentes do MaxComponentsUi — que são construídos sobre o PrimeVue e, por isso, expõem classes internas `.p-*` via `:deep(...)` — ou VueFinder). Use os componentes MaxComponentsUi na aplicação; não instancie componentes PrimeVue diretamente.
  - Definição de animações de keyframes complexas não representáveis facilmente na configuração do UnoCSS.
  - Criação de ajustes de layout aninhados muito específicos onde classes utilitárias tornariam a leitura do código confusa.
- Organize os blocos do componente SFC sempre na ordem: `<template>`, `<script setup lang="ts">`, `<style lang="scss">` (ou `<style scoped lang="scss">` nos casos excepcionais acima).

### 6. Convenção de Formatação de Atributos de Componente
- Dentro do bloco `<template>`, mantenha todos os atributos e props de um componente Vue em uma **única linha (estilo inline)**. Não quebre os atributos em múltiplas linhas, mesmo que a linha fique longa.
- Exemplo: `<MaxButton danger pointer label="Remover Item" @click="handleDelete" />`

### 7. Modo Escuro (.dark) e Tokens do Tema — capacidade a habilitar, não padrão vigente
- Hoje o engeapp **não liga** nenhuma classe `.dark` ao DOM: existe apenas a flag `settings.darkMode` (alternada em `UserSection.vue`), sem qualquer efeito visual — `useDark`/`useColorMode`/`usePreferredDark` não são usados em nenhum lugar de `resources/`.
- O tema já traz a paleta escura pronta em `@maxvue/max-components-ui/src/themes/colors.scss`, que define um bloco `.dark { ... }` **aninhado dentro de `:root`** (compila para o seletor descendente `:root .dark`, não `:root.dark`/`html.dark`). Para habilitar o dark mode, a classe `.dark` precisa estar em um **descendente** de `<html>` (ex.: `<body>` ou o wrapper do app) — aplicá-la em `document.documentElement` (comportamento padrão de `useDark()`/`useColorMode()` do VueUse) **não troca a paleta** do tema, embora ative os tokens escuros do PrimeVue (`darkModeSelector: '.dark'`), produzindo um estado inconsistente.
- Para habilitar, use os composables reexportados por `@maxvue/max-use` (que envolvem o VueUse) — `useColorMode`, `useDark`, `usePreferredDark` — configurando o `selector` para `body` ou o wrapper do app (ex.: `useDark({ selector: 'body' })`), ou corrigindo o seletor em `colors.scss`. Não importe VueUse cru — o padrão do projeto é sempre passar pelo `@maxvue/max-use`.
- Como todas as classes/atributos do `presetMaxUno` apontam para as mesmas `var(--...)`, uma vez o escopo `.dark` corretamente aplicado, a UI inteira troca de paleta automaticamente — desde que você tenha usado tokens do tema (Seção 1) e não hexadecimais fixos (regra de ouro: só estilização baseada em tokens participa do dark mode).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- Os vars semânticos base do tema (`--primary`, `--secondary`, `--success`, `--danger`, `--error`, `--info`, `--warn`, `--text`, `--white`) também existem e podem ser consumidos via `bg-<nome>` ou dentro do SCSS.
- **Não crie regras CSS em folhas de estilo globais** quando puderem ser resolvidas por meio de utilitários UnoCSS ou SCSS local (`<style scoped lang="scss">`).
- **Não utilize Options API** sob nenhuma circunstância; sempre implemente a Composition API `<script setup lang="ts">` usando TypeScript.
- **Mantenha todos os comentários em Português do Brasil (pt-BR)** dentro dos arquivos SFC de código, respeitando as regras globais do projeto.
