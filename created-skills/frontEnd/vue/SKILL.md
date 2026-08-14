---
name: vue
description: "Use for core Vue 3 Composition API fundamentals in Engeapp. Covers script setup, defineProps, defineEmits, defineModel, reactivity, built-in components, composables, component splitting, and list performance."
metadata: {'author': 'Anthony Fu', 'version': '2026.1.31', 'source': 'Generated from https://github.com/vuejs/docs, scripts at https://github.com/antfu/skills'}
---
# Vue

## Objetivo
Use for core Vue 3 Composition API fundamentals in Engeapp. Covers script setup, defineProps, defineEmits, defineModel, reactivity, built-in components, composables, component splitting, and list performance.

> Fundamentos puros de Vue 3. O engeapp usa Vue `^3.6.0-rc.2` (recursos 3.4/3.5 abaixo continuam válidos). Sempre use a Composition API com `<script setup lang="ts">`.

## Instruções

### Preferências

- Prefira TypeScript em vez de JavaScript
- Prefira `<script setup lang="ts">` em vez de `<script>`
- Por desempenho, prefira `shallowRef` em vez de `ref` quando a reatividade profunda não for necessária
- Sempre use a Composition API em vez da Options API
- Desencoraje o Reactive Props Destructure. O código real do engeapp usa `const props = defineProps<{...}>()` e acessa `props.x`; mantenha esse padrão para não quebrar a consistência do projeto.

### Convenções obrigatórias do engeapp (não copie os padrões crus dos exemplos)

Os exemplos das referências abaixo são fundamentos genéricos de Vue. No engeapp, NÃO os use crus:

- **Fetch / estado / rotas:** todo GET passa por uma store MaxPinia (`@maxvue/max-pinia`); nunca faça `fetch()` direto em componente. Chamadas imperativas usam `apiGetRoute`/`apiPostRoute` de `@maxvue/max-use` com **nome de rota Ziggy pontilhado** (ex.: `apiGetRoute('project.station.elements', { station_id })`), nunca strings `'/api/...'`. Ziggy está configurado; o resolvedor é registrado em `resources/app.ts`.
- **Composables utilitários:** não escreva `useMouse`/`useFetch` caseiros nem use `vueuse` cru. Consuma helpers de `@maxvue/max-use` (ex.: `useMouseInElement`, `formatDate`, `hasContent`).
- **Componentes:** não use inputs/botões nativos nem PrimeVue cru; use os `Max*` de `@maxvue/max-components-ui`.
- Comentários de código em pt-BR.

Detalhes do ecossistema Max ficam nas skills dedicadas (`vue-max-stack-frontend-best-practices`, `vue-pinia-state-management-best-practices`, `vue-max-ecosystem-api-reference`). Esta skill cobre só o Vue de base.

### Núcleo

| Tópico | Descrição | Referência |
|-------|-------------|-----------|
| Script Setup & Macros | `<script setup>`, defineProps, defineEmits, defineModel, defineExpose, defineOptions, defineSlots, generics | [script-setup-macros](references/script-setup-macros.md) |
| Reatividade & Ciclo de Vida | ref, shallowRef, computed, watch, watchEffect, effectScope, hooks de ciclo de vida, composables | [core-new-apis](references/core-new-apis.md) |

### Recursos

| Tópico | Descrição | Referência |
|-------|-------------|-----------|
| Fluxo de dados entre componentes | props↓/eventos↑, v-model, provide/inject com `InjectionKey` tipado | [component-data-flow](references/component-data-flow.md) |
| Composables | extrair lógica reutilizável/com estado; APIs pequenas e tipadas | [composables](references/composables.md) |
| Slots & fallthrough attrs | pai controla conteúdo do filho; wrappers encaminham attrs/eventos | [component-slots](references/component-slots.md), [component-fallthrough-attrs](references/component-fallthrough-attrs.md) |
| KeepAlive / Teleport / Suspense | cache de views, overlays/portais, fronteiras assíncronas | [component-keep-alive](references/component-keep-alive.md), [component-teleport](references/component-teleport.md), [component-suspense](references/component-suspense.md) |
| Transições & animação | entrada/saída, mutações de lista, baseada em classe/estado | [component-transition](references/component-transition.md), [component-transition-group](references/component-transition-group.md), [animation-class-based-technique](references/animation-class-based-technique.md), [animation-state-driven-technique](references/animation-state-driven-technique.md) |
| Diretivas / async / render fn / plugins / estado | recursos menos comuns, só quando o requisito existir | [directives](references/directives.md), [component-async](references/component-async.md), [render-functions](references/render-functions.md), [plugins](references/plugins.md), [state-management](references/state-management.md) |

### Divisão de componentes (gatilhos objetivos)

Mantenha componentes focados: uma responsabilidade clara por componente. **Divida** o componente se **qualquer** condição for verdadeira:

- Detém tanto orquestração/estado quanto marcação de apresentação substancial para múltiplas seções.
- Tem 3+ seções de UI distintas (ex.: formulário, filtros, lista, rodapé/status).
- Um bloco de template se repete ou poderia virar reutilizável (linhas, cards, itens de lista).

Regras de fatiamento:

- Mova **seções de UI** para filhos (props↓/eventos↑) e **estado/efeitos colaterais** para composables (`useXxx()`).
- Mantenha componentes de entrada/raiz e views de rota enxutos: shell/layout, wiring de providers e composição de funcionalidades — não implementações completas de features com partes independentes.
- Para CRUD/lista (todo, tabela, catálogo, inbox), divida ao menos em: contêiner da feature + input/formulário + lista (e/ou item) + rodapé/ações ou filtro/status.
- Arquivo único só para demos descartáveis muito pequenas, com justificativa explícita.

### Performance (etapa pós-funcionalidade)

Otimize só depois que o comportamento central estiver correto e verificado.

| Sintoma | Referência |
|---------|-----------|
| Renderização de listas grandes lenta | [perf-virtualize-large-lists](references/perf-virtualize-large-lists.md) |
| Subárvores estáticas re-renderizando à toa | [perf-v-once-v-memo-directives](references/perf-v-once-v-memo-directives.md) |
| Sobre-abstração em caminhos quentes de lista | [perf-avoid-component-abstraction-in-lists](references/perf-avoid-component-abstraction-in-lists.md) |
| Atualizações custosas disparadas com frequência | [updated-hook-performance](references/updated-hook-performance.md) |

### Autoverificação final

- Comportamento central funciona e corresponde aos requisitos.
- Modelo de reatividade mínimo e previsível (estado de origem mínimo, derive com `computed`).
- Estrutura de SFC (`<template>` → `<script>` → `<style>`) e regras de segurança de template (`v-html`, listas, condicionais) seguidas.
- Componentes focados e bem fatorados; decisões de divisão explícitas e defensáveis.
- Entrada/raiz e views de rota permanecem como superfícies de composição (salvo exceção de demo pequena).
- Contratos de fluxo de dados explícitos e tipados (`defineProps`/`defineEmits`/`InjectionKey`).
- Composables usados onde reutilização/complexidade os justifica; estado/efeitos movidos para eles.
- Recursos opcionais usados só quando os requisitos exigem.
- Otimizações de performance aplicadas só após a funcionalidade completa.
- Convenções do engeapp respeitadas: GET via store MaxPinia, `apiGetRoute`/`apiPostRoute` com nome Ziggy, helpers `@maxvue/max-use`, componentes `Max*`, comentários em pt-BR.

### Referência Rápida

### Template de Componente

```vue
<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps<{
  title: string
  count?: number
}>()

const emit = defineEmits<{
  update: [value: string]
}>()

const model = defineModel<string>()

const doubled = computed(() => (props.count ?? 0) * 2)

watch(() => props.title, (newVal) => {
  console.log('Title changed:', newVal)
})

onMounted(() => {
  console.log('Component mounted')
})
</script>

<template>
  <div>{{ title }} - {{ doubled }}</div>
</template>
```

### Principais Imports

```ts
// Reactivity
import { ref, shallowRef, computed, reactive, readonly, toRef, toRefs, toValue } from 'vue'

// Watchers
import { watch, watchEffect, watchPostEffect, onWatcherCleanup } from 'vue'

// Lifecycle
import { onMounted, onUpdated, onUnmounted, onBeforeMount, onBeforeUpdate, onBeforeUnmount } from 'vue'

// Utilities
import { nextTick, defineComponent, defineAsyncComponent } from 'vue'
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
