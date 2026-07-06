---
name: vue
description: Fundamentos de Vue 3 Composition API (Vue 3.6) no engeapp — script setup, defineProps/defineEmits/defineModel, reatividade, watchers e componentes embutidos (Transition/Teleport/Suspense/KeepAlive). Use ao escrever SFCs. Para fetch/estado/rotas siga MaxPinia + MaxUse (apiGetRoute/Ziggy), não fetch cru.
metadata:
  author: Anthony Fu
  version: "2026.1.31"
  source: Generated from https://github.com/vuejs/docs, scripts at https://github.com/antfu/skills
---

# Vue

> Fundamentos puros de Vue 3. O engeapp usa Vue `^3.6.0-beta.17` (recursos 3.4/3.5 abaixo continuam válidos). Sempre use a Composition API com `<script setup lang="ts">`.

## Preferências

- Prefira TypeScript em vez de JavaScript
- Prefira `<script setup lang="ts">` em vez de `<script>`
- Por desempenho, prefira `shallowRef` em vez de `ref` quando a reatividade profunda não for necessária
- Sempre use a Composition API em vez da Options API
- Desencoraje o Reactive Props Destructure. O código real do engeapp usa `const props = defineProps<{...}>()` e acessa `props.x`; mantenha esse padrão para não quebrar a consistência do projeto.

## Convenções obrigatórias do engeapp (não copie os padrões crus dos exemplos)

Os exemplos das referências abaixo são fundamentos genéricos de Vue. No engeapp, NÃO os use crus:

- **Fetch / estado / rotas:** todo GET passa por uma store MaxPinia (`@maxvue/max-pinia`); nunca faça `fetch()` direto em componente. Chamadas imperativas usam `apiGetRoute`/`apiPostRoute` de `@maxvue/max-use` com **nome de rota Ziggy pontilhado** (ex.: `apiGetRoute('project.station.elements', { station_id })`), nunca strings `'/api/...'`. Ziggy está configurado; o resolvedor é registrado em `resources/app.ts`.
- **Composables utilitários:** não escreva `useMouse`/`useFetch` caseiros nem use `vueuse` cru. Consuma helpers de `@maxvue/max-use` (ex.: `useMouseInElement`, `formatDate`, `hasContent`).
- **Componentes:** não use inputs/botões nativos nem PrimeVue cru; use os `Max*` de `@maxvue/max-components-ui`.
- Comentários de código em pt-BR.

Detalhes do ecossistema Max ficam nas skills dedicadas (`vue-max-stack-frontend-best-practices`, `vue-pinia-state-management-best-practices`, `vue-max-ecosystem-api-reference`). Esta skill cobre só o Vue de base.

## Núcleo

| Tópico | Descrição | Referência |
|-------|-------------|-----------|
| Script Setup & Macros | `<script setup>`, defineProps, defineEmits, defineModel, defineExpose, defineOptions, defineSlots, generics | [script-setup-macros](references/script-setup-macros.md) |
| Reatividade & Ciclo de Vida | ref, shallowRef, computed, watch, watchEffect, effectScope, hooks de ciclo de vida, composables | [core-new-apis](references/core-new-apis.md) |

## Recursos

| Tópico | Descrição | Referência |
|-------|-------------|-----------|
| Componentes e Diretivas Embutidos | Transition, Teleport, Suspense, KeepAlive, v-memo, diretivas customizadas | [advanced-patterns](references/advanced-patterns.md) |

## Referência Rápida

### Template de Componente

```vue
<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps<{
  title: string
  count?: number
}>()

const emit = defineEmits<{
  update: [value: string]
}>()

const model = defineModel<string>()

const doubled = computed(() => (props.count ?? 0) * 2)

watch(() => props.title, (newVal) => {
  console.log('Title changed:', newVal)
})

onMounted(() => {
  console.log('Component mounted')
})
</script>

<template>
  <div>{{ title }} - {{ doubled }}</div>
</template>
```

### Principais Imports

```ts
// Reactivity
import { ref, shallowRef, computed, reactive, readonly, toRef, toRefs, toValue } from 'vue'

// Watchers
import { watch, watchEffect, watchPostEffect, onWatcherCleanup } from 'vue'

// Lifecycle
import { onMounted, onUpdated, onUnmounted, onBeforeMount, onBeforeUpdate, onBeforeUnmount } from 'vue'

// Utilities
import { nextTick, defineComponent, defineAsyncComponent } from 'vue'
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
