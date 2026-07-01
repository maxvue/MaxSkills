# Tela de login do Maxdmin com MaxAuthCard

Stack: **Laravel 13** (backend, auth por sessão) + **Vue** + **MaxPinia** (`@maxvue/max-pinia`) + **Ziggy**, **sem Inertia**. Componente `MaxAuthCard` vem de `@maxvue/max-components-ui`, e o `useToggle` de `@maxvue/max-use`.

## Arquivos entregues

```
pages/Login.vue              # a tela (MaxAuthCard ligado na store)
stores/auth.ts               # store MaxPinia com a action de login
wiring/router.ts             # rota /login no Vue Router
wiring/routes-web.php        # rotas Laravel (login, logout, OAuth)
wiring/LoginController.php    # action de login no backend (email OU telefone)
```

## Como o componente se liga na store

O `MaxAuthCard` é um componente "burro" de apresentação: ele emite `@submit` e recebe
`:loading` e `:errors`. Toda a lógica fica na store.

1. **Página** (`Login.vue`): mantém o estado do formulário local (`form.login`, `form.password`)
   e o `remember` via `useToggle` do MaxUse. No `@submit`, chama `auth.login(...)`.
2. **Store** (`auth.ts`): a action `login` faz `this.post(route('login'), payload)`.
   - As rotas são **strings resolvidas via Ziggy** (`route('login')`), conforme o contrato do MaxPinia.
   - O `.post` do store já injeta o cookie CSRF e `credentials: 'include'` para a sessão.
   - Em erro 422, mapeia `errors.{campo}` para um `Record<string,string>` que o
     `MaxAuthCard` exibe inline.
3. Em sucesso, a página redireciona via Vue Router (`router.push({ name: 'dashboard' })`).

> Por que `.post` imperativo e não o GET/auto-save automático do MaxPinia? Porque login é
> um fluxo de comando (ação única, com efeito colateral de sessão), não um recurso que se
> sincroniza continuamente. O auto-GET/auto-save do MaxPinia é para estado de tela; aqui
> usamos a action explícita.

## A action de login (resumo)

```ts
async function login(credentials) {
  loading.value = true
  errors.value = {}
  try {
    const { data } = await this.post(route('login'), {
      login: credentials.login,      // e-mail OU telefone, mesmo campo
      password: credentials.password,
      remember: credentials.remember,
    })
    user.value = data.user
  } catch (err) {
    if (err?.status === 422) errors.value = mapErrors(err.body.errors)
    throw err
  } finally {
    loading.value = false
  }
}
```

## E-mail OU telefone

O front manda um único campo `login`. O `LoginController` decide o campo de busca:

```php
$field = filter_var($data['login'], FILTER_VALIDATE_EMAIL) ? 'email' : 'phone';
Auth::attempt([$field => $data['login'], 'password' => $data['password']], $remember);
```

Assim o mesmo input serve para os dois, e o "lembrar-me" vira o 2º argumento do `Auth::attempt`.

## Google e Facebook

Login social é OAuth e exige redirect de browser — não é AJAX. A store expõe `loginWith(provider)`
que faz `window.location.href = route('oauth.redirect', { provider })`. No backend, use **Laravel
Socialite** nas rotas `oauth.redirect` / `oauth.callback`.

## Pré-requisitos no projeto

- `Ziggy` publicado no front (diretiva `@routes` ou import do `ziggy-js`) para `route()` resolver.
- CSRF: chamar `GET /sanctum/csrf-cookie` uma vez no bootstrap do app (ou garantir que o
  cliente HTTP do MaxPinia já faça isso) antes do primeiro POST.
- `laravel/socialite` instalado e os providers Google/Facebook configurados em `config/services.php`.
- Coluna `phone` na tabela `users` (e indexada) para login por telefone.
