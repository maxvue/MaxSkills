---
name: vue-tenant-client-context-best-practices
description: Use when designing, implementing, or reviewing tenant/client active context selection and state isolation in Vue 3 frontend, managing useSelectedClient store via @maxvue/max-pinia, persisting active client ID, or injecting the active client header into HTTP requests. Triggers on selected client changes, resetting client-dependent state stores, or configuring client workspace route guards.
---

# Boas Práticas para Contexto de Cliente Tenant no Vue 3

## Objetivo
Estabelecer um fluxo de contexto ativo do cliente (tenant) rigoroso, reativo e seguro no front-end Vue 3. Garantir o isolamento do estado entre os clientes, a parametrização das chaves de persistência local pelo ID do cliente, a injeção automática de cabeçalho HTTP e guardas globais de redirecionamento para evitar vazamento de dados ou poluição do cache ao alternar entre clientes/projetos fotovoltaicos do EngeApp.

## Instruções

### 1. Store do Cliente Selecionado (`useSelectedClientStore`)
- Separe responsabilidades em duas stores: uma store MaxPinia de GET para a **lista de clientes** (`useClientListStore`, com `isCached = ref(true)` e `options.get.route` como caminho string `'/api/clients'` — a store chama `apiGetRoute` internamente) e uma store leve para o **cliente ativo** (`useSelectedClientStore`).
- A store da lista segue o contrato canônico do `@maxvue/max-pinia`: `defineStore` importado de `pinia`, `isCached`, `data` tipado e `options` com `get`/`key`. O plugin faz o GET automaticamente ao montar e cacheia no LocalForage (NUNCA use GET manual / axios solto).
- A store do cliente ativo não faz GET: ela apenas persiste o ID selecionado no `localStorage` com uma chave global (ex: `'selected.client.id'`) e deriva o cliente atual consumindo `useClientListStore`.
- Implemente um observador (watcher) sobre `clientList.data`. Se a lista for carregada e o ID do cliente atualmente armazenado não estiver presente (ex: sessão antiga, cliente excluído ou cliente desvinculado), limpe a seleção ativa e redirecione o usuário de volta ao painel de listagem e seleção de clientes.

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

### 1a. Store da Lista de Clientes (`useClientListStore.ts`)
A lista de clientes é um GET puro ao back-end, portanto é uma store MaxPinia canônica:
declara `isCached = ref(true)`, um `data` tipado e `options.get.route` com caminho string `/api/...` (a store chama `apiGetRoute` internamente).
O plugin `@maxvue/max-pinia` faz o GET automaticamente ao montar a store e cacheia no LocalForage — nunca use `axios.get` manual.

```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface Client {
    id: string;
    name: string;
}

export const useClientListStore = defineStore('client.list', () => {
    const isCached = ref(true);
    const data = ref<Client[]>([]);

    // GET automático ao montar a store; resposta cacheada no LocalForage.
    // route é caminho string /api/...; a store chama apiGetRoute internamente.
    const options = computed(() => ({
        get: { route: '/api/clients' },
        key: 'client-list',
    }));

    return { isCached, data, options };
});
```

### 1b. Store do Cliente Selecionado (`useSelectedClientStore.ts`)
Esta store NÃO faz GET (não tem `isCached`/`options`): ela apenas mantém o ID ativo persistido em `localStorage`
e deriva o cliente atual consumindo a `useClientListStore` (que por sua vez já carrega a lista via MaxPinia).

```typescript
import { defineStore } from 'pinia';
import { ref, Ref, computed, watch } from 'vue';
import router from '@/router';
import { useClientListStore } from './useClientListStore';

export const useSelectedClientStore = defineStore('selected.client', () => {
    const STORAGE_KEY = 'selected.client.id';

    // Resolve a store da lista de forma lazy para evitar dependência circular.
    const clientList = useClientListStore();

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

    // Obtém os dados completos do cliente selecionado a partir da lista cacheada via MaxPinia
    const data = computed(() => {
        if (!id.value || !clientList.data?.length) return null;
        return clientList.data.find((c) => c.id === id.value) ?? null;
    });

    // Valida se o ID persistido ainda pertence à lista atual de clientes
    watch(
        () => clientList.data,
        (clients) => {
            if (!Array.isArray(clients) || clients.length === 0) return;
            if (!id.value) return;
            const valid = clients.some((c) => c.id === id.value);
            if (!valid) {
                setClient(null);
                router.push({ name: 'clients' });
            }
        }
    );

    return { id, data, setClient };
});
```

> A lista de clientes vem de uma store MaxPinia (`useClientListStore`) com `isCached = ref(true)` e `options.get`:
> o plugin `@maxvue/max-pinia` cuida do GET automático e do cache no LocalForage. Para stores que também escrevem,
> adicione `save: '/api/...'` (caminho string; a store chama `apiPostRoute` internamente) em `options` e o auto-save (debounce 300ms) é disparado ao alterar `data`.
> Nunca use `axios.get`/`axios.post` manuais nem o composable `useCachedApi` solto para dados de página.

### 2. Store Dependente de Cliente (`useActivePlantStore.ts`)
```typescript
import { defineStore } from 'pinia';
import { ref, Ref, watch } from 'vue';
import { useSelectedClientStore } from './useSelectedClientStore';

export const useActivePlantStore = defineStore('active.plant.store', () => {
    const _selectedClient = useSelectedClientStore();

    // Gera uma chave de cache no localStorage associada ao cliente selecionado
    function _plantKey(clientId: string | null) {
        return clientId ? `active.plant.id::${clientId}` : 'active.plant.id';
    }

    const data: Ref<any | null> = ref(null);
    const id: Ref<string | null> = ref(localStorage.getItem(_plantKey(_selectedClient.id)));

    // Salva o ID da usina no localStorage usando a chave correspondente ao cliente ativo
    watch(id, (newId: string | null) => {
        const key = _plantKey(_selectedClient.id);
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
            id.value = localStorage.getItem(_plantKey(newClientId));
            data.value = null;
        }
    );

    return { id, data };
});
```

### 3. Contexto de Tenant: injeção já embutida no MaxUse (NÃO crie axios paralelo)
Os helpers de rota do `@maxvue/max-use` (`apiGetRoute`/`apiPostRoute`/etc.) **já injetam** o cabeçalho
`X-Client-Id` (lido de `localStorage['selected.client.id']`) e já enviam `withCredentials` (sessão+cookie,
guard web — sem Bearer/JWT/Sanctum). Portanto **NÃO** monte um `axios` global paralelo com
`interceptors.request`/`response` só para injetar header/credenciais — isso duplica o que a lib já faz e cria
duas fontes de verdade.

Atenção: `setApiRequestConfig` **não** é um hook de resposta — ele aceita apenas um objeto plano
`{ headers?, withCredentials? }` (merge estático de cabeçalho/credenciais) e não expõe `onResponseError`
nem qualquer interceptor. Além disso, os helpers `apiGetRoute`/`apiPostRoute` **engolem os erros
internamente**: em qualquer falha HTTP (inclusive `403`) eles retornam `null`/`false` e o status **não é
propagado** para o chamador. Ou seja, não há como um interceptor de `403` disparar por meio da lib.

Para tratar tenant inválido/negado, detecte no código chamador (após `await`) o resultado `null`/`false`
combinado com uma revalidação fresca da `clientList` — exatamente como já é feito no `watch` de
`useSelectedClientStore`. Se sua aplicação mantiver um axios global próprio com interceptor de resposta
configurado, o `403` pode ser tratado lá; mas isso é infraestrutura da app, não do MaxUse:

```typescript
import { apiGetRoute } from '@maxvue/max-use';
import router from '@/router';

// X-Client-Id e withCredentials já são injetados pelos helpers apiGetRoute/apiPostRoute.
// Como os helpers retornam null/false em erro (status não exposto), detectamos tenant
// inválido pelo resultado nulo + revalidação da lista de clientes.
const data = await apiGetRoute('/api/clients/current');
if (data === null) {
    // Cliente ativo inválido ou negado: limpa a seleção e volta à listagem
    localStorage.removeItem('selected.client.id');
    router.push({ name: 'clients' });
}
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
import { useSelectedClientStore } from '@/stores/useSelectedClientStore';

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
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** permita vazamento de dados entre clientes. Garanta que todo estado reativo dependente do cliente ativo seja limpo imediatamente após a alternância de cliente.
- **NÃO** utilize uma chave global única de localStorage para persistir dados que são específicos do cliente. Sempre paramerize as chaves na estrutura `nome_chave::${clientId}`.
- **NÃO** gerencie o redirecionamento ou limpeza por erro 403 manualmente em cada componente de dados. Centralize esse comportamento no interceptor de resposta global.
- **NÃO** faça GET/save manual de dados de página com `axios.get`/`axios.post` ou `useCachedApi` solto. Use stores `@maxvue/max-pinia` (cache + auto-save) com rotas string via `apiGetRoute`/`apiPostRoute`.
- **NÃO** utilize a Options API para a criação de componentes ou stores. Use a Composition API (`<script setup>` e `lang="ts"`).
- **NÃO** misture estilos dinâmicos no script de componentes Vue. Utilize classes estruturadas de SCSS em blocos `<style scoped lang="scss">`.
