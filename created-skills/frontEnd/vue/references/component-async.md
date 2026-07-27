---
title: Async Component Best Practices
impact: MEDIUM
impactDescription: Poor async component strategy can create loading UI flicker
type: best-practice
tags: [vue3, async-components, performance, ux]
---

# Async Component Best Practices

> **Nota engeapp:** o engeapp é uma SPA client-only (`createApp`, sem `createSSRApp`/SSR). As estratégias de lazy hydration (`hydrateOnVisible`/`hydrateOnIdle`) são exclusivas de SSR e não se aplicam aqui — use apenas `delay`/`timeout`/`loadingComponent`/`errorComponent`.

**Impact: MEDIUM** - Async components should reduce JavaScript cost without degrading perceived performance. Focus on stable loading UX.

## Task List

- Keep `loadingComponent` delay near the default `200ms` unless real UX data suggests otherwise
- Configure `delay` and `timeout` together for predictable loading behavior

## Prevent Loading Spinner Flicker

Avoid showing loading UI immediately for components that usually resolve quickly.

**BAD:**
```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'
import LoadingSpinner from './LoadingSpinner.vue'

const AsyncDashboard = defineAsyncComponent({
  loader: () => import('./Dashboard.vue'),
  loadingComponent: LoadingSpinner,
  delay: 0
})
</script>
```

**GOOD:**
```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'
import LoadingSpinner from './LoadingSpinner.vue'
import ErrorDisplay from './ErrorDisplay.vue'

const AsyncDashboard = defineAsyncComponent({
  loader: () => import('./Dashboard.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorDisplay,
  delay: 200,
  timeout: 30000
})
</script>
```

## Delay Guidelines

| Scenario | Recommended Delay |
|----------|-------------------|
| Small component, fast network | `200ms` |
| Known heavy component | `100ms` |
| Background or non-critical UI | `300-500ms` |
