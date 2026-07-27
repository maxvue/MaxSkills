---
title: State Management Strategy
impact: HIGH
impactDescription: Choosing the wrong store pattern can cause brittle mutation flows and poor scaling
type: best-practice
tags: [vue3, state-management, pinia, composables, vueuse]
---

# State Management Strategy

**Impact: HIGH** - Use the lightest state solution that fits the app architecture. O engeapp é uma SPA client-only (`createApp`, sem SSR).

## Task List

- Keep state local first, then promote to shared/global only when needed
- Expose global state as readonly and mutate through explicit actions
- Avoid exporting mutable module-level reactive state directly
- Para qualquer dado que sincroniza com o backend, use uma cached store `@maxvue/max-pinia` (nome de rota Ziggy pontilhado, nunca `/api/...`)

## Choose the Lightest Store Approach

- **Feature composable:** Default for reusable logic with local/feature-level state.
- **`createGlobalState` (via `@maxvue/max-use`):** small client-side global state (UI, carrinho efêmero) que não sincroniza com o backend.
- **Cached store `@maxvue/max-pinia`:** qualquer dado que venha do/vá para o servidor.

## Avoid Exporting Mutable Module State

**BAD:**
```ts
// store/cart.ts
import { reactive } from 'vue'

export const cart = reactive({
  items: [] as Array<{ id: string; qty: number }>
})
```

**GOOD (estado puramente client-side, via `defineStore` em setup store):**
```ts
// stores/cart.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCartStore = defineStore('cart', () => {
  const items = ref<Array<{ id: string; qty: number }>>([])

  function addItem(id: string, qty = 1) {
    const existing = items.value.find((item) => item.id === id)
    if (existing) {
      existing.qty += qty
      return
    }
    items.value.push({ id, qty })
  }

  return { items, addItem }
})
```

> **Stack alvo (EngeApp/Laravel 13 + Vue 3 SPA):** para dados que sincronizam com o backend, o contrato de store é `@maxvue/max-pinia` (cached store). A rota é sempre um **nome de rota Ziggy pontilhado** passado como string — nunca um path `/api/...`. Ex.: `options.get.route = 'client.data'`, `options.save = 'client.save'`. GETs avulsos usam `apiGetRoute('concessionaire.list.all.subsidiaries')` e mutações usam `apiPostRoute(...)`. Use `defineStore` do Pinia puro (acima) apenas para estado puramente client-side (carrinho efêmero, UI); qualquer dado servidor deve trafegar por nome de rota Ziggy via cached store MaxPinia ou `apiGetRoute`/`apiPostRoute`. Detalhes do contrato MaxPinia (`isCached`, `options` com `get.route`/`save`/`key`, `getKey()`) estão na skill `vue-max-stack-frontend-best-practices`.

## Use `createGlobalState` for Small SPA Global State

> Importe `createGlobalState` via `@maxvue/max-use` (não diretamente de `@vueuse/core`): no stack alvo, os utilitários VueUse passam pelo MaxUse.

`createGlobalState` remove o boilerplate de singleton para estado global client-side que não sincroniza com o backend:

```ts
import { createGlobalState } from '@maxvue/max-use'
import { computed, ref } from 'vue'

export const useAuthState = createGlobalState(() => {
  const token = ref<string | null>(null)
  const isAuthenticated = computed(() => token.value !== null)

  function setToken(next: string | null) {
    token.value = next
  }

  return {
    token,
    isAuthenticated,
    setToken
  }
})
```
