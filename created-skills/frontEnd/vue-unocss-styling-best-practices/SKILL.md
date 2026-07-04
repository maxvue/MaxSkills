---
name: vue-unocss-styling-best-practices
description: Use when designing, styling, or editing Vue 3 component templates, styles, and layouts in Engeapp, as well as implementing or configuring dark mode styling and theme preferences. Triggers on UnoCSS class usage, Tailwind/Wind3 utilities, custom styling rules, CSS/SCSS writing, dark mode toggling, system preferences detection, and edits in uno.config.ts.
---

# Melhores Práticas de Estilização com Vue 3 e UnoCSS

## Objetivo
Estabelecer diretrizes claras, sólidas e padrões consistentes para estilizar componentes do Vue 3 usando o UnoCSS no ecossistema Engeapp, garantindo a conformidade visual com o tema oficial Aura/Max (`presetMaxUno`), otimização de performance e estruturas de visualização de fácil manutenção.

## Instruções

### 1. Integração do UnoCSS e Preset de Tema
- O Engeapp utiliza um preset customizado chamado `presetMaxUno` (importado de `@maxvue/max-components-ui/preset`), juntamente com `presetWind3()`, `presetAttributify()` e `presetIcons()`.
- O `presetMaxUno` compila as variáveis do tema (como `--pink-X`, `--red-X`, `--blue-X`, `--emerald-X`, etc.) no elemento raiz (:root) do documento.
- Não insira cores hexadecimais ou variáveis CSS manualmente no HTML. Use classes utilitárias mapeadas diretamente para as cores do tema:
  - `bg-emerald-700` ou `text-blue-600`
  - Atalhos personalizados como `fs-1.2` ou `font-size-1.2` para definir o tamanho da fonte (compila para `font-size: 1.2rem !important`)
  - Atalhos utilitários para altura/largura como `h-full`, `h-flex`, `w-full`, `w-flex` (compila para `100% !important`)
  - Atalhos personalizados de margem e preenchimento (ex: `p-10`, `m-20`) processados pelo `presetMaxUno`.

### 2. Uso do Preset Attributify para Atributos Comuns de Layout
- O Engeapp utiliza o `presetAttributify()` para suportar atributos semânticos de estilização diretamente nas tags HTML, evitando classes sobrecarregadas.
- Sempre que aplicável, utilize essas propriedades predefinidas em formato de atributo em vez de escrever classes complexas. Exemplos:
  - `danger`, `cancel`, `confirm`, `transparent` para estilização de tipos de botões.
  - `noborder` para remover rapidamente bordas e contornos.
  - `no-padding`, `no-gap`, `no-row-gap`, `no-column-gap` para redefinição de espaçamento.
  - `grid-center` ou atributos de alinhamento como `left`, `right`, `center`, `start`, `end`, `center-start`, `center-end`, etc.
  - `pointer` para definir `cursor: pointer !important`.
  - `absolute`, `relative` para posicionamento.
  - `upper`, `lower` para transformações de texto.
  - `full`, `flex` para largura e altura de `100%`.

### 3. Agrupamento de Variantes (transformerVariantGroup)
- O agrupamento de variantes está ativo por meio do `transformerVariantGroup()`. Use parênteses para aplicar múltiplos modificadores de hover, focus, modo escuro, estados responsivos ou filhos para melhorar a legibilidade.
- **Bom:** `hover:(bg-primary-600 text-white shadow-md)`
- **Ruim:** `hover:bg-primary-600 hover:text-white hover:shadow-md`

### 4. Estilização Dinâmica e Condicional
- Para classes condicionais, prefira a sintaxe padrão de binding do Vue com notação de objeto ou array.
- Agrupe classes estáticas em um atributo `class` comum e declare as classes dinâmicas/condicionais dentro do `:class`.
- Mantenha a declaração limpa e reativa.
  - **Bom:** `<div class="p-4 rounded-md border" :class="{ 'border-emerald-700 bg-emerald-50': isActive, 'border-background-200 bg-background-0': !isActive }">`

### 5. Classes Utilitárias vs. SCSS Localizado `<style scoped lang="scss">`
- Dê preferência total às classes utilitárias do UnoCSS para 90% das tarefas de estilo (layout, cores, espaçamento, bordas e tipografia).
- Utilize o bloco `<style scoped lang="scss">` *apenas* nos seguintes cenários:
  - Sobrescrita de estilos de bibliotecas de terceiros complexas (como modificações visuais no PrimeVue ou VueFinder).
  - Definição de animações de keyframes complexas não representáveis facilmente na configuração do UnoCSS.
  - Criação de ajustes de layout aninhados muito específicos onde classes utilitárias tornariam a leitura do código confusa.
- Organize os blocos do componente SFC sempre na ordem obrigatória: `<template>`, `<script setup lang="ts">`, `<style scoped lang="scss">`.

### 6. Convenção de Formatação de Atributos de Componente
- Dentro do bloco `<template>`, mantenha todos os atributos e props de um componente Vue em uma **única linha (estilo inline)**. Não quebre os atributos em múltiplas linhas, mesmo que a linha fique longa.
- Exemplo: `<MaxButton danger pointer label="Remover Item" @click="handleDelete" />`

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Não quebre os atributos de componentes em várias linhas** nos templates Vue.
- **Não escreva cores hexadecimais manualmente** no HTML ou em CSS inline. Utilize sempre os tokens que realmente existem no tema do `presetMaxUno` — escalas numéricas (`bg-background-0`, `bg-red-700`, `bg-emerald-700`, `text-blue-600`, `text-primary-600`, etc.) ou os vars semânticos existentes (`--primary`, `--secondary`, `--success`, `--danger`, `--error`, `--info`, `--warn`, `--text`, `--white`).
- **Não crie regras CSS em folhas de estilo globais** quando puderem ser resolvidas por meio de utilitários UnoCSS ou SCSS local (`<style scoped lang="scss">`).
- **Não utilize Options API** sob nenhuma circunstância; sempre implemente a Composition API `<script setup lang="ts">` usando TypeScript.
- **Mantenha todos os comentários em Português do Brasil (pt-BR)** dentro dos arquivos SFC de código, respeitando as regras globais do projeto.
