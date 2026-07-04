---
name: vue
description: Vue 3 Composition API, script setup macros, reactivity system, and built-in components. Use when writing Vue SFCs, defineProps/defineEmits/defineModel, watchers, or using Transition/Teleport/Suspense/KeepAlive.
metadata:
  author: Anthony Fu
  version: "2026.1.31"
  source: Generated from https://github.com/vuejs/docs, scripts at https://github.com/antfu/skills
---

# Vue

> Baseado no Vue 3.5. Sempre use a Composition API com `<script setup lang="ts">`.

## Preferências

- Prefira TypeScript em vez de JavaScript
- Prefira `<script setup lang="ts">` em vez de `<script>`
- Por desempenho, prefira `shallowRef` em vez de `ref` quando a reatividade profunda não for necessária
- Sempre use a Composition API em vez da Options API
- Desencoraje o uso do Reactive Props Destructure

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
