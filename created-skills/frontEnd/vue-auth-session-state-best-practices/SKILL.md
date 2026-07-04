---
name: vue-auth-session-state-best-practices
description: Use when implementing, refactoring, reviewing, or debugging authentication baseada em sessão por cookie (Vue 3 + Vue Router 4 + backend Laravel Sanctum SPA) — login/logout, login social, estado do usuário atual via store MaxPinia (@maxvue/max-pinia), guards de rotas protegidas e tratamento de HTTP 401 em interceptors do Axios. Triggers em stores de sessão MaxPinia, guards de rotas protegidas, views de login e interceptors do cliente de API.
---

## Objetivo
Padronizar o fluxo de autenticação por sessão (cookie) no frontend do Maxdmin: login/logout via API, recuperação do usuário atual por store MaxPinia, login social por redirecionamento, guards de rotas no Vue Router e tratamento global de HTTP 401 com Axios. Backend é Laravel com **Sanctum (autenticação SPA por sessão + cookie)**; não é token/Bearer. O fluxo exige um GET prévio em `/sanctum/csrf-cookie` para semear o cookie `XSRF-TOKEN` antes do login. A validade da sessão é de 30 dias quando `remember` estiver marcado.

## Endpoints reais
- `POST /api/login` — body `{ email, password, remember? }`. Cria a sessão.
- `GET /api/user/data` — usuário atual ("me"), protegido por auth. Deve ser consumido via store MaxPinia.
- `POST /api/logout` — encerra a sessão.
- `GET /api/auth/providers` — lista de provedores sociais disponíveis.
- `GET /api/auth/:provider/redirect` — inicia o login social (Google/Facebook).
- `GET /api/auth/:provider/callback` — callback do provedor, redireciona para `/projects`.

> Rotas são strings (`/api/...`). Os helpers `apiGetRoute` / `apiPostRoute` do `@maxvue/max-use` são **funções assíncronas que JÁ executam a requisição** (`await apiGetRoute('/...')` retorna `response.data`) — não são resolvedores de URL e NÃO devem ser embrulhados em `axios.get(...)`. Para dados de página, prefira a store MaxPinia (que faz GET/save por baixo); use `apiGetRoute`/`apiPostRoute` apenas em chamadas pontuais que não são estado de página (ex.: submit de login). Aqui o backend é **Laravel Sanctum (SPA)**: a autenticação É por sessão + cookie via Sanctum (não invente token/Bearer). O MaxPinia consome rotas em string (`apiGetRoute('/api/...')`), o que coexiste com o Ziggy do Laravel — não afirme "sem Ziggy".

## Instruções

## 1. Store de Sessão com MaxPinia
- Todo GET ao backend passa por uma store `@maxvue/max-pinia` (cache + auto-save). O estado do usuário atual (`/api/user/data`) DEVE vir de uma store MaxPinia, nunca de `axios.get` manual espalhado pelas views.
- Declare a store com Composition API (`defineStore`) e configure o `get` apontando para `/user/data`:
  `options: computed(() => ({ get: { route: '/api/user/data' }, key: 'user' }))`.
- O MaxPinia injeta `status`, `reload()` e `clearAll()` na própria instância da store. Leia o estado SEMPRE pela instância (`userStore.status.server.get.is_requested`), nunca via `this` dentro da setup store.
- Implemente `waitRequest(store)` como helper que recebe a instância da store e retorna uma promessa resolvida quando a primeira requisição de sessão concluir (observando `store.status.server.get.is_requested`). Isso evita race conditions nos guards do router ao recarregar a página.

## 2. Configuração do Cliente de API & CSRF
- A configuração genérica do Axios (`withCredentials`, `withXSRFToken`, `baseURL`, headers) é canônica na skill **`vue-axios-api-integration-best-practices`** — não a reduplique aqui. Autenticação é por SESSÃO via cookie (Laravel Sanctum SPA).
- Detalhe específico do fluxo de login: no Sanctum SPA, faça um GET em `/sanctum/csrf-cookie` **antes** do primeiro POST de mutação (login) para semear o cookie `XSRF-TOKEN`. Com `withXSRFToken = true` o Axios lê esse cookie e o reenvia no header `X-XSRF-TOKEN` automaticamente:
  ```typescript
  await axios.get('/sanctum/csrf-cookie');
  // agora o POST de login enviará o header X-XSRF-TOKEN corretamente
  ```

## 3. Interceptors Globais do Axios
- O interceptor de resposta genérico (tratamento de `401/403/422/500`) é definido **uma única vez** na skill `vue-axios-api-integration-best-practices` — veja lá o bloco completo. Não redeclare o interceptor aqui.
- Comportamento específico de sessão que este fluxo exige do caso **401 Unauthorized**: limpe os estados de sessão (cache da store, chaves locais obsoletas) e redirecione para o login usando rota nomeada (`router.push({ name: 'login' })`), **exceto** quando o usuário já estiver na página de login (evita loop de redirecionamento). Garanta que o interceptor canônico contemple essa limpeza de sessão + guarda de `/login`.

## 4. Proteção de Rotas com Vue Router Guard
- Implemente `router.beforeEach` para proteger rotas com base nos metadados (`requiresAuth` ou rotas exclusivas de visitante).
- Aguarde a validação inicial da sessão com `await waitRequest(userStore)` antes de decidir o redirecionamento.
- Avalie o status de autenticação pelo estado da store (dados do usuário) e por eventual 401 da última requisição:
  ```typescript
  const serverIs401 = userStore.status?.server?.get?.error?.response?.status === 401;
  const isAuthenticated = !!userStore.data?.id && !serverIs401;
  ```
- Redirecione para o login se a rota exigir autenticação e o usuário não estiver autenticado.
- Redirecione usuários autenticados que tentem acessar rotas exclusivas de visitante (`login`, `forgot_password`, `reset_password`) para a área principal (por exemplo, `projects`).

## 5. Login Social
- Carregue a lista de provedores de `GET /api/auth/providers` e renderize um botão por provedor.
- O botão deve REDIRECIONAR o navegador (full page) para `/api/auth/:provider/redirect` — não use XHR/fetch, pois o fluxo OAuth depende de navegação real:
  ```typescript
  function loginWith(provider: string): void {
      window.location.href = `/api/auth/${provider}/redirect`;
  }
  ```
- Após o callback do provedor, o backend redireciona para `/projects`.

## 6. Estrutura SFC (Views)
- Ordem padrão de blocos SFC: `<template>`, `<script setup lang="ts">`, `<style lang="scss">` (scoped quando apropriado).
- Toda a lógica em TypeScript (`lang="ts"`) e toda a estilização em SCSS (`lang="scss"`).
- No `<template>`, chame componentes Vue de forma linear (inline), sem quebrar atributos em múltiplas linhas.
- Comentários estritamente em Português do Brasil (pt-BR).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- NUNCA use a Options API. Use Composition API com `<script setup lang="ts">`.
- Não use caminhos fixos (hardcoded) para redirecionamento; use rotas nomeadas (`router.push({ name: 'login' })`).
- Não consuma `/user/data` com `axios.get` solto — sempre pela store MaxPinia.
- Não introduza autenticação por token/Bearer; o modelo é Sanctum SPA (sessão + cookie). Não desative o CSRF nem pule o GET em `/sanctum/csrf-cookie`.
- Em logout ou 401, limpe estados desatualizados do usuário, contextos e chaves locais.
- Mantenha atributos de template em uma única linha.

# Examples

### Exemplo 1: Store de Sessão MaxPinia (useUser.Store.ts)
```typescript
import { ref, computed, watch, type Ref } from 'vue';
import { defineStore } from 'pinia';

// `status`, `reload()` e `clearAll()` são injetados pelo plugin MaxPinia na instância da store.
export const useUserStore = defineStore('user', () => {
    // Estado do usuário autenticado, vindo de GET /user/data via MaxPinia
    const data: Ref<any | null> = ref(null);
    const isCached = ref(true);
    const options = computed(() => ({ get: { route: '/api/user/data' }, key: 'user' }));

    return { data, options, isCached };
});

/**
 * Aguarda a primeira requisição de dados do usuário concluir.
 * Evita race condition nos route guards do Vue Router ao recarregar.
 * Recebe a instância da store e lê `store.status` (injetado pelo MaxPinia) —
 * nunca use `this` dentro da setup store.
 */
export function waitRequest(store: ReturnType<typeof useUserStore>): Promise<void> {
    return new Promise((resolve) => {
        if (store.status?.server?.get?.is_requested) return resolve();

        const unwatch = watch(
            () => store.status?.server?.get?.is_requested,
            (isRequested) => {
                if (isRequested) {
                    unwatch();
                    resolve();
                }
            }
        );
    });
}
```

### Exemplo 2: View de Login (LoginPage.vue)
```vue
<template>
  <MaxAuthCard title="Maxdmin" subtitle="Acesse sua conta" icon="mdi:lock-outline" :providers="providers" :loading="loading" :error="error" :forgot-to="{ name: 'forgot_password' }" @submit="submit" @social="loginWith" />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { apiPostRoute, apiGetRoute } from '@maxvue/max-use';
import { useUserStore } from '@/Stores/UserStores/useUser.Store';

const router = useRouter();
const userStore = useUserStore();

const loading = ref(false);
const error = ref('');
const providers = ref<Array<{ id: string; label: string; icon?: string }>>([]);

// Carrega os provedores de login social disponíveis.
// apiGetRoute já executa o GET e retorna response.data (não embrulhe em axios.get).
onMounted(async () => {
    const res = await apiGetRoute('/api/auth/providers');
    providers.value = res?.providers ?? res ?? [];
});

// Redireciona o navegador para o fluxo OAuth do provedor (navegação real)
const loginWith = (provider: string): void => {
    window.location.href = `/api/auth/${provider}/redirect`;
};

// Efetua a submissão das credenciais via sessão por cookie
const submit = async (payload: { email: string; password: string; remember: boolean }): Promise<void> => {
    if (loading.value) return;
    loading.value = true;
    error.value = '';

    try {
        // apiPostRoute executa o POST (cookies/CSRF já incluídos) e retorna response.data.
        // Ele NÃO lança em erro de HTTP: retorna null (erro de rede/servidor, ex.: 401/422)
        // ou false (rota inválida). Por isso ramifique pelo valor de retorno — não use e.response.
        const res = await apiPostRoute('/api/login', payload);
        if (!res || (res as any).errors) {
            error.value = (res as any)?.message
                ?? 'Falha na autenticação. Verifique suas credenciais.';
            return;
        }

        // Limpa chaves locais obsoletas e recarrega o usuário pela store MaxPinia
        localStorage.removeItem('selected.client.id');
        userStore.reload();

        router.push({ name: 'projects' });
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped lang="scss">
// Sem cores fixas: use tokens/variáveis do tema (presetMaxUno / CSS vars).
.btn-google {
    --bg: var(--surface-0);
    --border-color: var(--border-base);
    color: var(--text-default);
    &:hover {
        background-color: var(--surface-100) !important;
    }
}
</style>
```

### Exemplo 3: Logout
```typescript
import { apiPostRoute } from '@maxvue/max-use';

// Encerra a sessão no backend e limpa o estado local.
// apiPostRoute executa o POST e já trata o erro (retorna null) — não embrulhe em axios.post.
async function logout(router: any, userStore: any): Promise<void> {
    try {
        await apiPostRoute('/api/logout');
    } finally {
        localStorage.removeItem('selected.client.id');
        // O plugin MaxPinia injeta clearAll() (não `clear`) para limpar cache + estado.
        if (typeof userStore.clearAll === 'function') await userStore.clearAll();
        router.push({ name: 'login' });
    }
}
```
