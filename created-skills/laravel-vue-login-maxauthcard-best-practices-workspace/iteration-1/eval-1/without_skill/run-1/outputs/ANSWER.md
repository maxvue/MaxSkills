# Usuário logado no front + proteção de rotas (sem o bug do F5)

No **engeapp** (Laravel 13 + Vue Router + MaxPinia + Ziggy) você recupera o usuário
logado via uma **store MaxPinia** (`useUser`) e protege rotas num **guard
`beforeEach`** que **espera a store resolver** antes de decidir. O bug de "ao
recarregar acha que não tá logado" vem de o guard ler o estado **antes** do GET do
usuário terminar — a correção é aguardar a resolução.

## Por que o bug acontece

A sessão fica no **cookie** (Laravel session/Sanctum), não no JS. Quando você dá F5,
o front sobe do zero: a store `useUser` ainda não tem `data` (é `null`). Se o guard
faz `if (!useUser().isLoggedIn) redirect('login')` **síncrono**, ele dispara antes do
servidor confirmar a sessão e te chuta pro login mesmo logado.

`null` é ambíguo: pode significar "ainda carregando" **ou** "deslogado". A solução é
**nunca decidir enquanto `data` não foi resolvido pelo menos uma vez**.

## Como funciona a solução

1. **`useUser` (store MaxPinia)** — declara o contrato `data` / `isCached` /
   `options` com `get: { route: 'user.data' }`. Aqui usamos o **nome de rota Ziggy**
   (não string `/api/...`), porque o MaxUse resolve nomes via `resolveRoute` → `route()`
   do Ziggy. O plugin MaxPinia, ao montar a store: carrega do cache (localforage,
   hidratação otimista), faz o GET em `user.data` revalidando, e expõe `status`
   reativo + `is_done_to_show`.

2. **Backend `user.data`** precisa devolver **200 com o usuário** quando autenticado e
   **401** quando não. O 401 é o que deixa o front diferenciar "deslogado" de
   "carregando" — sem ele, o estado `null` continua ambíguo.

3. **Guard `beforeEach`** — antes de avaliar `requiresAuth`/`requiresGuest`, chama
   `await ensureUserResolved()`. Esse helper:
   - retorna na hora se o GET já está *settled* (`status.server.get.is_requested`);
   - senão, dispara `reload()` e faz polling reativo curto até o GET assentar
     (sucesso **ou** 401), com timeout de segurança;
   - deduplica chamadas concorrentes (uma só resolução por carga de página).

   Só **depois** disso o guard lê `userStore.isLoggedIn`. Resultado: no F5 ele espera
   a sessão ser confirmada e não te desloga indevidamente.

## Pontos de atenção

- **GET sempre via store MaxPinia** — não faça `axios.get('/api/user')` solto no
  componente/guard. O `data` do usuário vem da store; o guard só consome o `status`.
- **Logout**: chame `clearAll()` (MaxPinia, limpa o cache localforage) + `clearUser()`
  e force re-resolução (o `ensureUserResolved` re-resolve porque zera o `resolveOnce`
  ao assentar). Senão o usuário antigo "ressuscita" do cache.
- **Redirect pós-login**: o guard salva `?redirect=` ao mandar pro login; sua página
  de login deve respeitar essa query.
- **Ziggy mantido** (este é stack Laravel, onde Ziggy continua). As rotas no MaxPinia
  e no MaxUse usam **nomes** (`'user.data'`, `'dashboard'`), não paths.
- O CSRF dos POSTs sai do `getSessionToken` configurado no `createMaxPinia` no boot.

## Arquivos entregues

- `useUser.ts` — store MaxPinia do usuário logado (`data`/`isCached`/`options`,
  getters `isLoggedIn`/`hasRole`/`can`, `clearUser`).
- `router.ts` — Vue Router + guard `beforeEach` com `ensureUserResolved()` que mata o
  bug do F5.
