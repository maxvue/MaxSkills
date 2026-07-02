---
name: vue-3-dynamic-components-and-keep-alive-caching-best-practices
description: Use when designing, implementing, or optimizing dynamic component loading using Vue 3 <component :is="...">, rendering asynchronous components with defineAsyncComponent, or managing component caching and lifecycle hooks with <KeepAlive> (e.g., handling onActivated/onDeactivated, cache invalidation, and custom cache keys). Triggers when creating dynamic tab interfaces, multi-step wizards, or dashboard layouts with state retention.
---

## Goal
Provide guidelines, standards, and best practices for implementing dynamic component rendering, asynchronous loading, and screen/tab caching using Vue 3, focusing on performance optimization, proper state retention, and memory management.

## Instructions
1. **Dynamic Rendering with `<component :is="...">`**:
   - Utilize `<component :is="currentComponent" />` for rendering dynamic component interfaces such as tabs or wizards.
   - **Performance (shallowRef/markRaw)**: Always wrap dynamically loaded component definitions in `shallowRef` instead of `ref`, or wrap them with `markRaw` when assigning to reactive state. This prevents Vue from deeply observing the component instance (methods, internal state, etc.), which degrades performance and triggers console warnings.
   - **Strong Typing**: Define mapping objects for components with TypeScript to ensure type safety.

2. **Asynchronous Components (`defineAsyncComponent`)**:
   - Use `defineAsyncComponent` to perform code-splitting on heavy components (e.g., complex editors, preview panel simulators, charts) that are not needed during initial page load.
   - Configure options such as `loadingComponent` (spinner/skeleton), `errorComponent` (fallback UI), `delay` (prevent flashing loading states), and `timeout` (limit loading times).

3. **State Retention and Caching (`<KeepAlive>`)**:
   - Wrap `<component :is="...">` inside `<KeepAlive>` to cache instances of deactivated components, preserving their internal DOM state and reactive variables.
   - **Cache Limits (`max`)**: Always set a `max` attribute (e.g., `<KeepAlive :max="10">`) to limit the number of cached instances and prevent memory leaks.
   - **Targeted Caching (`include` / `exclude`)**: Use `include` or `exclude` props to specify exactly which components should be cached. Ensure components have a defined `name` option (or are automatically named based on the file name) to match these patterns.

4. **Component Lifecycle Hooks (`onActivated` / `onDeactivated`)**:
   - Use `onActivated` to run code when a cached component is re-inserted into the DOM (e.g., fetching fresh data, starting animations, subscribing to web sockets).
   - Use `onDeactivated` to clean up resources when the component is cached but removed from the view (e.g., pausing intervals, unsubscribing from event listeners, persisting draft states).
   - Avoid using `onMounted` or `onUnmounted` for tasks that must execute every time the user navigates back to a cached tab, as these hooks only fire once per component mount/unmount cycle.

5. **Composition API & SFC Standards**:
   - Ensure all components use `<script setup lang="ts">`.
   - Style via UnoCSS attributify (`presetMaxUno`) with theme tokens (`bg-primary`, `bg-background`, `color-text`, `border-$gray-light`, etc.) applied as inline attributes on the elements — do NOT write `<style scoped lang="scss">` blocks or raw hex colors.
   - Block order must strictly follow: `<template>`, then `<script>`.
   - In templates, format component tags with all parameters on a single line (inline layout, do not wrap attributes into multiple lines).

## Examples

### Example 1: Strongly Typed Dynamic Tabs with KeepAlive and shallowRef
```vue
<template>
  <div flex flex-col w-full>
    <div flex gap-2 mb-4>
      <MaxButton v-for="tab in tabItems" :key="tab.id" :variant="activeTab === tab.id ? undefined : 'text'" :label="tab.label" @click="activeTab = tab.id" />
    </div>
    <div>
      <KeepAlive :max="5">
        <component :is="activeComponent" />
      </KeepAlive>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, shallowRef, markRaw } from 'vue';
import TabOverview from './TabOverview.vue';
import TabAnalytics from './TabAnalytics.vue';
import TabSettings from './TabSettings.vue';

// Define a estrutura para cada item de aba
interface TabItem {
  id: string;
  label: string;
  component: any;
}

// Mapeamento dos componentes usando markRaw para evitar reatividade profunda desnecessária
const tabItems = ref<TabItem[]>([
  { id: 'overview', label: 'Visão Geral', component: markRaw(TabOverview) },
  { id: 'analytics', label: 'Métricas', component: markRaw(TabAnalytics) },
  { id: 'settings', label: 'Configurações', component: markRaw(TabSettings) }
]);

const activeTab = ref<string>('overview');

// Utiliza computed para obter o componente ativo
const activeComponent = computed(() => {
  const currentTab = tabItems.value.find(tab => tab.id === activeTab.value);
  return currentTab ? currentTab.component : null;
});
</script>
```

> Estado ativo/inativo da aba: use a própria prop `variant` do `MaxButton` (aba ativa = variante sólida padrão; abas inativas = `variant="text"`), em vez de tentar estilizar uma classe interna inventada como `.max-button` — o `MaxButton` renderiza um `<Button>` do PrimeVue e só aplica condicionalmente `.max-button-dashed` / `.icon-button-b`, nunca uma classe `.max-button`. Layout/espaçamento via atributos UnoCSS (attributify) com tokens do tema.

### Example 2: Code Splitting with defineAsyncComponent and Cache Lifecycle Hooks
```vue
<template>
  <div p-6 bg-background>
    <h2>Painel Executivo</h2>
    <div mt-4 min-h-75>
      <KeepAlive include="AsyncChartWidget" :max="3">
        <component :is="chartComponent" />
      </KeepAlive>
    </div>
  </div>
</template>

<script setup lang="ts">
import { shallowRef, defineAsyncComponent, defineComponent, h } from 'vue';
import LoadingSpinner from './LoadingSpinner.vue';
import ErrorDisplay from './ErrorDisplay.vue';

// O wrapper de defineAsyncComponent NÃO expõe o nome do componente interno,
// então `<KeepAlive include="AsyncChartWidget">` não casaria. Damos um nome
// explícito ao wrapper para que o `include` resolva corretamente.
const AsyncChartInner = defineAsyncComponent({
  loader: () => import('./components/AsyncChartWidget.vue'),
  loadingComponent: LoadingSpinner,
  delay: 200, // Evita flash do spinner para conexões rápidas
  errorComponent: ErrorDisplay,
  timeout: 5000 // Limite de 5 segundos para carregar
});

const AsyncChartWidget = defineComponent({
  name: 'AsyncChartWidget', // nome que o KeepAlive `include` irá casar
  render: () => h(AsyncChartInner)
});

// shallowRef para melhor performance ao gerenciar o componente dinâmico
const chartComponent = shallowRef(AsyncChartWidget);
</script>
```

### Example 3: Inside a Cached Tab Component (AsyncChartWidget.vue)
```vue
<template>
  <div b="1 solid $gray-light" p-4 rounded-lg>
    <h3>Relatório de Engajamento</h3>
    <div>
      <div v-if="loading">Carregando dados atualizados...</div>
      <div v-else>Gráfico renderizado: {{ chartData }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onActivated, onDeactivated } from 'vue';

// Define o nome do componente explicitamente para compatibilidade com KeepAlive include/exclude
defineOptions({
  name: 'AsyncChartWidget'
});

const loading = ref<boolean>(false);
const chartData = ref<string>('');
let dataInterval = null as any;

// Função para simular carregamento de dados periódicos
const fetchData = async () => {
  loading.value = true;
  // Simula requisição de API
  chartData.value = 'Métricas atualizadas em ' + new Date().toLocaleTimeString();
  loading.value = false;
};

// Dispara toda vez que a aba com este componente é exibida/ativada
onActivated(() => {
  fetchData();
  // Configura atualização periódica em segundo plano apenas enquanto ativo
  dataInterval = setInterval(fetchData, 30000);
  console.log('Componente de métricas ativado. Intervalo registrado.');
});

// Limpa recursos quando o usuário muda de aba e o componente é ocultado/desativado
onDeactivated(() => {
  if (dataInterval) {
    clearInterval(dataInterval);
    dataInterval = null;
  }
  console.log('Componente de métricas desativado. Intervalo limpo.');
});
</script>
```

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **Do NOT** use Options API (`data`, `methods`, etc.). All logic must use Composition API (`<script setup lang="ts">`).
- **Do NOT** wrap dynamic components in standard `ref()` without wrapping the component definition in `markRaw()`, or assigning to a `shallowRef()`. Wrapping large component instances in a deep reactive proxy will cause severe performance degradation and browser warnings.
- **Do NOT** omit the `max` prop on `<KeepAlive>`. Unbounded caches can lead to browser memory exhaustion, especially on heavy dashboards.
- **Do NOT** use `onMounted` or `onUnmounted` for actions that must execute every time the user enters or leaves a cached view (e.g., starting pollers, updating data). Use `onActivated` and `onDeactivated` instead.
- **Do NOT** write `<style scoped lang="scss">` blocks or raw hex colors (e.g. `#007bff`). All styling must use UnoCSS attributify (`presetMaxUno`) via inline attributes on the elements, using theme tokens (`bg-primary`, `bg-background`, `color-white`, `border-$gray-light`) instead of hardcoded colors.
- **Do NOT** break Vue component tags into multiple lines in the `<template>` section. Keep all attributes inline on a single line.
- **Do NOT** write code comments in English. All code comments in examples must be written in Brazilian Portuguese (pt-BR).
