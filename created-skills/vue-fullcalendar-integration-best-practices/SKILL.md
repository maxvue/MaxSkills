---
name: vue-fullcalendar-integration-best-practices
description: Use when creating, modifying, or debugging interactive calendars using FullCalendar in Vue 3 (using @fullcalendar/vue3, @fullcalendar/core, daygrid, and interaction plugins). Triggers on calendar view setup, event binding, reactive event updates, and customization of FullCalendar headers and themes.
---

# Melhores Práticas de Integração do FullCalendar no Vue 3

## Objetivo
Fornecer um guia robusto e padronizado para integrar, configurar e gerenciar eventos de forma reativa no FullCalendar usando Vue 3 (Composition API), TypeScript e SCSS, evitando a interferência de proxies de reatividade do Vue (como os erros de tipo `pauseRendering` ou `__vnode`) e garantindo suporte adequado de idioma para pt-BR.

## Instruções

### 1. Referência de Instância com `shallowRef`
Para obter a referência do componente ou a API do FullCalendar, sempre utilize `shallowRef` em vez de `ref`.
O uso de `ref` comum envelopa a instância interna complexa do FullCalendar em um proxy reativo do Vue, o que gera erros fatais de renderização (ex: `TypeError: Cannot read properties of undefined (reading 'pauseRendering')` ou `TypeError: Cannot set properties of null (setting '__vnode')`).

```typescript
import { shallowRef } from 'vue';
import FullCalendar from '@fullcalendar/vue3';

// Use shallowRef em vez de ref para a referência da API/Componente
const calendarRef = shallowRef<InstanceType<typeof FullCalendar> | null>(null);

// Para acessar a API do FullCalendar com segurança:
const getCalendarApi = () => {
    return calendarRef.value?.getApi();
};
```

### 2. Ordenação SFC e Composition API
Siga as diretrizes de desenvolvimento Vue do Engeapp:
1. Ordem dos blocos: `<template>` -> `<script setup lang="ts">` -> `<style scoped lang="scss">`.
2. Atributos dentro de templates devem ser escritos inline em uma única linha (sem quebra de atributos em múltiplas linhas).

```vue
<template>
  <div class="calendar-container">
    <FullCalendar ref="calendarRef" :options="calendarOptions" />
  </div>
</template>

<script setup lang="ts">
import { computed, shallowRef } from 'vue';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import interactionPlugin from '@fullcalendar/interaction';
import { CalendarOptions } from '@fullcalendar/core';

const calendarRef = shallowRef<InstanceType<typeof FullCalendar> | null>(null);

// Configuração das opções usando computed para rastreamento estável de dependências reativas
const calendarOptions = computed<CalendarOptions>(() => ({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: 'pt-br',
  editable: false,
  selectable: true,
  // ...outras opções
}));
</script>

<style scoped lang="scss">
.calendar-container {
  // Estilização aqui
}
</style>
```

### 3. Atualizações de Eventos Reativos
Ao vincular eventos, evite reinstanciar o array de origem `events` inteiro se isso fizer o FullCalendar redesenhar desnecessariamente.
* O GET dos eventos deve passar por uma store `@maxvue/max-pinia` (com cache + auto-save), não por `axios.get` manual. Forneça o array reativo dessa store (ex.: `store.events`) diretamente nas opções computadas ou como uma prop separada. Você também pode definir `events` como uma função callback que lê da store.
* Se estiver usando a propriedade `events` dentro de `calendarOptions`, certifique-se de que o array reativo mapeado para ela seja atualizado de forma rasa ou utilize uma referência estável.

```typescript
const calendarOptions = computed<CalendarOptions>(() => ({
  plugins: [dayGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: 'pt-br',
  // store é uma store @maxvue/max-pinia que faz o GET dos eventos (cache + auto-save)
  events: store.events.map(event => ({
    id: event.id,
    title: event.title,
    start: event.start_at,
    end: event.end_at,
    extendedProps: { ...event }
  })),
  // ...
}));
```

### 4. Internacionalização (pt-BR)
Sempre configure a opção `locale: 'pt-br'` e defina os textos de botões apropriados:

```typescript
buttonText: {
  today: 'Hoje',
  month: 'Mês',
  week: 'Semana',
  day: 'Dia',
  list: 'Agenda'
}
```

### 5. Customização de Estilos DOM (Deep Selectors)
Como os elementos HTML do FullCalendar são criados dinamicamente fora do escopo de estilo scoped do Vue, use o seletor `:deep()` no SCSS ou envolva o calendário em uma classe contêiner para personalizar o cabeçalho, botões e células de grade.

```scss
<style scoped lang="scss">
.calendar-container {
  :deep(.fc) {
    .fc-toolbar-title {
      font-size: 1.25rem;
      font-weight: 600;
    }
    .fc-button-primary {
      background-color: var(--primary-color);
      border-color: var(--primary-color);
      &:hover {
        background-color: var(--primary-color-dark);
      }
    }
  }
}
</style>
```

## Restrições
* **NÃO** utilize `ref` ou `reactive` comuns para armazenar instâncias de API ou componentes do FullCalendar. Você deve usar `shallowRef`.
* **NÃO** quebre atributos em múltiplas linhas no bloco `<template>`.
* **NÃO** utilize a Options API. Sempre utilize a Composition API (`<script setup lang="ts">`).
* **NÃO** escreva comentários em outro idioma que não seja o Português do Brasil (pt-BR) no código do projeto.
