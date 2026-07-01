// resources/app.ts
//
// Bootstrap da SPA. Sem isto, a store useUser nem consegue buscar o "me":
// o MaxUse precisa de um resolver de rotas (Ziggy) e o Axios precisa mandar o
// cookie de sessão + XSRF (Sanctum SPA stateful).

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { ZiggyVue, route } from 'ziggy-js';
import { setRouteResolver } from '@maxvue/max-use';
import MaxComponentsUi from '@maxvue/max-components-ui';
import axios from 'axios';
import App from './App.vue';
import router from '@/Js/router';
import { useUserStore } from '@/Stores/UserStores/useUser.Store';

// MaxUse resolve `apiGetRoute('user.data')` / `apiPostRoute('login', ...)` por
// NOME de rota Ziggy. Sem registrar o resolver, esses helpers lançam
// "Route resolver não configurado".
setRouteResolver((name: string, params?: any) => route(name, params));

// Sessão por cookie + CSRF (Sanctum SPA stateful):
// o GET de `user.data` só identifica o usuário se o cookie de sessão for enviado.
axios.defaults.withCredentials = true;
axios.defaults.withXSRFToken = true;

// 401 global -> sessão expirou/invalidou: limpa a store e volta ao login.
// Cobre o caso de o cookie morrer enquanto a SPA está aberta.
axios.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response?.status === 401 && router.currentRoute.value.name !== 'login') {
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
