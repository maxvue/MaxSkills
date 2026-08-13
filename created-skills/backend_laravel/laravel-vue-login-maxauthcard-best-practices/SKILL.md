---
name: laravel-vue-login-maxauthcard-best-practices
description: "Use when implementing or debugging authentication in Engeapp (Laravel + Ziggy + Vue Router + MaxPinia): AuthenticatedSessionController, cookie sessions, MaxAuthCard, useLogin/useUser stores, and social login redirects. Covers objectives and central authentication stack."
---
# Login full-stack (Laravel 13 + Vue 3.6 + MaxAuthCard)

## Objetivo

Padronizar o fluxo de **login** e o **estado de sessão** no ecossistema engeapp: backend Laravel 13 (autenticação **por sessão + cookie**, guard `web`, Socialite para login social) e frontend Vue 3.6 (sem Inertia) com **Ziggy + Vue Router + MaxPinia + MaxComponentsUi**. A tela de login usa o componente **`MaxAuthCard`** — um componente puramente visual — e toda a lógica vive em stores e helpers, nunca dentro do card.

Este é o stack do **engeapp (Laravel 13)**: aqui **existe** Ziggy, e as rotas podem ser **nomeadas** (resolvidas por `route()`) além das rotas string usadas pelas cached stores do MaxPinia. O modelo é **sessão + cookie** — não é token/Bearer. `remember` é repassado a `Auth::attempt($creds, $remember)` para emitir o cookie de "lembrar-me" padrão do Laravel (sem prazo customizado configurado no projeto). **Importante:** este projeto **não** tem camada global de Axios (`axios.defaults`, interceptadores, `baseURL`), nem fluxo Sanctum SPA stateful com `withXSRFToken`/`csrf-cookie`, nem interceptor global de `401` — veja a seção "Axios / CSRF / 401 / logout".

## Princípio central do stack

O MaxPinia (`@maxvue/max-pinia`) é a camada de cache + salvamento automático: **todo GET de estado de página passa por uma store MaxPinia** e qualquer alteração no estado dispara auto-save no backend. O login é a **exceção deliberada**: é uma transição de autenticação (um POST pontual), então usa `apiPostRoute('login', ...)` do MaxUse — não é "estado de página". Depois do login, o usuário atual (`user.data`) é estado de página e **deve** vir da store MaxPinia `useUser`, nunca de `axios.get` espalhado.

Regra de ouro: o helper `apiPostRoute`/`apiGetRoute` do `@maxvue/max-use` recebe um **nome de rota Ziggy** (ex.: `'login'`, `'user.data'`) e **já executa a requisição** (retorna `response.data`). Internamente ele resolve o nome via `route()` do Ziggy. Não passe URL crua; não embrulhe em `axios.get(...)`.

## Endpoints e rotas nomeadas

Defina os nomes em `routes/auth.php` (o Ziggy os expõe ao frontend via `route(nome)`):

| Nome Ziggy            | Método | URI                          | Descrição                                  |
|-----------------------|--------|------------------------------|--------------------------------------------|
| `login`               | POST   | `/login_request`             | Cria a sessão (e-mail OU telefone + senha) |
| `logout`              | POST   | `/logout`                    | Encerra a sessão                           |
| `logout.post`         | GET    | `/logout`                    | Encerra a sessão (nome contraintuitivo — é a rota GET, usada de fato pelo `window.location.href = '/logout'` do frontend) |
| `user.data`           | GET    | `/user/data`                 | Usuário atual ("me"), via store MaxPinia   |
| `user.save`           | POST   | `/user/save`                 | Auto-save do usuário (MaxPinia)            |
| `social.providers`    | GET    | `/auth/providers`            | Lista de provedores sociais habilitados    |
| `social.redirect`     | GET    | `/auth/{provider}/redirect`  | Inicia o OAuth (redirect do navegador)     |
| `social.callback`     | GET    | `/auth/{provider}/callback`  | Callback do provedor → cria sessão         |

> Os nomes acima são o contrato. Mantenha-os estáveis: o frontend referencia `route('login')`, `route('social.redirect', { provider })`, etc. Renomear uma rota quebra o Ziggy silenciosamente.

## Backend (Laravel 13)

Leia o arquivo de referência [references/backend-laravel.md](references/backend-laravel.md) para o código completo. Pontos não-negociáveis:

1. **Divisão controller/request no login por e-mail OU telefone.** O **`AuthenticatedSessionController::store`** converte o telefone para o formato internacional (`App\Classes\PhoneClass::getInternationalPhoneNumber()` — namespace real é `App\Classes`, **não** `App\Support`) e faz `$request->merge(['phone_number' => ...])` ANTES de chamar `$request->authenticate()`. O **`LoginRequest`** só autentica: descarta as sentinelas do frontend (`email = 'undefined@enge.tec.br'`, `phone_number = 'undefined'`/`null`) e faz `Auth::attempt` na coluna correta (`email` vs `international_phone_number`), com telefone tendo prioridade quando presente. Aplique rate limiting (5 tentativas) com `RateLimiter` + `throttleKey()`.
2. **Sessão por cookie, não token.** Guard `web`, `SESSION_DRIVER=database`, tabela `sessions`. Após autenticar, **sempre** `session()->regenerate()` (previne session fixation). No logout: `Auth::guard('web')->logout()` + `session()->invalidate()` + `session()->regenerateToken()`. Sem Sanctum (ver seção "Axios / CSRF / 401 / logout" para a cadeia real de CSRF: `csrf_token()` sai em `user.data` → store `useUser` → `useSystemStore.token`/`headerRequests`).
3. **Login social com Laravel Socialite.** Configure `google` e `facebook` em `config/services.php`. O `SocialiteController` tem `redirect()` (→ `Socialite::driver($provider)->redirect()`) e `callback()` (busca usuário por e-mail; se não existir, **cria** com senha aleatória, depois `Auth::login($user)` e `redirect('/')`). Exponha `providers()` retornando só os provedores com credenciais preenchidas — é isso que o frontend consome para montar os botões. Valide o `provider` contra uma allowlist (`['google','facebook']`) e trate erros do OAuth redirecionando para `/login?error=...`. Padrões de driver, provisionamento seguro e mock em testes: skill `laravel-socialite-oauth-integration-best-practices`.
4. **`remember`.** Repasse o booleano `remember` para `Auth::attempt($creds, $remember)` para emitir o cookie de "lembrar-me".

## Frontend (Vue 3.6 + MaxAuthCard)

Leia [references/frontend-vue.md](references/frontend-vue.md) para os arquivos completos (LoginPage, store de login, store useUser, guard, bootstrap). Pontos não-negociáveis:

### MaxAuthCard é puramente visual

`MaxAuthCard` (do `@maxvue/max-components-ui`) **não conhece HTTP, router nem store**. Ele só renderiza inputs e emite eventos. Nunca coloque `axios`/`apiPostRoute` dentro dele. A página consumidora trata a lógica (arquivo real: `resources/Vue/Sections/Auth/Login.vue`):

```vue
<MaxAuthCard identifier="email-phone" :loading="login.loading" :error="login.error" v-model:email="login.value" v-model:password="login.password" v-model:remember="login.remember" :providers="login.providers" :forgot-to="{ query: { sub_page: 'forgot-password' } }" :register-to="{ query: { sub_page: 'register' } }" @submit="login.submit" @social="login.social">
  <template #header><Logo p /></template>
</MaxAuthCard>
```

`forgot-to`/`register-to` são `RouteLocationRaw` do **Vue Router** (não nomes Ziggy — confirmado em `MaxComponentsUi/src/components/MaxAuthCard.vue`, que tipa as props com `RouteLocationRaw` e usa `<router-link :to="...">`). No engeapp os nomes de rota do Vue Router vêm de glob de `resources/Vue/Pages/**/*.vue` e não existe página dedicada de "esqueci a senha"; a navegação entre sub-telas de auth é feita por query `sub_page` (mesmo padrão de `useSystem.Store.ts`), não por `{ name: ... }`.

Eventos/props relevantes do card (confirmados em `MaxComponentsUi/src/components/MaxAuthCard.vue`):
- `identifier` → `'email' | 'email-phone'` (padrão `'email'`). Com `'email-phone'` o card
  renderiza o `MaxInputPhoneMail` (campo combinado e-mail OU telefone) — **obrigatório** para
  o fluxo "login por e-mail OU telefone". Com `'email'` (padrão) só há input de e-mail.
- `@submit` → recebe `{ email, password, remember }`.
- `@social` → recebe o `providerId` (string).
- `:providers` → array `{ id, label, icon, class? }`. Vazio = seção social oculta.
- `:loading` / `:error` → estado do botão e mensagem de erro.
- v-models `email`, `password`, `remember`; prop `show-remember`, `register-to`, `forgot-to`, `labels`.

### Contrato de login, social, usuário e guard

Código completo em [references/frontend-vue.md](references/frontend-vue.md) §2-§4. Resumo do contrato:

- **Login** (`useLogin.Store.ts`) é um POST pontual via `apiPostRoute('login', { method, email, phone_number, password, remember })` — não é "estado de página". A store mantém um campo **único** `value` (e-mail OU telefone) e um `method` (`''` | `'email'` | `'phone'`), derivando `email`/`phone_number` por computeds; o `method` é detectado num `watch(value)`. `apiPostRoute` retorna valor falsy em falha (não lança): em sucesso, `location.reload()` (reidrata a sessão via boot); em falha, toast + mensagem de erro.
- **Social** não é XHR: `window.location.href = route('social.redirect', { provider })`. Os provedores são carregados no mount (`loadProviders`) junto com a leitura do `?error=` deixado pelo redirect do callback (`loadUrlError`) — as chaves de `SOCIAL_ERROR_MESSAGES` devem casar 1:1 com os códigos do `SocialiteController` (`invalid_provider`/`oauth_failed`/`no_email`).
- **Usuário atual** (`useUser.Store.ts`) é estado de página → store MaxPinia com `options.get.route = 'user.data'` e `save = 'user.save'`. **ATENÇÃO:** `options.key` é um campo herdado e NÃO define a chave de cache do MaxPinia — a chave real é `getKey() = $id + '.' + (id ?? options.id ?? 'global')`. `waitRequest()` resolve quando a 1ª busca de sessão concluir COM SUCESSO — observa `status.server.get.is_success` (NÃO `is_requested`); só `is_success` garante `user.data` populado antes de o guard checar `user.data?.id` (evita race no reload).
- **Guard do Vue Router** (`router.beforeEach`) aguarda `await user.waitRequest()` antes de checar `!!user.data?.id` e redirecionar.

### Axios / CSRF / 401 / logout

Ponto de fato (verificado contra o código real do engeapp) — **não invente Sanctum SPA stateful nem interceptors**:

- **Não há camada global de Axios.** O projeto **não** tem `axios.defaults`, interceptadores, `baseURL` nem fluxo `/sanctum/csrf-cookie`. Todo transporte HTTP das chamadas de app passa pelos helpers do `@maxvue/max-use` (`apiGetRoute`/`apiPostRoute`), que já injetam headers e `withCredentials` — ver skill `vue-axios-api-integration-best-practices`. **Não** configure `withXSRFToken` no Axios: não há camada global de Axios aqui.
- **CSRF.** A cadeia real: `csrf_token()` é serializado no payload de `user.data` (`UserDataControler.php`) → store MaxPinia `useUser` → `useSystemStore.token`/`headerRequests` (header `X-CSRF-TOKEN` + `withCredentials`). A meta tag `csrf-token` existe nos blades, mas o front **não** a lê. Para chamadas normais de API, **não** anexe o header CSRF à mão — os helpers cuidam disso. O **único** lugar onde um token CSRF é anexado manualmente é a configuração de bibliotecas externas de upload, passando `'XSRF-TOKEN': system.token` + `withCredentials: true`, lendo de `useSystemStore` (`token`, `base_url`) — ver `FileManager.vue`, `FilesCss.vue`. É exceção para libs que fazem HTTP próprio — não é o fluxo de login nem das chamadas de API do app.
- **401 e sessão.** **Não existem interceptadores de Axios** (não há handler global de `401/403/422/500`). Não invente um. A validação de sessão e o redirecionamento para o login são feitos pelo **guard do Vue Router**, que aguarda `user.waitRequest()` e redireciona quando `!user.data?.id`. Orientação genérica (não é código do projeto): se algum dia for preciso reagir a um `401` programaticamente, centralize no guard/na store e limpe cache com `clearAll()` antes de redirecionar por rota nomeada, evitando loop na tela de login.
- **Logout real = navegação full-page (GET).** O logout **não** é POST via `apiPostRoute`. É `window.location.href = '/logout'` (GET), disparado no menu do usuário (`resources/Vue/Layouts/PageLayout/TopMenu/UserSection.vue`, ~linha 86). O backend encerra a sessão (`Auth::guard('web')->logout()` + `session()->invalidate()`) e redireciona; a navegação full-page já reidrata o estado ao recarregar na tela de login. Não reescreva como `apiPostRoute('logout')` + `router.push` + `clearAll()`.
- **Resolver Ziggy no boot (obrigatório).** Registre o resolver do Ziggy no MaxUse — `setRouteResolver((name, params) => route(name, params))` — e use `ZiggyVue` no app. Sem isso, `apiPostRoute`/`apiGetRoute` lançam "Route resolver não configurado".

## Checklist de revisão

- [ ] Rotas de auth têm **nome** (Ziggy) e os nomes batem com o que o frontend chama.
- [ ] `LoginRequest` aceita e-mail OU telefone, com rate limiting e `session()->regenerate()`.
- [ ] Socialite: `redirect`/`callback`/`providers`, allowlist de provider, find-or-create de usuário, erro tratado.
- [ ] `MaxAuthCard` com `identifier="email-phone"` (habilita o campo combinado e-mail/telefone) e sem nenhuma lógica de HTTP/store; só emite `submit`/`social`.
- [ ] Login por telefone: controller converte via `App\Classes\PhoneClass` e faz merge ANTES do `authenticate()`; request descarta sentinelas (`undefined@enge.tec.br`/`undefined`).
- [ ] Login via `apiPostRoute('login', ...)`; social via `window.location.href = route('social.redirect', { provider })`.
- [ ] `user.data` vem da store MaxPinia (`get: { route: 'user.data' }`), não de axios solto.
- [ ] Guard usa `await user.waitRequest()` antes de checar `user.data?.id`; `waitRequest` observa `status.server.get.is_success` (não `is_requested`).
- [ ] Erro social: backend redireciona para `/login?error=<código>`; frontend chama `loadUrlError()` no mount; códigos (`invalid_provider`/`oauth_failed`/`no_email`) casam com `SOCIAL_ERROR_MESSAGES`.
- [ ] SEM `axios.defaults`/`withXSRFToken`/interceptor de 401 no runtime; SEM Sanctum SPA stateful/`csrf-cookie`. Resolver do Ziggy registrado no MaxUse.
- [ ] Logout = navegação full-page `window.location.href = '/logout'` (GET), não `apiPostRoute('logout')`. CSRF manual só em widgets de upload via `useSystemStore`.

## Skills relacionadas (não duplicar — referenciar)

- `laravel-socialite-oauth-integration-best-practices` — drivers, provisionamento, mock em Pest.
- `laravel-ziggy-routing-integration-best-practices` — geração e uso de rotas nomeadas.
- `vue-axios-api-integration-best-practices` — como os helpers MaxUse injetam headers/`withCredentials` (não há camada Axios global própria).
- `vue-max-use-development-best-practices` / `vue-max-use-usecachedapi-state-cache-best-practices` — helpers MaxUse/MaxPinia.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Estilo de front (não-negociável):** NUNCA use a Options API — sempre `<script setup lang="ts">`, com toda a lógica no script, estilos em `<style scoped lang="scss">` e componentes chamados de forma linear (inline) no `<template>`. Sem camada `services/` no front. Sem `vueuse`/`lodash`/PrimeVue crus — use `@maxvue/max-use` e componentes `Max*` (`MaxComponentsUi`). Nada de `<input>`/`<button>` nativos na tela de login: use `MaxAuthCard`.
