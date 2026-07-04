---
name: vue-3-dynamic-components-and-keep-alive-caching-best-practices
description: Use when designing, implementing, or optimizing dynamic component loading using Vue 3 <component :is="...">, rendering asynchronous components with defineAsyncComponent, or managing component caching and lifecycle hooks with <KeepAlive> (e.g., handling onActivated/onDeactivated, cache invalidation, and custom cache keys). Triggers when creating dynamic tab interfaces, multi-step wizards, or dashboard layouts with state retention.
---

## Objetivo
Fornecer diretrizes, padrões e boas práticas para implementar renderização dinâmica de componentes, carregamento assíncrono e cache de telas/abas usando Vue 3, com foco em otimização de performance, retenção adequada de estado e gerenciamento de memória.

## Instruções
1. **Renderização Dinâmica com `<component :is="...">`**:
   - Utilize `<component :is="currentComponent" />` para renderizar interfaces de componentes dinâmicos, como abas ou wizards.
   - **Performance (shallowRef/markRaw)**: Sempre encapsule as definições de componentes carregados dinamicamente em `shallowRef` em vez de `ref`, ou aplique `markRaw` ao atribuí-las a um estado reativo. Isso evita que o Vue observe profundamente a instância do componente (métodos, estado interno, etc.), o que degrada a performance e dispara avisos no console.
   - **Tipagem Forte**: Defina objetos de mapeamento para os componentes com TypeScript para garantir type safety.

2. **Componentes Assíncronos (`defineAsyncComponent`)**:
   - Use `defineAsyncComponent` para fazer code-splitting de componentes pesados (ex.: editores complexos, simuladores de painel de preview, gráficos) que não são necessários durante o carregamento inicial da página.
   - Configure opções como `loadingComponent` (spinner/skeleton), `errorComponent` (UI de fallback), `delay` (evita estados de carregamento piscando) e `timeout` (limita o tempo de carregamento).

3. **Retenção de Estado e Cache (`<KeepAlive>`)**:
   - Envolva `<component :is="...">` dentro de `<KeepAlive>` para armazenar em cache instâncias de componentes desativados, preservando seu estado interno do DOM e variáveis reativas.
   - **Limites de Cache (`max`)**: Sempre defina o atributo `max` (ex.: `<KeepAlive :max="10">`) para limitar o número de instâncias em cache e evitar vazamentos de memória.
   - **Cache Direcionado (`include` / `exclude`)**: Use as props `include` ou `exclude` para especificar exatamente quais componentes devem ser cacheados. Garanta que os componentes tenham uma opção `name` definida (ou sejam nomeados automaticamente com base no nome do arquivo) para casar com esses padrões.

4. **Hooks de Ciclo de Vida do Componente (`onActivated` / `onDeactivated`)**:
   - Use `onActivated` para executar código quando um componente cacheado é reinserido no DOM (ex.: buscar dados atualizados, iniciar animações, se inscrever em web sockets).
   - Use `onDeactivated` para limpar recursos quando o componente é cacheado mas removido da visualização (ex.: pausar intervalos, cancelar inscrições de listeners de eventos, persistir estados de rascunho).
   - Evite usar `onMounted` ou `onUnmounted` para tarefas que devem ser executadas toda vez que o usuário volta para uma aba cacheada, pois esses hooks disparam apenas uma vez por ciclo de mount/unmount do componente.

5. **Padrões da Composition API & SFC**:
   - Garanta que todos os componentes usem `<script setup lang="ts">`.
   - Estilize via UnoCSS attributify (`presetMaxUno`) com tokens de tema (`bg-primary`, `bg-background`, `color-text`, `border-$gray-light`, etc.) aplicados como atributos inline nos elementos — NÃO escreva blocos `<style scoped lang="scss">` nem cores hex cruas.
   - A ordem dos blocos deve seguir estritamente: `<template>`, depois `<script>`.
   - Nos templates, formate as tags de componente com todos os parâmetros em uma única linha (layout inline, não quebre os atributos em múltiplas linhas).

## Exemplos

### Exemplo 1: Abas Dinâmicas Fortemente Tipadas com KeepAlive e shallowRef
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

### Exemplo 2: Code Splitting com defineAsyncComponent e Hooks de Ciclo de Vida de Cache
```vue
<template>
  <div p-6 bg-background>
    <MaxTitle1 h2="Painel Executivo" />
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

### Exemplo 3: Dentro de um Componente de Aba Cacheado (AsyncChartWidget.vue)
```vue
<template>
  <div b="1 solid $gray-light" p-4 rounded-lg>
    <MaxTitle2>Relatório de Engajamento</MaxTitle2>
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

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- **NÃO** use a Options API (`data`, `methods`, etc.). Toda a lógica deve usar a Composition API (`<script setup lang="ts">`).
- **NÃO** encapsule componentes dinâmicos em um `ref()` padrão sem envolver a definição do componente em `markRaw()` ou atribuí-la a um `shallowRef()`. Encapsular instâncias grandes de componentes em um proxy reativo profundo causará severa degradação de performance e avisos no navegador.
- **NÃO** omita a prop `max` no `<KeepAlive>`. Caches sem limite podem levar ao esgotamento de memória do navegador, especialmente em dashboards pesados.
- **NÃO** use `onMounted` ou `onUnmounted` para ações que devem ser executadas toda vez que o usuário entra ou sai de uma view cacheada (ex.: iniciar pollers, atualizar dados). Use `onActivated` e `onDeactivated` em vez disso.
- **NÃO** escreva blocos `<style scoped lang="scss">` nem cores hex cruas (ex.: `#007bff`). Toda a estilização deve usar UnoCSS attributify (`presetMaxUno`) via atributos inline nos elementos, usando tokens de tema (`bg-primary`, `bg-background`, `color-white`, `border-$gray-light`) em vez de cores fixas.
- **NÃO** quebre as tags de componente Vue em múltiplas linhas na seção `<template>`. Mantenha todos os atributos inline em uma única linha.
- **NÃO** escreva comentários de código em inglês. Todos os comentários de código nos exemplos devem ser escritos em Português Brasileiro (pt-BR).
