---
name: laravel-ziggy-routing-integration-best-practices
description: Use when configuring, generating, or using Laravel Ziggy routes in the Vue frontend. Triggers on route generation commands (ziggy:generate), TypeScript definition issues with routes, and calling the route() helper in Vue components.
---

# Laravel Ziggy Routing Integration Best Practices

## Goal
Provide solid guidelines and consistent patterns for integrating and using strongly-typed Laravel routes in a Vue 3 frontend (Composition API) using Laravel Ziggy. This ensures type safety, autocomplete, and prevents hardcoded URLs in the client application.

## Instructions

### 1. Backend Route Security & Filtering
Do not expose private, administrative, or debug routes (e.g., `debugbar`, `horizon`, `telescope`, internal APIs) to the frontend.
Configure the `config/ziggy.php` file to filter routes using the `except` key:

```php
// config/ziggy.php
return [
    'except' => [
        'debugbar.*',
        'horizon.*',
        'telescope.*',
        'ignition.*',
        'admin.*', // Exclude admin panel routes if managed separately
    ],
    'output' => [
        'path' => 'resources/Js/ziggy.js',
    ],
];
```

### 2. Route & Type Generation
Whenever routes are added or modified in Laravel, regenerate the Ziggy JS and TypeScript declaration files:
```bash
php artisan ziggy:generate --types
```
This command outputs two files:
- `resources/Js/ziggy.js`: The JavaScript file containing the list of routes and configuration.
- `resources/Js/ziggy.d.ts`: The TypeScript definitions mapping the exact names and parameters of your backend routes.

### 3. TypeScript Compilation Config
Ensure the compiler knows how to resolve the Ziggy imports and files. Update `tsconfig.json`:

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

### 4. Global Typings for route() and apiGetRoute()
To enable global autocomplete in Vue templates and custom helpers without manually importing `route`, declare global typings in a `Global.d.ts` or `shims-ziggy.d.ts` file inside `resources/Types/`:

```typescript
import { RouteName, RouteParams } from 'ziggy-js';

declare global {
    // Enable type autocomplete for the global route() helper
    function route(): RouteName;
    function route<T extends RouteName>(
        name: T,
        params?: RouteParams<T>,
        absolute?: boolean
    ): string;

    // Type definition for Engeapp's custom API route helper
    function apiGetRoute<T extends RouteName>(
        routeName: T | null,
        data?: RouteParams<T>,
        options?: any
    ): Promise<any>;
}
```

### 5. Standard Usage in Vue 3 Components (<script setup lang="ts">)
Inside Vue components, use the composition hook `useRoute` or call the global typed helper.

#### Using `useRoute()` hook (Recommended for reactivity and local scope):
```vue
<script setup lang="ts">
import { useRoute } from 'ziggy-js';
import { ref } from 'vue';

const route = useRoute();
const projectId = ref(12);

// route() signature is fully typed and will autocomplete 'projects.show' and validate parameter types
const projectUrl = route('projects.show', { id: projectId.value });
</script>
```

#### Using `apiGetRoute()` for Axios/Fetch queries:
```vue
<script setup lang="ts">
import { onMounted, ref } from 'vue';

const listFiles = ref<any[]>([]);

onMounted(async () => {
    // Autocompletes route names and validates the parameters format
    listFiles.value = await apiGetRoute('datasheet.list.uploaded');
});
</script>
```

### 6. Passing Eloquent Models as Parameters
When passing route parameters, always pass the specific property key required by the route placeholder (usually `id` or `uuid`) to match TypeScript bindings, rather than passing the whole model object directly, unless the model type is specifically mapped.

```typescript
// Good: Parameter matches type expectations
route('project.show', { id: project.id });

// Avoid (unless model classes are typed and mapped in frontend):
route('project.show', project);
```

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **NO HARDCODED URLs:** Never write static strings for Laravel-controlled URLs in frontend components or stores. Always resolve them using `route()` or `apiGetRoute()`.
- **NO PRIVATE EXPOSURE:** Ensure internal-only routes are filtered out in `config/ziggy.php`.
- **REGENERATE ON BUILD:** Always run `php artisan ziggy:generate --types` as part of the frontend build pipeline or deployment workflow to keep frontend definitions synchronized with the backend.
- **TYPE COMPLIANCE:** Never type the route helper parameters as `any` or `string`. Keep the strict binding to `RouteName` for proper compile-time safety.
