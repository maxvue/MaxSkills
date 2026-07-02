---
name: vue-flow-diagram-integration-best-practices
description: Use when creating, configuring, or debugging interactive node-based editors, flowcharts, or diagrams using Vue Flow in Vue 3 (using @vue-flow/core, custom nodes, edges, and connection lines). Triggers on Vue Flow setup, node customization, event binding, reactive graph state updates, and flowchart styling.
---

# Melhores Práticas de Integração de Diagramas com Vue Flow

## Objetivo
Estabelecer diretrizes robustas e padrões de design consistentes para integrar, configurar e gerenciar editores interativos baseados em nós, fluxogramas ou diagramas de forma reativa e eficiente utilizando o Vue Flow no frontend do Engeapp (Vue 3, TypeScript, SCSS/UnoCSS).

## Instruções
1. **Arquitetura do Componente (SFC)**:
   - Sempre siga a ordem de blocos padrão do Single-File Component (SFC): `<template>`, `<script setup lang="ts">`. A estilização deve ser feita via UnoCSS attributify (`presetMaxUno`) com tokens de tema diretamente nos elementos; use um bloco `<style scoped lang="scss">` apenas quando for genuinamente inevitável (ex: seletores do Vue Flow que não podem ser expressos por atributos utilitários).
   - Dentro do bloco `<template>`, formate os componentes e elementos Vue mantendo todos os atributos/parâmetros na mesma linha (estilo inline). Não quebre parâmetros em várias linhas.
   - Use TypeScript (`lang="ts"`) e Composition API com `<script setup>` para toda a lógica.

2. **Inicialização e Configuração**:
   - Utilize o pacote `@vue-flow/core`.
   - Importe `<VueFlow>` e associe `nodes`, `edges` e as opções do grafo de forma reativa.
   - Mapeie tipos de nós customizados através do registro de `node-types` ou fornecendo-os diretamente ao elemento `<VueFlow>`.
   - Exemplo de estrutura para o container principal do diagrama:
     ```vue
     <template>
       <div w-full h-500px border="1 solid gray-300">
         <VueFlow v-model:nodes="nodes" v-model:edges="edges" :node-types="nodeTypes" :fit-view-on-init="true" bg-gray-50 />
       </div>
     </template>

     <script setup lang="ts">
     import { ref, markRaw } from 'vue';
     import { VueFlow } from '@vue-flow/core';
     import CustomProcessNode from './components/CustomProcessNode.vue';

     // Registrar nós customizados utilizando markRaw para evitar proxies profundos e otimizar performance
     const nodeTypes = {
       process: markRaw(CustomProcessNode),
     };

     const nodes = ref([
       { id: '1', type: 'process', position: { x: 250, y: 5 }, data: { label: 'Etapa Inicial' } },
       { id: '2', type: 'process', position: { x: 100, y: 100 }, data: { label: 'Etapa A' } },
     ]);

     const edges = ref([
       { id: 'e1-2', source: '1', target: '2', animated: true },
     ]);
     </script>
     ```

3. **Hooks da Composition API (`useVueFlow`)**:
   - Utilize o composable `useVueFlow()` para obter a instância do grafo, ajustar a visualização (`fitView`), adicionar/remover elementos programaticamente e exportar/importar estados.
   - Extraia lógicas complexas (como adição de nós, validação de conexões e ações de drag-and-drop) para composables Vue dedicados (seguindo os padrões do `vue-code-generators-best-practices`).

4. **Nós Customizados (Custom Nodes e Handles)**:
   - Implemente nós customizados como componentes Vue SFC dedicados.
   - Importe e posicione os elementos `<Handle>` de forma a definir as portas de conexão.
   - Sempre especifique o `type` do handle (`source` ou `target`) e sua `position` (`Position.Top`, `Position.Bottom`, `Position.Left`, `Position.Right`).
   - Use interfaces TypeScript estritas para as propriedades do nó customizado, estendendo ou mapeando a estrutura padrão do payload de dados.
   - Os comentários de código nos componentes devem estar em Português do Brasil (pt-BR).
   - Exemplo de Nó Customizado:
     ```vue
     <template>
       <div p-2.5 rounded-lg bg-white border="2 solid primary" shadow-md>
         <Handle type="target" :position="Position.Top" />
         <div>
           <span text-sm font-bold>{{ data.label }}</span>
         </div>
         <Handle type="source" :position="Position.Bottom" />
       </div>
     </template>

     <script setup lang="ts">
     import { Handle, Position } from '@vue-flow/core';

     // Definição de propriedades tipadas
     defineProps<{
       id: string;
       data: {
         label: string;
       };
     }>();
     </script>
     ```

5. **Otimização de Performance e Memória**:
   - Envolva os componentes de nós customizados em `markRaw` antes de passá-los para o registro `nodeTypes`. Isso impede que o sistema de reatividade do Vue crie proxies desnecessários para objetos complexos contidos nas definições dos nós.
   - A persistência do estado do grafo (nós/arestas/posições) deve passar por uma store `@maxvue/max-pinia`: vincule `nodes`/`edges` ao estado da store e o MaxPinia cuida do salvamento automático no backend (auto-save com debounce). Não faça `axios.post`/requisições manuais a cada movimento do mouse.
   - Para grafos com centenas de nós, atualize a store apenas em eventos significativos (ex: no evento `onNodeDragStop`) em vez de a cada `onNodeDrag`, deixando o debounce do MaxPinia agrupar as gravações para `/api/...`.
   - Limpe ouvintes de eventos e subscrições customizadas de forma adequada no desmonte de componentes ou em composables (`onScopeDispose`).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- Jamais utilize a Options API. Sempre utilize `<script setup lang="ts">` e TypeScript.
- Estilize os elementos via UnoCSS attributify (`presetMaxUno`) com tokens de tema, escritos como atributos utilitários diretamente nos elementos do `<template>`. Não fixe cores hexadecimais cruas nem tamanhos em px; recorra a um bloco `<style scoped lang="scss">` apenas quando genuinamente inevitável (ex: seletores internos do Vue Flow).
- Nunca quebre as propriedades ou parâmetros dos elementos em múltiplas linhas dentro do bloco `<template>`. Escreva-os todos na mesma linha para respeitar as regras SFC do Engeapp.
- Não incorpore lógica de persistência ou requisições de API brutas diretamente dentro dos componentes dos nós; o estado e a persistência devem viver em uma store `@maxvue/max-pinia` (auto-save debounced), consumida pelos containers pais ou composables dedicados. Não use `axios.get`/`axios.post` manuais para carregar ou salvar o grafo.
- Comentários de código no interior dos componentes, exemplos ou blocos de código devem sempre estar no idioma Português do Brasil (pt-BR).
