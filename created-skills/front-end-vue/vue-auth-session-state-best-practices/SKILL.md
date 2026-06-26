---
name: vue-auth-session-state-best-practices
description: Use when implementing, refactoring, reviewing, or debugging authentication baseada em sessão por cookie (Vue 3.6 + Vue Router 5 + backend AdonisJS) — login/logout, login social, estado do usuário atual via store MaxPinia (@maxvue/max-pinia), guards de rotas protegidas e tratamento de HTTP 401 em interceptors do Axios. Triggers em stores de sessão MaxPinia, guards de rotas protegidas, views de login e interceptors do cliente de API.
---

## Objetivo
Padronizar o fluxo de autenticação por sessão (cookie) no frontend do Maxdmin: login/logout via API, recuperação do usuário atual por store MaxPinia, login social por redirecionamento, guards de rotas no Vue Router e tratamento global de HTTP 401 com Axios. Backend é AdonisJS; a autenticação é por sessão em banco (não token), com validade de 30 dias quando `remember` estiver marcado.

## Endpoints reais
- `POST /api/login` — body `{ email, password, remember? }`. Cria a sessão.
- `GET /user/data` — usuário atual ("me"), protegido por auth. Deve ser consumido via store MaxPinia.
- `POST /logout` — encerra a sessão.
- `GET /auth/providers` — lista de provedores sociais disponíveis.
- `GET /auth/:provider/redirect` — inicia o login social (Google/Facebook).
- `GET /auth/:provider/callback` — callback do provedor, redireciona para `/projects`.

> Rotas são strings (`/api/...`). Use os helpers `apiGetRoute` / `apiPostRoute` do `@maxvue/max-use` para resolver para `/api`. NÃO existe Ziggy, Inertia ou Sanctum aqui (são de Laravel) — não invente esses recursos.

## Instruções

## 1. Store de Sessão com MaxPinia
- Todo GET ao backend passa por uma store `@maxvue/max-pinia` (cache + auto-save). O estado do usuário atual (`/user/data`) DEVE vir de uma store MaxPinia, nunca de `axios.get` manual espalhado pelas views.
- Declare a store com Composition API (`defineStore`) e configure o `get` apontando para `/user/data`:
  `options: computed(() => ({ get: { route: '/user/data' }, key: 'user' }))`.
- Implemente `waitRequest()` retornando uma promessa resolvida quando a primeira requisição de sessão concluir. Isso evita race conditions nos guards do router ao recarregar a página.

## 2. Configuração do Cliente de API & CSRF
- Autenticação é por SESSÃO via cookie. Configure o Axios para enviar cookies e o token XSRF automaticamente:
  ```typescript
  axios.defaults.withCredentials = true;
  axios.defaults.withXSRFToken = true;
  ```
- O backend AdonisJS define o cookie XSRF; com `withXSRFToken = true` o Axios o reenvia. Não há endpoint separado de "csrf-cookie" a buscar antes do login.

## 3. Interceptors Globais do Axios
- Intercepte respostas para capturar `401 Unauthorized` globalmente.
- Em 401, se o usuário não estiver na página `/login`, limpe os estados de sessão (cache da store, chaves locais obsoletas) e redirecione para o login:
  ```typescript
  axios.interceptors.response.use(
      (response) => response,
      (error) => {
          if (error?.response?.status === 401) {
              const currentPath = window.location.pathname;
              if (currentPath !== '/login') {
                  router.push({ name: 'login' });
              }
          }
          return Promise.reject(error);
      }
  );
  ```

## 4. Proteção de Rotas com Vue Router Guard
- Implemente `router.beforeEach` para proteger rotas com base nos metadados (`requiresAuth` ou rotas exclusivas de visitante).
- Aguarde a validação inicial da sessão com `await userStore.waitRequest()` antes de decidir o redirecionamento.
- Avalie o status de autenticação pelo estado da store (dados do usuário) e por eventual 401 da última requisição:
  ```typescript
  const serverIs401 = userStore.status?.server?.get?.error?.response?.status === 401;
  const isAuthenticated = !!userStore.data?.id && !serverIs401;
  ```
- Redirecione para o login se a rota exigir autenticação e o usuário não estiver autenticado.
- Redirecione usuários autenticados que tentem acessar rotas exclusivas de visitante (`login`, `forgot_password`, `reset_password`) para a área principal (por exemplo, `projects`).

## 5. Login Social
- Carregue a lista de provedores de `GET /auth/providers` e renderize um botão por provedor.
- O botão deve REDIRECIONAR o navegador (full page) para `/auth/:provider/redirect` — não use XHR/fetch, pois o fluxo OAuth depende de navegação real:
  ```typescript
  function loginWith(provider: string): void {
      window.location.href = `/auth/${provider}/redirect`;
  }
  ```
- Após o callback do provedor, o backend redireciona para `/projects`.

## 6. Estrutura SFC (Views)
- Ordem padrão de blocos SFC: `<template>`, `<script setup lang="ts">`, `<style lang="scss">` (scoped quando apropriado).
- Toda a lógica em TypeScript (`lang="ts"`) e toda a estilização em SCSS (`lang="scss"`).
- No `<template>`, chame componentes Vue de forma linear (inline), sem quebrar atributos em múltiplas linhas.
- Comentários estritamente em Português do Brasil (pt-BR).

## Restrições
- NUNCA use a Options API. Use Composition API com `<script setup lang="ts">`.
- Não use caminhos fixos (hardcoded) para redirecionamento; use rotas nomeadas (`router.push({ name: 'login' })`).
- Não consuma `/user/data` com `axios.get` solto — sempre pela store MaxPinia.
- Não introduza Ziggy, Inertia, Sanctum ou autenticação por token; o modelo é sessão + cookie.
- Em logout ou 401, limpe estados desatualizados do usuário, contextos e chaves locais.
- Mantenha atributos de template em uma única linha.

# Examples

### Exemplo 1: Store de Sessão MaxPinia (useUser.Store.ts)
```typescript
import { ref, computed, watch, type Ref } from 'vue';
import { defineStore } from 'pinia';

export const useUserStore = defineStore('user', () => {
    // Estado do usuário autenticado, vindo de GET /user/data via MaxPinia
    const data: Ref<any | null> = ref(null);
    const isCached = ref(true);
    const options = computed(() => ({ get: { route: '/user/data' }, key: 'user' }));

    /**
     * Aguarda a primeira requisição de dados do usuário concluir.
     * Evita race condition nos route guards do Vue Router ao recarregar.
     */
    function waitRequest(this: any): Promise<void> {
        return new Promise((resolve) => {
            if (this?.status?.server?.get?.is_requested) return resolve();

            const unwatch = watch(
                () => this?.status?.server?.get?.is_requested,
                (isRequested) => {
                    if (isRequested) {
                        unwatch();
                        resolve();
                    }
                }
            );
        });
    }

    return { data, options, isCached, waitRequest };
});
```

### Exemplo 2: View de Login (LoginPage.vue)
```vue
<template>
  <MaxAuthCard title="Maxdmin" subtitle="Acesse sua conta" icon="mdi:lock-outline" :providers="providers" :loading="loading" :error="error" :forgot-to="{ name: 'forgot_password' }" @submit="submit" @provider="loginWith" />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { apiPostRoute, apiGetRoute } from '@maxvue/max-use';
import { useUserStore } from '@/Stores/UserStores/useUser.Store';

const router = useRouter();
const userStore = useUserStore();

const loading = ref(false);
const error = ref('');
const providers = ref<Array<{ id: string; label: string; icon?: string }>>([]);

// Carrega os provedores de login social disponíveis
onMounted(async () => {
    try {
        const { data } = await axios.get(apiGetRoute('/auth/providers'));
        providers.value = data?.providers ?? data ?? [];
    } catch {
        providers.value = [];
    }
});

// Redireciona o navegador para o fluxo OAuth do provedor (navegação real)
const loginWith = (provider: string): void => {
    window.location.href = `/auth/${provider}/redirect`;
};

// Efetua a submissão das credenciais via sessão por cookie
const submit = async (payload: { email: string; password: string; remember: boolean }): Promise<void> => {
    if (loading.value) return;
    loading.value = true;
    error.value = '';

    try {
        // withCredentials/withXSRFToken já estão habilitados globalmente
        await axios.post(apiPostRoute('/login'), payload);

        // Limpa chaves locais obsoletas e recarrega o usuário pela store MaxPinia
        localStorage.removeItem('selected.client.id');
        if (typeof (userStore as any).reload === 'function') {
            (userStore as any).reload();
        }

        router.push({ name: 'projects' });
    } catch (e: any) {
        error.value = e?.response?.data?.message ?? 'Falha na autenticação. Verifique suas credenciais.';
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped lang="scss">
.btn-google {
    --bg: #ffffff;
    --border-color: #d1d5db;
    color: #374151;
    &:hover {
        background-color: #f9fafb !important;
    }
}
</style>
```

### Exemplo 3: Logout
```typescript
import axios from 'axios';
import { apiPostRoute } from '@maxvue/max-use';

// Encerra a sessão no backend e limpa o estado local
async function logout(router: any, userStore: any): Promise<void> {
    try {
        await axios.post(apiPostRoute('/logout'));
    } finally {
        localStorage.removeItem('selected.client.id');
        if (typeof userStore.clear === 'function') userStore.clear();
        router.push({ name: 'login' });
    }
}
```
