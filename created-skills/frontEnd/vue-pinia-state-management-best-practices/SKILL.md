---
name: vue-pinia-state-management-best-practices
description: "Use when creating, modifying, reviewing, or debugging Pinia stores in Vue 3, managing global state, or integrating API data fetching with the @maxvue/max-pinia plugin. ALL frontend GET requests MUST go through a MaxPinia store — never fetch directly in components. Triggers on defineStore, isCached, options with get/save routes, status.server, auto-save with debounce and offline cache."
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
  cacheName: 'engeapp-cache', // nome do banco LocalForage
  getSessionToken: () => useSystemStore().session_token, // token CSRF/sessão enviado em cada requisição
  isAppStarted: () => useSystemStore().started, // evita carregamentos prematuros antes do app inicializar
  loading: {
    start: (o) => useLoadingStore().start(o),
    stop: (k) => useLoadingStore().stop(k),
    update: (o) => useLoadingStore().update(o),
  },
}))
```

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
- `const options = computed(() => ({ get: {...}, save: '...' }))` — configura as rotas da API. (Não use `key`: o plugin **nunca** lê `options.key`. A chave de cache é derivada de `store.$id` + `store.id`/`store.options.id` via `getKey()`.)

O plugin então:
1. Carrega dados do cache LocalForage imediatamente.
2. Faz GET ao servidor em background para revalidar.
3. Monitora `data` e dispara POST automático (debounce 300ms) quando os dados mudam.

### 3. Propriedades de Status Injetadas
O plugin injeta automaticamente estas propriedades em toda store com `isCached = true`:
- `status.server.get.is_requesting` — GET em andamento.
- `status.server.get.is_requested` — GET **finalizado** (concluído, com sucesso OU erro; setado no `finally`). É este o flag para aguardar a 1ª carga (padrão `waitRequest` usado nos guards de rota) — não confunda com `is_requesting`/`is_success`.
- `status.server.get.is_success` — GET concluído **com sucesso**.
- `status.server.save.is_requesting` — POST/auto-save em andamento.
- `status.server.save.error` — erro no último save.
- `status.cache.get.is_success` — dados carregados do cache local.
- `is_done` — `true` quando o GET ao servidor teve sucesso (equivale a `status.server.get.is_success`).
- `is_done_to_show` — `true` quando dados do servidor OU do cache estão prontos para exibição.

### 4. Métodos de Controle Injetados
- `reload()` — limpa o estado anterior e força novo GET ao servidor.
- `cancelLoad(retryInSeconds?)` — aborta o GET ativo.
- `clearAll()` — limpa TODO o cache LocalForage (de todas as stores, via `localforage.clear()`); **não** reseta o estado reativo desta store. Para limpar apenas o estado da store, use `setDefaultData`/`reload`.
- `saveInServer()` — força POST imediato sem esperar o debounce.
- `saveInCache()` — persiste imediatamente no LocalForage.

### 5. Injeção de Dependências entre Stores (Cross-Store)
Para evitar loops de dependência circular:
- Nunca importe stores no escopo global de outro arquivo de store se isso criar importações circulares.
- Resolva stores dependentes de forma lazy dentro de ações ou computeds.

### 6. Tipagem TypeScript
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

  // route é caminho string /api/...; a store chama apiGetRoute internamente. Sem rotas nomeadas estilo Ziggy.
  const options = computed(() => ({
    get: { route: '/api/user' },
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

  // route/save são caminhos string /api/...; a store chama apiGetRoute/apiPostRoute internamente.
  // save ativa auto-save com debounce de 300ms ao alterar 'data'
  const options = computed(() => ({
    get: { route: '/api/brand-positioning' },
    save: '/api/brand-positioning',
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
// Ao editar store.data.company_name, o auto-save é disparado em 300ms automaticamente.
</script>
```

### GET com parâmetros dinâmicos
Para variar a chave de cache por parâmetro dinâmico, defina `options.id` (ou um `id` top-level na store) — NÃO use `key`, que é ignorado. A chave final é `store.$id + '.' + (store.id ?? store.options?.id ?? 'global')`.
```typescript
const options = computed(() => ({
  get: {
    route: '/api/project', // caminho string; a store executa apiGetRoute internamente
    data: { project_id: projectId.value }, // parâmetros reativos
  },
  id: `project-${projectId.value}`, // varia a chave de cache via getKey()
}))
```

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NUNCA** faça GET direto com `axios.get()` ou `fetch()` em componentes ou services — todo GET ao backend deve passar por uma store MaxPinia com `isCached = true`.
- **NUNCA** use Options API nas stores (sem `state`, `getters`, `actions`). Use exclusivamente Setup Stores.
- **NUNCA** escreva `setInterval` ou watchers manuais para sincronizar dados com o backend — o `@maxvue/max-pinia` cuida do debounce e auto-save via `options.save`.
- **NUNCA** substitua diretamente `data.value` por um objeto totalmente novo se isso quebrar a reatividade. Prefira `Object.assign(data.value, novosDados)` para manter as referências reativas.
- **NÃO** omita `isCached` ou deixe como `false` em stores que precisam de sincronização com o servidor.
- **NÃO** importe stores no escopo global de outros arquivos de store se isso criar dependências circulares. Resolva lazy dentro de ações ou computeds.

### Migração de `piniaWithCache` para `@maxvue/max-pinia`
Se encontrar stores usando o plugin legado `piniaWithCache`:
1. Substitua `pinia.use(piniaWithCache)` por `pinia.use(createMaxPinia({...}))` no `main.ts`.
2. A estrutura das stores (`data`, `isCached`, `options`) é 100% compatível — não precisa modificar as stores em si.
