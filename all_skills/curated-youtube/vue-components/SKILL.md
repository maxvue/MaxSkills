---
name: vue-components
description: "Author modular Vue 3 Single File Components using Composition API, script setup, typed props, emits, and slots. Use when creating reactive UI widgets, form controls, and accessible component architectures in Vue 3."
risk: safe
source: curated-youtube
---
# Vue 3 Component Architecture Guidelines

## When to Use
- Developing modern Vue 3 Single File Components (SFC) with `<script setup lang="ts">`.
- Defining type-safe component contracts with `defineProps`, `defineEmits`, and `defineSlots`.
- Managing scoped reactive state, computed properties, and lifecycle hooks.

## SFC Architecture Pattern

```vue
<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  title: string
  modelValue?: string
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  disabled: false
})

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'submit', payload: { value: string }): void
}>()

const inputRef = ref<HTMLInputElement | null>(null)
const characterCount = computed(() => props.modelValue.length)

function onInput(event: Event) {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

function handleAction() {
  if (props.disabled) return
  emit('submit', { value: props.modelValue })
}
</script>

<template>
  <div class="custom-card" :class="{ 'is-disabled': disabled }">
    <header class="card-header">
      <h3 class="card-title">{{ title }}</h3>
      <span class="badge">{{ characterCount }} caracteres</span>
    </header>

    <div class="card-body">
      <input
        ref="inputRef"
        type="text"
        :value="modelValue"
        :disabled="disabled"
        class="input-control"
        @input="onInput"
      />
    </div>

    <footer class="card-footer">
      <button :disabled="disabled" class="btn-primary" @click="handleAction">
        Confirmar
      </button>
    </footer>
  </div>
</template>

<style lang="scss" scoped>
.custom-card {
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  padding: 1rem;

  &.is-disabled {
    opacity: 0.6;
    pointer-events: none;
  }
}
</style>
```
