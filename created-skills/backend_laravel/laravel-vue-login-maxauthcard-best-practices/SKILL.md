---
name: laravel-vue-login-maxauthcard-best-practices
description: "Use ao implementar, refatorar, revisar ou depurar o LOGIN full-stack do engeapp (Laravel 13 + Ziggy + Vue Router + MaxPinia + MaxComponentsUi). Cobre backend (AuthenticatedSessionController, LoginRequest por e-mail ou telefone, sessão em banco, Sanctum CSRF, Socialite) e frontend (MaxAuthCard, store useUser, login via apiPostRoute, guard de rotas). Acione em tela de login ou autenticar."
---

# Login full-stack (Laravel 13 + Vue 3.6 + MaxAuthCard)

## Objetivo

Padronizar o fluxo de **login** no ecossistema engeapp: backend Laravel 13 (sessão por cookie, Sanctum para SPA, Socialite para login social) e frontend Vue 3.6 (sem Inertia) com **Ziggy + Vue Router + MaxPinia + MaxComponentsUi**. A tela de login usa o componente **`MaxAuthCard`** — um componente puramente visual — e toda a lógica vive em stores e helpers, nunca dentro do card.

Este é o stack do **engeapp (Laravel 13)**: aqui **existe** Ziggy e Sanctum, e as rotas podem ser **nomeadas** (resolvidas por `route()`) além das rotas string usadas pelas cached stores do MaxPinia. Para o padrão de sessão/estado de autenticação no cliente, veja também a skill irmã `vue-auth-session-state-best-practices`.

## Princípio central do stack

O MaxPinia (`@maxvue/max-pinia`) é a camada de cache + salvamento automático: **todo GET de estado de página passa por uma store MaxPinia** e qualquer alteração no estado dispara auto-save no backend. O login é a **exceção deliberada**: é uma transição de autenticação (um POST pontual), então usa `apiPostRoute('login', ...)` do MaxUse — não é "estado de página". Depois do login, o usuário atual (`user.data`) é estado de página e **deve** vir da store MaxPinia `useUser`, nunca de `axios.get` espalhado.

Regra de ouro: o helper `apiPostRoute`/`apiGetRoute` do `@maxvue/max-use` recebe um **nome de rota Ziggy** (ex.: `'login'`, `'user.data'`) e **já executa a requisição** (retorna `response.data`). Internamente ele resolve o nome via `route()` do Ziggy. Não passe URL crua; não embrulhe em `axios.get(...)`.

## Endpoints e rotas nomeadas

Defina os nomes em `routes/auth.php` (o Ziggy os expõe ao frontend via `route(nome)`):

| Nome Ziggy            | Método | URI                          | Descrição                                  |
|-----------------------|--------|------------------------------|--------------------------------------------|
| `login`               | POST   | `/login_request`             | Cria a sessão (e-mail OU telefone + senha) |
| `logout`              | POST   | `/logout`                    | Encerra a sessão                           |
| `user.data`           | GET    | `/user/data`                 | Usuário atual ("me"), via store MaxPinia   |
| `user.save`           | POST   | `/user/save`                 | Auto-save do usuário (MaxPinia)            |
| `social.providers`    | GET    | `/auth/providers`            | Lista de provedores sociais habilitados    |
| `social.redirect`     | GET    | `/auth/{provider}/redirect`  | Inicia o OAuth (redirect do navegador)     |
| `social.callback`     | GET    | `/auth/{provider}/callback`  | Callback do provedor → cria sessão         |

> Os nomes acima são o contrato. Mantenha-os estáveis: o frontend referencia `route('login')`, `route('social.redirect', { provider })`, etc. Renomear uma rota quebra o Ziggy silenciosamente.

## Backend (Laravel 13)

Leia o arquivo de referência [references/backend-laravel.md](references/backend-laravel.md) para o código completo. Pontos não-negociáveis:

1. **`LoginRequest` aceita e-mail OU telefone.** O campo de identificação chega como `email` ou `phone_number`. Converta o telefone para o formato internacional antes de autenticar (`PhoneClass::getInternationalPhoneNumber()`) e tente `Auth::attempt` na coluna correta (`email` vs `international_phone_number`). Aplique rate limiting (5 tentativas) com `RateLimiter` + `throttleKey()`, e registre falhas.
2. **Sessão por cookie, não token.** Guard `web`, `SESSION_DRIVER=database`, tabela `sessions`. Após autenticar, **sempre** `session()->regenerate()` (previne session fixation). No logout: `Auth::guard('web')->logout()` + `session()->invalidate()` + `session()->regenerateToken()`. Detalhes de CSRF/SPA na skill `laravel-sanctum-api-authentication`.
3. **Login social com Laravel Socialite.** Configure `google` e `facebook` em `config/services.php`. O `SocialiteController` tem `redirect()` (→ `Socialite::driver($provider)->redirect()`) e `callback()` (busca usuário por e-mail; se não existir, **cria** com senha aleatória, depois `Auth::login($user)` e `redirect('/')`). Exponha `providers()` retornando só os provedores com credenciais preenchidas — é isso que o frontend consome para montar os botões. Valide o `provider` contra uma allowlist (`['google','facebook']`) e trate erros do OAuth redirecionando para `/login?error=...`. Padrões de driver, provisionamento seguro e mock em testes: skill `laravel-socialite-oauth-integration-best-practices`.
4. **`remember`.** Repasse o booleano `remember` para `Auth::attempt($creds, $remember)` para emitir o cookie de "lembrar-me".

## Frontend (Vue 3.6 + MaxAuthCard)

Leia [references/frontend-vue.md](references/frontend-vue.md) para os arquivos completos (LoginPage, store de login, store useUser, guard, bootstrap). Pontos não-negociáveis:

### MaxAuthCard é puramente visual

`MaxAuthCard` (do `@maxvue/max-components-ui`) **não conhece HTTP, router nem store**. Ele só renderiza inputs e emite eventos. Nunca coloque `axios`/`apiPostRoute` dentro dele. A página consumidora trata a lógica:

```vue
<MaxAuthCard title="Maxdmin" subtitle="Acesse sua conta" icon="mdi:shield-account-outline" :loading="login.loading" :error="login.error" v-model:email="login.value" v-model:password="login.password" v-model:remember="login.remember" :providers="login.providers" :register-to="{ name: 'register' }" :forgot-to="{ name: 'password.request' }" @submit="login.submit" @social="login.social" />
```

Eventos/props relevantes do card:
- `@submit` → recebe `{ email, password, remember }`.
- `@social` → recebe o `providerId` (string).
- `:providers` → array `{ id, label, icon, class? }`. Vazio = seção social oculta.
- `:loading` / `:error` → estado do botão e mensagem de erro.
- v-models `email`, `password`, `remember`; slots `header`, `extra`, `footer`.

### Ação de login (store)

A submissão é um POST pontual via MaxUse com **nome de rota Ziggy**:

```ts
const submit = async () => {
  loading.value = true;
  error.value = '';
  const result = await apiPostRoute('login', {
    email: email.value,            // sentinela se for telefone (ver detecção)
    phone_number: phone_number.value,
    password: password.value,
    remember: remember.value,
  });
  if (result) location.reload();   // recarrega: o guard reidrata user.data
  else error.value = 'Usuário ou senha inválidos.';
  loading.value = false;
};
```

Detecte e-mail vs telefone no próprio store (watcher por regex sobre o campo único), como faz o engeapp. O `location.reload()` após sucesso é intencional: força o boot a reidratar a store `useUser` e o guard do router faz o redirecionamento.

### Login social (redirecionamento total)

Social **não** é XHR — é navegação do navegador para a rota Laravel, resolvida pelo Ziggy:

```ts
const social = (provider: string) => {
  window.location.href = route('social.redirect', { provider });
};
```

Carregue os provedores no mount e mapeie para o formato do card. No **mesmo** `onMounted`, leia o `?error=` deixado pelo redirect do callback social (fecha o ciclo de feedback do erro):

```ts
const PROVIDER_MAP = {
  google:   { label: 'Google',   icon: 'mdi:google',   class: 'btn-google' },
  facebook: { label: 'Facebook', icon: 'mdi:facebook', class: 'btn-facebook' },
};

// As CHAVES devem casar 1:1 com os códigos do SocialiteController.
const SOCIAL_ERROR_MESSAGES = {
  invalid_provider: 'Provedor de login inválido.',
  oauth_failed:     'Não foi possível autenticar com o provedor. Tente novamente.',
  no_email:         'Sua conta social não forneceu um e-mail. Use e-mail e senha.',
};

const loadProviders = async () => {
  const ids = await apiGetRoute('social.providers');        // ['google', ...]
  providers.value = (ids ?? []).filter(id => PROVIDER_MAP[id])
    .map(id => ({ id, ...PROVIDER_MAP[id] }));
};

// Lê o ?error= da URL (redirect do backend) e exibe a mensagem no card.
const loadUrlError = () => {
  const code = new URLSearchParams(window.location.search).get('error');
  if (code && SOCIAL_ERROR_MESSAGES[code]) error.value = SOCIAL_ERROR_MESSAGES[code];
};

// Na página: onMounted(() => { login.loadProviders(); login.loadUrlError(); });
```

> O fluxo do erro social é **backend redireciona para `/login?error=<código>` → frontend lê com `loadUrlError()` → card mostra a mensagem**. Se os códigos do controller e as chaves de `SOCIAL_ERROR_MESSAGES` divergirem, ou se o backend redirecionar para `/` em vez de `/login`, o usuário nunca vê o erro.

### Usuário atual via store MaxPinia

O "me" é estado de página → store MaxPinia, configurada por **nome de rota**:

```ts
export const useUserStore = defineStore('user', () => {
  const data = ref<User | null>(null);
  const isCached = ref(true);
  const options = computed(() => ({
    get: { route: 'user.data' },   // nome Ziggy; MaxPinia faz o GET
    save: 'user.save',             // auto-save ao alterar data
    key: 'user',
  }));
  // waitRequest(): resolve quando a 1ª busca de sessão concluir COM SUCESSO — observa
  // status.server.get.is_success (NÃO is_requested); só is_success garante user.data populado
  // antes de o guard checar user.data?.id (evita race no reload).
  return { data, isCached, options, waitRequest };
});
```

### Guard do Vue Router

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

### Axios / CSRF / 401

- A configuração do Axios (`withCredentials`, `withXSRFToken`) e o interceptor global de resposta (`401/403/422/500`, incluindo o `401` que limpa a store e redireciona ao login quando não se está em `/login`) são **canônicos** na skill `vue-axios-api-integration-best-practices` — não reduplique o bloco aqui; siga-a. Sanctum SPA stateful seta o cookie XSRF e o Axios o reenvia no header `X-XSRF-TOKEN`.
- Detalhe específico deste stack (Ziggy): no boot, registre o resolver do Ziggy no MaxUse — `setRouteResolver((name, params) => route(name, params))` — e use `ZiggyVue` no app. Sem isso, `apiPostRoute`/`apiGetRoute` lançam "Route resolver não configurado".

## Checklist de revisão

- [ ] Rotas de auth têm **nome** (Ziggy) e os nomes batem com o que o frontend chama.
- [ ] `LoginRequest` aceita e-mail OU telefone, com rate limiting e `session()->regenerate()`.
- [ ] Socialite: `redirect`/`callback`/`providers`, allowlist de provider, find-or-create de usuário, erro tratado.
- [ ] `MaxAuthCard` sem nenhuma lógica de HTTP/store; só emite `submit`/`social`.
- [ ] Login via `apiPostRoute('login', ...)`; social via `window.location.href = route('social.redirect', { provider })`.
- [ ] `user.data` vem da store MaxPinia (`get: { route: 'user.data' }`), não de axios solto.
- [ ] Guard usa `await user.waitRequest()` antes de checar `user.data?.id`; `waitRequest` observa `status.server.get.is_success` (não `is_requested`).
- [ ] Erro social: backend redireciona para `/login?error=<código>`; frontend chama `loadUrlError()` no mount; códigos (`invalid_provider`/`oauth_failed`/`no_email`) casam com `SOCIAL_ERROR_MESSAGES`.
- [ ] Axios com `withCredentials`/`withXSRFToken` e interceptor de 401; resolver do Ziggy registrado no MaxUse.

## Skills relacionadas (não duplicar — referenciar)

- `laravel-socialite-oauth-integration-best-practices` — drivers, provisionamento, mock em Pest.
- `laravel-sanctum-api-authentication` — SPA stateful, CSRF, domínios stateful.
- `laravel-ziggy-routing-integration-best-practices` — geração e uso de rotas nomeadas.
- `vue-auth-session-state-best-practices` — padrão de sessão/estado de autenticação no cliente (Sanctum SPA).
- `vue-max-use-development-best-practices` / `vue-max-use-usecachedapi-state-cache-best-practices` — helpers MaxUse/MaxPinia.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
