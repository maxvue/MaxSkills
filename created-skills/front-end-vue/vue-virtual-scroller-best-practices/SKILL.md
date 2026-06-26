---
name: vue-virtual-scroller-best-practices
description: Use when implementing, configuring, or optimizing list virtualization in Vue 3 using the vue-virtual-scroller package. Triggers on virtual scrolling setup, RecycleScroller or DynamicScroller component integration, handling large datasets in the frontend, and performance optimization for heavy DOM rendering.
---

# Boas Práticas do Vue Virtual Scroller

## Objetivo
Fornecer diretrizes claras, acionáveis e padrões estruturais para a implementação de alta performance na virtualização de listas no Vue 3 utilizando a biblioteca `vue-virtual-scroller` dentro do ecossistema Engeapp.

## Instruções

### 1. Guia de Seleção de Componentes
Escolha o mecanismo de virtualização adequado com base nas características de tamanho dos seus dados:
- **`RecycleScroller`**: Utilize quando todos os itens possuem um **tamanho fixo e idêntico** (altura para layouts verticais, largura para layouts horizontais), ou quando os tamanhos já foram pré-calculados e armazenados no objeto de dados. Possui altíssimo desempenho.
- **`DynamicScroller`**: Utilize quando os itens possuem **tamanhos desconhecidos ou variáveis** que só podem ser medidos após serem renderizados na DOM (ex: feeds de mensagens dinâmicos, seções de comentários ou cards de altura variável).
- **`WindowScroller`**: Utilize quando os eventos de scroll devem ser controlados pelo viewport/barra de rolagem principal do navegador (window) em vez de um container de rolagem local.
- **Composables Headless (`useRecycleScroller`, `useDynamicScroller`)**: Utilize quando estruturas DOM customizadas (como `<table>`, `<tr>` semânticos ou caixas flex complexas) forem necessárias e elementos empacotadores (wrappers) de componentes padrão interferirem no layout ou acessibilidade.

### 2. Padrões de Integração de Componentes
Siga estas convenções de configuração e implementação:
- **Importação do CSS:** Certifique-se de importar `vue-virtual-scroller/dist/vue-virtual-scroller.css` no ponto de entrada da aplicação.
- **Dimensões do Container de Rolagem:** O elemento pai de rolagem **deve** possuir dimensões definidas (ex: `height: 100%`, `height: 400px` ou `flex-grow: 1`) e controles de overflow (`overflow-y: auto`) para evitar que o scroller renderize todos os itens simultaneamente na tela.
- **Dimensionamento dos Itens (Sizing):**
  - No `RecycleScroller`, sempre defina o `item-size` (em pixels).
  - No `DynamicScroller`, sempre defina o `min-item-size` (estimativa inicial aproximada em pixels) e envolva os conteúdos de cada item no componente `<DynamicScrollerItem>`, fornecendo as props necessárias: `item`, `active-holder` (geralmente `active`) e `id`.
- **Chaves Dinâmicas (Keying):** Garanta que as listas utilizem uma chave identificadora única (ex: `key-field="id"`). Evite usar o índice do array como chave.
- **Reciclagem Reativa de Dados:** Compreenda que os elementos dentro do pool de virtualização são reciclados e reutilizados. Componentes filhos nas linhas devem reagir dinamicamente a mudanças de props. Não inicialize estado não reativo no bloco `setup()` esperando que ele seja reexecutado para cada nova linha exibida.
- **Estilização Customizada de CSS:** Use as variáveis CSS/SCSS estabelecidas no Engeapp/MaxComponentsUi para estilização.

### 3. Convenções de Código
- **Composition API:** Sempre utilize `<script setup lang="ts">`. A Options API é estritamente proibida.
- **TypeScript:** Toda a lógica do componente deve ser fortemente tipada usando TypeScript.
- **SCSS:** Toda a estilização do componente deve utilizar SCSS (`lang="scss"`).
- **Atributos Inline:** Formate as tags dos componentes Vue no template de forma inline. Mantenha todos os atributos em uma única linha (ex: `<RecycleScroller :items="items" :item-size="50" key-field="id" />`).
- **Idioma dos Comentários:** Todos os comentários dentro do arquivo de código devem ser escritos em Português do Brasil (pt-BR).

## Exemplos

### RecycleScroller (Itens com Tamanho Fixo)
```vue
<template>
  <div class="scroller-container">
    <RecycleScroller class="my-scroller" :items="logs" :item-size="40" key-field="id" v-slot="{ item }">
      <div class="log-row">
        <span class="log-time">{{ item.timestamp }}</span>
        <span class="log-message">{{ item.message }}</span>
      </div>
    </RecycleScroller>
  </div>
</template>

<script setup lang="ts">
// Importações automáticas (ref, computed, etc. não precisam ser importados manualmente)
interface LogItem {
  id: number;
  timestamp: string;
  message: string;
}

defineProps<{
  logs: LogItem[];
}>();
</script>

<style scoped lang="scss">
.scroller-container {
  height: 500px;
  width: 100%;
  border: 1px solid var(--background-300);

  .my-scroller {
    height: 100%;
  }

  .log-row {
    display: flex;
    align-items: center;
    height: 40px;
    padding: 0 12px;
    border-bottom: 1px solid var(--background-200);

    .log-time {
      color: var(--text-muted);
      margin-right: 16px;
    }
  }
}
</style>
```

### DynamicScroller (Itens com Altura Variável/Desconhecida)
```vue
<template>
  <div class="scroller-container">
    <DynamicScroller class="my-scroller" :items="messages" :min-item-size="50" key-field="id">
      <template #default="{ item, index, active }">
        <DynamicScrollerItem :item="item" :active="active" :data-index="index" :data-active="active">
          <div class="message-card">
            <span class="message-sender">{{ item.sender }}</span>
            <p class="message-content">{{ item.text }}</p>
          </div>
        </DynamicScrollerItem>
      </template>
    </DynamicScroller>
  </div>
</template>

<script setup lang="ts">
interface MessageItem {
  id: number;
  sender: string;
  text: string;
}

defineProps<{
  messages: MessageItem[];
}>();
</script>

<style scoped lang="scss">
.scroller-container {
  height: 600px;
  width: 100%;

  .my-scroller {
    height: 100%;
  }

  .message-card {
    padding: 12px;
    border-bottom: 1px solid var(--background-300);

    .message-sender {
      font-weight: 600;
      color: var(--blue-800);
    }

    .message-content {
      margin-top: 4px;
      word-break: break-word;
    }
  }
}
</style>
```

## Restrições
- **NUNCA** utilize a Options API.
- **NUNCA** escreva estilos com CSS puro (sempre utilize SCSS).
- **NUNCA** quebre os atributos dos elementos dos componentes em várias linhas nos templates; mantenha-os em uma única linha.
- **NUNCA** escreva comentários de código em inglês; eles devem ser sempre em Português do Brasil (pt-BR).
- **NUNCA** acione eventos `emitUpdate` ou `emitResize` no scroller a menos que solicitado explicitamente, pois isso prejudica o desempenho da virtualização.
- **NUNCA** omita a altura/dimensões do elemento container do scroller.
