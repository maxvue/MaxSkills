---
name: vue-3-dynamic-components-and-keep-alive-caching-best-practices
description: Use when designing, implementing, or optimizing dynamic component loading using Vue 3 <component :is="...">, rendering asynchronous components with defineAsyncComponent, or managing component caching and lifecycle hooks with <KeepAlive> (e.g., handling onActivated/onDeactivated, cache invalidation, and custom cache keys). Triggers when creating dynamic tab interfaces, multi-step wizards, or dashboard layouts with state retention.
---

## Objetivo
Fornecer diretrizes, padrões e melhores práticas para a implementação de renderização de componentes dinâmicos, carregamento assíncrono e cache de telas/abas usando o Vue 3, com foco em otimização de performance, retenção adequada de estado e gerenciamento de memória.

## Instruções
1. **Renderização Dinâmica com `<component :is="...">`**:
   - Utilize `<component :is="currentComponent" />` para renderizar interfaces de componentes dinâmicos, como abas ou assistentes passo a passo (wizards).
   - **Performance (shallowRef/markRaw)**: Sempre envolva as definições de componentes carregados dinamicamente em `shallowRef` em vez de `ref`, ou utilize `markRaw` ao atribuí-las ao estado reativo. Isso evita que o Vue observe profundamente a instância do componente (métodos, estado interno, etc.), o que degrada a performance e gera alertas no console.
   - **Tipagem Forte**: Defina objetos de mapeamento para componentes com TypeScript para garantir a segurança de tipos.

2. **Componentes Assíncronos (`defineAsyncComponent`)**:
   - Use `defineAsyncComponent` para realizar divisão de código (code-splitting) em componentes pesados (ex: editores complexos, simuladores de prévia de post, gráficos) que não são necessários durante o carregamento inicial da página.
   - Configure opções como `loadingComponent` (spinner/esqueleto de carregamento), `errorComponent` (interface de fallback de erro), `delay` (evita piscadas em conexões rápidas) e `timeout` (limita o tempo máximo de carregamento).

3. **Retenção de Estado e Cache (`<KeepAlive>`)**:
   - Envolva `<component :is="...">` com `<KeepAlive>` para cachear instâncias de componentes desativados, preservando o estado do DOM interno e as variáveis reativas.
   - **Limites de Cache (`max`)**: Sempre configure o atributo `max` (ex: `<KeepAlive :max="10">`) para limitar o número de instâncias mantidas em cache e evitar vazamentos de memória.
   - **Cache Direcionado (`include` / `exclude`)**: Use as propriedades `include` ou `exclude` para especificar exatamente quais componentes devem ser cacheados. Certifique-se de que os componentes tenham a opção `name` definida (ou sejam nomeados automaticamente com base no nome do arquivo) para corresponder a estes padrões.

4. **Ganchos de Ciclo de Vida do Componente (`onActivated` / `onDeactivated`)**:
   - Use `onActivated` para executar código quando um componente cacheado for reinserido no DOM (ex: buscar dados atualizados, iniciar animações, inscrever-se em websockets).
   - Use `onDeactivated` para liberar recursos quando o componente for mantido em cache mas removido da visualização (ex: pausar intervalos, cancelar inscrições de eventos, persistir rascunhos de formulários).
   - Evite usar `onMounted` ou `onUnmounted` para tarefas que devem ser executadas toda vez que o usuário navega de volta a uma aba cacheada, pois esses ganchos disparam apenas uma vez por ciclo de montagem/desmontagem do componente.

5. **Padrões de Composition API e Componentes de Arquivo Único (SFC)**:
   - Certifique-se de que todos os componentes utilizem `<script setup lang="ts">` e `<style scoped lang="scss">`.
   - A ordem dos blocos deve seguir estritamente: `<template>`, depois `<script>`, e por fim `<style>`.
   - Nos templates, formate as tags dos componentes com todos os parâmetros em uma única linha (layout inline, não quebre atributos em múltiplas linhas).

## Exemplos

### Exemplo 1: Abas Dinâmicas Fortemente Tipadas com KeepAlive e shallowRef
```vue
<template>
  <div class="tabs-container">
    <div class="tabs-header">
      <button v-for="tab in tabItems" :key="tab.id" :class="{ active: activeTab === tab.id }" @click="activeTab = tab.id">{{ tab.label }}</button>
    </div>
    <div class="tabs-content">
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

<style scoped lang="scss">
.tabs-container {
  display: flex;
  flex-direction: column;
  width: 100%;
  
  .tabs-header {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    
    button {
      padding: 8px 16px;
      border: 1px solid #ccc;
      background-color: #f9f9f9;
      cursor: pointer;
      
      &.active {
        background-color: #007bff;
        color: white;
        border-color: #007bff;
      }
    }
  }
}
</style>
```

### Exemplo 2: Divisão de Código com defineAsyncComponent e Ganchos do KeepAlive
```vue
<template>
  <div class="dashboard-panel">
    <h2>Painel Executivo</h2>
    <div class="widget-area">
      <KeepAlive include="AsyncChartWidget" :max="3">
        <component :is="chartComponent" />
      </KeepAlive>
    </div>
  </div>
</template>

<script setup lang="ts">
import { shallowRef, defineAsyncComponent } from 'vue';
import LoadingSpinner from './LoadingSpinner.vue';
import ErrorDisplay from './ErrorDisplay.vue';

// Carrega o componente de forma assíncrona com estados de carregamento e erro
const AsyncChartWidget = defineAsyncComponent({
  loader: () => import('./components/AsyncChartWidget.vue'),
  loadingComponent: LoadingSpinner,
  delay: 200, // Evita flash do spinner para conexões rápidas
  errorComponent: ErrorDisplay,
  timeout: 5000 // Limite de 5 segundos para carregar
});

// shallowRef para melhor performance ao gerenciar o componente dinâmico
const chartComponent = shallowRef(AsyncChartWidget);
</script>

<style scoped lang="scss">
.dashboard-panel {
  padding: 24px;
  background-color: #ffffff;
  
  .widget-area {
    margin-top: 16px;
    min-height: 300px;
  }
}
</style>
```

### Exemplo 3: Dentro do Componente Cacheado (AsyncChartWidget.vue)
```vue
<template>
  <div class="chart-widget">
    <h3>Relatório de Engajamento</h3>
    <div class="chart-container">
      <div v-if="loading">Carregando dados atualizados...</div>
      <div v-else class="chart-placeholder">Gráfico renderizado: {{ chartData }}</div>
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

<style scoped lang="scss">
.chart-widget {
  border: 1px solid #eaeaea;
  padding: 16px;
  border-radius: 8px;
}
</style>
```

## Restrições
- **NÃO** use Options API (`data`, `methods`, etc.). Toda a lógica de componente deve utilizar Composition API (`<script setup lang="ts">`).
- **NÃO** envolva componentes dinâmicos em `ref()` padrão sem envolver a definição do componente em `markRaw()`, ou atribuí-los a um `shallowRef()`. Envolver instâncias de componentes grandes em proxies reativos profundos causa degradação severa de performance e avisos no console do navegador.
- **NÃO** omita a propriedade `max` em `<KeepAlive>`. Caches sem limites podem levar à exaustão de memória no navegador, especialmente em painéis pesados de dashboard.
- **NÃO** utilize `onMounted` ou `onUnmounted` para ações que devem ser executadas todas as vezes que o usuário entra ou sai de uma visualização cacheada (ex: iniciar buscas periódicas, atualizar dados locais). Em vez disso, utilize os hooks `onActivated` e `onDeactivated`.
- **NÃO** escreva estilos em CSS puro. Toda a estilização deve utilizar SCSS (`lang="scss"`).
- **NÃO** quebre as tags de componentes Vue em várias linhas na seção `<template>`. Mantenha todos os atributos inline em uma única linha.
- **NÃO** escreva comentários do código de exemplo em outro idioma além do Português do Brasil (pt-BR).
