---
name: core-new-apis
description: Vue 3 reactivity system, lifecycle hooks, and composable patterns
---

# Reactivity, Lifecycle & Composables

## Reactivity

### ref vs shallowRef

```ts
import { ref, shallowRef } from 'vue'

// ref - deep reactivity (tracks nested changes)
const user = ref({ name: 'John', profile: { age: 30 } })
user.value.profile.age = 31  // Triggers reactivity

// shallowRef - only .value assignment triggers reactivity (better performance)
const data = shallowRef({ items: [] })
data.value.items.push('new')  // Does NOT trigger reactivity
data.value = { items: ['new'] }  // Triggers reactivity
```

**Prefer `shallowRef`** for large data structures or when deep reactivity is unnecessary.

### computed

```ts
import { ref, computed } from 'vue'

const count = ref(0)

// Read-only computed
const doubled = computed(() => count.value * 2)

// Writable computed
const plusOne = computed({
  get: () => count.value + 1,
  set: (val) => { count.value = val - 1 }
})
```

### reactive & readonly

```ts
import { reactive, readonly } from 'vue'

const state = reactive({ count: 0, nested: { value: 1 } })
state.count++  // Reactive

const readonlyState = readonly(state)
readonlyState.count++  // Warning, mutation blocked
```

Note: `reactive()` loses reactivity on destructuring. Use `ref()` or `toRefs()`.

## Watchers

### watch

```ts
import { ref, watch } from 'vue'

const count = ref(0)

// Watch single ref
watch(count, (newVal, oldVal) => {
  console.log(`Changed from ${oldVal} to ${newVal}`)
})

// Watch getter
watch(
  () => props.id,
  (id) => fetchData(id),
  { immediate: true }
)

// Watch multiple sources
watch([firstName, lastName], ([first, last]) => {
  fullName.value = `${first} ${last}`
})

// Deep watch with depth limit (Vue 3.5+)
watch(state, callback, { deep: 2 })

// Once (Vue 3.4+)
watch(source, callback, { once: true })
```

### watchEffect

Runs immediately and auto-tracks dependencies.

O conceito central aqui é `onWatcherCleanup` (Vue 3.5+): limpar recursos ao re-executar ou desmontar. No engeapp a requisição em si vai por `apiGetRoute` (nome de rota Ziggy) ou store MaxPinia, nunca `fetch('/api/...')`.

```ts
import { ref, watchEffect, onWatcherCleanup } from 'vue'
import { apiGetRoute } from '@maxvue/max-use'

const id = ref(1)

watchEffect(async () => {
  let cancelado = false
  // Limpa ao re-executar ou desmontar (Vue 3.5+)
  onWatcherCleanup(() => { cancelado = true })

  const res = await apiGetRoute('project.station.elements', { station_id: id.value })
  if (!cancelado) data.value = res
})

// Pause/resume (Vue 3.5+)
const { pause, resume, stop } = watchEffect(() => {})
pause()
resume()
stop()
```

### Flush Timing

```ts
// 'pre' (default) - before component update
// 'post' - after component update (access updated DOM)
// 'sync' - immediate, use with caution

watch(source, callback, { flush: 'post' })
watchPostEffect(() => {})  // Alias for flush: 'post'
```

## Lifecycle Hooks

```ts
import {
  onBeforeMount,
  onMounted,
  onBeforeUpdate,
  onUpdated,
  onBeforeUnmount,
  onUnmounted,
  onErrorCaptured,
  onActivated,      // KeepAlive
  onDeactivated,    // KeepAlive
  onServerPrefetch  // SSR only
} from 'vue'

onMounted(() => {
  console.log('DOM is ready')
})

onUnmounted(() => {
  // Cleanup timers, listeners, etc.
})

// Error boundary
onErrorCaptured((err, instance, info) => {
  console.error(err)
  return false  // Stop propagation
})
```

## Effect Scope

Group reactive effects for batch disposal.

```ts
import { effectScope, onScopeDispose } from 'vue'

const scope = effectScope()

scope.run(() => {
  const count = ref(0)
  const doubled = computed(() => count.value * 2)
  
  watch(count, () => console.log(count.value))
  
  // Cleanup when scope stops
  onScopeDispose(() => {
    console.log('Scope disposed')
  })
})

// Dispose all effects
scope.stop()
```

## Composables

Composables are functions that encapsulate stateful logic using Composition API.

### Naming Convention

- Start with `use`: `useMouse`, `useFetch`, `useCounter`

> No engeapp NÃO reescreva composables utilitários já existentes no `@maxvue/max-use` (ele encapsula o VueUse). Para mouse/pointer, DOM, datas etc. importe do MaxUse — ex.: `useMouseInElement` é usado em `resources/Vue/Sections/Dashboard/Sections/DataTable/ListCardItem.vue`. Escreva composables próprios apenas para lógica de domínio que não existe no MaxUse.

```ts
// Prefira o MaxUse a reimplementar listeners de mouse à mão
import { useMouseInElement } from '@maxvue/max-use'
const { isOutside } = useMouseInElement(cardElement)
```

### Pattern (para lógica de domínio própria)

```ts
// composables/useContador.ts — exemplo de lógica que não vem do MaxUse
import { ref } from 'vue'

export function useContador(inicial = 0) {
  const count = ref(inicial)
  const increment = () => count.value++
  const reset = () => { count.value = inicial }

  return { count, increment, reset }
}
```

### Accept Reactive Input

Use `toValue()` (Vue 3.3+) para normalizar refs, getters ou valores simples num composable de domínio.

> NÃO escreva um `useFetch` caseiro no engeapp. Data-fetching é responsabilidade das stores MaxPinia (todo GET) e de `apiGetRoute`/`apiPostRoute` do `@maxvue/max-use` — veja as skills `vue-pinia-state-management-best-practices` e `vue-max-use-usecachedapi-state-cache-best-practices`. O exemplo abaixo mostra apenas o padrão `toValue`/`MaybeRefOrGetter` com um parâmetro reativo qualquer.

```ts
import { computed, toValue, type MaybeRefOrGetter } from 'vue'

// Aceita ref, getter ou valor simples e normaliza com toValue
export function usePrecoFormatado(valor: MaybeRefOrGetter<number>) {
  return computed(() => toValue(valor).toLocaleString('pt-BR', {
    style: 'currency', currency: 'BRL',
  }))
}

// Usos — todos funcionam:
usePrecoFormatado(10)
usePrecoFormatado(valorRef)
usePrecoFormatado(() => props.total)
```

### Return Refs (Not Reactive)

Always return plain object with refs for destructuring compatibility.

```ts
// Good - preserves reactivity when destructured
return { x, y }

// Bad - loses reactivity when destructured
return reactive({ x, y })
```

<!--
Source references:
- https://vuejs.org/api/reactivity-core.html
- https://vuejs.org/api/reactivity-advanced.html
- https://vuejs.org/api/composition-api-lifecycle.html
- https://vuejs.org/guide/reusability/composables.html
-->
