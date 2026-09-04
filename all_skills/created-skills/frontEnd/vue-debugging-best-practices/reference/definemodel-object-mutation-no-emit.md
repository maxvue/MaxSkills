---
title: defineModel Object Mutation — Deep-Watched in 3.4+, but the Parent Must Own a Reactive Object
impact: HIGH
impactDescription: The real caveat isn't that mutations don't emit — in 3.4+ they do (deep-watched); it's that the parent must own/pass a reactive object for the round-trip to hold
type: gotcha
tags: [vue3, v-model, defineModel, objects, reactivity, two-way-binding]
---

# defineModel Object Mutation — Deep-Watched in 3.4+, but the Parent Must Own a Reactive Object

**Impact: HIGH** - In Vue 3.4+, `defineModel()` **deep-watches** its local value, so mutating a nested property like `model.value.prop = x` **DOES** emit `update:modelValue`. The old claim that in-place mutation "never emits" is wrong for 3.4+.

The real caveat: the round-trip only holds if the **parent owns/passes a reactive object**. If the parent binds a plain (non-reactive) object, or doesn't persist the emitted value back, the child's mutation won't be reflected — the sync failure is on the parent side, not because the emit was skipped.

Replacing the whole reference is still valid **defensive** practice (clearer intent, avoids relying on deep-watch semantics, and works identically across setups), but it is no longer required to trigger the emit.

## Task Checklist

- [ ] Ensure the parent passes/owns a **reactive** object (e.g. from `ref`/`reactive`) to `v-model`
- [ ] Prefer replacing the reference when you want explicit, version-agnostic emits: `model.value = {...model.value, prop: x}`
- [ ] For arrays, spread or slice when replacing: `model.value = [...model.value, newItem]`
- [ ] Know that in 3.4+ deep mutation (`model.value.prop = x`) also emits — the deep watcher covers it
- [ ] Consider structuredClone for deeply nested objects when you need a clean detached copy

**Fragile - relies on parent owning a reactive object:**
```vue
<script setup>
// Child component with object v-model
const model = defineModel<{ name: string; age: number }>()

function updateName(newName: string) {
  // In Vue 3.4+ this DOES emit update:modelValue (deep watch),
  // but only round-trips if the parent passes/owns a reactive object.
  model.value.name = newName
}

function addToList() {
  // Same: push is deep-watched in 3.4+, yet depends on the parent's binding.
  model.value.items.push('new item')
}
</script>
```

**Correct - Replace object reference to trigger event:**
```vue
<script setup>
const model = defineModel<{ name: string; age: number }>()

function updateName(newName: string) {
  // CORRECT: Create new object reference
  // This triggers update:modelValue event to parent
  model.value = {
    ...model.value,
    name: newName
  }
}

function addToList() {
  // CORRECT: Create new array reference
  model.value = {
    ...model.value,
    items: [...model.value.items, 'new item']
  }
}
</script>
```

## Deep Nesting Requires Full Path Replacement

```vue
<script setup>
const model = defineModel<{
  user: {
    address: {
      city: string
    }
  }
}>()

// WRONG: Deep mutation
model.value.user.address.city = 'New York'

// CORRECT: Replace entire chain
model.value = {
  ...model.value,
  user: {
    ...model.value.user,
    address: {
      ...model.value.user.address,
      city: 'New York'
    }
  }
}

// ALTERNATIVE: Use structuredClone for complex updates
function updateCity(city: string) {
  const updated = structuredClone(model.value)
  updated.user.address.city = city
  model.value = updated  // New reference triggers event
}
</script>
```

## Race Condition Warning with Spread Operator

When multiple updates occur rapidly, earlier changes can be lost:

```vue
<script setup>
const model = defineModel<{ a: string; b: string }>()

// CAUTION: Race condition if called in same tick
function updateBothWrong() {
  model.value = { ...model.value, a: 'new-a' }  // First update
  model.value = { ...model.value, b: 'new-b' }  // May use stale model.value!
}

// CORRECT: Batch updates into single assignment
function updateBothCorrect() {
  model.value = {
    ...model.value,
    a: 'new-a',
    b: 'new-b'
  }
}
</script>
```

## Alternative: useVModel with Deep Option

Para objetos complexos, considere `useVModel`. No engeapp ele vem de `@maxvue/max-use` (reexporta o VueUse), nunca de `@vueuse/core`:

```vue
<script setup>
import { useVModel } from '@maxvue/max-use'

const props = defineProps<{ modelValue: { name: string } }>()
const emit = defineEmits(['update:modelValue'])

// Deep tracking with passive updates
const model = useVModel(props, 'modelValue', emit, { deep: true, passive: true })

// Now direct mutations work
model.value.name = 'New Name'  // Properly syncs with parent
</script>
```

## Reference
- [Vue.js Component v-model](https://vuejs.org/guide/components/v-model.html)
- [GitHub Discussion: defineModel with objects](https://github.com/orgs/vuejs/discussions/10538)
- [SIMPL Engineering: Vue defineModel Pitfalls](https://engineering.simpl.de/post/vue_definemodel/)
