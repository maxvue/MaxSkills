# Recuperar o usuário logado e proteger rotas (engeapp: Laravel 13 + Vue Router + MaxPinia)

## TL;DR

1. O usuário atual ("me") é **estado de página** → vem de uma **store MaxPinia `useUser`** configurada por **nome de rota Ziggy** (`get: { route: 'user.data' }`), **nunca** de `axios.get` solto.
2. O guard do Vue Router lê **só** `useUser` como fonte de verdade.
3. O bug do "recarreguei e o guard achou que não tô logado" se resolve com **`await user.waitRequest()` antes** de checar `user.data?.id`. Esse é o ponto inteiro.

## Por que o bug acontece

Quando você dá F5, a SPA reinicializa do zero. A store `useUser` começa com `data = null` e dispara o GET de `user.data` de forma **assíncrona**. O guard do router roda **imediatamente** no primeiro paint — antes do GET voltar. Se ele checar `user.data?.id` nesse instante, encontra `null`, conclui "não autenticado" e te chuta para `/login` — mesmo a sessão por cookie no backend estando perfeitamente válida.

Ou seja: não é um problema de autenticação, é uma **race condition** entre o guard e a 1ª busca da sessão.

## A correção

A store `useUser` expõe um `waitRequest()` que resolve uma `Promise` quando a **1ª** requisição de `user.data` conclui (lendo o flag `status.server.get.is_requested` que o MaxPinia injeta na instância). O guard faz `await user.waitRequest()` **antes** de decidir:

```ts
router.beforeEach(async (to, _from, next) => {
  const user = useUserStore();
  const requiresAuth = to.meta.public ? false : (to.meta.requiresAuth ?? true);

  await user.waitRequest();              // <- espera a sessão carregar
  const isAuthenticated = !!user.data?.id;

  if (requiresAuth && !isAuthenticated) return next({ name: 'login' });
  if (to.name === 'login' && isAuthenticated) return next({ name: 'board' });
  next();
});
```

Em navegações seguintes (sem reload) o `waitRequest()` resolve na hora, porque a sessão já foi buscada — então não há custo extra.

## Recuperar o usuário em qualquer lugar do app

Como o "me" mora na store MaxPinia, em qualquer componente você faz:

```ts
const user = useUserStore();
// user.data?.name, user.data?.email, ...
```

Você ganha de graça cache (não refaz o GET a cada rota) e auto-save (alterar `user.data` salva via `user.save`). Por isso **nunca** use `axios.get('/user/data')` espalhado: além de duplicar requisições, isso ignora o `waitRequest` e reintroduz a race no guard.

## Pré-requisitos no boot (senão nada disso funciona)

No `app.ts`:

- `setRouteResolver((name, params) => route(name, params))` — sem isso o MaxUse não resolve `user.data`/`login` e lança "Route resolver não configurado".
- `axios.defaults.withCredentials = true` e `axios.defaults.withXSRFToken = true` — o GET de `user.data` só identifica o usuário se o **cookie de sessão** for enviado (Sanctum SPA stateful).
- Interceptor global de **401** → limpa a store e volta ao login (cobre a sessão expirando com a SPA aberta).

## Marcação das rotas

- Login / públicas: `meta: { requiresAuth: false, public: true }`.
- Protegidas: `meta: { requiresAuth: true }` (é o padrão quando o meta não diz nada).

## Armadilhas (não faça)

- Checar `user.data?.id` no guard **sem** `await user.waitRequest()` → é exatamente o bug do reload.
- Buscar o "me" com `axios.get` em vez da store MaxPinia → quebra cache/auto-save e o `waitRequest`.
- Passar URL crua para `apiGetRoute`/`apiPostRoute` → eles recebem **nome de rota Ziggy**.
- Esquecer `setRouteResolver(...)` no boot.

## Arquivos entregues

- `useUser.Store.ts` — store MaxPinia do usuário atual, com `waitRequest()`.
- `router.ts` — Vue Router + guard `beforeEach` com `await user.waitRequest()`.
- `app.ts` — bootstrap (resolver Ziggy + Axios withCredentials/XSRF + interceptor 401).
