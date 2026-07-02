---
name: vue-pinia-best-practices
description: "Pinia stores, state management patterns, store setup, and reactivity with stores."
version: 1.0.0
license: MIT
author: github.com/vuejs-ai
---

Pinia best practices, common gotchas, and state management patterns.

> **Target ecosystem — @maxvue/max-pinia (READ FIRST).** As páginas de referência abaixo ensinam a mecânica geral do Pinia (timing de setup, reatividade, gotchas), e essa mecânica continua válida. Porém, no projeto-alvo o GET/salvamento de dados de página **NÃO** é feito com `fetch()`/`axios` manual dentro de actions nem com `createPinia()` puro. Ele flui por **stores cacheadas do `@maxvue/max-pinia`**:
>
> - O plugin é registrado com `createMaxPinia()` (`pinia.use(createMaxPinia({ axios }))`); `createMaxPinia` e `useAsyncStatus` são os **únicos** exports de `@maxvue/max-pinia` (o `defineStore` continua vindo de `'pinia'`).
> - A store adere ao contrato de cache **retornando** do setup: `data` (dados do servidor), `isCached` (`ref(true)` — flag de opt-in que ativa o plugin) e `options` (um `computed`), ex.:
>   ```typescript
>   import { defineStore } from 'pinia'
>
>   export const useUserStore = defineStore('user', () => {
>     const data = ref<UserData | null>(null)
>     const isCached = ref(true)
>     const options = computed(() => ({
>       get: { route: '/api/user' }, // rota STRING '/api/...'; sem Ziggy/route()
>       save: '/api/user',           // rota STRING de save (POST)
>       key: 'user',
>     }))
>     return { data, isCached, options }
>   })
>   ```
> - Com isso o plugin faz **GET automático** (cache localforage → servidor) e **auto-save debounced** (watch em `store.data`, ~300ms). O estado de carregamento é lido em `store.status.server.get.is_success` / `store.is_done`, **não** em `isCached`.
> - `apiGetRoute`/`apiPostRoute` do `@maxvue/max-use` são para requisições avulsas **fora** do fluxo de store cacheada — são assíncronas, resolvem para caminhos string `/api/...` e retornam o payload; não são o mecanismo interno do MaxPinia.
>
> Persistência é responsabilidade do cache localforage do MaxPinia — **não** use `pinia-plugin-persistedstate`.

### Store Setup
- Getting "getActivePinia was called" error at startup → See [pinia-no-active-pinia-error](reference/pinia-no-active-pinia-error.md)
- Setup stores missing state in DevTools or SSR → See [pinia-setup-store-return-all-state](reference/pinia-setup-store-return-all-state.md)

### Reactivity
- Store destructuring stops updating UI reactively → See [pinia-store-destructuring-breaks-reactivity](reference/pinia-store-destructuring-breaks-reactivity.md)
- Store methods lose context in template calls → See [store-method-binding-parentheses](reference/store-method-binding-parentheses.md)

### State Patterns
- Filters reset on refresh or can't be shared → See [state-url-for-ephemeral-filters](reference/state-url-for-ephemeral-filters.md)
- Building production app without DevTools or conventions → See [state-use-pinia-for-large-apps](reference/state-use-pinia-for-large-apps.md)

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
