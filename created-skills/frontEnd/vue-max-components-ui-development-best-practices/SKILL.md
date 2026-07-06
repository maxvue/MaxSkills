---
name: vue-max-components-ui-development-best-practices
description: Use when developing, modifying, or creating components within the @maxvue/max-components-ui library. Triggers on changes inside the MaxComponentsUi project, adding new PrimeVue wraps, implementing InputBase wrappers, running generateResolver.ts script, and writing tests for UI components using Vitest and @vue/test-utils.
---

## Objetivo
Estabelecer convenções rígidas de arquitetura, estilização, testes e registro para o desenvolvimento e manutenção dos componentes UI da biblioteca `@maxvue/max-components-ui`.

## Instruções

### 1. Estrutura SFC (Single-File Component) e Convenções de Código
* **Composition API**: É estritamente obrigatório utilizar a Composition API (`<script setup lang="ts">`). A Options API é proibida.
* **Estilização**: Use sempre `<style lang="scss">` ou `<style scoped lang="scss">`. CSS puro não é permitido.
* **Ordem dos Blocos**: Mantenha as seções do SFC exatamente nesta ordem:
  1. `<template>`
  2. `<script setup lang="ts">`
  3. `<style>`
* **Formatação do SFC**:
  - A indentação deve ser obrigatoriamente de **4 espaços** (não use 2 espaços).
  - Use **aspas simples** para strings.
  - O ponto e vírgula é **obrigatório**.
  - Dentro do bloco `<template>`, mantenha **sempre** todos os atributos/parâmetros de uma tag (componente, `div` ou qualquer elemento) em **uma única linha** (estilo inline), por mais atributos que tenha. **Nunca** quebre atributos em várias linhas. Ex.: `<MaxModal ref="cardModal" no-button class="card-modal">` — e nunca a forma quebrada com `ref`, `no-button` e `class` cada um em sua própria linha.
  - **Nunca use `<section>`**: use sempre `<div>` no lugar de `<section>` (e de outras tags seccionais) para agrupar conteúdo.

### 2. Componentes de Entrada de Formulário e `InputBase`
* Todos os componentes que funcionam como inputs de formulário devem ser encapsulados usando o componente `<InputBase>` como o elemento externo mais abrangente.
* O `<InputBase>` gerencia:
  - Layouts de labels flutuantes (`FloatLabel`) e campos com ícone (`IconField`/`InputIcon`).
  - Estados de validação: `done`, `error`, `caution`, `required` e `noStatus`.
  - Exibição de mensagens de feedback ou erro logo abaixo do campo.
  - Modos de label em linha (inline) e ícones personalizados.
* Certifique-se de repassar as propriedades de validação (`error`, `done`, `caution` e `required`) corretamente do seu componente para o componente interno `<InputBase>`.

### 3. Extensão de Componentes PrimeVue
* Ao criar wrappers para componentes PrimeVue 4, integre-os ao preset de tema personalizado (`MaxStyle`) e utilize as variáveis de estilo padrão do tema.
* Utilize variáveis CSS derivadas do tema (`var(--max-primary-500)`, `var(--background-300)`, `var(--blue-600)`) dentro dos seus blocos SCSS em vez de usar cores hexadecimais estáticas (hardcoded).
* Integre classes utilitárias do UnoCSS (`virtual:uno.css`) para gerenciar layout, espaçamentos e configurações de flexbox quando apropriado.

### 4. Especificações de Testes (Vitest)
* Todos os arquivos de componentes devem possuir testes unitários correspondentes dentro da pasta `tests/components/` (ex: `tests/components/MaxInputText.test.ts`).
* **Configuração dos Testes**:
  - Faça o mock do Pinia globalmente nos testes utilizando `setActivePinia(createPinia())` dentro do gancho `beforeEach`.
  - Use `@vue/test-utils` e `happy-dom` para montagem dos componentes.
* **Casos de Teste**:
  - Verifique se o componente é renderizado corretamente com as propriedades padrão.
  - Assegure que o componente emite o evento `update:modelValue` quando o valor do input é alterado pelo usuário.
  - Garanta que atualizações externas de `modelValue` refletem no valor do elemento de entrada de forma reativa.
  - Valide os comportamentos de formulário (ex: acionar erro de campo obrigatório ao disparar `blur` com o campo vazio, e validar se as props `done` ou `error` são propagadas corretamente no componente filho `<InputBase>`).

### 5. Registro de Componentes e Auto-Import (Resolver)
* As aplicações consumidoras dependem do arquivo `src/components-manifest.json` para resolver e auto-importar componentes dinamicamente.
* Sempre que um componente em `src/components/` for adicionado, renomeado ou excluído, você **deve** atualizar o manifesto.
* Execute o script gerador do resolver com o seguinte comando:
  ```bash
  npx tsx src/scripts/generateResolver.ts
  ```
* Certifique-se de que os aliases do componente estejam devidamente definidos em `src/scripts/generateResolver.ts` e exportados no arquivo `src/index.ts` (por exemplo, exportando aliases como `MaxInputText`, `InputText` e `InputField` apontando para o mesmo arquivo).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Sem Options API**: Não use `data()`, `methods`, `computed`, etc., dentro do objeto padrão de opções.
* **Estilização**: Não escreva CSS puro; use SCSS com variáveis MaxTheme ou classes utilitárias do UnoCSS.
* **Layout de Atributos**: Nunca divida os atributos de tags HTML/Vue em múltiplas linhas dentro do `<template>`.
* **Testes**: Não envie um novo componente sem pelo menos 80% de cobertura de testes e sem a suíte Vitest devidamente configurada.
* **Registro de Componentes**: Nunca esqueça de rodar o comando `generateResolver.ts` para reconstruir o manifesto de auto-import após adicionar componentes.
