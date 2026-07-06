---
name: vue-best-practices
description: MUST be used for Vue.js tasks. Strongly recommends Composition API with `<script setup>` and TypeScript as the standard approach. Covers Vue 3, SSR, Volar, vue-tsc. Load for any Vue, .vue files, Vue Router, Pinia, or Vite with Vue work. ALWAYS use Composition API unless the project explicitly requires Options API.
license: MIT
metadata:
  version: "3.x"
---

# Fluxo de Trabalho de Boas Práticas do Vue

Use esta skill como um conjunto de instruções. Siga o fluxo de trabalho na ordem, a menos que o usuário peça explicitamente uma ordem diferente.

## Princípios Fundamentais
- **Mantenha o estado previsível:** uma única fonte de verdade, derive todo o resto.
- **Torne o fluxo de dados explícito:** props para baixo, eventos para cima na maioria dos casos.
- **Prefira componentes pequenos e focados:** mais fáceis de testar, reutilizar e manter.
- **Evite re-renderizações desnecessárias:** use propriedades computadas e watchers com sabedoria.
- **Legibilidade importa:** escreva código claro e autodocumentado.

## 1) Confirme a arquitetura antes de programar (obrigatório)

- Stack padrão: Vue 3 + Composition API + `<script setup lang="ts">`.
- Só use Options API ou JSX se o projeto exigir explicitamente; caso contrário, mantenha `<script setup>` com TypeScript. Estas boas práticas assumem Composition API.

### 1.1 Referências centrais de leitura obrigatória (obrigatório)

- Antes de implementar qualquer tarefa em Vue, certifique-se de ler e aplicar estas referências centrais:
  - `references/reactivity.md`
  - `references/sfc.md`
  - `references/component-data-flow.md`
  - `references/composables.md`
- Mantenha essas referências no contexto de trabalho ativo durante toda a tarefa, não apenas quando um problema específico aparecer.

### 1.2 Planeje os limites dos componentes antes de programar (obrigatório)

Crie um breve mapa de componentes antes da implementação para qualquer funcionalidade não trivial.

- Defina a responsabilidade única de cada componente em uma frase.
- Mantenha os componentes de entrada/raiz e de view de nível de rota como superfícies de composição por padrão.
- Mova a UI de funcionalidade e a lógica de funcionalidade para fora dos componentes de entrada/raiz/view, a menos que a tarefa seja intencionalmente uma pequena demo em arquivo único.
- Defina os contratos de props/emits para cada componente filho no mapa.
- Prefira um layout de pasta por funcionalidade (`components/<feature>/...`, `composables/use<Feature>.ts`) ao adicionar mais de um componente.

## 2) Aplique os fundamentos essenciais do Vue (obrigatório)

Estes são fundamentos essenciais e indispensáveis. Aplique todos eles em toda tarefa em Vue usando as referências centrais já carregadas na seção `1.1`.

### Reatividade

- Referência de leitura obrigatória de `1.1`: [reactivity](references/reactivity.md)
- Mantenha o estado de origem mínimo (`ref`/`reactive`), derive tudo o que for possível com `computed`.
- Use watchers para efeitos colaterais quando necessário.
- Evite recalcular lógica custosa nos templates.

### Estrutura de SFC e segurança de template

- Referência de leitura obrigatória de `1.1`: [sfc](references/sfc.md)
- Mantenha as seções do SFC nesta ordem: `<template>` → `<script>` → `<style>`.
- Mantenha as responsabilidades do SFC focadas; divida componentes grandes.
- Mantenha os templates declarativos; mova ramificações/derivações para o script.
- Aplique as regras de segurança de template do Vue (`v-html`, renderização de listas, escolhas de renderização condicional).

### Mantenha os componentes focados

Divida um componente quando ele tiver **mais de uma responsabilidade clara** (ex: orquestração de dados + UI, ou múltiplas seções de UI independentes).

- Prefira **componentes menores + composables** em vez de um único "megacomponente".
- Mova **seções de UI** para componentes filhos (props para dentro, eventos para fora).
- Mova **estado/efeitos colaterais** para composables (`useXxx()`).

Aplique gatilhos objetivos de divisão. Divida o componente se **qualquer** condição for verdadeira:

- Ele detém tanto orquestração/estado quanto marcação de apresentação substancial para múltiplas seções.
- Ele tem 3+ seções de UI distintas (por exemplo: formulário, filtros, lista, rodapé/status).
- Um bloco de template é repetido ou poderia se tornar reutilizável (linhas de itens, cards, entradas de lista).

Regra de entrada/raiz e view de rota:

- Mantenha os componentes de entrada/raiz e de view de rota enxutos: shell/layout da aplicação, wiring de providers e composição de funcionalidades.
- Não coloque implementações completas de funcionalidades nos componentes de entrada/raiz/view quando essas funcionalidades contêm partes independentes.
- Para funcionalidades de CRUD/lista (todo, tabela, catálogo, inbox), divida ao menos em:
  - componente contêiner da funcionalidade
  - componente de input/formulário
  - componente de lista (e/ou item)
  - componente de rodapé/ações ou filtro/status
- Permita uma implementação em arquivo único apenas para demos descartáveis muito pequenas; se escolhida, justifique explicitamente por que a divisão é desnecessária.

### Fluxo de dados entre componentes

- Referência de leitura obrigatória de `1.1`: [component-data-flow](references/component-data-flow.md)
- Use props para baixo, eventos para cima como modelo principal.
- Use `v-model` apenas para contratos de componente de mão dupla verdadeiros.
- Use provide/inject apenas para dependências de árvore profunda ou contexto compartilhado.
- Mantenha os contratos explícitos e tipados com `defineProps`, `defineEmits` e `InjectionKey` conforme necessário.

### Composables

- Referência de leitura obrigatória de `1.1`: [composables](references/composables.md)
- Extraia lógica para composables quando ela for reutilizada, com estado, ou carregada de efeitos colaterais.
- Mantenha as APIs de composables pequenas, tipadas e previsíveis.
- Separe a lógica de funcionalidade dos componentes de apresentação.

## 3) Considere funcionalidades opcionais apenas quando os requisitos as exigirem

### 3.1 Funcionalidades opcionais padrão

Não adicione estas por padrão. Carregue a referência correspondente apenas quando o requisito existir.

- Slots: o pai precisa controlar o conteúdo/layout do filho -> [component-slots](references/component-slots.md)
- Atributos de fallthrough: componentes wrapper/base devem encaminhar attrs/eventos com segurança -> [component-fallthrough-attrs](references/component-fallthrough-attrs.md)
- Componente nativo `<KeepAlive>` para cache de views com estado -> [component-keep-alive](references/component-keep-alive.md)
- Componente nativo `<Teleport>` para overlays/portais -> [component-teleport](references/component-teleport.md)
- Componente nativo `<Suspense>` para fronteiras de fallback de subárvore assíncrona -> [component-suspense](references/component-suspense.md)
- Funcionalidades relacionadas a animação: escolha a abordagem mais simples que atenda ao comportamento de movimento necessário.
  - Componente nativo `<Transition>` para efeitos de entrada/saída -> [transition](references/component-transition.md)
  - Componente nativo `<TransitionGroup>` para mutações de lista animadas -> [transition-group](references/component-transition-group.md)
  - Animação baseada em classes para efeitos que não sejam de entrada/saída -> [animation-class-based-technique](references/animation-class-based-technique.md)
  - Animação orientada por estado para animação dirigida por input do usuário -> [animation-state-driven-technique](references/animation-state-driven-technique.md)

### 3.2 Funcionalidades opcionais menos comuns

Use estas apenas quando houver necessidade explícita de produto ou técnica.

- Diretivas: o comportamento é específico do DOM e não se encaixa bem em um composable/componente -> [directives](references/directives.md)
- Componentes assíncronos: UI pesada/raramente usada deve ser carregada sob demanda (lazy) -> [component-async](references/component-async.md)
- Render functions apenas quando os templates não conseguirem expressar o requisito -> [render-functions](references/render-functions.md)
- Plugins quando o comportamento deve ser instalado em toda a aplicação -> [plugins](references/plugins.md)
- Padrões de gerenciamento de estado: estado compartilhado por toda a aplicação que cruza fronteiras de funcionalidades -> [state-management](references/state-management.md)

## 4) Execute a otimização de performance depois que o comportamento estiver correto

O trabalho de performance é uma etapa pós-funcionalidade. Não otimize antes que o comportamento central esteja implementado e verificado.

- Gargalos de renderização de listas grandes -> [perf-virtualize-large-lists](references/perf-virtualize-large-lists.md)
- Subárvores estáticas re-renderizando desnecessariamente -> [perf-v-once-v-memo-directives](references/perf-v-once-v-memo-directives.md)
- Sobre-abstração em caminhos quentes de lista -> [perf-avoid-component-abstraction-in-lists](references/perf-avoid-component-abstraction-in-lists.md)
- Atualizações custosas disparadas com frequência demais -> [updated-hook-performance](references/updated-hook-performance.md)

## 5) Autoverificação final antes de concluir

- O comportamento central funciona e corresponde aos requisitos.
- Todas as referências de leitura obrigatória foram lidas e aplicadas.
- O modelo de reatividade é mínimo e previsível.
- A estrutura de SFC e as regras de template são seguidas.
- Os componentes são focados e bem fatorados, dividindo quando necessário.
- Os componentes de entrada/raiz e de view de rota permanecem como superfícies de composição, a menos que haja uma exceção explícita de demo pequena.
- As decisões de divisão de componentes são explícitas e defensáveis (os limites de responsabilidade são claros).
- Os contratos de fluxo de dados são explícitos e tipados.
- Os composables são usados onde a reutilização/complexidade os justifica.
- Estado/efeitos colaterais foram movidos para composables, se aplicável.
- Funcionalidades opcionais são usadas apenas quando os requisitos exigem.
- Mudanças de performance foram aplicadas apenas depois que a funcionalidade estava completa.

## Restrições
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
