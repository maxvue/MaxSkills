---
name: vue-router-best-practices
description: "Use when designing, debugging, or reviewing any Vue Router concern in the Vue 3 frontend: dynamic routing via import.meta.glob, dynamic layout selection (guest/default), navigation guards with auth and loading state, programmatic navigation with useRouter, reading params/query with useRoute, or route meta properties."
---

# Melhores Práticas de Vue Router

## Objetivo
Estabelecer padrões de desenvolvimento para toda a configuração de Vue Router no frontend Vue 3: registro automático de rotas, layouts dinâmicos, navegação programática, acesso a parâmetros de rota e guards de navegação globais com gerenciamento de autenticação e estado de carregamento.

## Instruções

### 1. Arquitetura de Roteamento Dinâmico Automático
O frontend registra as páginas de forma dinâmica utilizando o `import.meta.glob` do Vite:
- Todos os arquivos de página Vue devem residir em `resources/Js/Pages/**/*.vue`.
- Os componentes de página devem seguir a convenção PascalCase com o sufixo `Page` (ex: `SettingsPage.vue`, `ProjectDetailPage.vue`).
- Os nomes e caminhos das rotas são gerados transformando o nome do arquivo:
  - Remove a extensão do arquivo (`.vue`).
  - Remove o sufixo `Page` do final, se presente.
  - Converte o resultado para `snake_case` (ex: `EditProfilePage.vue` → `edit_profile`, caminho `/edit_profile`).
  - `BoardPage.vue` é especial: mapeia para o caminho raiz `/` e registra `/board` como alias.
  - `home` mapeia diretamente para `/`.

### 2. Gerenciamento de Layouts Dinâmicos
- Os metadados de cada rota devem definir um template de layout (`meta: { layout }`).
- Layouts disponíveis: `'default'` (páginas autenticadas) e `'guest'` (páginas públicas como login/registro).
- O `App.vue` raiz seleciona o layout com um booleano simples `isGuestRoute` derivado de `route.meta.layout === 'guest'`: rotas guest renderizam o `<RouterView>` puro, todas as demais são envolvidas por `<PageLayout>`.

```vue
<template>
  <!-- Rotas de guest (login/register) — sem layout -->
  <RouterView v-if="isGuestRoute" />

  <!-- Rotas autenticadas — com layout completo -->
  <PageLayout v-else>
    <RouterView />
  </PageLayout>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';

const route = useRoute();

const isGuestRoute = computed(() => {
    return route.meta?.layout === 'guest';
});
</script>
```

### 3. Guards de Navegação — Autenticação e Estados de Carregamento
Os guards globais são configurados em `resources/Js/router.ts`.

- **Estado de carregamento:** Acione `loading.start()` em `beforeEach` e `loading.end()` em `afterEach` via `useLoadingStore()`.
- **Resolução de sessão:** Sempre `await user.waitRequest()` antes de verificar `user.data?.id` para evitar race conditions durante a carga inicial do SPA.
- **Controle de acesso:** As rotas requerem autenticação por padrão (`meta.requiresAuth ?? true`). Use `meta.public: true` para marcar rotas públicas explicitamente.

```typescript
router.beforeEach(async (to, from) => {
    const loading = useLoadingStore();
    if (loading) {
        loading.start({ message: 'Acessando dados da página...', key: 'router' });
    }

    const user = useUserStore();
    const requiresAuth = to.meta.public ? false : (to.meta.requiresAuth ?? true);
    await user.waitRequest();
    // Se o servidor retornou 401, o dado em user.data pode ser cache antigo — não considerar autenticado.
    const serverIs401 = user.status?.server?.get?.error?.response?.status === 401;
    const isAuthenticated = !!user.data?.id && !serverIs401;

    // Vue Router v5: controle de fluxo por RETORNO (o callback `next()` está obsoleto).
    if (requiresAuth && !isAuthenticated) {
        return { name: 'login' };
    }
    const guestOnlyRoutes = ['login', 'register', 'forgot_password', 'reset_password', 'home'];
    if ((guestOnlyRoutes.includes(to.name as string) || !to.name) && isAuthenticated) {
        return { name: 'clients' };
    }

    return true;
});

router.afterEach(() => {
    const loading = useLoadingStore();
    if (loading) {
        loading.end('router');
    }
});
```

### 4. Navegação Programática
Sempre use `useRouter` do `vue-router` para navegação programática dentro do `<script setup lang="ts">`.
- Navegue pelo **nome** da rota, nunca por caminhos estáticos.
- Forneça tipagens TypeScript explícitas para payloads de parâmetros complexos.

```typescript
import { useRouter } from 'vue-router';

const router = useRouter();

// Navegar para uma rota nomeada
const navigateToClients = () => {
    router.push({ name: 'clients' });
};

// Navegar para uma rota com parâmetro dinâmico + query params
const navigateToWorkspace = (clientId: string) => {
    router.push({
        name: 'client.workspace',
        params: { clientId },
        query: { tab: 'calendar' }
    });
};
```

### 5. Leitura de Parâmetros e Consultas de Rota
Use `useRoute` para acessar params, caminho atual ou query string dentro dos componentes.
- Converta explicitamente os tipos de params/query quando a tipagem estrita for necessária.

```typescript
import { useRoute } from 'vue-router';
import { computed } from 'vue';

const route = useRoute();

// Parâmetros de rota (ex: /project/:id)
const projectId = computed<string>(() => route.params.id as string);

// Parâmetros de consulta (ex: ?status=active)
const filterStatus = computed<string>(() => (route.query.status as string) || 'all');
```

### 6. Ordem de Blocos SFC e Formatação de Atributos
- Ordem dos blocos SFC: `<template>` → `<script setup lang="ts">` → `<style lang="scss">`.
- Mantenha todos os atributos de elementos na mesma linha — não quebre em múltiplas linhas.
- Todos os comentários de código devem ser escritos em português brasileiro (pt-BR).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- NÃO registre rotas estáticas manualmente em `router.ts` sem aprovação explícita — confie no mapeamento glob dinâmico.
- NÃO ignore o `await user.waitRequest()` nos guards de navegação.
- NÃO referencie rotas por caminhos de URL estáticos — sempre use `name`.
- NÃO formate atributos de componentes Vue em múltiplas linhas no `<template>`.
- NÃO escreva comentários de código em outro idioma além do pt-BR.
- NÃO remova nem altere `meta: { layout, requiresAuth }` ao criar novas páginas — padrão: layout `default` e `requiresAuth: true`.
