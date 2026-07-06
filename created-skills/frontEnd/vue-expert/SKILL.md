---
name: vue-expert
description: "Use when creating or editing Vue 3.6 components, pages, composables, cached Pinia stores, vue-router routes or styles in the Maxdmin front-end. Builds Composition API SFCs (script setup lang=ts), wires @maxvue/max-pinia cached stores to Laravel named (Ziggy) API routes, composes UI from MaxComponentsUi, and styles with UnoCSS attributify (presetMaxUno). Covers SFC, state and styling conventions."
license: MIT
metadata:
  version: "2.0.0"
  domain: frontend
  triggers: Vue 3, Vue 3.6, Composition API, script setup, ref, reactive, computed, watch, vue-router, MaxPinia, max-pinia, cached store, MaxComponentsUi, MaxButton, MaxUse, UnoCSS, presetMaxUno, attributify, apiGetRoute, apiPostRoute, Laravel API, Reverb, laravel/ai
  role: specialist
  scope: implementation
  output-format: code
  related-skills: vue-max-stack-frontend-best-practices, vue-max-ecosystem-api-reference, vue-unocss-styling-best-practices, vue-typescript-best-practices
---

# Vue Expert

Especialista sênior em Vue 3 para o front-end do **Maxdmin** (backend Laravel 13 sobre MySQL). Domínio profundo do sistema de reatividade da Composition API e do ecossistema Max local: **@maxvue/max-pinia** (stores cacheadas), **@maxvue/max-components-ui** (componentes `Max*`), **@maxvue/max-use** (composables/rotas) e **UnoCSS** (`presetMaxUno`, attributify).

Stack-alvo: **Vue 3.6 + vue-router 5**, sem Nuxt, sem SSR. Dados vêm do Laravel (Eloquent) via **nomes de rota (Ziggy)** — ex.: `'user.data'` — roteados por stores cacheadas (o helper resolve o nome para a URL `/api/...`). Realtime via **Laravel Reverb + `@laravel/echo-vue`**; IA via **`laravel/ai`** (Gemini via `google-gemini-php/laravel`).

## Fluxo de Trabalho Principal

1. **Analisar requisitos** - Identificar a hierarquia de componentes, necessidades de estado e roteamento
2. **Projetar a arquitetura** - Planejar composables, stores cacheadas (max-pinia) e componentes `Max*`
3. **Implementar** - Construir componentes com `<script setup lang="ts">`, reatividade correta e UnoCSS attributify
4. **Validar** - Rodar `vue-tsc --noEmit` para erros de tipo; verificar a reatividade com o Vue DevTools. Se forem encontrados erros de tipo: corrija cada problema e rode `vue-tsc --noEmit` novamente até que a saída esteja limpa antes de prosseguir
5. **Otimizar** - Minimizar re-renderizações, otimizar computed properties, fazer lazy load
6. **Testar** - Escrever testes de componente com Vue Test Utils e Vitest. Se os testes falharem: inspecione a saída da falha, identifique se a causa raiz é um bug do componente ou uma asserção de teste incorreta, corrija de acordo e rode novamente até que todos os testes passem

## Guia de Referência

Carregue orientações detalhadas conforme o contexto:

| Tópico | Referência | Carregar Quando |
|-------|-----------|-----------|
| Composition API | `references/composition-api.md` | ref, reactive, computed, watch, lifecycle |
| Componentes | `references/components.md` | Props, emits, slots, provide/inject, MaxComponentsUi |
| Gerenciamento de Estado | `references/state-management.md` | stores cacheadas @maxvue/max-pinia, GET/save via nome de rota (Ziggy) |
| TypeScript | `references/typescript.md` | Tipagem de props, componentes genéricos, stores type-safe |
| Build Tooling | `references/build-tooling.md` | Config do Vite, presets do UnoCSS, sourcemaps, bundling |

## Exemplo Rápido

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

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
### DEVE FAZER
- Usar a Composition API (NÃO a Options API) com `<script setup lang="ts">`
- Usar props type-safe com TypeScript
- Usar `ref()` para primitivos, `reactive()` para objetos
- Usar `computed()` para estado derivado
- Usar os lifecycle hooks corretos (onMounted, onUnmounted, etc.)
- Implementar a limpeza (cleanup) adequada em composables
- Rotear **todo GET** de dados por uma store **@maxvue/max-pinia** cacheada (`isCached` + `options.get.route` com o **nome da rota (Ziggy)**, ex.: `'user.data'`)
- Usar helpers de rota do `@maxvue/max-use` (`apiGetRoute`/`apiPostRoute`/`apiPutRoute`/`apiDeleteRoute`) para mutações — nunca `fetch()`/`axios.get` cru em componentes/actions
- Usar componentes `Max*` da MaxComponentsUi no lugar de qualquer controle HTML nativo (`MaxButton`, `MaxInputText`, `MaxInputSelect`…)
- Usar composables/utilitários do `@maxvue/max-use` (nunca importar `@vueuse/core` ou `lodash` direto)
- Estilizar com UnoCSS attributify (`presetMaxUno`) + tokens de tema, atributos inline; usar `<div>` (nunca `<section>`)

### NÃO DEVE FAZER
- Usar a Options API (data, methods, computed como objeto)
- Misturar a Composition API com a Options API
- Mutar props diretamente
- Criar objetos reativos desnecessariamente
- Usar watch quando computed for suficiente
- Esquecer de limpar watchers e effects
- Acessar o DOM antes de onMounted
- Usar `pinia` cru (`defineStore` de `'pinia'` com sintaxe de objeto, `createPinia`, `storeToRefs` de `pinia`, `pinia-plugin-persistedstate`) — o stack usa `@maxvue/max-pinia` (setup-style, cacheado)
- Usar `fetch()`/`axios.get` cru em actions ou componentes para buscar dados
- Usar `<button>`/`<input>`/`<select>`/`<textarea>`/checkbox nativos em código de aplicação
- Escrever SCSS/CSS à mão para layout que o UnoCSS resolve; usar `<section>`
- Usar Nuxt, SSR ou um ORM de Node (Prisma) — o backend é Laravel/Eloquent. (O Ziggy existe e é usado: as rotas são passadas como **nome** — ex.: `'user.data'` — e os helpers do MaxUse resolvem internamente via `route()` para a URL `/api/...`; você não chama `route()` direto no código de app.)

## Templates de Saída

Ao implementar funcionalidades Vue, forneça:
1. Arquivo de componente com `<script setup lang="ts">`, componentes `Max*` e UnoCSS attributify
2. Composable, se houver lógica reutilizável
3. Store cacheada (`@maxvue/max-pinia`), se forem necessários dados globais/de página
4. Breve explicação das decisões de reatividade

## Referência de Conhecimento

Vue 3.6 Composition API, vue-router 5, @maxvue/max-pinia (stores cacheadas), @maxvue/max-components-ui, @maxvue/max-use, UnoCSS (presetMaxUno/attributify), Vite, TypeScript, Vitest, Vue Test Utils, Laravel Eloquent API (`/api/...`), Laravel Reverb + @laravel/echo-vue (realtime), laravel/ai, programação reativa, otimização de performance
