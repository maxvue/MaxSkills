// wiring/router.ts
// Registro da rota da tela de login no Vue Router (sem Inertia).

import { createRouter, createWebHistory } from 'vue-router'
import Login from '../pages/Login.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: Login, meta: { guest: true } },
    {
      path: '/',
      name: 'dashboard',
      component: () => import('../pages/Dashboard.vue'),
      meta: { requiresAuth: true },
    },
  ],
})
