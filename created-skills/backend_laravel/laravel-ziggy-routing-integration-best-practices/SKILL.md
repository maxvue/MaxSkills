---
name: laravel-ziggy-routing-integration-best-practices
description: Use ao configurar, gerar ou consumir rotas Ziggy (tightenco/ziggy ^2.4) no front-end Vue 3 do engeapp (Laravel 13 SPA). Cobre config/ziggy.php (output.path), php artisan ziggy:generate --types, tsconfig paths, o plugin ZiggyVue/route() e o consumo por NOMES pontilhados via apiGetRoute (auto-importado de @maxvue/max-use) e stores MaxPinia. Acione em rotas, ziggy:generate ou route().
---

# Boas Práticas de Integração de Rotas com Laravel Ziggy

## Objetivo
Padronizar como o back-end Laravel 13 expõe rotas nomeadas via Ziggy e como o front-end Vue 3 (SPA, Composition API) as consome por NOME pontilhado — nunca por URL fixa. Isso garante uma única fonte de verdade para as URLs e evita strings estáticas espalhadas no cliente.

## Contexto do projeto (verdade-base — não invente)
- `route()` vem do plugin **ZiggyVue** registrado em `resources/app.ts` (`import { ZiggyVue, route } from 'ziggy-js'` → `app.use(ZiggyVue)`). Não há declaração global de `route()` em `resources/`; o autocomplete vem das tipagens da própria lib.
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
- as definições TypeScript com os nomes exatos e parâmetros das rotas do back-end (usadas para autocomplete de `route()`).

### 3. Configuração de Compilação TypeScript
O `tsconfig.json` do projeto resolve o import `ziggy-js` para o pacote publicado dentro de `vendor/`:

```jsonc
{
  "compilerOptions": {
    "paths": {
      "ziggy-js": ["./vendor/tightenco/ziggy"]
    }
  }
}
```
Mantenha esse alias ao mexer em paths — sem ele, `import { route, ZiggyVue } from 'ziggy-js'` em `resources/app.ts` não resolve.

### 4. De onde vêm route() e apiGetRoute (não redeclare)
`route()` e os helpers `api*Route` **já estão disponíveis** — não crie `Global.d.ts`/`shims-ziggy.d.ts` com `declare global` para eles. Isso geraria declarações duplicadas e conflitantes.

- `route()` — provido pelo plugin `ZiggyVue` (`app.use(ZiggyVue)` em `resources/app.ts`); tipado pela própria `ziggy-js`.
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

### 5. Uso em Componentes e Stores
Passe sempre o **nome pontilhado** da rota (ex.: `'datasheet.list.uploaded'`, `'projects.show'`).

#### GET via store MaxPinia (padrão para busca de dados):
```typescript
// resources/.../stores/useProjects.ts
export const useProjects = defineStore('projects', {
    // ...
    options: {
        get: { route: 'projects.index' }, // nome Ziggy pontilhado
    },
});
```

#### route() para montar uma URL (navegação, href, link):
```vue
<script setup lang="ts">
import { ref } from 'vue';

const projectId = ref(12);
// route() está global via ZiggyVue — não precisa importar
const projectUrl = route('projects.show', { id: projectId.value });
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

### 6. Passando Models Eloquent como Parâmetros
Passe a chave específica exigida pelo placeholder da rota (`id`/`uuid`), não o objeto inteiro do model:

```typescript
// Bom
route('projects.show', { id: project.id });

// Evite
route('projects.show', project);
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), independentemente do idioma do corpo desta skill. Comentários de código em pt-BR.
- **SEM URLs FIXAS:** Nunca escreva strings de URL do Laravel no front-end. Resolva pelo NOME pontilhado via store MaxPinia (`options.get.route`), `apiGetRoute`/`apiPostRoute` ou `route()`.
- **NÃO REDECLARE HELPERS:** Não crie `declare global` para `route()` ou `apiGetRoute()` — o primeiro vem do plugin ZiggyVue e o segundo é auto-importado de `@maxvue/max-use`.
- **RESPEITE O CONTRATO DA LIB:** Não retipe `apiGetRoute` para genéricos `RouteName`/`RouteParams<T>`; a assinatura real é `(RouteName: string | null, data: any, options: any)`.
- **GET PASSA POR STORE:** Prefira stores MaxPinia para buscas; use `apiGetRoute` direto apenas fora do fluxo de cache (ex.: `{ file: true }`).
- **REGENERE AO ALTERAR ROTAS:** Rode `php artisan ziggy:generate --types` após adicionar/renomear rotas para manter o front sincronizado.
