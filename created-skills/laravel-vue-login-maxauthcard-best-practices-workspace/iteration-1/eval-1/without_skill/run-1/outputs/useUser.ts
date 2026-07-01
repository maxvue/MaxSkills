// resources/js/Stores/useUser.ts
//
// Store do usuário logado para engeapp (Laravel 13 + Vue Router + MaxPinia + Ziggy).
//
// Esta store segue o contrato @maxvue/max-pinia: declara `data`, `isCached` e
// `options`. O plugin MaxPinia cuida sozinho de:
//   - carregar do cache (localforage) ao montar  -> hidratação otimista
//   - fazer o GET em 'user.data' (rota nomeada Ziggy) para revalidar
//   - expor `status` reativo e `is_done_to_show`
//
// IMPORTANTE: o endpoint 'user.data' (Laravel: GET /api/user/data, no grupo
// auth:sanctum/web) deve responder:
//   - 200 com o JSON do usuário quando autenticado
//   - 401 quando NÃO autenticado
// O 401 é o que permite o guard distinguir "deslogado" de "ainda carregando".

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export interface User {
    id: number
    name: string
    email: string
    email_verified_at: string | null
    // ...demais campos expostos pelo UserResource do Laravel
    roles?: string[]
    permissions?: string[]
}

export const useUser = defineStore('user', () => {
    // `data` é o que o MaxPinia preenche (cache -> servidor).
    // null = sem usuário resolvido ainda OU usuário deslogado (401 limpa).
    const data = ref<User | null>(null)

    // Ativa o plugin MaxPinia nesta store.
    const isCached = ref(true)

    // Contrato MaxPinia. Em Laravel usamos NOMES de rota Ziggy (não strings /api),
    // pois o MaxUse resolve via resolveRoute -> route() do Ziggy.
    const options = computed(() => ({
        get: { route: 'user.data' }, // GET automático + cache + revalidação
        key: 'user', // chave do registro no localforage
        // sem `save`: o usuário logado é read-only no front; nada de auto-POST.
    }))

    // --------- Getters de conveniência (derivados de `data`) ---------

    const user = computed(() => data.value)

    // Logado SOMENTE quando há um usuário de fato resolvido.
    const isLoggedIn = computed(() => data.value !== null)

    const hasRole = (role: string) => computed(() => data.value?.roles?.includes(role) ?? false)

    const can = (permission: string) =>
        computed(() => data.value?.permissions?.includes(permission) ?? false)

    // --------- Ações expostas para o guard ---------
    //
    // O plugin MaxPinia injeta em runtime: `status`, `reload()`, `clearAll()`,
    // `is_done_to_show`, `cancelLoad()`, etc. Eles existem na instância da store,
    // mas não aparecem aqui no setup. O guard usa `(store as any).status` /
    // `(store as any).reload()` — ver router/index.ts. Para tipagem limpa, veja
    // a interface MaxPiniaStore lá.

    // Limpa estado local de usuário (chamar no logout, junto com clearAll do MaxPinia).
    function clearUser() {
        data.value = null
    }

    return {
        // estado/contrato MaxPinia
        data,
        isCached,
        options,
        // getters de app
        user,
        isLoggedIn,
        hasRole,
        can,
        // ações
        clearUser,
    }
})

export type UseUserStore = ReturnType<typeof useUser>
