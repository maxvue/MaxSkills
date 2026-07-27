---
title: Avoid Expensive Operations in Updated Hook
impact: MEDIUM
impactDescription: Heavy computations in updated hook cause performance bottlenecks and potential infinite loops
type: capability
tags: [vue3, vue2, lifecycle, updated, performance, optimization, reactivity]
---

> **Nota engeapp:** exemplos abaixo com `fetch`/`useFetch('/api/...')` são ilustrações genéricas do padrão Vue. No engeapp, todo GET de página vai por store MaxPinia e mutações por `apiPostRoute` (nome Ziggy) — nunca `fetch`/`useFetch` cru. Veja `vue-max-stack-frontend-best-practices`.

# Avoid Expensive Operations in Updated Hook

**Impact: MEDIUM** - The `updated`/`onUpdated` hook runs after every reactive state change that causes a re-render. Placing expensive operations, API calls, or state mutations here can cause severe performance degradation, infinite loops, and dropped frames below the optimal 60fps threshold.

Use `onUpdated` sparingly for post-DOM-update operations that cannot be handled by watchers or computed properties. For most reactive data handling, prefer watchers (`watch`/`watchEffect`) which provide more control over what triggers the callback.

## Task List

- Never perform API calls in `onUpdated`
- Never mutate reactive state inside `onUpdated` (causes infinite loops)
- Use conditional checks to verify updates are relevant before acting
- Prefer `watch` or `watchEffect` for reacting to specific data changes
- Use throttling/debouncing if updated operations are expensive
- Reserve `onUpdated` for low-level DOM synchronization tasks

**BAD:**
```vue
<script setup>
import { ref, onUpdated } from 'vue'

const items = ref([])

// BAD: API call in onUpdated - fires on every re-render
onUpdated(() => {
  fetch('/api/sync', { method: 'POST', body: JSON.stringify(items.value) })
})
</script>
```

```vue
<script setup>
import { ref, onUpdated } from 'vue'

const renderCount = ref(0)

// BAD: state mutation in onUpdated - infinite loop
onUpdated(() => {
  renderCount.value++ // causa outro update, que dispara onUpdated de novo!
})
</script>
```

**GOOD:**
```vue
<!-- GOOD: Composition API with targeted watchers -->
<script setup>
import { ref, watch, onUpdated } from 'vue'
import { useDebounceFn } from '@maxvue/max-use' // no engeapp, VueUse vem reexportado do MaxUse

const items = ref([])
const scrollContainer = ref(null)

// Watch specific data - not all updates
watch(items, (newItems) => {
  syncToServer(newItems)
}, { deep: true })

const syncToServer = useDebounceFn((items) => {
  fetch('/api/sync', { method: 'POST', body: JSON.stringify(items) })
}, 500)

// Only use onUpdated for DOM synchronization
onUpdated(() => {
  // Scroll to bottom only if content changed height
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  }
})
</script>
```

```vue
<!-- GOOD: Conditional check in onUpdated -->
<script setup>
import { ref, onUpdated } from 'vue'
import { useDebounceFn } from '@maxvue/max-use'

const content = ref('')
const lastSyncedContent = ref('')

const syncContent = useDebounceFn(() => {
  // Sync logic
}, 300)

onUpdated(() => {
  // Only act if specific condition is met
  if (content.value !== lastSyncedContent.value) {
    syncContent()
    lastSyncedContent.value = content.value
  }
})
</script>
```

## Valid Use Cases for Updated Hook

```vue
<script setup>
import { onUpdated, nextTick } from 'vue'

// GOOD: Low-level DOM synchronization
onUpdated(() => {
  // Sync third-party library with Vue's DOM
  thirdPartyWidget.refresh()

  // Update scroll position after content change
  nextTick(() => {
    maintainScrollPosition()
  })
})
</script>
```

## Prefer Computed Properties for Derived Data

```vue
<script setup>
import { ref, onUpdated } from 'vue'

const numbers = ref([1, 2, 3, 4, 5])
const sum = ref(0)

// BAD: Calculating derived data in onUpdated
onUpdated(() => {
  sum.value = numbers.value.reduce((a, b) => a + b, 0) // causa outro update!
})
</script>
```

```vue
<script setup>
import { ref, computed } from 'vue'

const numbers = ref([1, 2, 3, 4, 5])

// GOOD: use a computed property instead
const sum = computed(() => numbers.value.reduce((a, b) => a + b, 0))
</script>
```
