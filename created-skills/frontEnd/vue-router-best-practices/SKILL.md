---
name: vue-router-best-practices
description: "Use ao projetar, depurar ou revisar Vue Router no frontend Vue 3 do engeapp: registro dinâmico de páginas via import.meta.glob de resources/Vue/Pages, layouts default/guest/site, rotas dinâmicas registradas manualmente (integrador_client_show/:id), guards beforeEach com callback next(), useUserStore.waitRequest, useLoadingStore, navegação com useRouter e leitura de params com useRoute."
---

# Melhores Práticas de Vue Router

## Objetivo
Estabelecer padrões para o Vue Router (`vue-router` ^5.1.0) no frontend Vue 3 do engeapp: registro automático de páginas via `import.meta.glob`, rotas dinâmicas registradas manualmente, layouts, navegação programática, leitura de params/query e guards globais de autenticação e carregamento. Toda a verdade-base está em `resources/Js/router.ts` e `resources/App.vue`.

## Instruções

### 1. Registro Dinâmico de Páginas
O `router.ts` registra as páginas automaticamente com `import.meta.glob`:
- Todas as páginas ficam em `resources/Vue/Pages/**/*.vue` (o diretório real é `Vue/Pages`, NÃO `Js/Pages`).
- Cada arquivo vira uma rota transformando o nome do arquivo:
  - Remove a extensão e o sufixo `Page` do final.
  - Converte para `snake_case` (ex.: `AdminCompaniesPage.vue` → nome `admin_companies`, caminho `/admin_companies`).
  - `BoardPage.vue` é especial: nome `board`, caminho raiz `/` e alias `/board`.
  - O fallback `|| 'home'` no `snakeCase` só existe como guarda para nomes vazios; NÃO há página `Home` e nenhuma rota `home` é registrada na prática.
- `meta` gerado no glob: `layout` é `'guest'` apenas para `login`, senão `'default'`; `requiresAuth` é `false` apenas para `login`, senão `true`.

```typescript
const pages = import.meta.glob('../Vue/Pages/**/*.vue');
const name = snakeCase(path.split('/').pop()?.replace(/\.\w+$/, '').replace(/Page$/, '') || 'home');
const routePath = name === 'board' ? '/' : `/${name}`;
```

### 2. Rotas Dinâmicas e Site Público (registro manual)
Rotas com parâmetro de path NÃO saem do glob — são excluídas via `DYNAMIC_ROUTES` e registradas à mão:
- A única rota dinâmica real é `integrador_client_show`, com `path: '/integrador_client_show/:id'` (param `:id`). Ela está no `Set DYNAMIC_ROUTES` para ser filtrada do glob e recadastrada com o path parametrizado.
- O bloco `/site` é registrado manualmente com layout próprio de marketing: rotas nomeadas `site.home`, `site.prices`, `site.posts`, `site.post` (`publicacoes/:slug`), todas com `meta: { public: true, layout: 'site' }`.
- Para criar uma nova rota com parâmetro de path, adicione o nome ao `DYNAMIC_ROUTES` e faça o `routes.push` manual — não confie no glob para paths com `:param`.

### 3. Seleção de Layout no App.vue
O `resources/App.vue` NÃO usa um booleano `isGuestRoute`. Ele escolhe o que renderizar em cascata de `v-if`, e só renderiza qualquer coisa quando `route.name` existe:
- `route.meta?.layout === 'site'` → `<RouterView />` puro (site de marketing).
- `system?.page` em (`'Pay'`, `'Page'`, `'contatos'`, `'Contract'`, `'Wire'`, `'SolarCompanySubdomain'`) → `<RouterView />` puro (páginas fora do shell do app).
- `user.status?.server?.get?.is_success && !system?.user?.data?.id` → `<RouterView />` puro (sessão resolvida, sem usuário logado — telas guest como login).
- `user.status?.server?.get?.is_success && system?.user?.data?.id` → `<PageLayout><RouterView /></PageLayout>` (usuário autenticado, shell completo).
- Enquanto nada disso resolve, exibe `<LoadScreen />`. Fora do `route.name`, sempre há `<MaxPopoverConfirm />`, `<MaxToast />`, `<VoipDialer />`, `<VoipReverbListener />` e `<IncomingCallModal />`.

Os três valores de `layout` que existem no projeto são `'default'`, `'guest'` (só `login`) e `'site'` (bloco `/site`). Não invente outros.

```vue
<template>
    <div v-if="route.name">
        <div v-if="route.meta?.layout === 'site'"><RouterView /></div>
        <div v-else-if="system?.page === 'Pay' || system?.page === 'Page' || system?.page === 'contatos' || system?.page === 'Contract' || system?.page === 'Wire' || system?.page === 'SolarCompanySubdomain'"><RouterView /></div>
        <div v-else-if="user.status?.server?.get?.is_success && !system?.user?.data?.id"><RouterView /></div>
        <div v-else-if="user.status?.server?.get?.is_success && system?.user?.data?.id"><PageLayout><RouterView /></PageLayout></div>
        <LoadScreen />
    </div>
    <MaxPopoverConfirm />
    <MaxToast />
    <VoipDialer />
    <VoipReverbListener />
    <IncomingCallModal />
</template>
```

### 4. Guards de Navegação — Autenticação e Carregamento
Os guards globais ficam em `resources/Js/router.ts`. O projeto usa o **callback `next()`** (assinatura `(to, from, next)`), NÃO o controle por valor de retorno — mantenha esse padrão. Só existem guards **globais** (`beforeEach`/`afterEach`) — o projeto NÃO usa `beforeRouteEnter`/`beforeRouteLeave` in-component nem `beforeEnter` por rota. No `router.ts` real, cada guard de permissão é um bloco `if` independente (ver exemplo abaixo).

- **Carregamento:** `loading.start({ message: 'Acessando dados da página...', key: 'router' })` no `beforeEach`; `loading.end('router')` no `afterEach`, ambos via `useLoadingStore()` (checado com `if (loading)`).
- **Resolução de sessão:** sempre `await user.waitRequest()` antes de checar `user.data?.id`, evitando race na carga inicial do SPA.
- **Autenticação:** derive apenas de `!!user.data?.id`. NÃO existe checagem de status 401 em `user.status.server.get.error.response.status` — não invente esse caminho.
- **Regra guest:** apenas `to.name === 'login'` com usuário autenticado redireciona; o destino é `{ name: 'board' }` (não existe rota `clients`, `forgot_password`, `reset_password` nem `home`).
- **Guards de UX por permissão:** rotas cujo nome começa com `integrador_` exigem `projeto.ver`; `menu_roles`, `admin_companies` e `menus_admin` exigem `usuario.gerenciar`. São guards defensivos de UX — a segurança real fica no backend. Sem a permissão, redireciona para `{ name: 'board' }`.

```typescript
router.beforeEach(async (to, from, next) => {
    const loading = useLoadingStore();
    if (loading) loading.start({ message: 'Acessando dados da página...', key: 'router' });

    const user = useUserStore();
    const requiresAuth = to.meta.public ? false : (to.meta.requiresAuth ?? true);
    await user.waitRequest();
    const isAuthenticated = !!user.data?.id;

    if (requiresAuth && !isAuthenticated) return next({ name: 'login' });
    if (to.name === 'login' && isAuthenticated) return next({ name: 'board' });

    // Guards de UX por permissão (a segurança real fica no backend)
    const routeName = typeof to.name === 'string' ? to.name : '';
    const permissions: string[] = user.data?.permissions ?? [];
    if (routeName.startsWith('integrador_') && isAuthenticated && !permissions.includes('projeto.ver')) return next({ name: 'board' });
    if (['menu_roles', 'admin_companies', 'menus_admin'].includes(routeName) && isAuthenticated && !permissions.includes('usuario.gerenciar')) return next({ name: 'board' });

    next();
});

router.afterEach(() => {
    const loading = useLoadingStore();
    if (loading) loading.end('router');
});
```

### 5. Navegação Programática
Use `useRouter` do `vue-router` dentro do `<script setup lang="ts">` e navegue pelo **nome** da rota, nunca por caminho estático.
- Nomes válidos vêm dos arquivos em `Vue/Pages` (ex.: `board`, `login`, `integrador_clients`) ou das rotas registradas manualmente (`integrador_client_show`, `site.home`, `site.prices`, `site.posts`, `site.post`).
- A única rota com param de path é `integrador_client_show`, cujo param é `:id`.
- Navegação por query string por nome de rota também é usada (ex.: abrir projeto passando o `id` em `query`, não em `params`).

```typescript
import { useRouter } from 'vue-router';

const router = useRouter();

const irParaClientes = () => router.push({ name: 'integrador_clients' });

// Rota com parâmetro de path :id
const abrirCliente = (id: string) => router.push({ name: 'integrador_client_show', params: { id } });

// Navegação por query string (ex.: NewProjectPage.vue, IncomingCallModal.vue)
const abrirProjeto = (id: string) => router.push({ name: 'project', query: { id, sub_page: 'project_data' } });
```

### 6. Leitura de Parâmetros e Query
Use `useRoute` para acessar `params` e `query`, convertendo os tipos quando necessário.

```typescript
import { useRoute } from 'vue-router';
import { computed } from 'vue';

const route = useRoute();

// Param de path (ex.: /integrador_client_show/:id)
const clientId = computed<string>(() => route.params.id as string);

// Query (ex.: ?status=active)
const filterStatus = computed<string>(() => (route.query.status as string) || 'all');
```

## Restrições
- **Idioma:** comunique-se com o usuário humano em Português (pt-BR), sempre, independentemente do idioma do corpo desta skill.
- Páginas do app ficam em `resources/Vue/Pages`; NÃO use `resources/Js/Pages` (não existe).
- NÃO registre páginas estáticas simples manualmente — confie no glob. Registro manual é só para rotas com param de path (via `DYNAMIC_ROUTES`) e para o bloco `/site`.
- NÃO ignore `await user.waitRequest()` nos guards.
- NÃO referencie rotas por caminho de URL — sempre use `name`.
- NÃO derive autenticação de status HTTP 401; use `!!user.data?.id`.
- NÃO troque o callback `next()` por controle de fluxo por retorno — este projeto usa `next()`.
- NÃO formate atributos de componentes Vue em múltiplas linhas no `<template>`.
- NÃO escreva comentários de código fora do pt-BR.
