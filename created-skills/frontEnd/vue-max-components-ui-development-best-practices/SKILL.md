---
name: vue-max-components-ui-development-best-practices
description: Use when developing, modifying, or creating components within the @maxvue/max-components-ui library. Triggers on changes inside the MaxComponentsUi project, adding new PrimeVue wraps, implementing InputBase wrappers, running generateResolver.ts script, writing tests for UI components using Vitest and @vue/test-utils, or working on the active PrimeVue-independence migration.
---

## Objetivo
Estabelecer convenções rígidas de arquitetura, estilização, testes e registro para o desenvolvimento e manutenção dos componentes UI da biblioteca `@maxvue/max-components-ui`.

## Instruções

### 1. Estrutura SFC (Single-File Component) e Convenções de Código
* **Composition API**: É estritamente obrigatório utilizar a Composition API (`<script setup lang="ts">`). A Options API é proibida.
* **Estilização**: Use sempre `<style lang="scss">` ou `<style scoped lang="scss">`. CSS puro não é permitido. Evite `scoped` em componentes de biblioteca quando os estilos precisam afetar componentes filhos do PrimeVue.
* **Ordem dos Blocos**: Mantenha as seções do SFC exatamente nesta ordem:
  1. `<template>`
  2. `<script setup lang="ts">`
  3. `<style>`
* **Formatação do SFC**:
  - A indentação deve ser obrigatoriamente de **4 espaços** (não use 2 espaços).
  - Use **aspas simples** para strings.
  - O ponto e vírgula é **obrigatório**.
  - Sem vírgula final em listas/objetos (`comma-dangle: never`).
  - Dentro do bloco `<template>`, mantenha **sempre** todos os atributos/parâmetros de uma tag (componente, `div` ou qualquer elemento) em **uma única linha** (estilo inline), por mais atributos que tenha. **Nunca** quebre atributos em várias linhas. Ex.: `<MaxModal ref="cardModal" no-button class="card-modal">` — e nunca a forma quebrada com `ref`, `no-button` e `class` cada um em sua própria linha.
  - **Nunca use `<section>`**: use sempre `<div>` no lugar de `<section>` (e de outras tags seccionais) para agrupar conteúdo.
  - Tipar props e emits via `defineProps<Interface>()` / `defineEmits<{...}>()`, documentando cada prop com TSDoc (`/** ... */`).

### 2. Componentes de Entrada de Formulário e `InputBase`
* Todos os componentes que funcionam como inputs de formulário devem ser encapsulados usando o componente `<InputBase>` como o elemento externo mais abrangente.
* O `<InputBase>` gerencia:
  - Layout de label e campo via `<div>`s próprios (`max-input-main-div`, `max-input-field-div`) e o componente `<MaxIcon>` — não depende mais de `FloatLabel`/`IconField`/`InputIcon` do PrimeVue (a prop `float` só mantém o nome herdado do conceito).
  - Estados de validação: `done`, `error`, `caution`, `required` e `noStatus`.
  - Exibição de mensagens de feedback ou erro logo abaixo do campo.
  - Modos de label em linha (inline) e ícones personalizados.
* Certifique-se de repassar as propriedades de validação (`error`, `done`, `caution` e `required`) corretamente do seu componente para o componente interno `<InputBase>`.

### 3. Extensão de Componentes PrimeVue
* Ao criar wrappers para componentes PrimeVue 4, integre-os ao preset de tema personalizado (`MaxStyle`) e utilize as variáveis de estilo padrão do tema.
* Utilize variáveis CSS derivadas do tema (`var(--max-primary-500)`, `var(--background-300)`, `var(--blue-600)`) dentro dos seus blocos SCSS em vez de usar cores hexadecimais estáticas (hardcoded).
* Integre classes utilitárias do UnoCSS (`virtual:uno.css`) para gerenciar layout, espaçamentos e configurações de flexbox quando apropriado.

### 3.1. Migração em andamento: independência do PrimeVue
* **O código ainda depende do PrimeVue hoje** — existe um esforço ativo, ainda não executado, para tornar a biblioteca independente do PrimeVue (a partir do PrimeVue 5 ele deixará de ser open source). Novos componentes devem evitar criar novas dependências de PrimeVue quando possível.
* Arquivos de controle na raiz do repositório: `status-primevue.migration.yaml` (fonte de verdade do progresso, com `level`/`status` por componente: `waiting`/`in_progress`/`done`/`blocked`), `migration_plans/[Componente].md` (33 planos, um por componente) e `migration_executor.md` (protocolo do agente executor).
* **Protocolo**: cada invocação migra exatamente **um** componente (o próximo `waiting` de menor número), depois para e atualiza o status tanto no YAML quanto na fila do executor. Não migre mais de um componente por invocação e não reordene a fila.
* Restrições de ordem: `InputBase` primeiro (destrava ~19 inputs); `MaxInputSelect` antes dos dropdowns que o reutilizam; o conjunto `MaxTable` → `MaxTableColumn` → `MaxTableFields` migra junto.

### 4. Especificações de Testes (Vitest)
* Os componentes devem possuir testes unitários dentro da pasta `tests/components/`. A maioria segue correspondência 1:1 (ex: `tests/components/MaxInputText.test.ts`), mas agrupamentos temáticos para componentes relacionados/simples são práticas aceitas no projeto (ex.: `LayoutComponents.test.ts`, `DisplayAndTransitions.test.ts`, `IconsAndLoaders.test.ts`).
* **Configuração dos Testes**:
  - `tests/setup.ts` é o mecanismo global: instala Pinia e PrimeVue via `config.global.plugins = [createPinia(), [PrimeVue, { ripple: false }]]`, stuba as diretivas `tooltip`/`maska`, e mocka `localStorage`, `getComputedStyle` (vars CSS), `fetch`, `indexedDB` e `virtual:uno.css`.
  - `vitest.config.ts` referencia esse setup (`setupFiles: ['./tests/setup.ts']`), usa `environment: 'happy-dom'`, `pool: 'forks'` com `singleFork: true`, e define o alias `@maxvue/max-use` → `../MaxUse/src/index.ts`.
  - `setActivePinia(createPinia())` no `beforeEach` é um complemento opcional, usado apenas em testes que instanciam stores diretamente (não é o mecanismo principal de configuração do Pinia).
  - Use `@vue/test-utils` e `happy-dom` para montagem dos componentes.
  - Para rodar um único arquivo: `npx vitest run tests/components/MaxButton.test.ts`.
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
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Testes**: Não envie um novo componente sem testes unitários e sem a suíte Vitest devidamente configurada.
