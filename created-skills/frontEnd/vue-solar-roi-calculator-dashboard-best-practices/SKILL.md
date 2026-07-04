---
name: vue-solar-roi-calculator-dashboard-best-practices
description: Use when creating, modifying, styling, or debugging the financial ROI (Return on Investment) calculator dashboard or financial feasibility components in Vue 3 (Engeapp). Triggers on components rendering payback tables, cumulative savings charts, electricity tariff inflation settings, discount rates, equipment depreciation, or cash flow projections for photovoltaic solar energy systems.
---

## Objetivo
Fornecer diretrizes de design, padrões de implementação matemática e melhores práticas de UX para o desenvolvimento e manutenção do dashboard da calculadora de ROI financeiro solar e visões de viabilidade econômica em Vue 3 (Engeapp).

## Instruções
1. **Arquitetura de Componentes e Layout**:
   - Crie um layout limpo com parâmetros-chave em uma barra lateral (sidebar) ou em um card de configuração dedicado, e os indicadores de saída (VPL, TIR, Payback, Economia Acumulada) em cards visuais de destaque no topo.
   - Use o componente `MaxInputNumber` da biblioteca `@maxvue/max-components-ui` para todas as entradas numéricas, com seus respectivos prefixos (ex: `prefix="R$"` para custos de investimento) ou sufixos (ex: `suffix="%"` para taxas de inflação, degradação ou desconto).
   - Mantenha a formatação de atributos em uma única linha (inline) dentro do template do Vue para todos os componentes de UI.

2. **Cálculos Financeiros Reativos (Composition API)**:
   - **Persistência via MaxPinia**: parâmetros de entrada (custo do sistema, geração, tarifa, inflação, taxa de desconto) e cenários salvos são dados de página. Carregue-os e salve-os por uma store `@maxvue/max-pinia` (rotas string `/api/...`); o salvamento é automático/debounced ao alterar o estado da store. Não faça GET/POST manual nem mantenha esses parâmetros apenas em `ref` locais quando forem persistidos por projeto/proposta. Use `ref` locais apenas para simulações efêmeras de "what-if".
   - Vincule os valores de entrada a propriedades reativas (vindas da store ou `ref` locais para simulação). Use propriedades computadas (`computed`) para valores derivados (como degradação anual, geração anual ajustada e projeções de fluxo de caixa anuais).
   - Projete os valores do fluxo de caixa por até 25 anos. Mantenha os cálculos reativos usando o sistema de reatividade do Vue.
   - Calcule separadamente os custos de energia usando os componentes de TUSD (Tarifa de Uso do Sistema de Distribuição) e TE (Tarifa de Energia) para tratar os cenários tributários corretos (ICMS, PIS, COFINS) conforme as regras de tarifa de concessionárias expostas pelo backend AdonisJS. As tarifas e regras regulatórias devem ser carregadas via store `@maxvue/max-pinia` (GET para `/api/...`), nunca codificadas no front.
   - Considere a degradação anual dos painéis (tipicamente entre 0,5% e 0,8% ao ano), a inflação da tarifa de energia (tipicamente entre 5% e 10% ao ano) e a taxa de desconto (cálculo de VPL baseado na taxa Selic ou na taxa de atratividade mínima do cliente).
   - Certifique-se de deduzir a depreciação do inversor (custo de substituição) como uma despesa de manutenção (O&M) no ano 10 ou 15.
   - Para simulações de financiamento, implemente as fórmulas das tabelas SAC ou Price em composables locais.

3. **Representação Visual (Chart.js)**:
   - Integre um gráfico de linha do fluxo de caixa acumulado mostrando o ponto de transição do payback (do saldo acumulado negativo para positivo) ao longo de 25 anos.
   - Siga as diretrizes de `vue-chartjs-best-practices`: envolva o canvas dentro de um contêiner `.chart-container`, inicialize dentro do hook `onMounted` com `nextTick`, destrua no `onUnmounted` para evitar vazamentos de memória (memory leaks) e atualize os conjuntos de dados (datasets) reativamente usando um watch profundo.
   - Formate todos os rótulos de eixos e dicas de ferramentas (tooltips) usando o helper `formatCurrency` de `@maxvue/max-use`. Ele é auto-importado pelo `unplugin-auto-import` do projeto — NÃO escreva o `import` manualmente.

4. **Grade de Dados e Exportação (MaxTable)**:
   - Exiba uma tabela detalhada do fluxo de caixa ano a ano usando o componente `MaxTable`.
   - As colunas devem incluir: Ano, Geração de Energia (kWh), Economia Anual (R$), Custos de O&M (R$), Fluxo de Caixa Líquido (R$) e Saldo Acumulado (R$).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- NÃO utilize a Options API. Sempre use a Composition API do Vue 3 com `<script setup lang="ts">`.
- NÃO realize cálculos financeiros utilizando números de ponto flutuante brutos (floats) onde a precisão exata é exigida (especialmente ao lidar com centavos de Real); utilize inteiros representando centavos ou funções de arredondamento seguras.
- NÃO recalcule VPL/TIR/payback a partir de strings formatadas (ex.: `parseFloat(item.netFlow.replace(...))`). Mantenha os valores numéricos crus (ex.: `rawNetFlow`, `rawCumulative`) na estrutura de dados e use o número formatado APENAS para exibição. Fazer parse de string formatada de volta para número perde precisão e contraria a restrição acima.
- NÃO escreva estilos CSS diretamente inline. Use SCSS escopado (`<style scoped lang="scss">`) para o layout do dashboard.
- NÃO deixe instâncias do Chart.js ativas sem chamar o método `.destroy()` quando o componente for desmontado.
- NÃO quebre tags de componentes Vue em várias linhas no bloco `<template>`. As regras do formatador exigem atributos em linha única.
- NÃO escreva comentários no código em outro idioma que não seja o Português do Brasil (pt-BR) dentro dos componentes do cliente.

# Exemplos
### Exemplo de Componente de Calculadora de ROI Interativa

```vue
<template>
  <div class="solar-roi-dashboard">
    <!-- Indicadores no Topo -->
    <div class="metrics-grid">
      <div class="metric-card">
        <h3>VPL (Valor Presente Líquido)</h3>
        <p class="value">{{ formattedNpv }}</p>
      </div>
      <div class="metric-card">
        <h3>TIR (Taxa Interna de Retorno)</h3>
        <p class="value">{{ formattedIrr }}</p>
      </div>
      <div class="metric-card">
        <h3>Payback Descontado</h3>
        <p class="value">{{ paybackYears }} Anos</p>
      </div>
    </div>

    <!-- Controles e Tabela/Gráfico -->
    <div class="dashboard-body">
      <div class="controls-panel">
        <MaxInputNumber v-model="systemCost" label="Custo do Sistema" prefix="R$" />
        <MaxInputNumber v-model="annualGeneration" label="Geração Anual Inicial" suffix="kWh" />
        <MaxInputNumber v-model="energyTariff" label="Tarifa de Energia" prefix="R$/kWh" :minFractionDigits="4" />
        <MaxInputNumber v-model="inflationRate" label="Inflação da Tarifa (a.a.)" suffix="%" />
        <MaxInputNumber v-model="discountRate" label="Taxa de Desconto (a.a.)" suffix="%" />
      </div>

      <div class="visualization-panel">
        <!-- Gráfico de Fluxo de Caixa Acumulado -->
        <div class="chart-container">
          <canvas ref="chartCanvas" />
        </div>

        <!-- Tabela Detalhada -->
        <MaxTable :value="cashFlowData" stripedRows>
          <Column field="year" header="Ano" />
          <Column field="generation" header="Geração (kWh)" />
          <Column field="savings" header="Economia" />
          <Column field="costs" header="Custos O&M" />
          <Column field="netFlow" header="Fluxo Líquido" />
          <Column field="cumulative" header="Acumulado" />
        </MaxTable>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';
// `formatCurrency` é auto-importado (unplugin-auto-import); não importe manualmente.

Chart.register(...registerables);

// Parâmetros reativos de entrada
const systemCost = ref<number>(35000);
const annualGeneration = ref<number>(6000);
const energyTariff = ref<number>(0.85);
const inflationRate = ref<number>(6.5);
const discountRate = ref<number>(10.75);

const chartCanvas = ref<HTMLCanvasElement | null>(null);
let chartInstance: Chart | null = null;

// Cálculo do fluxo de caixa projetado para 25 anos
interface CashFlowItem {
  year: number;
  generation: number;
  // Valores numéricos crus — fonte de verdade para os cálculos financeiros.
  rawSavings: number;
  rawCosts: number;
  rawNetFlow: number;
  rawCumulative: number;
  // Strings formatadas — uso EXCLUSIVO de exibição.
  savings: string;
  costs: string;
  netFlow: string;
  cumulative: string;
}

const cashFlowData = computed<CashFlowItem[]>(() => {
  const data: CashFlowItem[] = [];
  const cost = systemCost.value;
  const initialGen = annualGeneration.value;
  const tariff = energyTariff.value;
  const inflation = inflationRate.value / 100;
  const degradation = 0.007; // 0.7% a.a.

  let cumulative = -cost;

  // Ano 0: Apenas investimento inicial
  data.push({
    year: 0,
    generation: 0,
    rawSavings: 0,
    rawCosts: cost,
    rawNetFlow: -cost,
    rawCumulative: -cost,
    savings: formatCurrency(0),
    costs: formatCurrency(cost),
    netFlow: formatCurrency(-cost),
    cumulative: formatCurrency(-cost)
  });

  for (let year = 1; year <= 25; year++) {
    // Geração ajustada com degradação do painel
    const gen = initialGen * Math.pow(1 - degradation, year - 1);
    // Tarifa reajustada com inflação
    const currentTariff = tariff * Math.pow(1 + inflation, year - 1);
    const savings = gen * currentTariff;

    // Custo de manutenção (O&M): 1% do custo do sistema, e troca do inversor no ano 12
    let maintenance = cost * 0.01;
    if (year === 12) {
      maintenance += cost * 0.15; // Custo estimado para substituição do inversor
    }

    const netFlow = savings - maintenance;
    cumulative += netFlow;

    data.push({
      year,
      generation: Math.round(gen),
      rawSavings: savings,
      rawCosts: maintenance,
      rawNetFlow: netFlow,
      rawCumulative: cumulative,
      savings: formatCurrency(savings),
      costs: formatCurrency(maintenance),
      netFlow: formatCurrency(netFlow),
      cumulative: formatCurrency(cumulative)
    });
  }

  return data;
});

// Valor Presente Líquido (VPL)
const npvValue = computed<number>(() => {
  const cost = systemCost.value;
  const rate = discountRate.value / 100;
  let npv = -cost;

  cashFlowData.value.slice(1).forEach((item, index) => {
    npv += item.rawNetFlow / Math.pow(1 + rate, index + 1);
  });

  return npv;
});

const formattedNpv = computed<string>(() => formatCurrency(npvValue.value));

// Payback Descontado (anos para retorno do investimento considerando taxa de desconto)
const paybackYears = computed<number>(() => {
  const cost = systemCost.value;
  const rate = discountRate.value / 100;
  let cumulativeValue = -cost;

  for (let i = 1; i <= 25; i++) {
    const item = cashFlowData.value[i];
    cumulativeValue += item.rawNetFlow / Math.pow(1 + rate, i);
    if (cumulativeValue >= 0) {
      return i;
    }
  }

  return 25;
});

// Taxa Interna de Retorno (TIR) - Estimativa simples via Newton-Raphson
const formattedIrr = computed<string>(() => {
  const flows = [
    -systemCost.value,
    ...cashFlowData.value.slice(1).map(item => item.rawNetFlow)
  ];

  let guess = 0.1;
  const maxIterations = 100;
  const precision = 1e-6;

  for (let i = 0; i < maxIterations; i++) {
    let npv = 0;
    let dNpv = 0;

    for (let t = 0; t < flows.length; t++) {
      npv += flows[t] / Math.pow(1 + guess, t);
      dNpv -= (t * flows[t]) / Math.pow(1 + guess, t + 1);
    }

    const nextGuess = guess - npv / dNpv;
    if (Math.abs(nextGuess - guess) < precision) {
      return `${(nextGuess * 100).toFixed(2)}%`;
    }
    guess = nextGuess;
  }

  return 'N/A';
});

// Gerenciamento e renderização do gráfico
const destroyChart = (): void => {
  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }
};

const renderChart = (): void => {
  destroyChart();
  if (!chartCanvas.value) return;

  const ctx = chartCanvas.value.getContext('2d');
  if (!ctx) return;

  const labels = cashFlowData.value.map(item => `Ano ${item.year}`);
  const chartData = cashFlowData.value.map(item => item.rawCumulative);

  chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Saldo Acumulado (R$)',
        data: chartData,
        // Puxe a cor do tema (token CSS) em vez de fixar um hex — mantém coerência com o theme.
        borderColor: getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim(),
        backgroundColor: `rgb(from ${getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim()} r g b / 0.1)`,
        fill: true,
        tension: 0.1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          ticks: {
            callback: (val) => formatCurrency(Number(val))
          }
        }
      }
    }
  });
};

// Reconstrói o gráfico quando os parâmetros mudam
watch([systemCost, annualGeneration, energyTariff, inflationRate, discountRate], () => {
  nextTick(() => renderChart());
});

onMounted(() => {
  nextTick(() => renderChart());
});

onUnmounted(() => {
  destroyChart();
});
</script>

<style scoped lang="scss">
.solar-roi-dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;

  .metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;

    .metric-card {
      background: var(--surface-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 15px;
      text-align: center;

      h3 {
        font-size: 14px;
        color: var(--text-color-secondary);
        margin-bottom: 8px;
      }

      .value {
        font-size: 20px;
        font-weight: bold;
        color: var(--primary-color);
      }
    }
  }

  .dashboard-body {
    display: grid;
    grid-template-columns: 300px 1fr;
    gap: 20px;

    .controls-panel {
      display: flex;
      flex-direction: column;
      gap: 15px;
      background: var(--surface-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 20px;
    }

    .visualization-panel {
      display: flex;
      flex-direction: column;
      gap: 20px;

      .chart-container {
        position: relative;
        height: 300px;
        background: var(--surface-card);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 15px;
      }
    }
  }
}
</style>
```
