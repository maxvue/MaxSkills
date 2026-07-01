// resources/Js/router.ts
//
// Vue Router (sem Inertia) + guard de autenticação do engeapp.
//
// O guard usa a store MaxPinia `useUser` como ÚNICA fonte de verdade do "me".
// O detalhe que mata o bug do reload: `await user.waitRequest()` ANTES de checar
// `user.data?.id`. Sem esse await, num F5 a store ainda não terminou o GET de
// `user.data`, então `data` está null e o guard manda para /login mesmo o usuário
// estando logado no backend (a sessão por cookie continua válida).

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { useUserStore } from '@/Stores/UserStores/useUser.Store';

// Cada rota declara sua exigência de auth via meta.
// - public/guest  -> requiresAuth: false  (login, registro, recuperar senha)
// - protegidas     -> requiresAuth: true   (default quando meta não diz nada)
const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/Vue/Pages/LoginPage.vue'),
    meta: { layout: 'guest', requiresAuth: false, public: true },
  },
  {
    path: '/',
    name: 'board',
    component: () => import('@/Vue/Pages/BoardPage.vue'),
    meta: { layout: 'default', requiresAuth: true },
  },
  // ... demais rotas protegidas herdam requiresAuth: true por padrão
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, _from, next) => {
  const user = useUserStore();

  // `public: true` força rota aberta; caso contrário, protegida por padrão.
  const requiresAuth = to.meta.public ? false : ((to.meta.requiresAuth as boolean) ?? true);

  // PONTO-CHAVE contra o bug do reload:
  // espera a 1ª busca de sessão (GET user.data) concluir antes de decidir.
  // Em navegações subsequentes isto resolve na hora (já requisitado).
  await user.waitRequest();

  const isAuthenticated = !!user.data?.id;

  // Rota protegida sem sessão -> manda para o login.
  if (requiresAuth && !isAuthenticated) {
    return next({ name: 'login' });
  }

  // Já logado tentando abrir o login -> manda para a home.
  if (to.name === 'login' && isAuthenticated) {
    return next({ name: 'board' });
  }

  next();
});

export default router;
