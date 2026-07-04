---
name: vueuse
description: Use when working with VueUse composables - track mouse position with useMouse, manage localStorage with useStorage, detect network status with useNetwork, debounce values with refDebounced, and access browser APIs reactively. Check VueUse before writing custom composables - most patterns already implemented.
license: MIT
---

# VueUse (via MaxUse)

Coleção de utilitários essenciais da Composition API do Vue. Verifique o VueUse antes de escrever composables customizados - a maioria dos padrões já está implementada.

**Versão estável atual:** VueUse 14.x para Vue 3.5+

## Acesso via MaxUse (regra do projeto)

No Engeapp (Vue 3 + Vite + Laravel) **não importe `@vueuse/core` diretamente**. O VueUse é reexportado pelo **MaxUse** (`@maxvue/max-use`), que também expõe o objeto `_` (estilo lodash) e os helpers próprios do projeto. Use os mesmos nomes de composable — apenas troque a fonte:

```ts
// ❌ Nunca
import { useMouse, useLocalStorage } from '@vueuse/core'

// ✅ Sempre (mesmos nomes, fonte MaxUse)
import { useMouse, useLocalStorage } from '@maxvue/max-use'
```

Na prática, o Engeapp registra o MaxUse no `unplugin-auto-import`, então os composables ficam **auto-importados** — na maioria dos componentes você nem escreve o `import` (`useMouse`, `useLocalStorage`, `unrefElement`, `isClient` etc. já estão disponíveis). Se precisar importar explicitamente, importe de `@maxvue/max-use`. Se faltar algo, adicione ao MaxUse encapsulando o VueUse — nunca importe `@vueuse/core` no código de aplicação.

## Categorias

| Categoria  | Exemplos                                                   |
| ---------- | ---------------------------------------------------------- |
| State      | useLocalStorage, useSessionStorage, useRefHistory          |
| Elements   | useElementSize, useIntersectionObserver, useResizeObserver |
| Browser    | useClipboard, useFullscreen, useMediaQuery                 |
| Sensors    | useMouse, useKeyboard, useDeviceOrientation                |
| Network    | useFetch, useWebSocket, useEventSource                     |
| Animation  | useTransition, useInterval, useTimeout                     |
| Component  | useVModel, useVirtualList, useTemplateRefsList             |
| Watch      | watchDebounced, watchThrottled, watchOnce                  |
| Reactivity | createSharedComposable, toRef, toReactive                  |
| Array      | useArrayFilter, useArrayMap, useSorted                     |
| Time       | useDateFormat, useNow, useTimeAgo                          |
| Utilities  | useDebounce, useThrottle, useMemoize                       |

## Referência Rápida

Carregue os arquivos de composables conforme a sua necessidade:

| Trabalhando em...        | Carregue o arquivo                                     |
| ------------------------ | ------------------------------------------------------ |
| Encontrar um composable  | [references/composables.md](references/composables.md) |
| Composable específico    | `composables/<name>.md`                                |

## Carregando Arquivos

**Considere carregar estes arquivos de referência conforme a sua tarefa:**

- [ ] [references/composables.md](references/composables.md) - se estiver procurando composables do VueUse por categoria ou funcionalidade

**NÃO carregue todos os arquivos de uma vez.** Carregue apenas o que for relevante para a sua tarefa atual.

## Padrões Comuns

**Persistência de estado:**

```ts
const state = useLocalStorage('my-key', { count: 0 })
```

**Rastreamento do mouse:**

```ts
const { x, y } = useMouse()
```

**Ref com debounce:**

```ts
const search = ref('')
const debouncedSearch = refDebounced(search, 300)
```

**Composable compartilhado (singleton):**

```ts
const useSharedMouse = createSharedComposable(useMouse)
```

## Guarda de ambiente (`isClient`)

O Engeapp é uma SPA (Vue + Vite + Laravel), sem SSR/Nuxt — os composables rodam no navegador. Ainda assim, ao acessar APIs do navegador em código que pode executar cedo demais, você pode guardar com `isClient` (auto-importado via MaxUse; se importar, use `@maxvue/max-use`):

```ts
import { isClient } from '@maxvue/max-use'

if (isClient) {
  // Código exclusivo do navegador
  const { width } = useWindowSize()
}
```

## Refs de Elementos-Alvo

Ao mirar em refs de componentes em vez de elementos do DOM:

```ts
import type { MaybeElementRef } from '@maxvue/max-use'

// Ref de componente precisa de .$el para obter o elemento do DOM
const compRef = ref<ComponentInstance>()
const { width } = useElementSize(compRef) // ❌ Não vai funcionar

// Use o padrão MaybeElementRef
import { unrefElement } from '@maxvue/max-use'

const el = computed(() => unrefElement(compRef)) // Obtém o .$el
const { width } = useElementSize(el) // ✅ Funciona
```

**Ou acesse `$el` diretamente:**

```ts
const compRef = ref<ComponentInstance>()

onMounted(() => {
  const el = compRef.value?.$el as HTMLElement
  const { width } = useElementSize(el)
})
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill está escrito.
