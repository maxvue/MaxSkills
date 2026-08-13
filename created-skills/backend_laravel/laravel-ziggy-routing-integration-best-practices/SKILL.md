---
name: laravel-ziggy-routing-integration-best-practices
description: "Use when configuring, generating, or consuming Ziggy routes in Vue 3 SPA. Covers config/ziggy.php, ziggy:generate, ziggy.d.ts, route() auto-import, and setRouteResolver."
---
# Boas Práticas de Integração de Rotas com Laravel Ziggy

## Objetivo
Padronizar como o back-end Laravel 13 expõe rotas nomeadas via Ziggy e como o front-end Vue 3 (SPA, Composition API) as consome por NOME pontilhado — nunca por URL fixa. Isso garante uma única fonte de verdade para as URLs e evita strings estáticas espalhadas no cliente.

## Contexto do projeto (verdade-base — não invente)
- Dentro de `<script setup>`, `route()` está disponível por **auto-import** (`vite.config.ts` → `unplugin-auto-import` com a entrada `{ 'ziggy-js': ['route'] }`, refletida em `auto-import.d.ts`). O plugin **ZiggyVue** (`app.use(ZiggyVue)` em `resources/app.ts`) serve ao uso em **template**, via `globalProperties`. Não há declaração global manual de `route()` em `resources/`.
- O autocomplete dos NOMES de rota vem do arquivo **gerado** `resources/Js/ziggy.d.ts` (`declare module 'ziggy-js' { interface RouteList { ... } }`), produzido por `ziggy:generate --types` — por isso regenerar é obrigatório após mexer em rotas.
- `apiGetRoute` (e `apiPostRoute`, `apiPutRoute`, `apiDeleteRoute`, `apiUploadRoute`) são helpers de **`@maxvue/max-use`**, **auto-importados** via `unplugin-auto-import` + `maxUseAutoImport` no `vite.config.ts`. Eles aparecem em `auto-import.d.ts` — não os declare manualmente e, na maioria dos casos, nem os importe.
- Convenção de dados: **todo GET passa por uma store MaxPinia** (`options.get.route` recebe o nome pontilhado da rota). Use `apiGetRoute` direto apenas para casos fora do fluxo de cache (ex.: download de arquivo com `{ file: true }`).

## Instruções

### 1. config/ziggy.php: apenas o caminho de saída
O arquivo real do projeto define somente o caminho do artefato gerado. **Não adicione uma chave `except` inventada** — ela não existe aqui.

```php
// config/ziggy.php (real)
return [
    /**
     * Set the generated path for php artisan ziggy:generate.
     */
    'output' => [
        'path' => 'resources/Js/ziggy.js',
    ],
];
```

Orientação geral (opcional, não configurada no projeto): o Ziggy suporta `only`/`except` para filtrar quais rotas vão ao cliente. Se um dia for necessário ocultar rotas de debug/admin, essa é a chave adequada — mas hoje o engeapp expõe o conjunto padrão e não depende desse filtro.

### 2. Geração de Rotas & Tipos
Sempre que rotas forem adicionadas ou renomeadas no Laravel, regenere os artefatos do Ziggy:
```bash
php artisan ziggy:generate --types
```
Isso atualiza:
- `resources/Js/ziggy.js`: lista de rotas e configuração consumida em runtime.
- `resources/Js/ziggy.d.ts`: a interface `RouteList` com os nomes exatos e parâmetros das rotas do back-end (usada para autocomplete e checagem de tipo de `route()`).

### 3. Configuração de Compilação TypeScript
O `tsconfig.json` do projeto tem um path para `ziggy-js`:

```jsonc
{
  "compilerOptions": {
    "paths": {
      "ziggy-js": ["./vendor/tightenco/ziggy"]
    }
  }
}
```
Esse path afeta apenas a resolução de **tipos** pelo compilador TS. A resolução do módulo em runtime/build vem do alias do Vite (`vite.config.ts` → `resolve.alias`, `'ziggy-js': path.resolve(__dirname, './node_modules/ziggy-js')`), necessário porque o auto-import de `route` injeta o import em qualquer arquivo processado, inclusive nas libs linkadas fora da raiz. Remover o path do tsconfig não quebraria o import em runtime — apenas degradaria o type-checking, apontando para outra fonte de tipos.

### 4. De onde vêm route() e apiGetRoute (não redeclare)
`route()` e os helpers `api*Route` **já estão disponíveis** — não os redeclare em nenhum `.d.ts` próprio (nenhum arquivo em `resources/Types/` declara `route()`). Isso geraria declarações duplicadas e conflitantes.

- `route()` — auto-importado de `ziggy-js` em `<script setup>` (entrada `{ 'ziggy-js': ['route'] }` no `unplugin-auto-import`); em template vem do plugin `ZiggyVue`. Os nomes de rota são tipados pelo `resources/Js/ziggy.d.ts` gerado.
- `apiGetRoute` — auto-importado de `@maxvue/max-use`. Assinatura **real** (não é genérica sobre `RouteName`):

```typescript
// @maxvue/max-use — src/Routes/apiGetRoute.ts
export async function apiGetRoute(
    RouteName: string | null,
    data: any = {},
    options: any = null
): Promise<any>
```
Os parâmetros são `string | null` e `any` por design da biblioteca instalada. Não “aperte” esses tipos para `RouteName`/`RouteParams<T>`: você estaria contrariando o contrato real do `@maxvue/max-use`.

### 5. Bootstrap em resources/app.ts: o elo que aceita NOMES de rota
`apiGetRoute` e `options.get.route` só aceitam nomes pontilhados porque o `app.ts` conecta o Ziggy às libs Max:

```typescript
// resources/app.ts
import { setLibraryRouter, setRouteResolver } from '@maxvue/max-use';

// Deve ocorrer ANTES de qualquer store/composable resolver rotas.
setRouteResolver((name: string, params?: any) => {
    try {
        const url: string = route(name, params);

        // O Ziggy devolve URL absoluta. O goToRoute() do MaxUse repassa esse valor
        // ao router.push(), que trata string como path relativo e duplicaria o domínio
        // (ex.: /https://dominio/settings). Reduz para path quando for a mesma origem.
        const origin = typeof window !== 'undefined' ? window.location.origin : '';
        return origin && url.startsWith(origin) ? (url.slice(origin.length) || '/') : url;
    } catch {
        return null;
    }
});

pinia.use(createMaxPinia({
    // ...
    resolveRoute: (name: string, params?: Record<string, any>) => route(name as any, params)
}));
```

Sem `setRouteResolver` os helpers `api*Route` do `@maxvue/max-use` não resolvem nomes; sem `resolveRoute` as stores MaxPinia não resolvem `options.get.route`/`save`.

### 6. Uso em Componentes e Stores
Passe sempre o **nome pontilhado** da rota (ex.: `'datasheet.list.uploaded'`, `'list.projects.all'`).

#### GET via store MaxPinia (padrão para busca de dados):
As stores do projeto são **setup stores** (função), nunca Options API. `options` é um `computed` retornado pela store:

```typescript
// resources/Stores/.../useProjects.Store.ts
export const useProjectsStore = defineStore('projects', () => {
    const isCached: Ref = ref(true);
    const data: Ref<any[] | null> = ref(null);
    const options: Ref = computed(() => ({
        get: { route: 'list.projects.all' }, // nome Ziggy pontilhado
        // opcionais: save (nome de rota POST), enabled, key, id
    }));

    return { data, options, isCached };
});
```

Atenção: `options.key` **não** é a chave de cache. A chave real do LocalForage é `store.$id + '.' + (store.id ?? store.options?.id ?? 'global')`.

#### route() para montar uma URL (navegação, href, link):
```vue
<script setup lang="ts">
import { ref } from 'vue';

const projectId = ref(12);
// route() é auto-importado de 'ziggy-js' — não precisa importar manualmente
const projectUrl = route('project.create.share', { id: projectId.value });
</script>
```

#### apiGetRoute direto (casos fora do cache — ex.: download):
```vue
<script setup lang="ts">
import { onMounted, ref } from 'vue';

const listFiles = ref<any[]>([]);

onMounted(async () => {
    // apiGetRoute é auto-importado de @maxvue/max-use
    listFiles.value = await apiGetRoute('datasheet.list.uploaded');
});
</script>
```

### 7. Passando Models Eloquent como Parâmetros
Passe a chave específica exigida pelo placeholder da rota (`id`/`uuid`), não o objeto inteiro do model:

```typescript
// Bom
route('project.create.share', { id: project.id });

// Evite
route('project.create.share', project);
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), independentemente do idioma do corpo desta skill. Comentários de código em pt-BR.
- **SEM URLs FIXAS:** Nunca escreva strings de URL do Laravel no front-end. Resolva sempre pelo NOME pontilhado.
