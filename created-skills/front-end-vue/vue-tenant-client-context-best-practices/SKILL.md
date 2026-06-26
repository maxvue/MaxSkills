---
name: vue-tenant-client-context-best-practices
description: Use when designing, implementing, or reviewing tenant/client active context selection and state isolation in Vue 3 frontend, managing useSelectedClient store via @maxvue/max-pinia, persisting active client ID, or injecting the active client header into HTTP requests. Triggers on selected client changes, resetting client-dependent state stores, or configuring client workspace route guards.
---

# Boas Práticas para Contexto de Cliente Tenant no Vue 3

## Objetivo
Estabelecer um fluxo de contexto ativo do cliente (tenant) rigoroso, reativo e seguro no front-end Vue 3. Garantir o isolamento do estado entre os clientes, a parametrização das chaves de persistência local pelo ID do cliente, a injeção automática de cabeçalho HTTP e guardas globais de redirecionamento para evitar vazamento de dados ou poluição do cache ao alternar entre clientes/projetos fotovoltaicos do EngeApp.

## Instruções

### 1. Store do Cliente Selecionado (`useSelectedClientStore`)
- Crie uma store `@maxvue/max-pinia` centralizada para gerenciar o cliente atualmente ativo.
- Persista o ID do cliente selecionado no `localStorage` utilizando uma chave global (ex: `'selected.client.id'`).
- Busque a lista de clientes disponíveis no back-end via store MaxPinia apontando para `apiGetRoute('/api/clients')` (NUNCA via GET manual / axios solto). O MaxPinia faz o cache da resposta automaticamente.
- Implemente um observador (watcher) na lista de clientes. Se a lista for carregada e o ID do cliente atualmente armazenado não estiver presente (ex: sessão antiga, cliente excluído ou cliente desvinculado), limpe a seleção ativa e redirecione o usuário de volta ao painel de listagem e seleção de clientes.

### 2. Isolamento de Estado do Cliente & Resets Reativos
- Qualquer store `@maxvue/max-pinia` que contenha dados específicos de um cliente (ex: usinas, projetos fotovoltaicos, propostas, inversores, dados de geração) deve isolar o seu estado por cliente.
- **Chaves de Cache Parametrizadas**: Parametrizar o `localStorage` ou chaves de cache utilizando o ID do cliente ativo (ex: `resource.key::${clientId}`).
- **Watchers Reativos**: Observar as mudanças de ID do cliente de `useSelectedClientStore` dentro das stores dependentes. Quando o ID do cliente mudar:
  - Resete todos os valores reativos da store para seus estados iniciais vazios (ex: `null`, `[]` ou objetos vazios) para evitar a exibição de dados antigos (stale).
  - Recarregue o ID ou configuração armazenada usando a nova chave de cache específica do cliente.
  - Dispare automaticamente o recarregamento dos recursos do cliente a partir do back-end (através da store MaxPinia correspondente) se um cliente válido estiver selecionado.

### 3. Injeção de Cabeçalho na Requisição & Validação de Sessão
- Use interceptores globais do cliente HTTP para anexar de forma transparente o ID do cliente ativo às requisições enviadas. O auth é por sessão+cookie (guard web), portanto envie credenciais (cookies) e NÃO use Bearer/JWT/Sanctum.
- **Interceptor de Requisição**: Recupere o ID do cliente ativo do `localStorage` e injete-o como o cabeçalho HTTP `X-Client-Id`.
- **Interceptor de Resposta**: Intercepte respostas HTTP `403 Forbidden`. Se ocorrer um erro `403` e a requisição continha o cabeçalho `X-Client-Id`:
  - Remova o ID do cliente ativo do `localStorage` (já que ele não é mais válido ou acessível).
  - Limpe o estado da store do cliente selecionado.
  - Redirecione o usuário para a página de listagem de clientes (`/clients`).

### 4. Sincronização do Vue Router & Guardas de Layout
- Sincronize o contexto do cliente selecionado no componente de layout do workspace (ex: `ClientWorkspacePage.vue`).
- Crie um watcher no parâmetro de rota `clientId`. Quando o parâmetro mudar, atualize o ID do cliente ativo na store através de `selectedClient.setClient(clientId)`.
- Habilite rotas de workspace com guardas de navegação apropriados para garantir que um cliente seja selecionado antes de acessar qualquer rota de trabalho.

---

## Exemplos

### 1. Store do Cliente Selecionado (`useSelectedClientStore.ts`)
```typescript
import { defineStore } from 'pinia';
import { ref, Ref, computed, watch } from 'vue';
import router from '@/Js/router';

export const useSelectedClientStore = defineStore('selected.client', () => {
    const STORAGE_KEY = 'selected.client.id';

    // Inicializa o ID do cliente a partir do localStorage
    const id: Ref<string | null> = ref(localStorage.getItem(STORAGE_KEY));

    // Modifica o cliente selecionado e sincroniza no localStorage
    function setClient(clientId: string | null) {
        id.value = clientId;
        if (clientId) {
            localStorage.setItem(STORAGE_KEY, clientId);
        } else {
            localStorage.removeItem(STORAGE_KEY);
        }
    }

    // Lista de clientes buscada do servidor
    const list = useCachedApi<any[]>('/api/clients', { defaultValue: [] });

    // Obtém os dados completos do cliente selecionado com base na lista
    const data = computed(() => {
        if (!id.value || !list.value?.length) return null;
        return (list.value as any[]).find((c: any) => c.id === id.value) ?? null;
    });

    // Valida se o ID persistido ainda pertence à lista atual de clientes
    watch(
        () => list.value,
        (clients) => {
            if (!Array.isArray(clients) || clients.length === 0) return;
            if (!id.value) return;
            const valid = clients.some((c: any) => c.id === id.value);
            if (!valid) {
                setClient(null);
                router.push({ name: 'clients' });
            }
        }
    );

    return { id, data, list, setClient };
});
```

### 2. Store Dependente de Cliente (`useSocialMediaAgent.Store.ts`)
```typescript
import { defineStore } from 'pinia';
import { ref, Ref, computed, watch } from 'vue';
import { useSelectedClientStore } from './useSelectedClient.Store';

export const useSocialMediaAgentStore = defineStore('social.media.agent.store', () => {
    const _selectedClient = useSelectedClientStore();

    // Gera uma chave de cache no localStorage associada ao cliente selecionado
    function _agentKey(clientId: string | null) {
        return clientId ? `social_media.agent.id::${clientId}` : 'social_media.agent.id';
    }

    const data: Ref<any | null> = ref(null);
    const id: Ref<string | null> = ref(localStorage.getItem(_agentKey(_selectedClient.id)));

    // Salva o ID do agente no localStorage usando a chave correspondente ao cliente ativo
    watch(id, (newId: string | null) => {
        const key = _agentKey(_selectedClient.id);
        if (newId) {
            localStorage.setItem(key, newId);
        } else {
            localStorage.removeItem(key);
        }
    });

    // Reseta o estado local e carrega o id correspondente ao novo cliente ao trocar de cliente ativo
    watch(
        () => _selectedClient.id,
        (newClientId) => {
            id.value = localStorage.getItem(_agentKey(newClientId));
            data.value = null;
        }
    );

    return { id, data };
});
```

### 3. Interceptores do Axios para o Contexto de Tenant
```typescript
import axios from 'axios';
import router from '@/Js/router';

// Configurações padrão de credenciais
axios.defaults.withCredentials = true;
axios.defaults.withXSRFToken = true;

// Injeta o cabeçalho X-Client-Id em todas as requisições de saída
axios.interceptors.request.use((config) => {
    const clientId = localStorage.getItem('selected.client.id');
    if (clientId) {
        config.headers['X-Client-Id'] = clientId;
    }
    return config;
});

// Trata respostas HTTP globais de autorização e tenant inválido
axios.interceptors.response.use(
    (response) => response,
    (error) => {
        // Redireciona para o login caso a sessão tenha expirado (401)
        if (error?.response?.status === 401) {
            const currentPath = window.location.pathname;
            if (currentPath !== '/login' && currentPath !== '/register') {
                router.push({ name: 'login' });
            }
        }

        // Limpa a seleção do cliente e redireciona caso o cliente ativo seja inválido ou negado (403)
        if (error?.response?.status === 403 && error?.config?.headers?.['X-Client-Id']) {
            localStorage.removeItem('selected.client.id');
            router.push({ name: 'clients' });
        }

        return Promise.reject(error);
    }
);
```

### 4. Sincronização do Workspace no Componente Layout
```vue
<template>
  <div class="client-workspace" id="client-workspace">
    <div class="workspace-content">
      <RouterView />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useSelectedClientStore } from '@/Stores/UserStores/useSelectedClient.Store';

const vueRoute = useRoute();
const selectedClient = useSelectedClientStore();

const clientId = computed(() => vueRoute.params.clientId as string);

// Sincroniza o cliente selecionado na store ao navegar
watch(clientId, (id) => {
    if (id) {
        selectedClient.setClient(id);
    }
}, { immediate: true });
</script>

<style scoped lang="scss">
.client-workspace {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.workspace-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0 2rem 1.5rem;
}
</style>
```

---

## Restrições
- **NÃO** permita vazamento de dados entre clientes. Garanta que todo estado reativo dependente do cliente ativo seja limpo imediatamente após a alternância de cliente.
- **NÃO** utilize uma chave global única de localStorage para persistir dados que são específicos do cliente. Sempre paramerize as chaves na estrutura `nome_chave::${clientId}`.
- **NÃO** gerencie o redirecionamento ou limpeza por erro 403 manualmente em cada componente de dados. Centralize esse comportamento no interceptor de resposta global do Axios.
- **NÃO** utilize a Options API para a criação de componentes ou stores. Use a Composition API (`<script setup>` e `lang="ts"`).
- **NÃO** misture estilos dinâmicos no script de componentes Vue. Utilize classes estruturadas de SCSS em blocos `<style scoped lang="scss">`.
