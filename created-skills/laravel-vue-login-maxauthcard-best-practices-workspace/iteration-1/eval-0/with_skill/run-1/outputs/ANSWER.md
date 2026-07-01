# Tela de login do Maxdmin com MaxAuthCard

Aqui está a tela de login full-stack do stack **Laravel 13 (sem Inertia) + Vue 3.6 com MaxPinia + Ziggy + MaxComponentsUi**. O foco foi o que você pediu: ligar o `MaxAuthCard` na store e mostrar a action de login. Suporta **e-mail OU telefone + senha**, **"lembrar-me"** e botões **Google/Facebook**.

## Arquivos entregues

| Arquivo | O que é |
|---|---|
| `LoginPage.vue` | Página de login. Só monta o `MaxAuthCard` e liga os eventos na store. |
| `useLogin.Store.ts` | Store de login (a action `submit`, o `social`, detecção e-mail/telefone, carga dos provedores). |
| `useUser.Store.ts` | Store MaxPinia do usuário atual ("me"), lida pelo guard. |
| `router.ts` | Trecho do guard do Vue Router. |
| `app.ts` | Bootstrap: resolver Ziggy no MaxUse + Axios (cookie/CSRF) + interceptor 401. |

## A ideia central

No stack engeapp, **todo estado de página passa por uma store MaxPinia** (GET + auto-save). O **login é a exceção deliberada**: é uma transição de autenticação, um POST pontual. Então:

- **Login** usa `apiPostRoute('login', ...)` do MaxUse (não é store MaxPinia).
- **Usuário atual** (`user.data`), aí sim, vem da store MaxPinia `useUserStore` (`get: { route: 'user.data' }`).

O `MaxAuthCard` é **puramente visual**: ele só renderiza os inputs/botões e emite `@submit` e `@social`. Nenhum `axios`/store vive dentro dele — toda a lógica está na store de login.

## Como o componente liga na store

Na página, você cria a store e passa estado por `v-model`/props e comportamento por eventos:

```vue
<MaxAuthCard
  v-model:email="login.value"        <!-- campo único: e-mail OU telefone -->
  v-model:password="login.password"
  v-model:remember="login.remember"  <!-- o "lembrar-me" -->
  :loading="login.loading"
  :error="login.error"
  :providers="login.providers"        <!-- botões Google/Facebook -->
  @submit="login.submit"              <!-- dispara a action de login -->
  @social="login.social"              <!-- redirect do OAuth -->
/>
```

```ts
const login = useLoginStore();
onMounted(login.loadProviders); // monta os botões sociais habilitados
```

## A action de login

É um POST pontual via MaxUse, com **nome de rota Ziggy** (`'login'`) — o helper já executa a requisição:

```ts
const submit = async () => {
  loading.value = true;
  error.value = '';
  const result = await apiPostRoute('login', {
    method: method.value,
    email: email.value,           // sentinela se o usuário entrou por telefone
    phone_number: phone_number.value,
    password: password.value,
    remember: remember.value,     // "lembrar-me"
  });
  if (result) location.reload();  // reidrata useUser e o guard redireciona
  else error.value = 'Usuário ou senha inválidos.';
  loading.value = false;
};
```

**E-mail OU telefone:** o campo do card é único (`login.value`). Um `watch` detecta por regex se é e-mail (tem `@`) ou telefone (só dígitos/símbolos) e define `method`. Daí derivamos `email` e `phone_number` para o backend (quando é telefone, manda um e-mail-sentinela para passar a validação `email`).

**"Lembrar-me":** o booleano `remember` vai no payload e o backend repassa a `Auth::attempt($creds, $remember)`.

## Login social (Google/Facebook)

Social **não é XHR** — é navegação real do navegador para a rota Laravel, resolvida pelo Ziggy:

```ts
const social = (provider: string) => {
  window.location.href = route('social.redirect', { provider });
};
```

Os botões aparecem só para os provedores que o backend retorna em `social.providers` (os que têm credenciais configuradas). Vazio = a seção social some sozinha.

## Wiring obrigatório (app.ts)

- `setRouteResolver((name, params) => route(name, params))` — sem isso, `apiPostRoute`/`apiGetRoute` lançam "Route resolver não configurado".
- `axios.defaults.withCredentials = true` e `withXSRFToken = true` — sessão por cookie + CSRF do Sanctum.
- Interceptor de `401` que limpa a store e volta ao login.

## Guard do router

Sempre `await user.waitRequest()` antes de checar `user.data?.id`, evitando race no reload pós-login:

```ts
router.beforeEach(async (to, _from, next) => {
  const user = useUserStore();
  await user.waitRequest();
  const isAuthenticated = !!user.data?.id;
  if ((to.meta.requiresAuth ?? true) && !isAuthenticated) return next({ name: 'login' });
  if (to.name === 'login' && isAuthenticated) return next({ name: 'board' });
  next();
});
```

## Backend (resumo — contrato que o front consome)

As rotas em `routes/auth.php` precisam ter **nome** (Ziggy): `login` (POST `/login_request`), `social.providers`, `social.redirect`, `social.callback`, `logout`. Pontos-chave:

- `LoginRequest` aceita **e-mail OU telefone** (converte telefone para internacional antes do `Auth::attempt`), com rate limiting (5 tentativas).
- Após autenticar, **sempre** `session()->regenerate()` (anti session fixation).
- `Auth::attempt($creds, $remember)` para emitir o cookie de "lembrar-me".
- `SocialiteController`: `redirect`/`callback`/`providers`, allowlist de provider (`['google','facebook']`), find-or-create do usuário (com senha aleatória) no callback.

Detalhes completos do backend nas skills irmãs: `laravel-socialite-oauth-integration-best-practices`, `laravel-sanctum-api-authentication`, `laravel-ziggy-routing-integration-best-practices`.

## Cuidados (armadilhas evitadas)

- Nada de `axios`/`apiPostRoute` dentro do `MaxAuthCard` — ele é visual.
- `apiPostRoute`/`apiGetRoute` recebem **nome de rota Ziggy**, nunca URL crua.
- Social é `window.location.href`, não XHR.
- `user.data` vem da store MaxPinia, não de `axios.get` solto.
- Não esquecer `setRouteResolver(...)` no boot nem `await waitRequest()` no guard.
