---
name: laravel-ziggy-routing-integration-best-practices
description: Use when configuring, generating, or using Laravel Ziggy routes in the Vue frontend. Triggers on route generation commands (ziggy:generate), TypeScript definition issues with routes, and calling the route() helper in Vue components.
---

# Boas Práticas de Integração de Rotas com Laravel Ziggy

## Objetivo
Fornecer diretrizes sólidas e padrões consistentes para integrar e usar rotas do Laravel fortemente tipadas em um frontend Vue 3 (Composition API) usando o Laravel Ziggy. Isso garante segurança de tipos, autocomplete e previne URLs fixas no código da aplicação cliente.

## Instruções

### 1. Segurança & Filtragem de Rotas no Backend
Não exponha rotas privadas, administrativas ou de debug (ex: `debugbar`, `horizon`, `telescope`, APIs internas) ao frontend.
Configure o arquivo `config/ziggy.php` para filtrar rotas usando a chave `except`:

```php
// config/ziggy.php
return [
    'except' => [
        'debugbar.*',
        'horizon.*',
        'telescope.*',
        'ignition.*',
        'admin.*', // Exclui rotas do painel admin se gerenciadas separadamente
    ],
    'output' => [
        'path' => 'resources/Js/ziggy.js',
    ],
];
```

### 2. Geração de Rotas & Tipos
Sempre que rotas forem adicionadas ou modificadas no Laravel, regenere os arquivos JS do Ziggy e de declaração TypeScript:
```bash
php artisan ziggy:generate --types
```
Este comando gera dois arquivos:
- `resources/Js/ziggy.js`: O arquivo JavaScript contendo a lista de rotas e a configuração.
- `resources/Js/ziggy.d.ts`: As definições TypeScript mapeando os nomes exatos e parâmetros das rotas do seu backend.

### 3. Configuração de Compilação TypeScript
Garanta que o compilador saiba como resolver os imports e arquivos do Ziggy. Atualize o `tsconfig.json`:

```json
{
  "compilerOptions": {
    "paths": {
      "ziggy-js": ["./vendor/tightenco/ziggy"]
    }
  },
  "include": [
    "./resources/Js/ziggy.d.ts",
    "./resources/**/*.ts",
    "./resources/**/*.vue"
  ]
}
```

### 4. Tipagens Globais para route() e apiGetRoute()
Para habilitar o autocomplete global em templates Vue e helpers customizados sem importar manualmente `route`, declare as tipagens globais em um arquivo `Global.d.ts` ou `shims-ziggy.d.ts` dentro de `resources/Types/`:

```typescript
import { RouteName, RouteParams } from 'ziggy-js';

declare global {
    // Habilita o autocomplete de tipo para o helper global route()
    function route(): RouteName;
    function route<T extends RouteName>(
        name: T,
        params?: RouteParams<T>,
        absolute?: boolean
    ): string;

    // Definição de tipo para o helper de rota de API customizado do Engeapp
    function apiGetRoute<T extends RouteName>(
        routeName: T | null,
        data?: RouteParams<T>,
        options?: any
    ): Promise<any>;
}
```

### 5. Uso Padrão em Componentes Vue 3 (<script setup lang="ts">)
Dentro de componentes Vue, use o hook de composição `useRoute` ou chame o helper global tipado.

#### Usando o hook `useRoute()` (Recomendado para reatividade e escopo local):
```vue
<script setup lang="ts">
import { useRoute } from 'ziggy-js';
import { ref } from 'vue';

const route = useRoute();
const projectId = ref(12);

// A assinatura de route() é totalmente tipada e fará autocomplete de 'projects.show' e validará os tipos dos parâmetros
const projectUrl = route('projects.show', { id: projectId.value });
</script>
```

#### Usando `apiGetRoute()` para queries Axios/Fetch:
```vue
<script setup lang="ts">
import { onMounted, ref } from 'vue';

const listFiles = ref<any[]>([]);

onMounted(async () => {
    // Faz autocomplete dos nomes de rota e valida o formato dos parâmetros
    listFiles.value = await apiGetRoute('datasheet.list.uploaded');
});
</script>
```

### 6. Passando Models Eloquent como Parâmetros
Ao passar parâmetros de rota, sempre passe a chave de propriedade específica exigida pelo placeholder da rota (geralmente `id` ou `uuid`) para casar com as tipagens TypeScript, em vez de passar o objeto do model inteiro diretamente, a menos que o tipo do model esteja especificamente mapeado.

```typescript
// Bom: Parâmetro casa com as expectativas de tipo
route('project.show', { id: project.id });

// Evite (a menos que as classes de model estejam tipadas e mapeadas no frontend):
route('project.show', project);
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **SEM URLs FIXAS:** Nunca escreva strings estáticas para URLs controladas pelo Laravel em componentes ou stores do frontend. Sempre resolva-as usando `route()` ou `apiGetRoute()`.
- **SEM EXPOSIÇÃO PRIVADA:** Garanta que rotas internas sejam filtradas em `config/ziggy.php`.
- **REGENERE NO BUILD:** Sempre execute `php artisan ziggy:generate --types` como parte do pipeline de build do frontend ou do workflow de deploy para manter as definições do frontend sincronizadas com o backend.
- **CONFORMIDADE DE TIPOS:** Nunca tipe os parâmetros do helper de rota como `any` ou `string`. Mantenha o binding estrito a `RouteName` para segurança adequada em tempo de compilação.
