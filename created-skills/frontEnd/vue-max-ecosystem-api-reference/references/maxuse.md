# MaxUse — Catálogo de API (`@maxvue/max-use`)

> Referência extraída do código-fonte (`/home/johnattas/GitHub/MaxUse/src`). Descrições em pt-BR.
>
> **Regra de ouro**: MaxUse **re-exporta todo o VueUse** (auto-import) — use os composables do VueUse a
> partir de `@maxvue/max-use`, nunca de `@vueuse/core`. E os utilitários lodash-style vêm do objeto `_`
> — ver a seção "O objeto `_`" abaixo para a ordem real de precedência (Lodash vence em colisão de nome),
> nunca `import 'lodash'` direto.
>
> Muitos "nomes" abaixo são aliases: `useRefCachedApi` → `useCachedApi`; `useTimeAgo` → `timeAgo`;
> `refAutoReset` (MaxUse) → `useDefaultReset`; `watchTrue` → `whenever` (VueUse).

---

# MaxUse — Referência de API (`@maxvue/max-use`)

Superset interno de utilitários Vue 3 (estilo VueUse). Extraído diretamente do código-fonte em `/home/johnattas/GitHub/MaxUse/src`.

Convenções: onde o código usa `MaybeRefOrGetter<T>` (aceita valor direto, `Ref` ou getter), o valor é resolvido internamente via `toValue()`.

---

## Composables

Fonte: `src/Composables/`. Todos re-exportados no top-level de `src/index.ts`.

### useRefCached
Import: `import { useRefCached } from '@maxvue/max-use'`
Assinatura: `useRefCached<T>(key: MaybeRefOrGetter<string | number | null | undefined>, default_value: T): ToRefCached<T>`
(`ToRefCached<T>` = `[T] extends [Ref] ? T : Ref<T>`)
Propósito: cria uma `Ref` sincronizada com `localStorage`, com reatividade entre abas (via evento nativo `storage`). Persiste automaticamente ao mudar (deep watch) e re-hidrata quando a chave (dinâmica) muda. Se a chave for `null`/`undefined`, usa `'no-key'`. Faz `JSON.parse`/`JSON.stringify`; em erro de parse cai no `default_value`.
Aliases: `useRefStorage`, `useCached`, `useSharedCache`, `useStorage`.
**Exemplo**
```ts
const tema = useRefCached('app-tema', 'escuro')
tema.value = 'claro' // salva em localStorage['app-tema']

const userId = ref(42)
const config = useRefCached(computed(() => `config-${userId.value}`), {})
```

### useRefCachedApi (useCachedApi)
Import: `import { useRefCachedApi } from '@maxvue/max-use'`
Assinatura: `useCachedApi<T>(route_name: string, options?: { data_get?: any; data?: any; key?: string | null; defaultValue?: T; sync?: boolean; watch?: boolean }): ToRefCachedApi<T>`
(`ToRefCachedApi<T>` = `T extends Ref ? T : Ref<T>`)
Propósito: `Ref` com cache local (`localStorage`) que sincroniza com uma rota GET. Carrega imediatamente do cache (se existir), grava mudanças no `localStorage` (a menos que `watch: false`) e, em background, dispara `apiGetRoute(route_name, data_get)` para atualizar (a menos que `sync: false`). `key` padrão = `route_name`; `data_get` padrão = `options.data_get ?? options.data ?? {}`.
Nome canônico da função: `useCachedApi`. Aliases: `useRefCachedApi`, `useSharedCacheApi`, `useInCacheApi`.
**Exemplo**
```ts
const usuarios = useCachedApi<Usuario[]>('api.usuarios.index', {
  defaultValue: [],
  data: { ativo: true }
})
const config = useCachedApi<Config>('api.config', { sync: false })
```

### useDateFormat (dateFormat)
Import: `import { useDateFormat } from '@maxvue/max-use'`
Assinatura: `useDateFormat(initialDate: MaybeRefOrGetter<Date | number | string | undefined | null>, format: string): UseDateFormatReturn`
Propósito: wrapper do `useDateFormat` do VueUse com fallback seguro. Se a data for inválida (`isNotValid`), formata `new Date()` no lugar. Retorna objeto reativo com a string formatada (`.value`).
Alias: `dateFormat`. (Também há `formatDate` puro re-exportado do VueUse em Helpers/VueUse.)
**Exemplo**
```ts
const formatted = useDateFormat('2026-05-24', 'DD/MM/YYYY') // .value → '24/05/2026'
```

### useTimeAgo (timeAgo)
Import: `import { useTimeAgo } from '@maxvue/max-use'`
Assinatura: `timeAgo(initialDate: MaybeRefOrGetter<Date | number | string | undefined | null>, format?: string = 'br'): UseTimeAgoReturn`
Propósito: wrapper do `useTimeAgo` do VueUse com mensagens pt-BR e vários presets. Se a data for inválida, usa `new Date()`. Formatos: `'br'` (completo pt-BR), `'abbrev'` (abreviado), `'action'` (orientado a ação — "Realizar Hoje", "Atrasado: 2 dias"), `'limit'`, `'limitAbbrev'`/`'limit_abbrev'`/`'future'`. Formato desconhecido cai em `br`.
Nome canônico: `timeAgo`. Alias: `useTimeAgo`.
**Exemplo**
```ts
const tempo = timeAgo('2026-05-20')            // .value → '4 dias'
const prazo = timeAgo('2026-05-30', 'action')  // .value → 'Realizar em 6 dias'
```

### watchTrue
Import: `import { watchTrue } from '@maxvue/max-use'`
Assinatura: `watchTrue = whenever` (alias direto do `whenever` do VueUse)
Propósito: executa o callback somente quando o `source` for truthy.
**Exemplo**
```ts
watchTrue(isReady, () => carregar())
```

### watchIfValid
Import: `import { watchIfValid } from '@maxvue/max-use'`
Assinatura: `watchIfValid<T, Immediate extends Readonly<boolean> = false>(source: WatchSource<T>, callback: (value: NonNullable<T>, oldValue: T | undefined) => void, options?: WheneverOptions<Immediate>): WatchHandle`
Propósito: watch que só dispara quando o valor é válido/não-vazio (via `isNotEmpty`). Suporta `once` (para o handle no `nextTick` após disparar). Retorna o `WatchHandle`.
Aliases: `watchValid`, `watchIsValid`, `watchIsValidComputed`, `watchComputedIsValid`.
**Exemplo**
```ts
const usuario = ref<Usuario | null>(null)
watchIfValid(usuario, (user) => console.log('carregado:', user.nome))
```

### watchDebounceIfValid
Import: `import { watchDebounceIfValid } from '@maxvue/max-use'`
Assinatura: `watchDebounceIfValid<T, Immediate extends Readonly<boolean> = false>(source: WatchSource<T>, callback: (value: NonNullable<T>, oldValue: T | undefined) => void, options?: WatchDebouncedOptions<Immediate>): WatchHandle`
Propósito: combina `watchDebounced` (VueUse) com a validação `isNotEmpty`. Aceita `debounce`, `maxWait`, `once`, etc.
Aliases: `watchDebouncedValid`, `watchDebouncedIsValid`, `watchDebounceValid`, `watchComputedDebounceValid`, `watchComputedDebounceIsValid`.
**Exemplo**
```ts
const termo = ref('')
watchDebounceIfValid(termo, (t) => buscarUsuarios(t), { debounce: 300 })
```

### useDefaultReset (refAutoReset)
Import: `import { useDefaultReset } from '@maxvue/max-use'`
Assinatura: `useDefaultReset<T>(initialData: T, timer?: number | null = null): DefaultReset<T>`
(`DefaultReset<T>` = `Ref<T> & { reset(): void; initialData?: any; timer?: number | null }`)
Propósito: `Ref` com método `reset()` que restaura ao valor inicial (clonado via JSON). Se `timer` (ms) for informado, auto-reseta após inatividade (via `watchDebounced`). Comportamentos especiais no objeto inicial: `id: 'ulid'` gera novo ULID a cada reset; `created_at: 'now'` define `new Date().toISOString()` a cada reset.
Alias: `refAutoReset`. (Atenção: o VueUse também tem `refAutoReset` — aqui o próprio helper tem precedência no `_` e nos exports.)
**Exemplo**
```ts
const form = useDefaultReset({ nome: '', email: '' })
form.value.nome = 'João'
form.reset() // volta para { nome: '', email: '' }

const msg = useDefaultReset('', 3000) // auto-reset após 3s de inatividade
```

---

## Rotas

Fonte: `src/Routes/`. Distinção importante: `getRoute` retorna **string de path** (ex: `/api/...`) ou `null`; `goToRoute` **navega**; funções `api*Route`, `getCachedApi*` e `postCachedApiIDB` **executam requisições HTTP** (axios) e retornam `Promise`.

A resolução depende de um resolver injetado via `setRouteResolver`. Nada é resolvido antes disso.

### config — setRouteResolver / setApiRequestConfig e internos
Import: `import { setRouteResolver, setApiRequestConfig } from '@maxvue/max-use'`
Exports do módulo `config.ts`:
- `setRouteResolver(resolver: RouteResolver): void` — registra o resolvedor `(name, params?) => string | null`. Deve ser chamado na inicialização. **Não faz request.**
- `setApiRequestConfig(config: ApiRequestConfig): void` — mescla config global. `ApiRequestConfig = { headers?: Record<string, string | (() => string)>; withCredentials?: boolean }`. Headers são aplicados em POST/PUT/DELETE/UPLOAD (e nos cached).
- `resolveRoute(name: string, params?: any): string` — `@internal`; resolve ou lança erro se resolver ausente/rota inexistente.
- `hasRoute(name: string): boolean` — `@internal`; true se a rota existe.
- `getConfiguredHeaders(): Record<string, string>` — `@internal`; resolve headers dinâmicos (executa funções).
- `getWithCredentials(): boolean` — `@internal`; padrão `true`.
- `resetConfig(): void` — `@internal`; reseta config (uso em testes).
- Tipos exportados: `RouteResolver`, `ApiRequestConfig`.
**Exemplo**
```ts
setRouteResolver((name, params) => {
  const routes = { 'api.usuarios.index': '/api/usuarios', 'api.usuarios.show': '/api/usuarios/:id' }
  let url = routes[name]; if (!url) return null
  if (params) for (const [k, v] of Object.entries(params)) url = url.replace(`:${k}`, String(v))
  return url
})
setApiRequestConfig({ withCredentials: true, headers: { Authorization: () => `Bearer ${getToken()}` } })
```

### getRoute (getRouteByName)
Import: `import { getRoute } from '@maxvue/max-use'`
Assinatura: `getRoute(routeName?: MaybeRefOrGetter<string | null> = null, data?: any = {}): string | null`
Propósito: **retorna a string de URL** da rota (não faz request). Retorna `null` se o nome for vazio/`isBlank` ou a rota não existir (`hasRoute`).
Alias: `getRouteByName`.
**Exemplo**
```ts
const url = getRoute('dashboard.show', { id: 7 }) // → '/dashboard/7' ou null
```

### goToRoute (goToRouteByName) + setLibraryRouter
Import: `import { goToRoute, setLibraryRouter } from '@maxvue/max-use'`
Assinaturas:
- `setLibraryRouter(router: Router): void` — registra a instância do Vue Router.
- `goToRoute(route?: MaybeRefOrGetter<string | null> = null, data?: any = {}): boolean` — **navega**. Se a rota existe no resolver, faz `router.push(url)`; senão faz `router.push({ name, params: data, query: data })`. Retorna `false` se nome vazio; lança erro se `setLibraryRouter` não foi chamado.
Alias: `goToRouteByName`.
**Exemplo**
```ts
setLibraryRouter(router)
goToRoute('usuarios.show', { id: 10 })
```

### apiRoute
Import: `import { apiRoute } from '@maxvue/max-use'`
Assinatura: `apiRoute(RouteName: string | null, data?: any = null, options?: any = null, method?: string = 'GET'): { option_load_screen: any; routeURL: string } | null`
Propósito: função base (usada pelas `api*Route`). Resolve a URL (para GET passa `data` como params; para outros métodos ignora `data` na resolução) e devolve `{ routeURL, option_load_screen }`. Retorna `null` se `RouteName` for falsy. **Não faz request** por si só.

### apiGetRoute
Import: `import { apiGetRoute } from '@maxvue/max-use'`
Assinatura: `apiGetRoute(RouteName: string | null, data?: any = {}, options?: any = null): Promise<any>`
Propósito: **GET via axios**. `data` vira params da URL. Adiciona headers configurados + `X-Client-Id` (de `localStorage['selected.client.id']`) e `withCredentials`. `options.file === true` → `responseType: 'blob'`. `options.error === false` silencia o `console.error`. Retorna `response.data` ou `null` em erro.
**Exemplo**
```ts
const usuarios = await apiGetRoute('api.usuarios.index', { ativo: true })
const pdf = await apiGetRoute('api.doc.download', { id: 1 }, { file: true })
```

### apiPostRoute
Import: `import { apiPostRoute } from '@maxvue/max-use'`
Assinatura: `apiPostRoute(RouteName: string | null, data?: any | null = null, options?: any = null): Promise<any>`
Propósito: **POST via axios** com `data` como corpo JSON. Headers: `Accept`, `Content-Type: application/json`, `X-Requested-With`, headers configurados, `X-Client-Id`. Retorna `response.data`, `null` em erro, ou `false` se a rota for inválida (`apiRoute` retornou `null`).
**Exemplo**
```ts
const novo = await apiPostRoute('api.usuarios.store', { nome: 'Ana' })
```

### apiPutRoute
Import: `import { apiPutRoute } from '@maxvue/max-use'`
Assinatura: `apiPutRoute(RouteName: string, data?: any | null = null, options?: any = null): Promise<any>`
Propósito: **PUT via axios** com corpo JSON. Mesmos headers do POST. Retorna `response.data`, `null` em erro, `false` se rota inválida.
**Exemplo**
```ts
await apiPutRoute('api.usuarios.update', { id: 1, nome: 'Ana2' })
```

### apiDeleteRoute
Import: `import { apiDeleteRoute } from '@maxvue/max-use'`
Assinatura: `apiDeleteRoute(RouteName: string | null, data?: any | null = null, options?: any = null): Promise<any>`
Propósito: **DELETE via axios**; `data` vai no campo `data` do `axios.delete` (corpo). Mesmos headers do POST. Retorna `response.data`, `null` em erro, `false` se rota inválida.
**Exemplo**
```ts
await apiDeleteRoute('api.usuarios.destroy', { id: 1 })
```

### apiUploadRoute
Import: `import { apiUploadRoute } from '@maxvue/max-use'`
Assinatura: `apiUploadRoute(RouteName: string, files?: any = null, data?: any = {}, options?: any = null): Promise<any>`
Propósito: **upload multipart POST**. Monta `FormData`: cada chave de `data` (objetos aninhados são serializados via `JSON.stringify`), e os arquivos como `files[i]`. Aceita `files` como `{ files: File[] }` ou `File[]`. Header `Content-Type: multipart/form-data`. Retorna `response.data` (ou `false` se rota inválida).
**Exemplo**
```ts
await apiUploadRoute('api.documentos.upload', [file1, file2], { pasta: 'contratos' })
```

### getCachedApi
Import: `import { getCachedApi } from '@maxvue/max-use'`
Assinatura: `getCachedApi(routeName: MaybeRefOrGetter<string | null | undefined>, dataToRequest?: MaybeRefOrGetter<any> = null, keyCache?: MaybeRefOrGetter<string | null | undefined> = null): Promise<any>`
Propósito: **GET com cache em `localStorage`**. Se houver valor cacheado na chave, retorna imediatamente sem request; senão faz o GET (via `resolveRoute` + axios, `withCredentials: true`) e grava. Chave padrão = `routeName + '_' + JSON.stringify(data)`. Retorna `null` se `routeName` vazio (`!hasContent`).
**Exemplo**
```ts
const dados = await getCachedApi('api.config', { escopo: 'app' })
```

### getCachedApiIDB
Import: `import { getCachedApiIDB } from '@maxvue/max-use'`
Assinatura: `getCachedApiIDB(routeName: MaybeRefOrGetter<string | null | undefined>, dataToRequest?: MaybeRefOrGetter<any> = null, keyCache?: MaybeRefOrGetter<string | null | undefined> = null, ttl?: number): Promise<any>`
Propósito: **GET com cache em IndexedDB** (`max_cache` / store `api_cache`). Retorna do cache se existir e não expirado; senão faz GET e grava com `timestamp`. `ttl` em ms (ausente = nunca expira). Entradas expiradas são removidas em background. Chave padrão = `routeName_JSON(params)`. Retorna `null` se `routeName` vazio (`isBlank`).
Também exporta (deste módulo): `deleteFromIDB(key: string): Promise<void>` e `clearCacheIDB(): Promise<void>`.
**Exemplo**
```ts
const dados = await getCachedApiIDB('api.relatorio', { mes: 5 }, null, 60000) // TTL 1 min
```

### postCachedApiIDB
Import: `import { postCachedApiIDB } from '@maxvue/max-use'`
Assinatura: `postCachedApiIDB(routeName: MaybeRefOrGetter<string | null | undefined>, routeParams?: MaybeRefOrGetter<any> = null, postData?: MaybeRefOrGetter<any> = null, keyCache?: MaybeRefOrGetter<string | null | undefined> = null, ttl?: number): Promise<any>`
Propósito: **POST com cache em IndexedDB** (mesmo banco/store do GET IDB). Retorna do cache se válido; senão faz POST (`routeParams` como params da URL, `postData` como corpo) com headers configurados e grava. Chave padrão = `routeName_JSON(routeParams)_JSON(postData)`. Retorna `null` se `routeName` vazio.
**Exemplo**
```ts
const r = await postCachedApiIDB('api.busca', {}, { termo: 'x' }, null, 30000)
```

---

## Helpers de Data

Fonte: `src/Helpers/Dates/`. Tipo `RefDate` = `MaybeRefOrGetter<string | number | Date | null | undefined>` (resolvido via `toValue`). Todas re-exportadas no top-level.

| Função | Assinatura | Descrição |
| --- | --- | --- |
| `now` | `now(): number` | Timestamp atual em ms (`Date.now()`), estilo `_.now` do Lodash. |
| `isDate` | `isDate(valor: MaybeRefOrGetter<string \| number \| null \| undefined>): boolean` | true se o valor é uma data válida (`Date`, string ou número parseável). |
| `inDateInterval` | `inDateInterval(value: MaybeRefOrGetter<TDate>, interval: MaybeRefOrGetter<{ start: Date\|string; end?: Date\|string\|null }>): boolean` | true se a data está no intervalo `[start, end]` (`end` opcional = aberto); se data/intervalo ausente, true. |
| `isInDateInterval` | igual a `inDateInterval` | Alias de `inDateInterval`. |
| `isSameDay` | `isSameDay(dates: MaybeRefOrGetter<Date[] \| string[]>, operator?: 'and' \| 'or' = 'or'): boolean` | `'and'`: todas no mesmo dia; `'or'`: existe ao menos um dia repetido. ≤1 data → true. |
| `hasPassedHours` | `hasPassedHours(dateValue: MaybeRefOrGetter<string\|Date\|null\|undefined>, hours?: number = 1): boolean` | true se passaram mais de `hours` horas desde a data (data ausente/inválida → true). |
| `hasPassedMinutes` | `hasPassedMinutes(dateValue, minutes?: number = 1): boolean` | true se passaram mais de `minutes` minutos desde a data. |
| `hasPassedDays` | `hasPassedDays(dateValue, days?: number = 1): boolean` | true se passaram mais de `days` dias desde a data. |
| `isPast` | `isPast(dateValue: MaybeRefOrGetter<TDate>): boolean` | true se a data está no passado (ausente/inválida → false). |
| `isFuture` | `isFuture(dateValue: MaybeRefOrGetter<TDate>): boolean` | true se a data está no futuro (ausente/inválida → false). |
| `addTime` | `addTime(dateValue: MaybeRefOrGetter<TDate>, amount: MaybeRefOrGetter<number>, unit?: MaybeRefOrGetter<TUnit> = 'days'): Date \| null` | Soma/subtrai tempo (`unit`: day(s)/month(s)/year(s)/hour(s)/minute(s)/second(s)); retorna novo `Date` ou `null`. |
| `isWeekend` | `isWeekend(dateValue: MaybeRefOrGetter<TDate>): boolean` | true se a data cai em sábado (6) ou domingo (0). |
| `diffInSeconds` | `diffInSeconds(date1: RefDate, date2: RefDate): number` | Diferença absoluta em segundos (0 se inválido). |
| `diffInMinutes` | `diffInMinutes(date1, date2): number` | Diferença absoluta em minutos. |
| `diffInHours` | `diffInHours(date1, date2): number` | Diferença absoluta em horas. |
| `diffInDays` | `diffInDays(date1, date2): number` | Diferença absoluta em dias. |
| `diffInMonths` | `diffInMonths(date1, date2): number` | Diferença absoluta em meses (por ano*12 + mês). |
| `diffInYears` | `diffInYears(date1, date2): number` | Diferença absoluta em anos (por `getFullYear`). |
| `secondsAgo` | `secondsAgo(value: RefDate): number` | Segundos decorridos desde `value` até agora (0 se inválido). |
| `minutesAgo` | `minutesAgo(value: RefDate): number` | Minutos decorridos desde `value`. |
| `hoursAgo` | `hoursAgo(value: RefDate): number` | Horas decorridas desde `value`. |
| `daysAgo` | `daysAgo(value: RefDate): number` | Dias decorridos desde `value`. |
| `monthsAgo` | `monthsAgo(value: RefDate): number` | Meses (aprox. base 30 dias) decorridos desde `value`. |
| `yearsAgo` | `yearsAgo(value: RefDate): number` | Anos (aprox. base 360 dias) decorridos desde `value`. |

Obs.: `now` é re-exportado explicitamente para resolver ambiguidade (existe também `useNow`/`timestamp` no VueUse). O `timeAgo` de `Composables` (wrapper VueUse) tem precedência sobre o `secondsAgo`/etc de Dates — nomes diferentes, sem conflito.

**Exemplo**
```ts
if (hasPassedDays(user.lastLogin, 30)) reautenticar()
const vencimento = addTime(new Date(), 15, 'days')
const dias = diffInDays('2026-01-01', '2026-03-01') // 59
```

---

## Helpers de Browser

Fonte: `src/Helpers/Browser/`. Re-exportadas no top-level.

| Função | Assinatura | Descrição |
| --- | --- | --- |
| `isTouchDevice` | `isTouchDevice(): boolean` | true se o dispositivo suporta toque (`ontouchstart` / `maxTouchPoints` / `msMaxTouchPoints`). |
| `getColorFromVar` | `getColorFromVar(color_var_value: MaybeRefOrGetter<string>): ColorInstance` | Resolve uma cor a partir de valor direto, nome de var CSS (`--x`) ou `var(--x)`; retorna instância da lib `color`. Trata `!important`, `rgb`, e vars não resolvidas → `transparent`. |
| `contrastColor` | `contrastColor(color_var_value: MaybeRefOrGetter<string>): string` | Cor contrastante em hex+alpha: escurece 0.5 se a cor é clara, senão clareia 0.9. |
| `getContrastColor` | igual a `contrastColor` | Alias de `contrastColor`. |
| `getColorOpposite` | igual a `contrastColor` | Alias de `contrastColor`. |
| `getOppositeColor` | igual a `contrastColor` | Alias de `contrastColor`. |

**Exemplo**
```ts
const primaria = getColorFromVar('var(--primary-color)')
const texto = contrastColor('--primary-color') // hex contrastante
if (isTouchDevice()) habilitarGestos()
```

---

## O objeto `_` e re-export do VueUse

### Re-export completo do VueUse (auto-import)
`src/index.ts` faz `export * as vueUse from '@vueuse/core'` e `export * from './Helpers/VueUse'`. O módulo `src/Helpers/VueUse/index.ts` (+ `core.ts`) reexporta **todo o `@vueuse/core`** — como namespace `vueUse`, como re-exports de tipo (`export type *`), e como consts individuais (`useMouse`, `useDark`, `watchDebounced`, `refDebounced`, etc.). Consequência prática: **todos os composables do VueUse mantêm o mesmo nome, porém importados de `@maxvue/max-use`**:

```ts
import { useMouse, useDark, useToggle, watchDebounced } from '@maxvue/max-use'
```

O script `src/scripts/buildAutoImport.ts` gera `Helpers/autoImportData.json` (consumido por `maxUseAutoImport`) com a lista de nomes de valor (helpers próprios + VueUse + `'_'` + `'vueUse'`) e os nomes de tipo do VueUse/`@vueuse/shared`, prontos para o `unplugin-auto-import`.

### O objeto `_` (estilo Lodash)
Definido no fim de `src/index.ts` e exportado (`export const _`). É a agregação de três camadas — mas a
ordem real de precedência é **helpers próprios < VueUse < Lodash**, porque o Lodash **não é filtrado**
e entra por último no spread:

```ts
const ownHelpers = { ...Composables, ...Routes, ...Browser, ...Dates, ...Iterables,
  ...Math, ...Objects, ...Strings, ...Types, ...Validations, ...Electrical, ...Format }
// VueUse filtrado: só entram chaves que NÃO existem em ownHelpers (e nunca 'vueUse')
// Lodash NÃO é filtrado: todas as chaves do lodash-es entram por último e sobrescrevem
export const _ = { ...ownHelpers, ...filteredVueUse, ...filteredLodash }
```

Regra de resolução de nome ao acessar `_.x`:
1. Se `x` existe no Lodash → **o Lodash vence**, mesmo que exista homônimo próprio da MaxUse.
2. Senão, se `x` existe no VueUse (e não em ownHelpers) → usa o do VueUse.
3. Senão → usa o helper próprio da MaxUse.

Como o spread final é `{...ownHelpers, ...filteredVueUse, ...filteredLodash}`, e apenas o VueUse é
filtrado (`filteredVueUse` só inclui chaves ausentes de `ownHelpers`), o Lodash entra por último sem
filtro e **sobrescreve qualquer homônimo** — inclusive helpers próprios.

**Exemplo**
```ts
import { _ } from '@maxvue/max-use'

_.debounce(fn, 300)      // Lodash (não há homônimo próprio nem no VueUse)
_.cloneDeep(obj)         // Lodash
_.groupBy(lista, 'tipo') // Lodash-es (não a versão própria de MaxUse/Iterables) — Lodash vence a colisão
_.size(x)                // Lodash-es (não a versão própria de MaxUse) — mesma colisão
```

Atenção: onde MaxUse e Lodash têm o mesmo nome (`groupBy`, `size`, `filter`, `first`, `last`, `get`,
`set`, `now`, `isObject`, `uniq`, `chunk`, `sample`, `shuffle`, `sumBy`, `countBy`, `keyBy`, `orderBy`,
`sortBy`, `truncate`, `capitalize`, `camelCase`, etc.), acessar via `_` resolve para o **Lodash**, não
para a versão MaxUse. Para obter a semântica MaxUse desses nomes colidentes, use o **import nomeado**
(ex.: `import { groupBy, size } from '@maxvue/max-use'`), não `_.groupBy`/`_.size`. Alguns nomes (`now`,
`get`, `set`, `isObject`) são reexportados explicitamente pelo `index.ts` para resolver ambiguidade nos
**imports nomeados** — isso não muda a precedência dentro do objeto `_`.

---

## Exports públicos

Top-level de `src/index.ts` (`import { ... } from '@maxvue/max-use'`):

- **Namespace**: `vueUse` (`export * as vueUse from '@vueuse/core'`).
- **Composables** (`export * from './Composables'`): `useRefCached` (+aliases `useRefStorage`/`useCached`/`useSharedCache`/`useStorage`), `useCachedApi`/`useRefCachedApi` (+`useSharedCacheApi`/`useInCacheApi`), `useDateFormat`/`dateFormat`, `timeAgo`/`useTimeAgo`, `watchTrue`, `watchIfValid` (+aliases), `watchDebounceIfValid` (+aliases), `useDefaultReset`/`refAutoReset`, e os tipos `ToRefCached`, `ToRefCachedApi`, `DefaultReset`.
- **Routes** (`export * from './Routes'`): `setRouteResolver`, `setApiRequestConfig`, `resolveRoute`, `hasRoute`, `getConfiguredHeaders`, `getWithCredentials`, `resetConfig`, tipos `RouteResolver`/`ApiRequestConfig`; `apiGetRoute`, `apiPostRoute`, `apiPutRoute`, `apiDeleteRoute`, `apiUploadRoute`, `apiRoute`; `getRoute`/`getRouteByName`; `goToRoute`/`goToRouteByName`/`setLibraryRouter`; `getCachedApi`; `getCachedApiIDB` (+`deleteFromIDB`, `clearCacheIDB`); `postCachedApiIDB`.
- **Helpers modulares** (`export * from ...`): `Browser`, `Dates`, `Iterables`, `Math`, `Objects`, `Strings`, `Types`, `Validations`, `Electrical`, `Format`, `VueUse` (VueUse completo) — ver tabelas detalhadas abaixo (Iteráveis, Math, Objetos, Strings, Types, Validações).
- **Re-exports explícitos (desambiguação)**: `refAutoReset`, `useCached`, `useStorage`, `useTimeAgo`, `useDateFormat` (de Composables); `now` (de Dates); `get`, `set` (de Objects); `isObject` (de Types).
- **Auto-import**: `maxUseItems` (função → `string[]` com todos os nomes) e `maxUseAutoImport` (JSON gerado para `unplugin-auto-import`).
- **O objeto `_`**: `export const _` — ver ordem real de precedência na seção "O objeto `_`" acima.


---

# Helpers utilitários (acessíveis também via `_`)

> **Nota:** Todas as funções abaixo também são acessíveis através do objeto agregador `_` (ex.: `_.isCpf(...)`, `_.formatCurrency(...)`), mas cuidado com colisão de nome com Lodash — ver a ordem real de precedência na seção "O objeto `_`" acima (Lodash vence a colisão; para a semântica MaxUse de nomes colidentes, prefira o import nomeado). Os objetos de namespace (`_.Obj`, `_.Str`, `_.StrFilter`, `_.StrCase`, `_.validate`, `_.format`, `_.electrical`) também estão disponíveis. Praticamente todos os parâmetros aceitam `MaybeRefOrGetter` (valores reativos do Vue), resolvidos internamente via `toValue`.

## Helpers de Iteráveis (Iterables)

| Função | Assinatura | Descrição |
|--------|-----------|-----------|
| `countBy` | `countBy(collection: MaybeRefOrGetter<Record<string,any> \| null \| undefined>, key: string, value?: any = true): number` | Conta quantos elementos de uma coleção (array ou objeto de objetos) possuem `item[key] === value`. Retorna 0 se não for objeto. |
| `filter` | `filter(collection: MaybeRefOrGetter<Record<string,any> \| any[] \| null \| undefined>, callback: (card: any) => void): T[] \| Record<string, T>` | Filtra uma coleção por uma função callback. Preserva o tipo: array → array filtrado; objeto → objeto filtrado. Retorna `{}` se não for objeto. |
| `filterBy` | `filterBy(collection: MaybeRefOrGetter<T[] \| Record<string,T> \| null \| undefined>, key: keyof T, value?: unknown = true): T[] \| Record<string, T>` | Mantém apenas os elementos cujo `item[key] === value`. Preserva array/objeto. Retorna `[]` se não for objeto. |
| `filterByNot` | `filterByNot(collection: MaybeRefOrGetter<Record<string,any> \| any[] \| null \| undefined>, key: string, value?: any = true): T[] \| Record<string, T>` | Remove os elementos cujo `item[key]` corresponda a `value`. Se `value` for array, exclui qualquer item cujo valor esteja incluído nele. |
| `groupBy` | `groupBy<T>(collection: MaybeRefOrGetter<T[] \| Record<string,T> \| any>, iteratee: string \| ((item: T) => string \| number)): Record<string, T[]>` | Agrupa elementos por uma chave (string) ou função iteratee. Semelhante ao `_.groupBy` do Lodash. Chaves são convertidas para string. |
| `keyBy` | `keyBy(collection: MaybeRefOrGetter<T \| any[]>, key: string): Record<string, T>` | Cria um objeto indexando cada item pela sua propriedade `key`. Chaves numéricas recebem um espaço sufixo (`String(k) + ' '`) para preservar a ordem. |
| `orderBy` | `orderBy<T>(collection: MaybeRefOrGetter<T[] \| Record<string,T> \| null \| undefined>, criteria?: Criterion<T> \| Criterion<T>[], orders?: 'asc' \| 'desc' \| ('asc' \| 'desc')[]): T[]` | Ordena por um ou mais critérios (string de propriedade ou função extratora), com direção global ou por critério. `null`/`undefined` vão para o fim. Unifica `sortBy`, `sortByMulti` e `orderBy`. |
| `sortBy` | `sortBy = orderBy` | Alias de `orderBy`. |
| `sortByMulti` | `sortByMulti = orderBy` | Alias de `orderBy`. |
| `orderByWithKey` | `orderByWithKey(collection: MaybeRefOrGetter<T[] \| Record<string,T> \| null \| undefined>, criteria: keyof T \| (keyof T)[] \| { [K in keyof T]?: 'asc' \| 'desc' }, object_keyBy: keyof T, order?: 'asc' \| 'desc' = 'asc'): Record<string, T>` | Ordena a coleção pelos critérios (aceita mapa `{ chave: direção }`) e depois indexa o resultado por `object_keyBy` (combina `orderBy` + `keyBy`). |
| `sum` | `sum(collection: MaybeRefOrGetter<number[] \| any>): number` | Soma todos os valores de um array/objeto, usando `parseFloat` e ignorando `NaN`. Semelhante ao `_.sum`. |
| `sumBy` | `sumBy(collection: MaybeRefOrGetter<T[] \| Record<string,T> \| null \| undefined>, key: keyof T): number` | Soma os valores numéricos da propriedade `key` em cada item (`Number(item[key]) \|\| 0`). |
| `uniq` | `uniq<T>(array: MaybeRefOrGetter<T[] \| any>): T[]` | Retorna um array sem duplicatas (via `Set`). Retorna `[]` se não for array. Semelhante ao `_.uniq`. |
| `uniqueBy` | `uniqueBy<T>(array: MaybeRefOrGetter<T[] \| any>, key: string \| ((item: T) => any)): T[]` | Remove duplicatas de um array de objetos com base numa propriedade ou função seletora (mantém a primeira ocorrência). |
| `valuesInKey` | `valuesInKey(collection: MaybeRefOrGetter<Record<string,any> \| any[] \| null \| undefined>, key: string, default_value?: any = false): any[]` | Extrai um array achatado (flat) com os valores de `key` de cada item; arrays/objetos aninhados são expandidos. Usa `default_value` quando a chave é nula/ausente. |
| `size` | `size(value: MaybeRefOrGetter<Record<string,any> \| string \| number \| null \| undefined>, allow_number?: boolean = true): number` | Retorna o tamanho de coleção, string, objeto, Map ou Set. Se `allow_number` e valor for número, retorna o próprio número. 0 para valores em branco. |
| `sample` | `sample<T>(collection: MaybeRefOrGetter<T[] \| Record<string,T> \| any>): T \| undefined` | Retorna um elemento aleatório da coleção (`undefined` se vazia). Semelhante ao `_.sample`. |
| `shuffle` | `shuffle<T>(array: MaybeRefOrGetter<T[]>): T[]` | Retorna uma nova cópia do array embaralhada (algoritmo Fisher-Yates). |
| `chunk` | `chunk<T>(array: MaybeRefOrGetter<T[]>, size?: number = 1): T[][]` | Divide um array em sub-arrays de tamanho `size`. Retorna `[]` se vazio ou `size <= 0`. |
| `findLast` | `findLast<T>(collection: MaybeRefOrGetter<T[] \| null \| undefined>, predicate: (value: T, index: number, collection: T[]) => boolean): T \| undefined` | Retorna o último item que satisfaz o predicado, iterando de trás para frente. `undefined` se nenhum. |
| `first` | `first<T>(array: MaybeRefOrGetter<T[] \| null \| undefined>): T \| undefined` | Retorna o primeiro elemento do array de forma segura (`undefined` se vazio/não-array). |
| `getFirst` | `getFirst<T>(...values: MaybeRefOrGetter<T>[]): NonNullable<T> \| undefined` | Retorna o primeiro valor dos argumentos que passe em `hasContent` (primeiro valor "com conteúdo"). |
| `last` | `last<T>(array: MaybeRefOrGetter<T[] \| null \| undefined>): T \| undefined` | Retorna o último elemento do array de forma segura (`undefined` se vazio/não-array). |
| `objectSize` | `objectSize(object: MaybeRefOrGetter<any>): number` | Retorna o número de chaves próprias de um objeto. 0 para nulos, em branco, arrays ou não-objetos. |
| `isObjectValid` | `isObjectValid<V>(value: V): value is Object & NonNullable<V>` | Type-guard: verdadeiro se o valor for um objeto não-vazio (`objectSize > 0`). |

## Helpers de Matemática (Math)

| Função | Assinatura | Descrição |
|--------|-----------|-----------|
| `average` | `average(numbers: MaybeRefOrGetter<number[]>): number` | Calcula a média aritmética de um array de números. Retorna 0 se vazio. |
| `roundUp` | `roundUp(value: MaybeRefOrGetter<number>, decimals?: MaybeRefOrGetter<number> = 0): number` | Arredonda para cima (`Math.ceil`) com N casas decimais. |
| `roundDown` | `roundDown(value: MaybeRefOrGetter<number>, decimals?: MaybeRefOrGetter<number> = 0): number` | Arredonda para baixo (`Math.floor`) com N casas decimais. |
| `median` | `median(numbers: MaybeRefOrGetter<number[]>): number` | Calcula a mediana de um array de números (resistente a outliers). Retorna 0 se vazio; média dos dois centrais quando o tamanho é par. |

## Helpers de Objetos (Objects)

| Função | Assinatura | Descrição |
|--------|-----------|-----------|
| `deepClone` | `deepClone<T>(value: MaybeRefOrGetter<T>, map?: WeakMap = new WeakMap()): T` | Clonagem profunda tratando referências circulares, `Date`, `RegExp`, `Map`, `Set`, arrays, objetos e símbolos. Semelhante ao `_.cloneDeep`. |
| `cloneDeep` | `cloneDeep = deepClone` | Alias de `deepClone`. |
| `get` | `get<T = any>(object: MaybeRefOrGetter<any>, path: string \| string[], defaultValue?: T): T` | Obtém o valor num caminho (dot/bracket notation ou array). Retorna `defaultValue` se resolver para `undefined`. Semelhante ao `_.get`. |
| `set` | `set<T = any>(object: MaybeRefOrGetter<any>, path: string \| string[], value: any): T` | Define o valor num caminho, criando objetos intermediários se necessário. Muta e retorna o objeto. |
| `unset` | `unset(object: MaybeRefOrGetter<any>, path: string \| string[]): boolean` | Remove a propriedade num caminho. Retorna `true` se removida (ou se o caminho não existia). Semelhante ao `_.unset`. |
| `isEqual` | `isEqual(value: MaybeRefOrGetter<any>, other: MaybeRefOrGetter<any>): boolean` | Comparação profunda de equivalência, tratando `NaN`, `Date`, `RegExp`, `Map`, `Set`, arrays e objetos. Semelhante ao `_.isEqual`. |
| `deepMerge` | `deepMerge<T extends object>(target: MaybeRefOrGetter<T>, ...sources: any[]): T` | Mescla profundamente objetos aninhados. Muta e retorna o `target`. Arrays não são mesclados recursivamente (sobrescritos). |
| `renameKeys` | `renameKeys(object: MaybeRefOrGetter<Record<string,any>>, map: MaybeRefOrGetter<Record<string,string>>): Record<string, any>` | Retorna um novo objeto renomeando chaves conforme o mapa `{ chaveAntiga: chaveNova }`. Chaves ausentes no mapa são mantidas. |
| `pick` | `pick<T extends object, K extends keyof T>(obj: MaybeRefOrGetter<T>, keys: K[]): Pick<T, K>` | Retorna um novo objeto contendo apenas as chaves especificadas. |
| `omit` | `omit<T extends object, K extends keyof T>(obj: MaybeRefOrGetter<T>, keys: K[]): Omit<T, K>` | Retorna uma cópia do objeto sem as chaves especificadas. |
| `mapValues` | `mapValues<T extends object, V>(obj: MaybeRefOrGetter<T>, fn: (value: T[keyof T], key: keyof T, object: T) => V): { [K in keyof T]: V }` | Cria um novo objeto transformando os valores (via `fn`) e mantendo as chaves originais. |
| `diff` | `diff<T extends Record<string,any>>(oldObj: MaybeRefOrGetter<T \| null \| undefined>, newObj: MaybeRefOrGetter<T \| null \| undefined>, alwaysKeep?: string[] = []): Partial<T>` | Retorna apenas as propriedades alteradas entre dois objetos (útil para PATCH). `alwaysKeep` força a inclusão de certas chaves. Usa `isEqual`. |
| `keyExists` | `keyExists(keys: MaybeRefOrGetter<string \| string[]>, item: MaybeRefOrGetter<any>, mode?: 'some' \| 'every' = 'some'): boolean` | Verifica se uma ou mais chaves existem no objeto, com suporte a dot notation. `'some'` = ao menos uma; `'every'` = todas. |

> Namespace `Obj` (e `_.Obj`) agrupa todas as funções acima (incluindo `Obj.cloneDeep`).

## Helpers de Strings (Strings)

| Função | Assinatura | Descrição |
|--------|-----------|-----------|
| `Random` | `Random(arg1?: MaybeRefOrGetter<number \| Typecode> = 20, arg2?: MaybeRefOrGetter<number \| Typecode> = 'letter lower'): string` | Gera string aleatória. Os args aceitam comprimento (número) ou código de tipo (ex.: `'upper'`, `'number'`, `'letter lower'`, `'nonumber'`). Se qualquer arg incluir `'ulid'`, retorna um ULID minúsculo. |
| `ulid` | `ulid(): string` | Gera um ULID (identificador ordenável lexicograficamente) em letras minúsculas. |
| `intervalRandom` | `intervalRandom(min?: MaybeRefOrGetter<number> = 0, max?: MaybeRefOrGetter<number> = 1000): number` | Gera um número inteiro aleatório no intervalo `[min, max]`. |
| `formatCep` | `formatCep(value: MaybeRefOrGetter<string \| number \| null \| undefined>): string` | Aplica máscara de CEP (`00000-000`). Retorna `''` se em branco, ou a string original se não tiver 8 dígitos. |
| `formatCpf` | `formatCpf(value: RefString): string` | Aplica máscara de CPF (via `js-brasil`). `''` se em branco. |
| `formatCnpj` | `formatCnpj(value: RefString): string` | Aplica máscara de CNPJ (via `js-brasil`). `''` se em branco. |
| `formatCpfCnpj` | `formatCpfCnpj(value: RefString): string` | Aplica máscara de CPF ou CNPJ conforme o tamanho (via `js-brasil`). `''` se em branco. |
| `formatPhone` | `formatPhone(phone_number: RefString): string` | Formata telefone brasileiro: trata 0800, 10, 11, 12 e 13 dígitos (com prefixo 55). `''` se em branco; string original se não casar. |
| `maskSensitive` | `maskSensitive(value: RefString, type?: 'email' \| 'card' \| 'text' = 'text'): string` | Ofusca dado sensível (LGPD): e-mail (mascara usuário/domínio), cartão (`**** **** **** 1234`) ou texto (mantém 2 primeiros/últimos). |
| `onlyLetters` | `onlyLetters(value: RefString, space?: boolean = false): string` | Mantém apenas letras (inclui acentuadas); opcionalmente preserva espaços. |
| `onlyNumbers` | `onlyNumbers(value: RefString, space?: boolean = false): string` | Mantém apenas dígitos; opcionalmente preserva espaços. |
| `onlySymbols` | `onlySymbols(value: RefString): string` | Mantém apenas símbolos (remove alfanuméricos via `[^\W_]`). |
| `onlyLettersAndNumbers` | `onlyLettersAndNumbers(value: RefString, space?: boolean = false): string` | Mantém apenas letras (com acentos) e números; opcionalmente preserva espaços. |
| `removeSpaces` | `removeSpaces(value: RefString): string` | Remove todos os espaços da string. |
| `snakeCase` | `snakeCase(value: RefString): string` | Converte para `snake_case`. |
| `kebabCase` | `kebabCase(value: RefString): string` | Converte para `kebab-case`. |
| `camelCase` | `camelCase(value: RefString): string` | Converte para `camelCase`. |
| `capitalize` | `capitalize(value: RefString): string` | Primeira letra maiúscula, restante minúsculo. |
| `toSearchableString` | `toSearchableString(value: RefString): string` | Normaliza para busca: sem acentos, sem especiais, minúsculo (remove tudo que não seja `a-z0-9`). |
| `normalizeToSearch` | `normalizeToSearch = toSearchableString` | Alias de `toSearchableString`. |
| `toNumber` | `toNumber(value: RefString, decimals?: number \| null = null): number` | Converte para número; se `decimals` fornecido, arredonda para N casas. 0 se em branco/`NaN`. |
| `truncate` | `truncate(value: RefString, limit?: number = 20, suffix?: string = '...'): string` | Encurta a string em `limit` caracteres, adicionando `suffix` se exceder. |
| `slugify` | `slugify(value: RefString): string` | Gera slug amigável para URL (sem acentos/especiais, espaços → hífen). |
| `stripHtml` | `stripHtml(value: RefString): string` | Remove tags HTML e converte `&nbsp;` em espaço. Também exportado como `noHtml`. |
| `noHtml` | `noHtml = stripHtml` | Alias de `stripHtml`. |
| `initials` | `initials(value: RefString, limit?: number = 2): string` | Extrai iniciais de um nome (ex.: "João Silva" → "JS"), limitadas a `limit`. |
| `readingTime` | `readingTime(value: RefString, wordsPerMinute?: number = 200): string` | Estima o tempo de leitura ("N min de leitura"), removendo HTML antes de contar palavras. |

> Namespaces: `Str` (`Random`/`code`, `ulid`, `intervalRandom`/`interval`, `truncate`, `slugify`, `capitalize`, `noHtml`, `initials`, `readingTime`); `StrFilter` (`onlyLetters`, `onlyNumbers`, `onlyLettersAndNumbers`, `onlySymbols`, `removeSpaces`); `StrCase` (`snakeCase`, `kebabCase`, `camelCase`, `capitalize`).

## Helpers de Tipos (Types)

| Função | Assinatura | Descrição |
|--------|-----------|-----------|
| `isArray` | `isArray(value: MaybeRefOrGetter<any>): value is any[]` | Type-guard: verdadeiro se for array. Semelhante ao `_.isArray`. |
| `isObject` | `isObject(value: MaybeRefOrGetter<any>): boolean` | Verdadeiro se for objeto (inclui arrays, funções, regex; exclui `null`). Semelhante ao `_.isObject`. |
| `isNumber` | `isNumber(value: MaybeRefOrGetter<any>): boolean` | Verdadeiro se for número válido. Falso para em branco, booleanos ou `NaN`. |
| `isNumeric` | `isNumeric = isNumber` | Alias de `isNumber`. |
| `numeric` | `numeric = isNumber` | Alias de `isNumber`. |
| `isBlank` | `isBlank<V>(value: V, if_zero?: boolean = false): boolean` | Verdadeiro se o valor estiver "em branco" (inverso de `hasContent`). `if_zero=true` faz o número 0 NÃO ser considerado em branco. |
| `blank` | `blank<V>(value: V, if_zero?: boolean = false): boolean` | Alias de `isBlank`. |
| `hasContentFn` | `hasContentFn(value: MaybeRefOrGetter<any>, if_zero?: boolean = false): boolean` | Verdadeiro se o valor tiver conteúdo (não vazio/nulo/`'null'`/`'undefined'`; strings trimadas, arrays/objetos/Map/Set com itens). `if_zero` controla se 0 conta como conteúdo. |
| `hasContent` | `hasContent<V>(value: V, if_zero?: boolean = false): value is NonNullable<V>` | Type-guard sobre `hasContentFn`: restringe o tipo para `NonNullable<V>` quando tem conteúdo. |
| `canIterate` | `canIterate<T>(obj: MaybeRefOrGetter<any>): obj is Iterable<T>` | Type-guard: verdadeiro se o objeto for iterável (possui `Symbol.iterator`). |
| `isIterable` | `isIterable = canIterate` | Alias de `canIterate`. |

## Helpers de Validações (Validations)

| Função | Assinatura | Descrição |
|--------|-----------|-----------|
| `isCpf` | `isCpf(value: MaybeRefOrGetter<string \| number \| null \| undefined>): boolean` | Valida CPF (dígitos verificadores, via `js-brasil`), com ou sem máscara. |
| `isCnpj` | `isCnpj(value: RefString): boolean` | Valida CNPJ (dígitos verificadores, via `js-brasil`). |
| `isCpfCnpj` | `isCpfCnpj(value: RefString): boolean` | Valida CPF ou CNPJ, detectando automaticamente pelo tamanho. |
| _aliases de documentos_ | `cpf`, `cnpj`, `cpfcnpj`, `cpfIsValid`, `cnpjIsValid`, `cpfCnpjIsValid`, `isCpfOrCnpj`, `cpfOrCnpj`, `isCnpjOrCpf`, `cnpjOrCpf`, `isValidCpf`, `isValidCnpj`, `isValidCpfCnpj`, `isValidCpfOrCnpj`, `isValidCnpjOrCpf`, `validCpf`, `validCnpj`, `validCpfCnpj`, `validCpfOrCnpj`, `validCnpjOrCpf`, `hasValidCpf`, `hasValidCnpj`, `hasValidCpfCnpj`, `hasValidCpfOrCnpj`, `hasValidCnpjOrCpf` | Aliases de `isCpf` / `isCnpj` / `isCpfCnpj` (mesma assinatura, apenas nomes semânticos alternativos). |
| `isEmail` | `isEmail(value: MaybeRefOrGetter<string \| null \| undefined>): boolean` | Valida formato de e-mail via regex. Falso se não for string. |
| _aliases de e-mail_ | `email`, `emailIsValid`, `isValidEmail`, `hasValidEmail`, `validEmail`, `hasEmail`, `isEMail`, `eMail`, `eMailIsValid`, `isValidEMail`, `hasValidEMail`, `validEMail`, `hasEMail` | Aliases de `isEmail`. |
| `cepIsValid` | `cepIsValid(value: MaybeRefOrGetter<string \| number \| null \| undefined>): boolean` | Valida CEP (via `js-brasil`). Falso se em branco. |
| _aliases de CEP_ | `cep`, `isValidCep`, `isCepValid`, `hasValidCep` | Aliases de `cepIsValid`. |
| `phone` | `phone(value: MaybeRefOrGetter<string \| number \| null \| undefined>): boolean` | Valida telefone (via `libphonenumber-js`, país padrão BR / código 55). |
| _aliases de telefone_ | `isValidPhone`, `isPhoneValid`, `hasValidPhone`, `validPhone`, `isPhone`, `hasPhone`, `phoneIsValid` | Aliases de `phone`. |
| `notEmpty` | `notEmpty<V>(value: V): value is NonNullable<V>` | Verdadeiro se o valor não estiver vazio (`size > 0`); booleanos e números sempre `true`. |
| `isNotEmpty` | `isNotEmpty<V>(value: V): value is NonNullable<V>` | Alias semântico de `notEmpty`. |
| `noEmpty` | `noEmpty<V>(value: V): value is NonNullable<V>` | Alias de `notEmpty`. |
| `isEmpty` | `isEmpty<V>(value: V): value is NonNullable<V>` | Verdadeiro se vazio (`size === 0`); booleanos e números sempre `false`. Inverso de `notEmpty`. |
| `empty` | `empty<V>(value: V): boolean` | Alias simplificado de `isEmpty` (retorna `boolean`). |
| `isValid` | `isValid<V>(value: V): value is NonNullable<V>` | Verdadeiro se o valor não for `null` nem `undefined`. |
| `isNotValid` | `isNotValid<V>(value: V): value is Extract<V, null \| undefined>` | Verdadeiro se for `null` ou `undefined`. Inverso de `isValid`. |
| `notHasValidContent` | `notHasValidContent<V>(value: V): value is Extract<V, null \| undefined>` | Alias de `isNotValid`. |

> Namespace `validate` (e `_.validate`) agrupa documentos, e-mail, CEP, telefone e as funções de `isValid`.

## Helpers Elétricos (Electrical)

| Função | Assinatura | Descrição |
|--------|-----------|-----------|
| `wireSize` | `async wireSize(current: MaybeRefOrGetter<string \| number \| null>, options: WireOptions): Promise<{ wire: number; max_current: number; voltage_drop: number; loss_percent: number } \| null>` | Calcula a bitola (seção nominal) de cabo elétrico conforme NBR 5410, a partir da corrente e opções (material cobre/alumínio, isolação/temperatura, método de instalação, comprimento, tensão, fases, fatores FCA/FCT, tipo de circuito, queda máxima). Retorna `null` se a corrente estiver em branco; considera queda de tensão e tabelas de capacidade. |
| `calculaCabo` | `calculaCabo = wireSize` | Alias de `wireSize`. |
| `WireOptions` *(tipo)* | `type WireOptions = { current?; material?: 'copper'\|'aluminum'\|'cobre'\|'aluminio'\|'alumínio'\|'cu'\|'al'; isolation?: '70'\|'90'\|70\|90\|'pvc'\|'epr'\|'xlpe'; method?: 'a1'..'g'\|string; length?; voltage?; phases?: 1\|2\|3; max_loss?; voltage_drop?; fca?; fct?; circuit_type?: 'lighting'\|'power'\|'iluminacao'\|'tomada'\|'forca'\|string }` | Tipo de configuração do cálculo de bitola. |

> Namespace `electrical` (e alias `electric`, mais `_.electrical`/`_.electric`) expõe `wireSize` e `calculaCabo`.

## Helpers de Formatação (Format)

| Função | Assinatura | Descrição |
|--------|-----------|-----------|
| `formatCurrency` | `formatCurrency(value: MaybeRefOrGetter<string \| number \| null \| undefined>): string` | Formata para moeda brasileira (`R$` via `Intl.NumberFormat` pt-BR/BRL). Retorna `'R$ 0,00'` se em branco ou `NaN`. |
| `formatBytes` | `formatBytes(bytes: MaybeRefOrGetter<number \| string>, decimals?: MaybeRefOrGetter<number> = 2): string` | Converte bytes em string legível (Bytes, KB, MB … YB, base 1024). Retorna `'0 Bytes'` se 0/`NaN`. |
| `formatCep` | `formatCep(value: RefString): string` | Reexportado de `Strings/masks`. Ver Helpers de Strings. |
| `formatCpf` | `formatCpf(value: RefString): string` | Reexportado de `Strings/masks`. Ver Helpers de Strings. |
| `formatCnpj` | `formatCnpj(value: RefString): string` | Reexportado de `Strings/masks`. Ver Helpers de Strings. |
| `formatCpfCnpj` | `formatCpfCnpj(value: RefString): string` | Reexportado de `Strings/masks`. Ver Helpers de Strings. |
| `formatPhone` | `formatPhone(phone_number: RefString): string` | Reexportado de `Strings/masks`. Ver Helpers de Strings. |
| `maskSensitive` | `maskSensitive(value: RefString, type?: 'email' \| 'card' \| 'text' = 'text'): string` | Reexportado de `Strings/masks`. Ver Helpers de Strings. |

> Namespace `format` (e `_.format`): `currency`, `bytes`, `cep`, `cpf`, `cnpj`, `cpfCnpj`, `phone`, `sensitive`.

## VueUse (re-exports) — nota

A pasta `Helpers/VueUse/` **não contém helpers próprios**: `index.ts` apenas re-exporta ~330 funções/composables de `@vueuse/core` individualmente (ex.: `useLocalStorage`, `useDebounceFn`, `clamp`, `useToggle`, `refDebounced`, `watchDebounced`, etc.), além do namespace `vueUse` e dos tipos. No objeto `_`, o VueUse só entra quando não colide com um helper próprio da MaxUse (ver ordem de precedência na seção "O objeto `_`" acima). Como são apenas repasses da biblioteca VueUse, não estão documentadas função a função aqui.

## Locales — nota

A pasta `Helpers/Locales/` contém apenas arquivos de dados de localização (`br.js`, `pt_BR.js`) e não exporta funções helper.
