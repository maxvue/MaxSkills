// resources/app.ts (bootstrap — wiring obrigatório do Ziggy + MaxUse + Axios)
//
// Sem este wiring, apiPostRoute/apiGetRoute lançam "Route resolver não
// configurado" e a sessão por cookie/CSRF não funciona.

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { ZiggyVue, route } from 'ziggy-js';
import { setRouteResolver } from '@maxvue/max-use';
import MaxComponentsUi from '@maxvue/max-components-ui';
import axios from 'axios';
import App from './App.vue';
import router from '@/Js/router';
import { useUserStore } from '@/Stores/UserStores/useUser.Store';

// 1. MaxUse precisa de um resolver de rotas (Ziggy) para apiGetRoute/apiPostRoute.
//    É isto que faz apiPostRoute('login', ...) virar a URL nomeada correta.
setRouteResolver((name: string, params?: any) => route(name, params));

// 2. Sessão por cookie + CSRF (Sanctum SPA stateful).
axios.defaults.withCredentials = true;
axios.defaults.withXSRFToken = true;

// 3. 401 global -> limpa a store e volta ao login.
axios.interceptors.response.use(
  (r) => r,
  (error) => {
    if (
      error.response?.status === 401 &&
      router.currentRoute.value.name !== 'login'
    ) {
      useUserStore().data = null;
      router.push({ name: 'login' });
    }
    return Promise.reject(error);
  },
);

createApp(App)
  .use(ZiggyVue)
  .use(createPinia())
  .use(MaxComponentsUi)
  .use(router)
  .mount('#app');
