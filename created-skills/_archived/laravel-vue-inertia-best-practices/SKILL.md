---
name: laravel-vue-inertia-best-practices
description: Use when building, debugging, or optimizing full-stack Inertia.js integrations in Vue 3 and Laravel. Covers shared data and partial reloads, lazy and deferred props, Server-Side Rendering (SSR) with Octane, hydration mismatch prevention, SEO head injection, and useForm-based form handling with validation errors, file uploads, and duplicate submission prevention.
---

# Laravel + Vue Inertia.js Best Practices

## Goal
Establish high-performance guidelines and architectural patterns for Inertia.js full-stack development in the Engeapp ecosystem, covering the complete integration surface: data sharing, partial reloads, SSR with Octane compatibility, and frontend form management.

## Instructions

### Part 1: Data Sharing, Partial Reloads & Deferred Props

#### 1.1 Shared Data Optimization (Inertia Share)
- Limit globally shared data in `HandleInertiaRequests.php` to basic context attributes (e.g., authenticated user, app name, config flags, flash messages).
- Avoid sharing heavy Eloquent queries, large arrays, or dynamic collections globally. Pass dynamic data locally via controller props.

#### 1.2 Optional Evaluation (`Inertia::optional()`)
- Wrap non-essential props (logs, histories, metrics, complex detail modals) in `Inertia::optional()`. The query is skipped on initial load and only runs when explicitly requested by the client:
  ```php
  return Inertia::render('Project/Details', [
      'project' => $project,
      'history' => Inertia::optional(fn () => $project->history()->latest()->get()),
  ]);
  ```
  > Nota: `Inertia::lazy()` é o nome legado dessa API, depreciado no Inertia.js v2 e mantido apenas para compatibilidade. Prefira `Inertia::optional()`.

#### 1.3 Deferred Props (`Inertia::defer()`)
- In Laravel 11/12+, use `Inertia::defer()` for progressive async page loading. Deferred props send empty placeholders on initial load; the backend loads them in parallel once the page layout renders:
  ```php
  return Inertia::render('Project/Details', [
      'project' => $project,
      'financials' => Inertia::defer(fn () => $project->financials()->get()),
  ]);
  ```
  Optimizes LCP and FCP for pages depending on external services or complex aggregates.

#### 1.4 Vue 3 Request Optimization (`only` and `except`)
- Request only the necessary props in partial reloads to prevent re-downloading already loaded data:
  ```typescript
  import { router } from '@inertiajs/vue3';
  const reloadHistory = () => router.reload({ only: ['history'] });
  ```

#### 1.5 Loading States and Visual Feedback
- Always provide clear indicators (spinners, skeleton loaders, or progress bars) when loading lazy or deferred props.

### Part 2: Server-Side Rendering (SSR) with Octane

#### 2.1 SSR Entry Point (`resources/js/ssr.ts`)
```typescript
import { createSSRApp, h, DefineComponent } from 'vue';
import { renderToString } from '@vue/server-renderer';
import { createInertiaApp } from '@inertiajs/vue3';
import createServer from '@inertiajs/vue3/server';
import { ZiggyVue } from 'ziggy-js';

createServer((page) =>
  createInertiaApp({
    page,
    render: renderToString,
    resolve: (name) => {
      const pages = import.meta.glob('./Pages/**/*.vue', { eager: true });
      return pages[`./Pages/${name}.vue`] as DefineComponent;
    },
    setup({ App, props, plugin }) {
      return createSSRApp({ render: () => h(App, props) })
        .use(plugin)
        .use(ZiggyVue, (page.props as any).ziggy);
    },
  })
);
```

#### 2.2 Isomorphic Components (Safe Browser API Access)
- Do NOT reference browser globals (`window`, `document`, `localStorage`, `sessionStorage`, `navigator`) in `setup`, `beforeCreate`, or `created` hooks — these run during SSR.
- Use `onMounted()` for browser-only operations (it runs only on the client):
  ```typescript
  onMounted(() => {
    // Seguro: executa apenas no navegador (cliente)
    windowWidth.value = window.innerWidth;
  });
  ```
- Or conditionally check: `if (typeof window !== 'undefined') { ... }`

#### 2.3 Preventing Request State Pollution (Octane)
- Laravel Octane keeps the container in memory across requests. Always resolve stateful `Inertia::share()` properties inside a per-request closure or middleware — never in singleton constructors or `register()`:
  ```php
  // No arquivo HandleInertiaRequests.php
  public function share(Request $request): array
  {
      return array_merge(parent::share($request), [
          'auth' => [
              // Closure garante resolução por requisição, evitando vazamento no Octane
              'user' => fn () => $request->user() ? new UserResource($request->user()) : null,
          ],
      ]);
  }
  ```

#### 2.4 Preventing Hydration Mismatches
- Ensure server-rendered HTML matches the client DOM exactly on load. Avoid non-deterministic functions (`Math.random()`, dynamic IDs, client-timezone date formatting) in initial HTML.
- For browser-only components, use `<ClientOnly>` or dynamic imports:
  ```vue
  <ClientOnly><BrowserSpecificWidget /></ClientOnly>
  ```
- Standardize timezones: render ISO strings or UTC timestamps and format them inside `onMounted`.

#### 2.5 Dynamic SEO with Inertia `<Head>`
```vue
<template>
  <Head>
    <title>{{ pageTitle }}</title>
    <meta name="description" :content="pageDescription" />
    <meta property="og:title" :content="pageTitle" />
  </Head>
</template>
<script setup lang="ts">
import { Head } from '@inertiajs/vue3';
defineProps<{ pageTitle: string; pageDescription: string }>();
</script>
```

### Part 3: Form Handling with `useForm`

#### 3.1 Initialization
```typescript
import { useForm } from '@inertiajs/vue3';

interface ProjectForm { name: string; description: string; documents: File[]; }

const form = useForm<ProjectForm>({ name: '', description: '', documents: [] });
```

#### 3.2 Submission & Duplicate Prevention
- Bind with `@submit.prevent="submit"`. Use `form.processing` to disable buttons during submission:
  ```html
  <button type="submit" :disabled="form.processing">
    <span v-if="form.processing">Sending...</span>
    <span v-else>Submit</span>
  </button>
  ```

#### 3.3 Validation Errors
- Display with `form.errors`. Clear on input with `form.clearErrors('field')`:
  ```html
  <input v-model="form.name" @input="form.clearErrors('name')" />
  <span v-if="form.errors.name" class="error">{{ form.errors.name }}</span>
  ```

#### 3.4 File Uploads & Progress
- Inertia automatically converts data to `FormData` if it detects a `File` or `Blob`. Access `form.progress` for progress bars:
  ```html
  <progress v-if="form.progress" :value="form.progress.percentage" max="100" />
  ```

#### 3.5 Callbacks & Reset
- Use built-in callbacks instead of manual state variables:
  ```typescript
  form.post(route('projects.store'), {
    onSuccess: () => form.reset(),
    onError: (errors) => console.error('Form errors:', errors),
  });
  ```

## Constraints
- DO NOT return raw Eloquent queries inside lazy/deferred props. Always wrap in PHP closures `fn() => ...`.
- DO NOT use global Inertia share for data only needed in specific views.
- DO NOT access browser APIs (`window`, `document`, `localStorage`) outside `onMounted()` or client-side checks.
- DO NOT use static or cached models/singletons that pollute request boundaries under Octane.
- DO NOT manually track loading states (e.g., `const isLoading = ref(false)`). Always use `form.processing`.
- DO NOT manually construct `FormData` when using `useForm` — Inertia handles nested files and multi-part data automatically.
- DO NOT use Options API. All scripts must use `<script setup lang="ts">`.
