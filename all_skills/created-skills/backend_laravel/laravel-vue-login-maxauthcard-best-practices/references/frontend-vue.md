# Frontend Vue 3.6 — Login (MaxAuthCard + MaxPinia + Ziggy)

Código de referência do frontend de login do engeapp. Sem Inertia. Vue Router 5, Ziggy 2, MaxPinia (`@maxvue/max-pinia`), MaxUse (`@maxvue/max-use`), MaxComponentsUi (`@maxvue/max-components-ui`), UnoCss + `presetMaxUno`. `apiPostRoute`/`apiGetRoute`/`route` são auto-importados (unplugin-auto-import); componentes Max* são auto-registrados (unplugin-vue-components).

## 1. Página de login

`resources/Vue/Sections/Auth/Login.vue` (montado por `resources/Vue/Pages/LoginPage.vue`, que é só o shell com fundo/footer/transição entre Login/ForgotPassword/RecoveryPassword/Register)

```vue
<template>
  <MaxAuthCard identifier="email-phone" :loading="login.loading" :error="login.error" v-model:email="login.value" v-model:password="login.password" v-model:remember="login.remember" :providers="login.providers" :forgot-to="{ query: { sub_page: 'forgot-password' } }" :register-to="{ query: { sub_page: 'register' } }" @submit="login.submit" @social="login.social">
    <template #header>
      <Logo p />
    </template>
  </MaxAuthCard>
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

`MaxAuthCard` é puramente visual: emite `submit` (`{ email, password, remember }`) e `social` (`providerId`). Nunca coloque HTTP/store dentro dele. `forgot-to`/`register-to` são `RouteLocationRaw` do Vue Router (não nomes Ziggy); o engeapp navega entre as sub-telas de auth por query `sub_page`, já que os nomes de rota do Vue Router vêm de glob de `resources/Vue/Pages/**/*.vue` e não existe página dedicada de recuperação de senha.

**Prop `identifier`** (`'email' | 'email-phone'`, padrão `'email'`) — controla o campo de
identificação. Confirmado em `MaxComponentsUi/src/components/MaxAuthCard.vue`:

- `identifier="email"` → renderiza apenas um input de e-mail.
- `identifier="email-phone"` → renderiza o `MaxInputPhoneMail`, campo **combinado** que aceita
  e-mail OU telefone. É o valor **necessário** para o fluxo "login por e-mail OU telefone"
  que a store `useLogin` implementa (campo único `value` + detecção `email`/`phone`). Sem
  `identifier="email-phone"`, o card só aceita e-mail e o login por telefone fica inacessível.

O v-model `email` do card (mapeado para `login.value`) carrega o valor combinado quando
`identifier="email-phone"`; a store deriva `email`/`phone_number` a partir dele.

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
  const method    = ref('');            // '' | 'email' | 'phone'
  const password  = ref('');
  const remember  = ref(true);
  const error     = ref('');
  const providers = ref<ProviderBtn[]>([]);

  // Detecta e-mail vs telefone pelo conteúdo do campo único.
  watch(value, () => {
    const current = value.value ?? '';
    if (current.includes('@')) method.value = 'email';
    else if (/[0-9]/.test(current)) method.value = 'phone';
    else if (current.length === 0) method.value = '';
  });

  const email        = computed(() => (method.value === 'email' ? value.value : 'undefined@enge.tec.br'));
  const phone_number = computed(() => (method.value === 'phone' ? value.value : ''));

  const submit = async () => {
    loading.value = true;
    error.value = '';

    // Login é um POST pontual (transição de auth), não estado de página.
    // apiPostRoute recebe NOME de rota Ziggy e já executa a requisição.
    const result = await apiPostRoute('login', {
      method: method.value,
      email: email.value,
      password: password.value,
      remember: remember.value,
      phone_number: phone_number.value,
    });

    if (result) {
      // Recarrega: o boot reidrata a store useUser e o guard redireciona.
      location.reload();
    } else {
      // toast (vue3-toastify) além da mensagem exibida no card.
      toast('Não foi possível realizar o login. <br>Verifique os dados e tente novamente.', { type: 'error', dangerouslyHTMLString: true });
      error.value = 'Usuário ou senha inválidos.';
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

  return { email, value, phone_number, method, password, remember, loading, error, submit, providers, loadProviders, social, loadUrlError };
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

## 5. Logout — navegação full-page (GET), NÃO POST via apiPostRoute

O logout real do engeapp **não** é XHR nem `router.push`: é uma navegação full-page do
navegador para `GET /logout`, disparada no menu do usuário
(`resources/Vue/Layouts/PageLayout/TopMenu/UserSection.vue`, ~linha 86). O backend encerra
a sessão (`Auth::guard('web')->logout()` + `session()->invalidate()`) e redireciona; o
recarregamento total já reidrata o estado na tela de login. **Não** reescreva como
`apiPostRoute('logout')` + `router.push` + `clearAll()`.

```ts
// resources/Vue/Layouts/PageLayout/TopMenu/UserSection.vue
const logout = () => {
  window.location.href = '/logout'; // navegação full-page (GET)
};
```

## 6. Bootstrap — `resources/app.ts`

O boot **só** registra o resolver de rotas do Ziggy no MaxUse e monta o app. **Não** há
camada global de Axios (`axios.defaults`, `withCredentials`, `withXSRFToken`), **não** há
interceptor de `401` e **não** há Sanctum SPA stateful — nada disso existe no runtime real.
A validação de sessão e o redirecionamento ao login são responsabilidade do guard do Vue
Router (seção 4), que aguarda `user.waitRequest()`.

```ts
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createMaxPinia } from '@maxvue/max-pinia';
import { ZiggyVue, route } from 'ziggy-js';
import { setRouteResolver, setLibraryRouter } from '@maxvue/max-use';
import MaxComponentsUi from '@maxvue/max-components-ui';
import App from './App.vue';
import router from '@/Js/router';

// MaxUse precisa de um resolver de rotas (Ziggy) para apiGetRoute/apiPostRoute/useCachedApi.
// Deve ocorrer antes de qualquer store/composable resolver rotas.
setRouteResolver((name: string, params?: any) => {
  try {
    return route(name, params);
  } catch {
    return null;
  }
});

const pinia = createPinia();
pinia.use(createMaxPinia({
  cacheName: 'pinia',
  storeName: 'pinia-with-cache-plugin', // preserva o cache LocalForage já existente
  resolveRoute: (name: string, params?: Record<string, any>) => route(name as any, params),
  // ... getSessionToken/isAppStarted/onActivity/loading conforme o projeto
}));

setLibraryRouter(router as any);

createApp(App)
  .use(ZiggyVue)
  .use(pinia)
  .use(MaxComponentsUi)
  .use(router)
  .mount('#app');
```

> Sem `setRouteResolver(...)`, `apiGetRoute`/`apiPostRoute` lançam "Route resolver não
> configurado". Não configure `withXSRFToken`/interceptors: não há esse fluxo aqui.

## Armadilhas

- Colocar `axios`/`apiPostRoute` dentro do `MaxAuthCard` — ele é visual; a lógica fica na store.
- Buscar `user.data` com `axios.get` em vez da store MaxPinia — quebra cache/auto-save e o `waitRequest` do guard.
- Passar URL crua para `apiPostRoute`/`apiGetRoute` — eles recebem **nome de rota Ziggy**.
- Fazer login social com XHR — é `window.location.href = route('social.redirect', { provider })`.
- Fazer logout com `apiPostRoute('logout')` + `router.push` — o real é `window.location.href = '/logout'` (GET).
- Adicionar `axios.defaults.withXSRFToken`/interceptor de `401` no boot — não existe no runtime; a sessão é validada pelo guard.
- Esquecer `setRouteResolver(...)` no boot — `apiGetRoute`/`apiPostRoute` lançam "Route resolver não configurado".
- Checar `user.data?.id` no guard sem `await user.waitRequest()` — race condition no reload da página.
