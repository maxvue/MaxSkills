---
name: vue-pinia-state-management-best-practices
description: "Use when creating, reviewing, or debugging Pinia stores in Vue 3 with @maxvue/max-pinia plugin. Every page-level GET MUST go through a MaxPinia store (one-shot lookups may use apiGetRoute). Covers objectives and best practices, Registro main."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Gerenciamento de Estado com Vue 3, Pinia e MaxPinia

## Objetivo
Estabelecer a arquitetura de gerenciamento de estado padrão do ecossistema Engeapp: Pinia como base e `@maxvue/max-pinia` como plugin obrigatório para todas as stores que se comunicam com o backend. **Todos os GETs ao backend devem passar por uma store MaxPinia.** O plugin cuida automaticamente de: cache offline (LocalForage), requisição GET ao montar a store, e auto-save com debounce quando os dados mudam.

---

## Instalação e Registro (main.ts)

Registre o plugin uma única vez na inicialização do Pinia:

```ts
import { createPinia } from 'pinia'
import { createMaxPinia } from '@maxvue/max-pinia'

const pinia = createPinia()

pinia.use(createMaxPinia({
  cacheName: 'pinia', // nome do banco LocalForage
  storeName: 'pinia-with-cache-plugin', // mantido para preservar o cache já existente dos usuários
  resolveRoute: (name, params) => route(name, params), // transforma o NOME de rota Ziggy em URL (ver blockquote abaixo)
  getSessionToken: () => useSystemStore().session_token, // token CSRF enviado apenas no header X-CSRF-TOKEN dos POSTs de auto-save; não vai nos GETs
  isAppStarted: () => useSystemStore().started, // controla apenas a exibição do overlay de loading; não bloqueia GET/carregamento de dados
  loading: {
    start: (o) => useLoadingStore().start(o),
    stop: (k) => useLoadingStore().stop(k),
    update: (o) => useLoadingStore().update(o),
  },
}))
```

> **Como a store resolve a rota:** internamente o plugin faz `axios.get(cfg.resolveRoute(nomeRota, dados))` no GET e `axios.post(cfg.resolveRoute(nomeRota), ...)` no save. Ele **não** chama `apiGetRoute`/`apiPostRoute` — a store só conhece o `resolveRoute` injetado aqui (o `route()` do Ziggy). Os helpers `apiGetRoute`/`apiPostRoute` de `@maxvue/max-use` servem para consultas pontuais/one-shot (busca, autocomplete, lookup, ações de comando) direto em componentes/composables, fora do fluxo de store — nunca para GET de dados de página/estado compartilhado, que deve passar por uma store MaxPinia.

---

## Instruções

### 1. Estrutura de Setup Store (Composition API)
Sempre escreva stores como Setup Stores com Composition API:
- Use o formato de arrow function: `defineStore('id-da-store', () => { ... })`.
- Exponha explicitamente tudo que precisa ser público no `return`.
- Mantenha IDs únicos, descritivos e estáveis (ex: `'user'`, `'brand.positioning.store'`).

### 2. Ativando o MaxPinia (isCached + options)
Para que o plugin `@maxvue/max-pinia` gerencie a store, é **obrigatório** declarar:
- `const isCached = ref(true)` — sinal para o plugin interceptar esta store.
- `const options = computed(() => ({ get: {...}, save: '...' }))` — configura as rotas da API (por **nome de rota Ziggy**, não caminho `/api/...`). A chave real do cache (LocalForage) é derivada exclusivamente por `getKey()` = `store.$id + '.' + (store.id ?? store.options?.id ?? 'global')` — **não** use nem dependa de `options.key`, pois o plugin ignora esse campo para compor a chave de armazenamento (ver "GET com parâmetros dinâmicos").

O plugin então:
1. Carrega dados do cache LocalForage imediatamente (instância isolada por store).
2. Faz GET ao servidor em background para revalidar.
3. Monitora `data` e dispara POST automático (debounce 300ms) quando os dados mudam (salvo se o auto-save estiver pausado ou bloqueado).

### 3. Propriedades de Status Injetadas
O plugin injeta automaticamente estas propriedades em toda store com `isCached = true`:
- `status.server.get.is_requesting` — GET em andamento.
- `status.server.get.is_requested` — GET **finalizado** (concluído, com sucesso OU erro; setado no `finally`). Não confunda com `is_requesting`.
- `status.server.get.is_success` — GET concluído **com sucesso**. É este o flag que o padrão `waitRequest` (usado nos guards de rota) observa para aguardar a 1ª carga: `waitRequest()` só resolve em sucesso, não em erro (ver `useUser.Store.ts` — `waitRequest` faz `watch(() => status.server.get.is_success)` e `router.ts` chama `user.waitRequest()`).
- `status.server.save.is_requesting` — POST/auto-save em andamento.
- `status.server.save.is_success_now` — pulso transitório (500ms) indicando que o POST concluiu com sucesso agora.
- `status.server.save.error` — erro no último save.
- `status.cache.get.is_success` — dados carregados do cache local.
- `is_done` — alias de `status.server.get.is_success`.
- `is_done_to_show` — `true` quando dados do servidor (não vazios) OU do cache estão prontos para exibição.

### 4. Métodos de Controle e Ciclo de Auto-Save Injetados
- `reload(): Promise<void>` — executa `await loadInServer()`, aguardando a conclusão da requisição HTTP e a atualização do cache local antes de resolver, e em seguida invoca `store.afterReload?.()`. **Não** limpa o estado antes do GET — o `data` antigo permanece visível até a nova resposta chegar.
- `saveInServer(): Promise<void>` — força POST imediato ao endpoint configurado em `options.save` sem esperar o debounce de 300ms, aguardando a conclusão da rede e a atualização do cache.
- `saveInCache(): Promise<void>` — persiste imediatamente `store.data` no LocalForage e aguarda a conclusão.
- `setDefaultData(): void` — restaura `store.data` para uma cópia profunda isolada do valor inicial (`default_value`) sem disparar auto-save.
- `pauseSave(): void` / `resumeSave(): void` — suspende e retoma o agendamento de auto-save (controlado por pilha de profundidade `pauseDepth`, útil para mutações em lote ou edições em modais com confirmação).
- `cancelLoad(retryInSeconds?)` — aborta o GET ativo via `AbortController` (e opcionalmente agenda nova tentativa após `retryInSeconds` segundos).
- `clearAll(): Promise<void>` — remove do LocalForage **apenas os registros associados a esta store** (chaves iguais a `store.$id` ou prefixadas por `${store.$id}.`), preservando o cache das demais stores da aplicação; **não** reseta o estado reativo em memória (para resetar `data` em memória, chame `setDefaultData()`).

### 5. Controle de Auto-Save, Listagens e Payload de Escrita
- **Desativando Auto-Save Contínuo (`block_save` / `isList`):** Se a store representa uma listagem ou um formulário que só deve persistir ao clicar em um botão "Salvar", exponha `const block_save = ref(true)` (ou aliases `no_save`, `noSave`, `blockSave`, `isList`, `is_list`). Mutações em `data` não agendarão auto-save automático, mas chamadas explícitas a `await store.saveInServer()` continuarão funcionando normalmente.
- **Customizando Payload e Retorno do POST:**
  - `getSaveData`: função ou objeto em `store` / `options.save.data` para enviar um payload customizado no lugar de `store.data`.
  - `removeToSave` / `remove_to_save`: array de caminhos (paths) a omitir do payload antes do POST.
  - `save_return`: se `true`, atualiza `store.data` com `response.data.original ?? response.data` retornado pelo POST (com `pauseSave` automático); se string (nome de campo), atualiza caso o campo tenha mudado.
  - `reload_after_save`: se `true`, dispara `loadInServer()` automaticamente após um POST bem-sucedido.
- **Modo Exclusivamente Offline (`only_cache`):** Expor `only_cache = ref(true)` (ou `options.only_cache = true`) faz a store ler e gravar apenas no IndexedDB local, sem chamar o backend.

### 6. Injeção de Dependências entre Stores (Cross-Store)
Para evitar loops de dependência circular:
- Nunca importe stores no escopo global de outro arquivo de store se isso criar importações circulares.
- Resolva stores dependentes de forma lazy dentro de ações ou computeds.

### 7. Tipagem TypeScript
- Sempre tipifique `data` explicitamente: `const data = ref<MeuTipo | null>(null)`.
- Evite `any`. Use tipos de união quando necessário: `Ref<User | null>`.

---

## Exemplos

### Store de GET somente (somente leitura do servidor)
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface User {
  id: number
  name: string
  email: string
}

export const useUserStore = defineStore('user', () => {
  const isCached = ref(true)
  const data = ref<User | null>(null)

  // route é o NOME da rota Ziggy (ex.: 'user.data').
  const options = computed(() => ({
    get: { route: 'user.data' },
  }))

  return { data, isCached, options }
})
```

### Store com GET + Auto-Save (leitura e escrita automática)
```typescript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface BrandPositioning {
  company_name: string | null
  mission: string | null
  values: string | null
  content_pillars: string[]
}

export const useBrandPositioningStore = defineStore('brand.positioning.store', () => {
  const isCached = ref(true)

  const data = ref<BrandPositioning>({
    company_name: null,
    mission: null,
    values: null,
    content_pillars: [],
  })

  // save ativa auto-save com debounce (300ms) ao alterar 'data'
  const options = computed(() => ({
    get: { route: 'brand_positioning.data' },
    save: 'brand_positioning.save',
  }))

  return { isCached, data, options }
})
```

### Uso no componente
```vue
<template>
  <div>
    <div v-if="store.status.server.get.is_requesting">Carregando...</div>
    <div v-if="store.status.server.save.is_requesting">Salvando...</div>
    <div v-if="store.is_done_to_show">
      <MaxInputText v-model="store.data.company_name" label="Nome da empresa" />
    </div>
  </div>
</template>

<script setup lang="ts">
const store = useBrandPositioningStore()
// Sem necessidade de chamar fetch() — o MaxPinia faz automaticamente ao montar a store.
// Ao editar store.data.company_name, o auto-save é disparado automaticamente com debounce.
</script>
```

### GET com parâmetros dinâmicos
Os parâmetros da rota vão em `options.get.data` (reativos). Para variar a **chave de cache** por parâmetro, exponha um `id` reativo na store (ou `options.id`): o MaxPinia deriva a chave do LocalForage por `getKey()` = `store.$id + '.' + (store.id ?? store.options?.id ?? 'global')`. Não tente variar o cache por `options.key` — o plugin não lê esse campo para a chave do cache.
```typescript
export const useProjectDataStore = defineStore('project.data', () => {
  // `id` entra em getKey() → chave de cache vira 'project.data.<id>'
  const id = computed(() => projectId.value);
  const options = computed(() => ({
    get: {
      route: 'project.data', // NOME de rota Ziggy
      data: { project_id: projectId.value }, // parâmetros reativos da rota
    },
  }));
  return { id, options /* ...demais props */ };
})
```

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NUNCA** use `axios.get()`/`fetch()` diretamente; GETs de DADOS DE PÁGINA/ESTADO COMPARTILHADO devem passar por uma store MaxPinia com `isCached = true`. Consultas pontuais/one-shot (busca, autocomplete, lookup, ações de comando) podem usar `apiGetRoute` direto em componentes/composables.
- **NUNCA** use Options API nas stores (sem `state`, `getters`, `actions`). Use exclusivamente Setup Stores.
- **NUNCA** escreva `setInterval` ou watchers manuais para sincronizar dados com o backend — o `@maxvue/max-pinia` cuida do debounce e auto-save via `options.save`.
- Substituir `data.value` inteiro por um objeto novo é seguro e é o que o próprio plugin faz a cada carga (`store.data = response.data`); a troca é detectada pelo watcher de auto-save (`cloneDeep` + `isEqual`) e dispara o debounce normalmente.
- **NÃO** omita `isCached` ou deixe como `false` em stores que precisam de sincronização com o servidor.
