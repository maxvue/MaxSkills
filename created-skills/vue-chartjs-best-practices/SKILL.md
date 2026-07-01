---
name: vue-chartjs-best-practices
description: Use when creating, modifying, or debugging data visualization components, charts, and graphs using Chart.js in Vue 3. Triggers on chart instantiation, responsive canvas config, chart lifecycle (destroy/update), chart tooltips localization, and dynamic theme colors binding.
---

# Boas Práticas de Chart.js no Vue 3

## Objetivo
Estabelecer diretrizes e templates para a implementação, gerenciamento do ciclo de vida, atualização e vinculação de estilos de gráficos interativos utilizando Chart.js no Vue 3 dentro do ecossistema Engeapp.

## Instruções
1. **Ordenação de Blocos SFC:** Sempre estruture os arquivos Vue que contêm gráficos na seguinte ordem:
   1. `<template>`
   2. `<script setup lang="ts">`
   3. `<style scoped lang="scss">`

2. **Integração com Template:**
   - Defina um contêiner envolvente para responsividade (ex: `.chart-container`) com posicionamento relativo e dimensões fixas (largura/altura ou proporção de tela).
   - Use elementos `<canvas>` puros com o atributo `ref`.
   - Mantenha todos os atributos do `<canvas>` ou de componentes em uma única linha (formato inline).

3. **Gerenciamento do Ciclo de Vida e Vazamentos de Memória (Memory Leaks):**
   - Sempre armazene a instância criada do `Chart`.
   - Registre os elementos necessários global ou localmente utilizando `Chart.register(...registerables)`.
   - Chame `chartInstance.destroy()` dentro do hook `onUnmounted` ou antes de criar uma nova instância no mesmo canvas para evitar memory leaks e gráficos fantasmas.
   - Use `nextTick` antes de inicializar o gráfico para garantir que o elemento canvas no DOM esteja disponível.

4. **Reatividade e Atualização de Dados:**
   - Monitore os conjuntos de dados (datasets) ou o estado de origem usando `watch` do Vue com `{ deep: true }`.
   - Prefira atualizar os dados do gráfico diretamente (`chart.data.datasets[0].data = newData` seguido por `chart.update()`) em vez de destruir e reconstruir o gráfico do zero, a menos que as estruturas de configuração ou tipos de gráfico mudem.

5. **Vinculação de Cores de Tema (Escuro/Claro):**
   - Vincule cores a variáveis CSS personalizadas (custom properties) do sistema (ex: `var(--text-color)`, `var(--primary-color)`).
   - Resolva variáveis CSS programaticamente usando `getComputedStyle(document.documentElement).getPropertyValue('--nome-da-var').trim()` caso o Chart.js exija valores em string.
   - Atualize ou reconstrua o gráfico quando o tema da aplicação mudar.

6. **Localização e Formatação:**
   - Formate os rótulos dos eixos e os tooltips para a moeda brasileira (BRL) ou formatos de data brasileiros utilizando `Intl.NumberFormat('pt-BR', ...)` ou helpers de formatação customizados.

7. **Origem dos Dados:**
   - O componente de gráfico deve ser apresentacional e receber os dados via `props`.
   - Os dados de origem devem vir de uma store `@maxvue/max-pinia` no componente pai; não faça requisições GET manuais (axios/fetch) dentro do componente de gráfico.

## Restrições
- NÃO use a Options API. Sempre utilize a Composition API (`<script setup lang="ts">`).
- NÃO instancie gráficos em elementos canvas sem envolver a criação com `nextTick()` ou `onMounted()`.
- NÃO deixe instâncias de gráficos ativas sem destruí-las na desmontagem do componente (`onUnmounted`).
- NÃO quebre os atributos em várias linhas no bloco `<template>`. As regras de formatação exigem atributos na mesma linha.
- NÃO utilize cores estáticas (ex: `#ffffff`, `#333333`) para textos, grades e bordas; sempre use ou resolva as variáveis CSS de tema.

## Examples
### Componente de Gráfico de Barras Reativo Seguro

```vue
<template>
  <div class="chart-container">
    <canvas ref="canvasRef" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';

Chart.register(...registerables);

const props = defineProps<{
  chartData: number[];
  labels: string[];
}>();

const canvasRef = ref<HTMLCanvasElement | null>(null);
let chartInstance: Chart | null = null;

// Função para destruir o gráfico com segurança
const destroyChart = (): void => {
  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }
};

// Função para inicializar o gráfico
const initChart = (): void => {
  destroyChart();
  if (!canvasRef.value) return;

  const ctx = canvasRef.value.getContext('2d');
  if (!ctx) return;

  // Resolve as cores a partir das variáveis CSS de tema (claro/escuro)
  const rootStyles = getComputedStyle(document.documentElement);
  const textColor = rootStyles.getPropertyValue('--text-color').trim();
  const primaryColor = rootStyles.getPropertyValue('--primary-color').trim();
  const primaryColorSoft = rootStyles.getPropertyValue('--primary-color-soft').trim() || primaryColor;

  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: props.labels,
      datasets: [{
        label: 'Dados',
        data: props.chartData,
        backgroundColor: primaryColorSoft,
        borderColor: primaryColor,
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: textColor
          }
        }
      },
      scales: {
        x: {
          ticks: { color: textColor }
        },
        y: {
          ticks: { color: textColor }
        }
      }
    }
  });
};

// Observa mudanças nos dados para atualizar o gráfico reativamente
watch(() => props.chartData, (newData) => {
  if (chartInstance) {
    chartInstance.data.datasets[0].data = newData;
    chartInstance.update();
  } else {
    nextTick(() => initChart());
  }
}, { deep: true });

onMounted(() => {
  nextTick(() => initChart());
});

onUnmounted(() => {
  destroyChart();
});
</script>

<style scoped lang="scss">
.chart-container {
  position: relative;
  width: 100%;
  height: 300px;
}
</style>
```
