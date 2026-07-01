// resources/js/router/index.ts
//
// Vue Router para engeapp (Laravel 13 + Ziggy + MaxPinia).
//
// O guard `beforeEach` protege rotas marcadas com `meta.requiresAuth`.
//
// O BUG CLÁSSICO ("ao recarregar, o guard acha que não tá logado"):
//   Numa página recarregada (F5), a store de usuário ainda NÃO resolveu o GET
//   'user.data'. Se o guard lê `useUser().isLoggedIn` SÍNCRONO nesse instante,
//   `data` ainda é null -> o guard redireciona pro login mesmo com sessão válida.
//
// A correção é ESPERAR o usuário ser resolvido antes de decidir. O MaxPinia
// já dispara o GET ao montar a store; nós aguardamos `status.server.get` ficar
// "is_requested" (settled, sucesso OU 401) usando `ensureUserResolved()`.
// Só DEPOIS de settled é que lemos `isLoggedIn`.

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { setLibraryRouter } from '@maxvue/max-use/routes'
import { useUser } from '@/Stores/useUser'

// Forma mínima do status reativo que o plugin MaxPinia injeta na store.
interface MaxPiniaStore {
    status: {
        server: {
            get: {
                is_requested: boolean // já voltou (sucesso ou erro), settled
                is_success: boolean
                is_requesting: boolean
                error: unknown
            }
        }
        cache: { get: { is_success: boolean } }
    }
    is_done_to_show?: boolean
    reload: () => Promise<void> | void
    clearAll: () => Promise<void>
}

const routes: RouteRecordRaw[] = [
    {
        path: '/login',
        name: 'login',
        component: () => import('@/Pages/Auth/Login.vue'),
        meta: { requiresGuest: true },
    },
    {
        path: '/',
        name: 'dashboard',
        component: () => import('@/Pages/Dashboard.vue'),
        meta: { requiresAuth: true },
    },
    {
        path: '/projetos/:id',
        name: 'projects.show',
        component: () => import('@/Pages/Projects/Show.vue'),
        meta: { requiresAuth: true },
    },
    // ...demais rotas
]

const router = createRouter({
    history: createWebHistory(),
    routes,
})

// Necessário para goToRoute()/navegação por nome Ziggy funcionar no MaxUse.
setLibraryRouter(router)

/**
 * Garante que a store de usuário resolveu o GET 'user.data' ao menos uma vez.
 *
 * - Se o GET já está settled (`is_requested`), retorna imediatamente.
 * - Caso contrário (ex.: primeira navegação após F5), dispara/aguarda o reload
 *   e faz polling reativo até `is_requested` virar true (sucesso ou 401).
 *
 * Resultado: o guard NUNCA decide com `data` ainda não resolvido.
 */
let resolveOnce: Promise<void> | null = null

function ensureUserResolved(): Promise<void> {
    const store = useUser() as unknown as MaxPiniaStore

    // Já resolvido nesta sessão de página -> decisão imediata.
    if (store.status?.server?.get?.is_requested) {
        return Promise.resolve()
    }

    // Deduplica: várias rotas concorrentes esperam a MESMA resolução.
    if (resolveOnce) return resolveOnce

    resolveOnce = new Promise<void>((resolve) => {
        // Dispara o GET (MaxPinia já dispara on-mount, mas reload garante).
        Promise.resolve(store.reload()).catch(() => {
            /* 401 etc. são "settled", não erro fatal de fluxo */
        })

        const started = Date.now()
        const TIMEOUT_MS = 8000

        const tick = () => {
            const settled = store.status?.server?.get?.is_requested
            const timedOut = Date.now() - started > TIMEOUT_MS
            if (settled || timedOut) {
                resolveOnce = null // permite re-resolução depois (ex.: novo login)
                resolve()
                return
            }
            // poll curto; o status do MaxPinia é reativo e vira em ms.
            setTimeout(tick, 25)
        }
        tick()
    })

    return resolveOnce
}

router.beforeEach(async (to) => {
    const requiresAuth = to.matched.some((r) => r.meta.requiresAuth)
    const requiresGuest = to.matched.some((r) => r.meta.requiresGuest)

    // Rotas públicas sem restrição de convidado: passa direto.
    if (!requiresAuth && !requiresGuest) return true

    // Espera o usuário ser resolvido ANTES de qualquer decisão.
    // É isto que mata o bug do F5.
    await ensureUserResolved()

    const userStore = useUser()
    const isLoggedIn = userStore.isLoggedIn

    if (requiresAuth && !isLoggedIn) {
        // guarda o destino para redirecionar de volta após o login
        return { name: 'login', query: { redirect: to.fullPath } }
    }

    if (requiresGuest && isLoggedIn) {
        return { name: 'dashboard' }
    }

    return true
})

export default router

// Exporta o helper para reuso (ex.: chamar no logout para forçar re-resolução):
export { ensureUserResolved }
