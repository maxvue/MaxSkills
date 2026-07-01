// resources/Js/router.ts (trecho de wiring do guard)
//
// O guard lê a store MaxPinia useUserStore para decidir o acesso. Sempre
// `await user.waitRequest()` antes de checar `user.data?.id` — senão há race
// condition no reload da página (a sessão ainda não terminou de carregar).

import { createRouter, createWebHistory } from 'vue-router';
import { useUserStore } from '@/Stores/UserStores/useUser.Store';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // Login: página de convidado, não exige auth.
    {
      path: '/login',
      name: 'login',
      component: () => import('@/Vue/Pages/LoginPage.vue'),
      meta: { layout: 'guest', requiresAuth: false },
    },
    // Área autenticada (exemplo).
    {
      path: '/',
      name: 'board',
      component: () => import('@/Vue/Pages/BoardPage.vue'),
      meta: { layout: 'default', requiresAuth: true },
    },
    // ... demais rotas
  ],
});

router.beforeEach(async (to, _from, next) => {
  const user = useUserStore();
  const requiresAuth = to.meta.public ? false : (to.meta.requiresAuth ?? true);

  await user.waitRequest();
  const isAuthenticated = !!user.data?.id;

  if (requiresAuth && !isAuthenticated) return next({ name: 'login' });
  if (to.name === 'login' && isAuthenticated) return next({ name: 'board' });
  next();
});

export default router;
