# Frontend Vue 3.6 — Login (MaxAuthCard + MaxPinia + Ziggy)

Código de referência do frontend de login do engeapp. Sem Inertia. Vue Router 5, Ziggy 2, MaxPinia (`@maxvue/max-pinia`), MaxUse (`@maxvue/max-use`), MaxComponentsUi (`@maxvue/max-components-ui`), UnoCss + `presetMaxUno`. `apiPostRoute`/`apiGetRoute`/`route` são auto-importados (unplugin-auto-import); componentes Max* são auto-registrados (unplugin-vue-components).

## 1. Página de login

`resources/Vue/Pages/LoginPage.vue` (ou `Sections/Auth/Login.vue`)

```vue
<template>
  <MaxAuthCard title="Maxdmin" subtitle="Acesse sua conta" icon="mdi:shield-account-outline" :loading="login.loading" :error="login.error" v-model:email="login.value" v-model:password="login.password" v-model:remember="login.remember" :providers="login.providers" :register-to="{ name: 'register' }" :forgot-to="{ name: 'password.request' }" @submit="login.submit" @social="login.social" />
</template>

<script setup lang="ts">
  const login = useLoginStore();
  // No mount: carrega os provedores E lê o ?error= deixado pelo redirect social.
  onMounted(() => {
    login.loadProviders();
    login.loadUrlError();
  });
</script>
```

`MaxAuthCard` é puramente visual: emite `submit` (`{ email, password, remember }`) e `social` (`providerId`). Nunca coloque HTTP/store dentro dele.

## 2. Store de login — `useLogin.Store.ts`

`resources/Stores/UserStores/useLogin.Store.ts`

```ts
interface ProviderBtn { id: string; label: string; icon: string; class?: string }

const PROVIDER_MAP: Record<string, Omit<ProviderBtn, 'id'>> = {
  google:   { label: 'Google',   icon: 'mdi:google',   class: 'btn-google' },
  facebook: { label: 'Facebook', icon: 'mdi:facebook', class: 'btn-facebook' },
};

export const useLoginStore = defineStore('login', () => {
  const loading   = ref(false);
  const value     = ref('');            // campo único: e-mail OU telefone
  const method    = ref<'email' | 'phone'>('email');
  const password  = ref('');
  const remember  = ref(true);
  const error     = ref('');
  const providers = ref<ProviderBtn[]>([]);

  // Detecta e-mail vs telefone pelo conteúdo do campo único.
  watch(value, (v) => {
    const onlyDigits = v.replace(/[0-9()\-\s+]/g, '');
    if (v.includes('@') && onlyDigits.length > 0) method.value = 'email';
    else if (onlyDigits.length === 0 && v.length > 0) method.value = 'phone';
  });

  const email        = computed(() => (method.value === 'email' ? value.value : 'undefined@enge.tec.br'));
  const phone_number = computed(() => (method.value === 'phone' ? value.value : ''));

  const submit = async () => {
    if (loading.value) return;
    loading.value = true;
    error.value = '';

    // Login é um POST pontual (transição de auth), não estado de página.
    // apiPostRoute recebe NOME de rota Ziggy e já executa a requisição.
    const result = await apiPostRoute('login', {
      method: method.value,
      email: email.value,
      phone_number: phone_number.value,
      password: password.value,
      remember: remember.value,
    });

    if (result) {
      // Recarrega: o boot reidrata a store useUser e o guard redireciona.
      location.reload();
    } else {
      error.value = 'Usuário ou senha inválidos.';
      setTimeout(() => (error.value = ''), 4000);
    }
    loading.value = false;
  };

  // Login social = navegação total do navegador (não XHR), via Ziggy.
  const social = (provider: string) => {
    window.location.href = route('social.redirect', { provider });
  };

  const loadProviders = async () => {
    const ids: string[] | null = await apiGetRoute('social.providers');
    providers.value = (ids ?? [])
      .filter((id) => PROVIDER_MAP[id])
      .map((id) => ({ id, ...PROVIDER_MAP[id] }));
  };

  // Mensagens exibidas quando o callback social redireciona com ?error=.
  // As CHAVES devem casar 1:1 com os códigos do SocialiteController (invalid_provider,
  // oauth_failed, no_email). Divergir aqui = card silencioso.
  const SOCIAL_ERROR_MESSAGES: Record<string, string> = {
    invalid_provider: 'Provedor de login inválido.',
    oauth_failed:     'Não foi possível autenticar com o provedor. Tente novamente.',
    no_email:         'Sua conta social não forneceu um e-mail. Use e-mail e senha.',
  };

  // Lê ?error= da URL (deixado pelo redirect do backend) e popula error para o card exibir.
  const loadUrlError = () => {
    const code = new URLSearchParams(window.location.search).get('error');
    if (code && SOCIAL_ERROR_MESSAGES[code]) error.value = SOCIAL_ERROR_MESSAGES[code];
  };

  return { loading, value, password, remember, error, providers, submit, social, loadProviders, loadUrlError };
});
```

## 3. Store de usuário (MaxPinia) — `useUser.Store.ts`

`resources/Stores/UserStores/useUser.Store.ts`

```ts
interface User { id: string; name: string; email: string; /* ... */ }

export const useUserStore = defineStore('user', () => {
  const data     = ref<User | null>(null);
  const isCached = ref(true);

  // MaxPinia faz o GET por nome de rota e auto-save ao alterar `data`.
  const options = computed(() => ({
    get:  { route: 'user.data' },   // nome Ziggy
    save: 'user.save',
    key:  'user',
  }));

  // Resolve quando a 1ª busca de sessão concluir COM SUCESSO — evita race no guard ao recarregar.
  // Use is_success (não is_requested): is_requested vira true assim que a requisição é
  // registrada, antes de concluir; só is_success garante que user.data já foi populado.
  function waitRequest(this: any): Promise<void> {
    return new Promise((resolve) => {
      if (this?.status?.server?.get?.is_success) return resolve();
      const stop = watch(
        () => this?.status?.server?.get?.is_success,
        (isSuccess) => { if (isSuccess) { stop(); resolve(); } },
      );
    });
  }

  return { data, isCached, options, waitRequest };
});
```

> Leia o estado SEMPRE pela instância (`userStore.status...`), nunca via `this` fora dos métodos. `status`, `reload()` e `clearAll()` são injetados pelo MaxPinia.

## 4. Guard do Vue Router

`resources/Js/router.ts`

```ts
router.beforeEach(async (to, _from, next) => {
  const user = useUserStore();
  const requiresAuth = to.meta.public ? false : (to.meta.requiresAuth ?? true);

  await user.waitRequest();
  const isAuthenticated = !!user.data?.id;

  if (requiresAuth && !isAuthenticated) return next({ name: 'login' });
  if (to.name === 'login' && isAuthenticated) return next({ name: 'board' });
  next();
});
```

Meta das páginas: login → `{ layout: 'guest', requiresAuth: false }`; protegidas → `{ layout: 'default', requiresAuth: true }`.

## 5. Logout

```ts
const logout = async () => {
  try { await apiPostRoute('logout'); } finally {
    useUserStore().data = null;
    router.push({ name: 'login' });
  }
};
```

## 6. Bootstrap — `resources/app.ts`

```ts
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { ZiggyVue, route } from 'ziggy-js';
import { setRouteResolver } from '@maxvue/max-use';
import MaxComponentsUi from '@maxvue/max-components-ui';
import axios from 'axios';
import App from './App.vue';
import router from '@/Js/router';

// MaxUse precisa de um resolver de rotas (Ziggy) para apiGetRoute/apiPostRoute.
setRouteResolver((name: string, params?: any) => route(name, params));

// Sessão por cookie + CSRF (Sanctum SPA stateful).
axios.defaults.withCredentials = true;
axios.defaults.withXSRFToken = true;

// 401 global → volta ao login.
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
```

## Armadilhas

- Colocar `axios`/`apiPostRoute` dentro do `MaxAuthCard` — ele é visual; a lógica fica na store.
- Buscar `user.data` com `axios.get` em vez da store MaxPinia — quebra cache/auto-save e o `waitRequest` do guard.
- Passar URL crua para `apiPostRoute`/`apiGetRoute` — eles recebem **nome de rota Ziggy**.
- Fazer login social com XHR — é `window.location.href = route('social.redirect', { provider })`.
- Esquecer `setRouteResolver(...)` no boot — `apiGetRoute`/`apiPostRoute` lançam "Route resolver não configurado".
- Checar `user.data?.id` no guard sem `await user.waitRequest()` — race condition no reload da página.
