---
name: vue-router-best-practices
description: Use when designing, debugging, or reviewing any Vue Router concern in the Vue 3 frontend — dynamic routing via import.meta.glob, dynamic layout selection (guest/default), navigation guards with auth and loading states, programmatic navigation with useRouter, reading route params/query with useRoute, or route meta properties. Supersedes vue-router-routing-layouts-best-practices and vue-router-routing-navigation-best-practices.
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
- O componente wrapper de layout raiz resolve o layout dinâmicamente a partir de `route.meta.layout`:

```vue
<template>
  <component :is="layoutComponent">
    <RouterView />
  </component>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import DefaultLayout from '@/Layouts/DefaultLayout.vue';
import GuestLayout from '@/Layouts/GuestLayout.vue';

const route = useRoute();
const layouts = {
    default: DefaultLayout,
    guest: GuestLayout
};

const layoutComponent = computed(() => {
    const layoutName = route.meta.layout as keyof typeof layouts;
    return layouts[layoutName] || DefaultLayout;
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
    const isAuthenticated = !!user.data?.id;

    // Vue Router 4: controle de fluxo por RETORNO (o callback `next()` está obsoleto).
    if (requiresAuth && !isAuthenticated) {
        return { name: 'login' };
    }
    if ((to.name === 'login' || to.name === 'register') && isAuthenticated) {
        return { name: 'dashboard' };
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
const navigateToProfile = () => {
    router.push({ name: 'edit_profile' });
};

// Navegar com query params
const navigateWithFilters = (projectId: string) => {
    router.push({
        name: 'project_details',
        query: { project_id: projectId, tab: 'documents' }
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
- NÃO registre rotas estáticas manualmente em `router.ts` sem aprovação explícita — confie no mapeamento glob dinâmico.
- NÃO ignore o `await user.waitRequest()` nos guards de navegação.
- NÃO referencie rotas por caminhos de URL estáticos — sempre use `name`.
- NÃO formate atributos de componentes Vue em múltiplas linhas no `<template>`.
- NÃO escreva comentários de código em outro idioma além do pt-BR.
- NÃO remova nem altere `meta: { layout, requiresAuth }` ao criar novas páginas — padrão: layout `default` e `requiresAuth: true`.
