# State Management with @maxvue/max-pinia (cached stores)

> No EngeApp, **todo estado de dados de página passa por uma store cacheada `@maxvue/max-pinia`**. Não use
> `pinia` cru: nada de `defineStore` em sintaxe de objeto, `createPinia` no componente, `storeToRefs` de
> `'pinia'` para dados de servidor, nem `pinia-plugin-persistedstate`. O cache offline (localforage), o GET
> automático ao montar e o auto-save debounced já vêm do plugin `@maxvue/max-pinia`. Nunca faça
> `fetch('/api/...')` ou `axios.get` cru dentro de uma action — o GET é roteado pela camada de cache e as
> mutações usam os helpers `apiPostRoute`/`apiPutRoute`/`apiDeleteRoute` do `@maxvue/max-use`.

## Contrato mínimo de uma store cacheada

Uma store é setup-style (função) e faz opt-in de cache expondo `isCached: ref(true)` mais um `options`
(computed) com a rota de GET. A rota é o **nome da rota (Ziggy)** — ex.: `'user.data'` — que a camada de
cache resolve internamente (via `route()`) para a URL `/api/...`. Ao montar, o plugin dispara o GET
automaticamente e reidrata `data`.

No projeto real, `defineStore`, `ref`, `computed`, `watch` e os helpers `apiPostRoute`/`apiPutRoute`/
`apiDeleteRoute` são auto-importados (config `AutoImport` do Vite) — não os importe nas stores.

```typescript
// resources/Stores/User/useUser.Store.ts
interface User {
    id: number;
    name: string;
    email: string;
    role: 'admin' | 'user';
}

export const useUserStore = defineStore('user', () => {
    // `data` é lido pelo plugin como o estado cacheado. GET automático ao montar.
    const data = ref<User | null>(null);
    const isCached = ref(true);

    // GET automático + cache-first pela camada @maxvue/max-pinia — sem axios.get manual.
    // `save` (opcional) habilita o POST com auto-save debounced (300 ms).
    const options = computed(() => ({
        get: { route: 'user.data' }, // nome de rota (Ziggy); resolve para /api/...
        save: 'user.save',
        key: 'user' // ilustrativo; a chave real é `${$id}.${id|'global'}`
    }));

    // Getters derivados são apenas computed sobre `data`.
    const isAdmin = computed(() => data.value?.role === 'admin');

    return { data, options, isCached, isAdmin };
});
```

O plugin injeta métodos e status reativo na store (não precisam ser declarados): `reload()`,
`saveInServer()`, `saveInCache()`, `clearAll()`, `cancelLoad()`, `status`, `is_done`, `is_done_to_show`,
`countChanges`, `key`. Consulte a skill `vue-max-ecosystem-api-reference` (references/maxpinia.md) para o
contrato completo.

## Consumo no componente

`data` reidrata sozinho; use `status`/`is_done_to_show` para o estado de carga e `reload()` para revalidar.

```vue
<template>
    <div class="user-card" flex flex-col gap-2>
        <MaxLoader v-if="store.status.server.get.is_requesting" label="Carregando..." />
        <template v-else-if="store.is_done_to_show">
            <span text-default>{{ user?.name }}</span>
            <MaxButton label="Recarregar" icon="mdi:refresh" @click="store.reload()" />
        </template>
    </div>
</template>

<script setup lang="ts">
    // defineStore, useXxxStore e storeToRefs são auto-importados no projeto.
    const store = useUserStore();
    // storeToRefs preserva reatividade ao desestruturar o estado da store.
    const { data: user } = storeToRefs(store);
</script>
```

## Auto-save (POST debounced) e mutações explícitas

Quando `options.save` está presente, o plugin observa `data` e faz POST **300 ms** após a última mudança
válida — não escreva `watch` + `setTimeout` manuais. Para mutações explícitas (criar/atualizar/excluir),
use os helpers de rota do `@maxvue/max-use`, que executam a requisição e retornam o payload **diretamente**
(não `{ data }`).

```typescript
// resources/Stores/Todo/useTodo.Store.ts (defineStore/ref/computed/helpers auto-importados)
interface Todo {
    id: number;
    title: string;
    completed: boolean;
}

type TodoFilter = 'all' | 'active' | 'completed';

export const useTodoStore = defineStore('todos', () => {
    const data = ref<Todo[]>([]);
    const isCached = ref(true);
    const filter = ref<TodoFilter>('all');

    // GET automático pela camada de cache; `data` reidrata sozinho ao montar.
    const options = computed(() => ({ get: { route: 'todos.data' }, key: 'todos' }));

    // Getters = computed sobre `data`.
    const filteredTodos = computed(() => {
        switch (filter.value) {
            case 'active':
                return data.value.filter((t) => !t.completed);
            case 'completed':
                return data.value.filter((t) => t.completed);
            default:
                return data.value;
        }
    });

    const completedCount = computed(() => data.value.filter((t) => t.completed).length);

    // Mutações via apiPostRoute/apiDeleteRoute (não fetch/axios cru). Retornam o payload direto.
    async function addTodo(title: string): Promise<Todo> {
        const todo = await apiPostRoute('todos.save', { title, completed: false });
        data.value.push(todo);
        return todo;
    }

    async function toggleTodo(id: number): Promise<void> {
        const todo = data.value.find((t) => t.id === id);
        if (!todo) return;
        // Alterar `data` já dispara o auto-save debounced quando há options.save.
        // Aqui persistimos explicitamente via apiPutRoute para ter a resposta.
        const updated = await apiPutRoute('todos.update', { id, completed: !todo.completed });
        Object.assign(todo, updated);
    }

    async function deleteTodo(id: number): Promise<void> {
        await apiDeleteRoute('todos.delete', { id });
        const index = data.value.findIndex((t) => t.id === id);
        if (index > -1) data.value.splice(index, 1);
    }

    function setFilter(newFilter: TodoFilter): void {
        filter.value = newFilter;
    }

    return {
        data,
        isCached,
        options,
        filter,
        filteredTodos,
        completedCount,
        addTodo,
        toggleTodo,
        deleteTodo,
        setFilter
    };
});
```

## Aguardar a carga em guards de rota

Stores de dados críticos (usuário autenticado) expõem um `waitRequest` baseado no contrato do MaxPinia
(`status.server.get.is_requested`) para que os guards de `vue-router` aguardem antes de redirecionar.

```typescript
// stores/user.ts (trecho)
export const useUserStore = defineStore('user', () => {
    const data = ref<User | null>(null);
    const isCached = ref(true);
    const options = computed(() => ({ get: { route: 'user.data' }, key: 'user' }));

    // Aguarda a carga via contrato MaxPinia (status.server.get.is_requested).
    function waitRequest(this: any): Promise<void> {
        return new Promise((resolve) => {
            if (this?.status?.server?.get?.is_requested) return resolve();
            const unwatch = watch(
                () => this?.status?.server?.get?.is_requested,
                (isRequested) => {
                    if (isRequested) {
                        unwatch();
                        resolve();
                    }
                }
            );
        });
    }

    return { data, isCached, options, waitRequest };
});
```

```typescript
// router.ts (trecho) — aguarda o usuário antes de decidir o redirecionamento.
router.beforeEach(async (to) => {
    const user = useUserStore();
    await user.waitRequest();
    if (to.meta.requiresAuth && !user.data) return { path: '/login' };
});
```

## Acessando outras stores

Uma store cacheada pode consumir outra normalmente (as demais stores também são cacheadas).

```typescript
// resources/Stores/Cart/useCart.Store.ts (defineStore/ref/computed/helpers auto-importados)
interface CartItem {
    productId: number;
    quantity: number;
}

export const useCartStore = defineStore('cart', () => {
    const data = ref<CartItem[]>([]);
    const isCached = ref(true);
    const options = computed(() => ({ get: { route: 'cart.data' }, save: 'cart.save', key: 'cart' }));

    const userStore = useUserStore();
    const productStore = useProductStore();

    const total = computed(() =>
        data.value.reduce((sum, item) => {
            const product = productStore.getProductById(item.productId);
            return sum + (product?.price ?? 0) * item.quantity;
        }, 0)
    );

    function addItem(productId: number, quantity = 1): void {
        const existing = data.value.find((i) => i.productId === productId);
        if (existing) existing.quantity += quantity;
        else data.value.push({ productId, quantity });
        // Alteração de `data` dispara o auto-save debounced (options.save).
    }

    async function checkout(): Promise<void> {
        if (!userStore.data) throw new Error('Usuário precisa estar autenticado para finalizar');
        await apiPostRoute('cart.checkout', { items: data.value, total: total.value });
        data.value = [];
    }

    return { data, isCached, options, total, addItem, checkout };
});
```

## Testando stores cacheadas

Registre o Pinia com o plugin `createMaxPinia` no `beforeEach`. Mocke as chamadas HTTP (helpers de rota do
`@maxvue/max-use`) em vez de testar a rede real.

```typescript
// stores/__tests__/todos.spec.ts
import { setActivePinia, createPinia } from 'pinia';
import { createMaxPinia } from '@maxvue/max-pinia';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useTodoStore } from '../todos';

describe('Todo Store', () => {
    beforeEach(() => {
        const pinia = createPinia();
        pinia.use(createMaxPinia({ cacheName: 'test' }));
        setActivePinia(pinia);
    });

    it('adiciona um todo via apiPostRoute', async () => {
        vi.stubGlobal('apiPostRoute', vi.fn().mockResolvedValue({ id: 1, title: 'A', completed: false }));
        const store = useTodoStore();
        await store.addTodo('A');
        expect(store.data).toHaveLength(1);
        expect(store.completedCount).toBe(0);
    });
});
```

## Quick Reference

| Pattern | Use Case |
|---------|----------|
| `isCached: ref(true)` + `options` | Opt-in de cache do `@maxvue/max-pinia` |
| `options.get.route` (nome de rota Ziggy) | GET automático + cache-first (sem axios.get manual) |
| `options.save` (nome de rota Ziggy) | POST com auto-save debounced (300 ms) |
| `data` (ref) | Estado reidratado pelo plugin |
| `store.reload()` | Revalidar (refaz o GET) |
| `store.saveInServer()` | POST imediato (fora do debounce) |
| `store.status.server.get` | Estado de carga (`is_requesting`/`is_requested`/`is_success`) |
| `store.is_done_to_show` | Pronto para renderizar (cache ou servidor) |
| `apiPostRoute`/`apiPutRoute`/`apiDeleteRoute` | Mutações — retornam o payload direto |
| `storeToRefs(store)` | Preservar reatividade ao desestruturar |
| `waitRequest()` | Guards de rota aguardarem a carga |
| `createMaxPinia(config)` | Registrar o plugin (boot/tests) |
