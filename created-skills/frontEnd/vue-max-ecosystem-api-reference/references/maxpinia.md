# MaxPinia — Catálogo de API (`@maxvue/max-pinia`)

> Referência extraída do código-fonte (`/home/johnattas/GitHub/MaxPinia`, README + `src`). Descrições em pt-BR.
>
> **Aviso de contrato**: não existe interface `options` exportada — o formato de `options` é convenção,
> resolvida por resolvers que aceitam aliases (camelCase/kebab/snake) e paths aninhados. A `key` real de
> cache é `store.$id + '.' + (store.id ?? 'global')`, **não** `options.key` (o `key` do README é ilustrativo).
> Debounce de auto-save = **300 ms**.

---

# @maxvue/max-pinia — Referência de API

Plugin do **Pinia** que adiciona a stores setup: cache offline (localforage) com estratégia cache-first, GET automático ao montar, POST com auto-save debounced (300 ms), deduplicação de requisições concorrentes e status reativo completo. O pacote é 100% desacoplado: nada de `process.env` nem imports de stores/serviços do app — tudo é injetado via config no boot.

Fonte: `README.md`, `src/types.ts`, `src/index.ts`, `src/plugin.ts`, `src/helpers/internal.ts`.

## Instalação

Pacote: `@maxvue/max-pinia`.

```bash
npm install @maxvue/max-pinia
```

Peer deps (de `README.md`): `vue ^3.5`, `pinia ^3`, `axios ^1`, `@vueuse/core ^14`. Dependências internas usadas no código: `localforage`, `lodash-es`, `ulid`.

Registro no Pinia via `pinia.use(createMaxPinia(config))`:

```ts
import { createPinia } from 'pinia';
import { createMaxPinia } from '@maxvue/max-pinia';

const pinia = createPinia();

pinia.use(createMaxPinia({
    cacheName: 'app',
    // adapters opcionais — específicos do seu app
    getSessionToken: () => useSystemStore().session_token,
    isAppStarted:    () => useSystemStore().started,
    loading: {
        start:  (o) => useLoadingStore().start(o),
        stop:   (k) => useLoadingStore().stop(k),
        update: (o) => useLoadingStore().update(o),
    },
}));
```

`createMaxPinia(userConfig?: MaxPiniaConfig)` retorna um `PiniaPlugin`. O `axios` é resolvido de forma lazy: se `config.axios` não for fornecido, o pacote importa dinamicamente o `axios` global (`(await import('axios')).default`).

### `MaxPiniaConfig` (config de boot)

| Campo | Tipo | Default | Descrição |
|---|---|---|---|
| `cacheName` | `string` | `'pinia'` | Nome do banco localforage (`localforage.config({ name, storeName: 'max-pinia-cache' })`). |
| `axios` | `AxiosInstance` | axios global (lazy) | Instância axios a usar. |
| `getSessionToken` | `() => string \| null \| undefined` | `() => null` | Token CSRF/session enviado no header `X-CSRF-TOKEN` dos POSTs. |
| `isAppStarted` | `() => boolean` | `() => true` | Gate para exibir loading. |
| `loading` | `LoadingAdapter` | `{}` | Adapter de UI de loading `{ start?, stop?, update? }` (todos opcionais). |
| `requestTimeout` | `number` | `15000` | Timeout das requisições (ms), aplicado a GET e POST. |

## Contrato do store (isCached + options)

O plugin só age quando a store declara opt-in de cache. Na função `maxPiniaPlugin`, o guard é:

```ts
if (!store.isCached && !store.is_cached) return {};
```

Ou seja, a store deve expor `isCached` (ou `is_cached`) como ref verdadeira. Além disso deve expor um estado `data` (que é lido para `default_value` e depois zerado para `{}` no boot) e, tipicamente, um `options` (aceito como ref ou objeto plano — os campos são resolvidos com `store.options?.x`).

`options` **não** é definido por uma interface exportada no `types.ts`; seu formato é uma **convenção** lida por resolvers em `plugin.ts` que aceitam múltiplos aliases (camelCase / kebab-case / snake_case) e paths aninhados. Campos efetivamente lidos da fonte:

### GET

- **Rota** — via `getRouteName()`, resolvida (primeiro não-nulo) dentre:
  `options.get.route`, `options.get.get`, `options.get`, `options.get_route`, `options.route_get`, `options.route`.
  A rota é uma **string de path plano** (ex.: `'/user/data'`). `options.get` pode ser um objeto `{ route }` ou a própria string.
- **Params/query** — via `getRouteData()`: `store.get_data` ?? `store.data_get` ?? `store.options?.get?.data` ?? `{}`. Cada valor é desembrulhado (`.value ?? valor`) e anexado como query string por `buildUrl(url, params)`.
- **Não há `immediate` explícito**: o GET dispara automaticamente no boot via `loadInCache()` (que chama `loadInServer()`), no watcher `immediate: true` de `[store.id, store.enabled, store.options?.enabled]`.

### SAVE (POST) — debounce **300 ms**

- **Rota** — via `postRouteName()`, resolvida dentre:
  `options.save`, `options.post`, `options.route_post`, `options.post_route`, `options.save_route`, `options.route_save`, e também os aliases de topo `save`, `post`, `route_post`, `post_route`, `save_route`, `route_save`.
  Path plano (string), ex.: `'/user/save'`.
- **Payload** — via `getPostData()`: `store.getSaveData` ?? resolver sobre `post_data`, `data_post`, `options.post.data`, `options.post_data`, `options.data_post`, `saveData`, `data_save`, `options.save.data`, `options.saveData`, `options.data_save`. Pode ser função (é chamada) e cada campo é desembrulhado com `toValue`. Se nada disso existir, envia `{ ...store.data }`.
- **Debounce**: `watchDebounced(() => countChanges.value, () => saveInServer(), { debounce: 300 })` — confirmado **300 ms** (constante literal em `plugin.ts`).

### key

Não é lido de `options.key` diretamente para a chave de cache. A chave de cache é derivada:

```ts
const key = computed(() => store.$id + '.' + (store?.id ?? store.options?.id ?? 'global'));
```

Ou seja, `"<$id>.<id | options.id | 'global'>"`. (O `key: 'user'` do exemplo do README é apenas ilustrativo do contrato; o plugin usa `$id` + `id`.)

### Outros campos de convenção reconhecidos em `store`/`options`

| Campo(s) / aliases | Efeito |
|---|---|
| `enabled` / `options.enabled` | Se `false`, GET/POST/save-cache são abortados; ao mudar re-dispara o boot. `loading_options.enabled` também gateia o loading. |
| `only_cache` / `cache_only` (e em `options`) | Quando true, para no cache e não vai ao servidor (`checkOnlyCache()`). |
| `in_deduplication` / `in_get_deduplication` / `in_post_deduplication` / `in_save_deduplication` (e em `options`) | Estratégia de dedup: `'last'`\|`'cancel'`\|`'this'` (aborta a requisição anterior) ou `'ignore'`\|`'first'` (ignora a nova). Default `'last'`. |
| `includeCache` / `includeInCache` / `inCache` / `cacheInclude` (e variações em `options`, incl. `options.saveInCache`) | Lista de chaves extras da store a persistir/reidratar junto do `data` no cache (`getIncludes()`). |
| `isShallow` / `is_shallow` (e `options.isShallow`) | Modo shallow: reseta `data` para null antes de reatribuir ao carregar. |
| `block_save` / `no_save` / `noSave` / `blockSave` / `isList` / `is_list` | Bloqueia o auto-save (não incrementa `countChanges`). |
| `removeToSave` / `remove_to_save` | Lista de paths removidos (`unset`) do payload antes do POST. |
| `save_return` | `true` → substitui `data` por `response.data.original ?? response.data`; string → substitui se aquele campo mudou. |
| `reload_after_save` (+ `reload_after_save_default`) | Refaz GET após POST bem-sucedido. |
| `afterLoad` / `afterReload` / `getSaveData` | Hooks/callbacks chamados pela store. |
| `loading_options` (`{ target?, message?, enabled? }`) / `loading_target` | Controle do adapter de loading; sem `message` o loading não inicia. |
| `cache_name` (ref) | Sobrescreve o nome do banco localforage por store. |

## Propriedades e métodos injetados

Todo store cacheado passa a expor (retornados pelo plugin e/ou declarados em `PiniaCustomProperties`):

### `status: Status` (objeto reativo)

Estrutura (`useDefaultReset<Status>(...)`):

```
status.server.get   : OperationStatus
status.server.save  : OperationStatus
status.cache.get    : OperationStatus
status.cache.save   : OperationStatus
```

Cada `OperationStatus` tem os campos:

```ts
interface OperationStatus {
    is_requesting: boolean;
    is_requesting_now: boolean;   // true e volta a false após 500 ms
    is_requested: boolean;
    is_blank?: boolean;           // presente em get (server/cache); resposta/cache vazio
    is_success: boolean;
    is_success_now: boolean;      // true e volta a false após 500 ms
    is_error: boolean;
    error: any;
}
```

`is_requesting_now` / `is_success_now` são pulsos: espelham o estado e são zerados por `setTimeout(..., 500)`. Toda mudança de `status` dispara um `CustomEvent('status-updated', { detail: status.value, bubbles: true })` em `document`.

### Métodos e propriedades

| Nome | Assinatura | Propósito |
|---|---|---|
| `reload()` | `() => Promise<void>` (declarado `() => void`) | Reexecuta `loadInServer()` e chama `store.afterReload?()`. |
| `saveInServer()` | `() => void` (async) | POST manual imediato para a rota de save com o payload resolvido; atualiza `status.server.save`, salva no cache, aplica `save_return`/`reload_after_save`. |
| `saveInCache()` | `() => Promise<void>` | Persiste `{ data, ...includeInCacheValues }` no localforage sob a chave da store; atualiza `status.cache.save`. Aceita `data_save` opcional interno. |
| `clearAll()` | `() => Promise<void>` | `localforage.clear()` — limpa **todo** o banco de cache. |
| `cancelLoad(retryInSeconds?)` | `(retryInSeconds?: number \| boolean \| null) => void` | Aborta o GET em voo. Se `true`/`0` → reagenda em 50 ms; se número > 0 → reagenda `loadInServer()` após esse tempo (ms). |
| `setLoadingMessage(message)` | `(message: string) => void` | Emite `loading.update({ target, key, message })` via adapter. |
| `status` | `Status` | Ver acima. |
| `is_done_to_show` | `ComputedRef<boolean>` | `(server.get.is_success && !server.get.is_blank) \|\| cache.get.is_success` — pronto para renderizar (servidor ok não-vazio, ou cache ok). |
| `is_done` | `ComputedRef<boolean>` (retornado pelo plugin) | `server.get.is_success`. |
| `default_value` | `any` | Snapshot (cloneDeep) do `data` inicial da store, capturado no boot. |
| `countChanges` | `number` (ref) | Contador de mudanças válidas em `data`; alimenta o debounce de save. |
| `is_save_in_pause` | `boolean` (ref) | Flag que suspende o auto-save durante reidratações. |
| `key` | `ComputedRef<string>` | Chave de cache `"<$id>.<id\|'global'>"`. |
| `idx` | `any` (ref) | Espelha `store.id` no boot / troca de id. |

## Ciclo de vida / comportamento

Sequência exata a partir do boot do plugin (função `maxPiniaPlugin`):

1. **Guard**: se `!store.isCached && !store.is_cached`, retorna `{}` (não injeta nada).
2. **Setup**: configura localforage (`name: cacheName`, `storeName: 'max-pinia-cache'`), captura `default_value = cloneDeep(store.data)` e zera `store.data = {}`. Cria `status` e todos os watchers de pulso (500 ms) e o watcher que emite `status-updated`.
3. **Boot watcher** (`watch([store.id, store.enabled, store.options?.enabled], ..., { immediate: true })`): no primeiro run, pausa o save, aplica `setDefaultData()`, retoma o save, reseta `status` e — se `enabled !== false` — chama **`loadInCache()`**.
4. **Cache-first** (`loadInCache`): lê a chave via `localforage.getItem(key)`.
   - Se há `data_cache.data`, reidrata `store.data` (com `pauseSave`/`resumeSave`), reidrata as chaves de `includeInCache`. Se `only_cache` está ligado, para aqui.
   - Se cache corrompido, remove o item e segue.
   - Em seguida chama **`loadInServer()`** para revalidar (a menos que `only_cache`).
5. **Auto-GET** (`loadInServer`): resolve rota; aplica dedup se já há requisição em voo; faz `axios.get(url, { timeout, signal })`. No sucesso reidrata `store.data = response.data`, marca `server.get.is_success`, persiste no cache (`saveInCache`) e chama `store.afterLoad?()`.
6. **Auto-save debounced**: um `watch(() => cloneDeep(store.data))` incrementa `countChanges` apenas quando: save não está em pausa, valores antigo e novo são não-vazios, não estão bloqueados (`block_save`/`isList`/etc.) e são diferentes (`!isEqual`). Um **`watchDebounced(() => countChanges.value, () => saveInServer(), { debounce: 300 })`** dispara o POST **300 ms** após a última mudança.
7. **Auto-save POST** (`saveInServer`): resolve rota/payload, aplica dedup, monta headers (`X-CSRF-TOKEN` = `getSessionToken()`, `withCredentials: true`), faz `axios.post`. No sucesso: `save_return`, salva no cache, `reload_after_save`.

**Debounce**: **300 ms** (`watchDebounced ... { debounce: 300 }`).

**Deduplicação** (GET e POST usam o mesmo esquema, com `AbortController` por operação):
- `'last'` / `'cancel'` / `'this'` → aborta a requisição anterior e prossegue com a nova.
- `'ignore'` / `'first'` → ignora a nova requisição (mantém a em voo).
- Default: `'last'`.

Observação: o helper `useDefaultReset` também suporta um auto-reset por timer (debounced), mas para `status` é usado sem timer.

## Tipos

Exportados publicamente de `src/index.ts` (re-exportando de `types.ts`):

- `MaxPiniaConfig`
- `LoadingAdapter`
- `LoadingOptions`
- `Status`
- `OperationStatus`

Também exportados de `src/plugin.ts` (valores): `createMaxPinia`, `useAsyncStatus`.

Interfaces em `types.ts`: `OperationStatus`, `Status`, `LoadingOptions`, `LoadingAdapter`, `MaxPiniaConfig`; e a augmentação `declare module 'pinia' { interface PiniaCustomProperties { ... } }` (com `cancelLoad`, `reload`, `setLoadingMessage`, `clearAll`, `saveInServer`, `saveInCache`, `default_value`, `status`, `countChanges`, `is_save_in_pause`, `idx?`, `is_done?`, `is_done_to_show?`, `key?`). Reexporta `Ref` do `vue`.

Tipo interno (não exportado do pacote), em `helpers/internal.ts`: `DefaultReset<T>`.

`useAsyncStatus(): Ref<Status | null>` — hook utilitário que escuta o evento `status-updated` no `document` e devolve o último status agregado emitido por qualquer store cacheada.

## Exemplo completo

Contrato mínimo real (o plugin só precisa de `data`, `isCached` e uma rota de GET; `save` e `key` são opcionais):

```ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useUserStore = defineStore('user', () => {
    const data = ref(null);
    const isCached = ref(true);

    const options = computed(() => ({
        get:  { route: '/user/data' },  // GET automático + cache-first
        save: '/user/save',             // opcional: POST com auto-save (debounce 300ms)
        key:  'user',                   // ilustrativo; a chave real é `${$id}.${id|'global'}`
    }));

    return { data, options, isCached };
});
```

Uso do status/métodos injetados no componente:

```ts
const store = useUserStore();
store.status.server.get.is_requesting; // carregando do servidor
store.is_done_to_show;                 // pronto para renderizar (cache ou server)
store.reload();                        // refaz o GET
store.saveInServer();                  // POST imediato (fora do debounce)
await store.clearAll();                // limpa todo o cache localforage
```
