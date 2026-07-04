---
name: vue-code-generators-best-practices
description: Use when creating, modifying, or reviewing Vue 3 Single-File Components (.vue files), composables, API services, or Pinia stores within the Engeapp project or MaxComponentsUi library. Triggers on requests to create UI components, extract reactive state, integrate backend endpoints, or set up client-side state caching.
---

# Geradores de Código do Vue & Boas Práticas

## Objetivo
Estabelecer diretrizes padronizadas e otimizadas para a criação de componentes, composables, serviços de API e stores do Pinia do Vue 3 no projeto Maxdmin. Garantir a consistência do código, tipagem forte com TypeScript e integração perfeita com as bibliotecas MaxComponentsUi, MaxUse e `@maxvue/max-pinia`.

## Instruções
1. **Requisitos de TypeScript & Composition API:** Toda a lógica deve ser escrita em TypeScript (`lang="ts"`). Sempre use a Composition API (`<script setup>` ou `setup()`). A Options API é estritamente proibida.
2. **Idioma:** Todos os comentários e JSDoc DEVEM ser escritos em português do Brasil (pt-BR).

## Componentes (arquivos .vue)
1. **Ordenação dos Blocos no SFC:**
   - `<template></template>`
   - `<script setup lang="ts"></script>`
   - `<style scoped lang="scss"></style>`
2. **Convenções:**
   - Mantenha os atributos/parâmetros dos componentes em uma única linha (estilo inline) no template.
   - Use `defineProps` e `defineEmits` com interfaces do TypeScript.
   - Use SCSS (`lang="scss"`) para estilos; CSS puro é proibido.
3. **Integração com o Ecossistema:**
   - Dê prioridade a componentes `Max*` para a UI básica (ex: `MaxButton`, `MaxInputText`).
   - Use `@maxvue/max-use` para composables e helpers.
   - Auto-imports: Primitivos do Vue e muitos composables do `MaxUse` são importados automaticamente.

## Composables
1. **Nomenclatura e Estrutura:**
   - Prefixe as funções com `use` (ex: `useRefCached`).
   - Exporte como funções nomeadas.
2. **Definições de Tipos:**
   - Use genéricos `<T>`.
   - Defina explicitamente o tipo de retorno.
   - Use `MaybeRefOrGetter<T>` e resolva com `toValue()` quando aplicável.
3. **Reatividade & Limpeza:**
   - Use `ref`, `computed`, `watch`/`watchEffect`.
   - Limpe efeitos colaterais (event listeners, intervalos) dentro de `onScopeDispose` para evitar vazamentos de memória (memory leaks).

## Serviços de API
1. **Nomenclatura & Localização:**
   - Mantenha em `resources/js/services/` ou caminhos específicos do módulo, com o sufixo `Service.ts` (ex: `UserService.ts`).
2. **Integração:**
   - Use helpers de rotas do `@maxvue/max-use` (ex: `apiGetRoute`, `apiPostRoute`) em vez de chamadas diretas ao Axios.
   - Passe o caminho da rota como string `/api/...` (ou o nome interno registrado no Adonis). **Não existe Ziggy** — é nativo do Laravel e foi descontinuado.
   - **Prefira stores MaxPinia para GETs:** todo GET ao backend deve passar por uma store `@maxvue/max-pinia` (cache + auto-save). A camada `Service` abaixo destina-se a ações não-GET; não crie serviços só para buscar dados que caberiam numa store cacheada.
3. **Tipagem:**
   - Anote os tipos de retorno explicitamente (ex: `Promise<User[] | null>`).
   - Não use `any`. Importe DTOs de `resources/js/types/`.
4. **Consumo:**
   - Chame métodos de serviço a partir de stores do Pinia ou no `script setup` do componente. Nenhuma requisição de rede bruta deve ser feita dentro de stores/componentes.

## Stores do Pinia
1. **Nomenclatura & Localização:**
   - Padrão: arquivo `use{Name}.ts` exportando `use{Name}Store` (ex: `useProject.ts` exporta `useProjectStore`).
   - Insira sob `resources/js/stores/` (minúsculo).
2. **Configuração:**
   - Use `defineStore('project', () => { ... })` com um id plano (ex: `'user'`, `'project'`), condizente com as stores reais.
   - Defina explicitamente o tipo de todos os refs e propriedades computadas.
3. **Integração com `@maxvue/max-pinia`** (anteriormente `piniaWithCache`):
   - `isCached`: `ref(true)`
   - `id`: `computed(() => parent.id ?? null)`
   - `enabled`: `computed(() => id.value !== null)`
   - `data`: `ref<MyType | null>(null)`
   - `options`: Objeto computado onde a rota de GET vive em `options.get.route` (string), ex:
     ```typescript
     const options = computed(() => ({
       get: { route: '/api/...' },
       save: '/api/...',
       enabled,
       key,
     }))
     ```
4. **Overlay de Carregamento (Loading):**
   - Configure `loading_options` (ex: `message` e `target`) para o hook de overlay global.
   - Retorne todas as propriedades, estados e actions no objeto de retorno da setup store.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NUNCA** use a Options API.
- **NUNCA** use CSS puro (simpre use SCSS).
- **NUNCA** quebre tags de componentes do template em várias linhas.
- **NUNCA** escreva comentários ou JSDocs em inglês; sempre em português (pt-BR).
- **NUNCA** faça chamadas brutas ao Axios para dados de página nos componentes/stores; utilize stores `@maxvue/max-pinia` (GET/auto-save) ou os serviços de API abstraídos para ações não-GET. Exceções pontuais como o POST de login (fluxo de auth por sessão+cookie) podem usar a chamada HTTP direta dedicada da camada de autenticação.
