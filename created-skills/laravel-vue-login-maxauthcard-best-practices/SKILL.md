---
name: laravel-vue-login-maxauthcard-best-practices
description: Use ao implementar, refatorar, revisar ou depurar o fluxo de LOGIN full-stack do ecossistema engeapp (Laravel 13 sem Inertia, com Ziggy + Vue Router + MaxPinia + MaxComponentsUi). Cobre backend (AuthenticatedSessionController, LoginRequest com e-mail OU telefone, sessão em banco, Sanctum CSRF para SPA, rotas nomeadas para o Ziggy) e frontend (componente MaxAuthCard, store de sessão MaxPinia useUser, login via apiPostRoute do MaxUse, guard de rotas no Vue Router, redirecionamento de login social). Inclua login por redes sociais com Laravel Socialite (Google/Facebook). Acione SEMPRE que a tarefa mencionar tela de login, MaxAuthCard, "entrar"/autenticar, login social, guard de autenticação, sessão de usuário ou recuperar o usuário atual neste stack — mesmo que não citem "Laravel" explicitamente.
---

# Login full-stack (Laravel 13 + Vue 3.6 + MaxAuthCard)

## Objetivo

Padronizar o fluxo de **login** no ecossistema engeapp: backend Laravel 13 (sessão por cookie, Sanctum para SPA, Socialite para login social) e frontend Vue 3.6 (sem Inertia) com **Ziggy + Vue Router + MaxPinia + MaxComponentsUi**. A tela de login usa o componente **`MaxAuthCard`** — um componente puramente visual — e toda a lógica vive em stores e helpers, nunca dentro do card.

Este é o stack do **engeapp/Maxdmin web (Laravel)**. Não é o backend AdonisJS: aqui **existe** Ziggy e Sanctum, e as rotas são **nomeadas** (resolvidas por `route()`), não strings cruas de URL. Para o stack AdonisJS (rotas em string, sem Ziggy/Sanctum) use a skill irmã `vue-auth-session-state-best-practices`.

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

Carregue os provedores no mount e mapeie para o formato do card:

```ts
const PROVIDER_MAP = {
  google:   { label: 'Google',   icon: 'mdi:google',   class: 'btn-google' },
  facebook: { label: 'Facebook', icon: 'mdi:facebook', class: 'btn-facebook' },
};
onMounted(async () => {
  const ids = await apiGetRoute('social.providers');        // ['google', ...]
  providers.value = (ids ?? []).filter(id => PROVIDER_MAP[id])
    .map(id => ({ id, ...PROVIDER_MAP[id] }));
});
```

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
  // waitRequest(): resolve quando a 1ª busca de sessão concluir (evita race no guard)
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

- `axios.defaults.withCredentials = true` e `axios.defaults.withXSRFToken = true` (Sanctum SPA stateful seta o cookie XSRF; o Axios o reenvia).
- Interceptor global de `401`: se não estiver em `/login`, limpa a store e redireciona ao login.
- No boot, registre o resolver do Ziggy no MaxUse: `setRouteResolver((name, params) => route(name, params))` e use `ZiggyVue` no app. Sem isso, `apiPostRoute`/`apiGetRoute` lançam "Route resolver não configurado".

## Checklist de revisão

- [ ] Rotas de auth têm **nome** (Ziggy) e os nomes batem com o que o frontend chama.
- [ ] `LoginRequest` aceita e-mail OU telefone, com rate limiting e `session()->regenerate()`.
- [ ] Socialite: `redirect`/`callback`/`providers`, allowlist de provider, find-or-create de usuário, erro tratado.
- [ ] `MaxAuthCard` sem nenhuma lógica de HTTP/store; só emite `submit`/`social`.
- [ ] Login via `apiPostRoute('login', ...)`; social via `window.location.href = route('social.redirect', { provider })`.
- [ ] `user.data` vem da store MaxPinia (`get: { route: 'user.data' }`), não de axios solto.
- [ ] Guard usa `await user.waitRequest()` antes de checar `user.data?.id`.
- [ ] Axios com `withCredentials`/`withXSRFToken` e interceptor de 401; resolver do Ziggy registrado no MaxUse.

## Skills relacionadas (não duplicar — referenciar)

- `laravel-socialite-oauth-integration-best-practices` — drivers, provisionamento, mock em Pest.
- `laravel-sanctum-api-authentication` — SPA stateful, CSRF, domínios stateful.
- `laravel-ziggy-routing-integration-best-practices` — geração e uso de rotas nomeadas.
- `vue-auth-session-state-best-practices` — contraparte **AdonisJS** (rotas em string, sem Ziggy/Sanctum).
- `vue-max-use-development-best-practices` / `adonisjs-maxpinia-endpoint-patterns-best-practices` — helpers MaxUse/MaxPinia.
