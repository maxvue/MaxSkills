---
title: Call Composables Only in Setup Context Synchronously
impact: HIGH
impactDescription: Composables called outside setup context or asynchronously fail to register lifecycle hooks and may cause memory leaks
type: gotcha
tags: [vue3, composables, composition-api, setup, async, lifecycle]
---

# Call Composables Only in Setup Context Synchronously

**Impact: HIGH** - Composables must be called synchronously within `<script setup>`, the `setup()` function, or lifecycle hooks. Calling composables asynchronously (after await), in callbacks, or outside component context prevents Vue from associating lifecycle hooks with the component instance, causing silent failures.

This is critical because composables often register `onMounted` and `onUnmounted` hooks internally. If called in the wrong context, these hooks are never registered, leading to uninitialized state or memory leaks.

## Task Checklist

- [ ] Call all composables at the top level of `<script setup>` or `setup()`
- [ ] Never call composables inside async callbacks, setTimeout, or Promise.then
- [ ] Never call composables conditionally (if/else) - call unconditionally and handle the condition inside
- [ ] Never call composables inside loops - restructure to call once with array data
- [ ] Exception: Composables CAN be called in lifecycle hooks like `onMounted`

**Incorrect:**
```vue
<script setup>
import { useDadosCache } from './composables/useDadosCache'
import { useAuth } from './composables/useAuth'

// WRONG: Composable called after await
const config = await loadConfig()
const { data } = useDadosCache(config.routeName)  // Lifecycle hooks won't register!

// WRONG: Composable called conditionally
if (someCondition) {
  const { user } = useAuth()  // Inconsistent hook registration!
}

// WRONG: Composable called in callback
setTimeout(() => {
  const { data } = useDadosCache('projeto.detalhe')  // No component context!
}, 1000)

// WRONG: Composable called in loop
for (const routeName of routeNames) {
  const { data } = useDadosCache(routeName)  // Creates multiple instances incorrectly
}
</script>
```

**Correct:**
```vue
<script setup>
import { ref, onMounted } from 'vue'
import { apiGetRoute } from '@maxvue/max-use'
import { useDadosCache } from './composables/useDadosCache'
import { useAuth } from './composables/useAuth'

// CORRECT: Call composables synchronously at top level
const { user, isAuthenticated } = useAuth()
const routeName = ref('projeto.detalhe')
const { data, execute } = useDadosCache(routeName)

// Handle async config loading differently
onMounted(async () => {
  const config = await loadConfig()
  routeName.value = config.routeName  // Update the ref, composable reacts
})

// CORRECT: Handle condition inside, not outside
const showUserData = computed(() => isAuthenticated.value && someCondition)

// CORRECT: For multiple routes, use a different pattern.
// No engeapp, GETs vão por store MaxPinia ou apiGetRoute (nome Ziggy pontilhado), nunca fetch cru.
const routeNames = ref(['projeto.lista', 'cliente.lista', 'tarefa.lista'])
const results = ref([])

// Either fetch in onMounted or use a composable designed for arrays
onMounted(async () => {
  results.value = await Promise.all(routeNames.value.map(name => apiGetRoute(name)))
})
</script>
```

## Exception: Calling in Lifecycle Hooks

Composables CAN be called inside lifecycle hooks because Vue maintains the component context:

```vue
<script setup>
import { onMounted } from 'vue'
// No engeapp, composables do VueUse vêm de @maxvue/max-use (reexporta o VueUse), nunca de '@vueuse/core'
import { useEventListener } from '@maxvue/max-use'

// CORRECT: Called in lifecycle hook - component context is available
onMounted(() => {
  // This works because we're still in the component's execution context
  useEventListener(document, 'visibilitychange', handleVisibility)
})
</script>
```

## Special Case: Async Setup in `<script setup>`

Top-level await in `<script setup>` is special - Vue's compiler automatically preserves context:

```vue
<script setup>
import { useDadosCache } from './composables/useDadosCache'

// CORRECT: Top-level await in <script setup> preserves context
// Vue compiler handles this specially
const config = await loadConfig()
const { data } = useDadosCache(config.routeName)  // This works!

// But nested awaits still break context:
async function initLater() {
  await delay(1000)
  const { data } = useDadosCache('projeto.detalhe')  // WRONG: This won't work!
}
</script>
```

## Why This Matters

When you call a composable, Vue needs to know which component instance to associate it with. This association happens through an internal "current instance" that's only set during synchronous setup execution.

```javascript
// Inside a composable
export function useFetch(url) {
  const data = ref(null)

  // These need the current component instance!
  onMounted(() => { /* ... */ })
  onUnmounted(() => { /* cleanup */ })

  // If called outside setup context, Vue can't find the instance
  // and these hooks are silently ignored
  return { data }
}
```

## Reference
- [Vue.js Composables - Usage Restrictions](https://vuejs.org/guide/reusability/composables.html#usage-restrictions)
- [Vue.js Composition API - Setup Context](https://vuejs.org/api/composition-api-setup.html)
