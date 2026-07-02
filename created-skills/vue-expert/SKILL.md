---
name: vue-expert
description: Builds Vue 3.6 components with Composition API (`<script setup lang="ts">`), wires them to @maxvue/max-pinia cached stores that fetch/persist data through AdonisJS `/api/...` string routes, composes UI from MaxComponentsUi components, and styles with UnoCSS attributify (presetMaxUno). Use when creating or editing Vue 3 components, pages, composables, cached Pinia stores, vue-router routes or styles in the Maxdmin front-end; consuming the AdonisJS Lucid API; or deciding SFC, state, component and styling conventions.
license: MIT
metadata:
  version: "2.0.0"
  domain: frontend
  triggers: Vue 3, Vue 3.6, Composition API, script setup, ref, reactive, computed, watch, vue-router, MaxPinia, max-pinia, cached store, MaxComponentsUi, MaxButton, MaxUse, UnoCSS, presetMaxUno, attributify, apiGetRoute, apiPostRoute, AdonisJS API, Transmit, Vercel AI SDK
  role: specialist
  scope: implementation
  output-format: code
  related-skills: vue-max-stack-frontend-best-practices, vue-max-ecosystem-api-reference, vue-unocss-styling-best-practices, typescript-best-practices
---

# Vue Expert

Especialista sênior em Vue 3 para o front-end do **Maxdmin** (backend AdonisJS v6 sobre PostgreSQL). Domínio profundo do sistema de reatividade da Composition API e do ecossistema Max local: **@maxvue/max-pinia** (stores cacheadas), **@maxvue/max-components-ui** (componentes `Max*`), **@maxvue/max-use** (composables/rotas) e **UnoCSS** (`presetMaxUno`, attributify).

Stack-alvo: **Vue 3.6 + vue-router 5**, sem Nuxt, sem SSR/Fastify. Dados vêm do AdonisJS via caminhos string `/api/...` roteados por stores cacheadas. Realtime via **Transmit**; IA via **Vercel AI SDK**.

## Core Workflow

1. **Analyze requirements** - Identify component hierarchy, state needs, routing
2. **Design architecture** - Plan composables, cached stores (max-pinia) e componentes `Max*`
3. **Implement** - Build components with `<script setup lang="ts">`, reatividade correta e UnoCSS attributify
4. **Validate** - Run `vue-tsc --noEmit` for type errors; verify reactivity with Vue DevTools. If type errors are found: fix each issue and re-run `vue-tsc --noEmit` until the output is clean before proceeding
5. **Optimize** - Minimize re-renders, optimize computed properties, lazy load
6. **Test** - Write component tests with Vue Test Utils and Vitest. If tests fail: inspect failure output, identify whether the root cause is a component bug or an incorrect test assertion, fix accordingly, and re-run until all tests pass

## Reference Guide

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Composition API | `references/composition-api.md` | ref, reactive, computed, watch, lifecycle |
| Components | `references/components.md` | Props, emits, slots, provide/inject, MaxComponentsUi |
| State Management | `references/state-management.md` | @maxvue/max-pinia cached stores, GET/save via `/api/...` |
| TypeScript | `references/typescript.md` | Typing props, generic components, type-safe stores |
| Build Tooling | `references/build-tooling.md` | Vite config, UnoCSS presets, sourcemaps, bundling |

## Quick Example

Componente mínimo demonstrando os padrões preferidos — dados via store cacheada, botão `MaxButton`, UnoCSS attributify:

```vue
<template>
    <div class="counter" flex items-center gap-2>
        <span text-default>Contagem: {{ count }} (dobro: {{ doubled }})</span>
        <MaxButton label="Incrementar" icon="mdi:plus" @click="increment" />
    </div>
</template>

<script setup lang="ts">
    // ref/computed são auto-importados no projeto — confira auto-imports.d.ts antes de reimportar.
    import { ref, computed } from 'vue';

    const props = defineProps<{ initialCount?: number }>();

    const count = ref(props.initialCount ?? 0);
    const doubled = computed(() => count.value * 2);

    function increment(): void {
        count.value++;
    }
</script>
```

## Constraints

- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
### MUST DO
- Use Composition API (NOT Options API) com `<script setup lang="ts">`
- Use type-safe props with TypeScript
- Use `ref()` for primitives, `reactive()` for objects
- Use `computed()` for derived state
- Use proper lifecycle hooks (onMounted, onUnmounted, etc.)
- Implement proper cleanup in composables
- Rotear **todo GET** de dados por uma store **@maxvue/max-pinia** cacheada (`isCached` + `options.get.route` com path `/api/...`)
- Usar helpers de rota do `@maxvue/max-use` (`apiGetRoute`/`apiPostRoute`/`apiPutRoute`/`apiDeleteRoute`) para mutações — nunca `fetch()`/`axios.get` cru em componentes/actions
- Usar componentes `Max*` da MaxComponentsUi no lugar de qualquer controle HTML nativo (`MaxButton`, `MaxInputText`, `MaxInputSelect`…)
- Usar composables/utilitários do `@maxvue/max-use` (nunca importar `@vueuse/core` ou `lodash` direto)
- Estilizar com UnoCSS attributify (`presetMaxUno`) + tokens de tema, atributos inline; usar `<div>` (nunca `<section>`)

### MUST NOT DO
- Use Options API (data, methods, computed as object)
- Mix Composition API with Options API
- Mutate props directly
- Create reactive objects unnecessarily
- Use watch when computed is sufficient
- Forget to cleanup watchers and effects
- Access DOM before onMounted
- Usar `pinia` cru (`defineStore` de `'pinia'` com sintaxe de objeto, `createPinia`, `storeToRefs` de `pinia`, `pinia-plugin-persistedstate`) — o stack usa `@maxvue/max-pinia` (setup-style, cacheado)
- Usar `fetch()`/`axios.get` cru em actions ou componentes para buscar dados
- Usar `<button>`/`<input>`/`<select>`/`<textarea>`/checkbox nativos em código de aplicação
- Escrever SCSS/CSS à mão para layout que o UnoCSS resolve; usar `<section>`
- Usar Ziggy/`route()` (não existem no alvo Adonis), Nuxt, SSR/Fastify ou Prisma

## Output Templates

When implementing Vue features, provide:
1. Component file with `<script setup lang="ts">`, componentes `Max*` e UnoCSS attributify
2. Composable if reusable logic exists
3. Cached store (`@maxvue/max-pinia`) if global/page data is needed
4. Brief explanation of reactivity decisions

## Knowledge Reference

Vue 3.6 Composition API, vue-router 5, @maxvue/max-pinia (cached stores), @maxvue/max-components-ui, @maxvue/max-use, UnoCSS (presetMaxUno/attributify), Vite, TypeScript, Vitest, Vue Test Utils, AdonisJS Lucid API (`/api/...`), Transmit (realtime), Vercel AI SDK, reactive programming, performance optimization
