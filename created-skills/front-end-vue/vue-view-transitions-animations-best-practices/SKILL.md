---
name: vue-view-transitions-animations-best-practices
description: Use when implementing, refactoring, or optimizing page transitions, element animations, or reactive UI transitions in the Vue 3 frontend. Triggers on configuring Vue <Transition> or <TransitionGroup>, integrating UnoCSS animation utilities, implementing route-based animations with Vue Router, using @vueuse/motion, or optimizing animation rendering performance.
---

# Boas Práticas para Transições e Animações no Vue 3

## Objetivo
Estabelecer padrões rigorosos de design, desempenho e implementação para transições de rotas, animações de componentes e transições reativas de interface de usuário (UI) no frontend Vue 3, utilizando Composition API, SCSS e UnoCSS. Isso garante uma experiência visual fluida e premium, livre de deslocamentos de layout ou gargalos de renderização.

## Instruções

### 1. Ordem dos Blocos no Componente Single-File (SFC)
Todos os arquivos SFC do Vue devem seguir rigorosamente esta ordem de blocos:
1. `<template>` - Mantenha os atributos na mesma linha (estilo inline) sempre que possível.
2. `<script setup lang="ts">` - Uso obrigatório da Composition API com TypeScript.
3. `<style scoped lang="scss">` - Uso obrigatório de SCSS Escopo (scoped) para isolamento de estilos do componente.

### 2. Componentes `<Transition>` e `<TransitionGroup>` do Vue
- **Modo de Transição:** Sempre utilize `mode="out-in"` ao fazer transições entre dois elementos ou componentes usando `v-if`/`v-else` ou o componente dinâmico `<component :is="...">`. Isso evita que ambos os elementos coexistam no DOM ao mesmo tempo, quebrando a grade do layout.
- **Chaves (Keys):** Sempre forneça um atributo `:key` único e estável para os itens dentro do `<TransitionGroup>` (evite utilizar índices de arrays como chaves).
- **Animações de Lista FLIP:** Utilize a classe `v-move` fornecida automaticamente pelo `<TransitionGroup>` para animar o rearranjo de itens da lista de forma suave. Adicione `transition: transform 0.4s ease;` na classe `.list-move`.

### 3. Animações de Rota (Vue Router)
Configure transições de rota no nível de layout ou no arquivo raiz (`App.vue`) aninhando `<router-view>` e `<transition>` corretamente:
```vue
<template>
  <router-view v-slot="{ Component, route }">
    <transition name="fade-slide" mode="out-in">
      <component :is="Component" :key="route.path" />
    </transition>
  </router-view>
</template>
```

### 4. Animações Aceleradas por GPU
- **Propriedades CSS:** Anime apenas propriedades que não causam re-layout (reflow) ou redesenho (paint) no navegador. Limite as transições para:
  - `opacity`
  - `transform` (ex: `translate`, `scale`, `rotate`)
- **Evite animar:** `width`, `height`, `top`, `left`, `margin`, `padding`. Utilize translações (`translate`) ou escalas (`scale`) como alternativas.
- **Aceleração por Hardware:** Aplique `backface-visibility: hidden;` e `transform: translate3d(0, 0, 0);` nas classes de animação ativas para forçar a criação de uma camada de composição na GPU.
- **Will-Change:** Use a propriedade CSS `will-change` de forma dinâmica e moderada. Aplique-a apenas a elementos sob animações complexas ou contínuas.

### 5. Classes de Estilização e Nomenclatura de Transições em SCSS
Mapeie claramente as classes de ciclo de vida da transição dentro do `<style scoped lang="scss">`:
- `.fade-enter-active, .fade-leave-active` - Defina a duração da transição e a curva de aceleração (ex: `transition: opacity 0.25s cubic-bezier(0.4, 0, 0.2, 1);`).
- `.fade-enter-from, .fade-leave-to` - Defina os estados inicial e final (ex: `opacity: 0;`).

### 6. Integração com UnoCSS e Utilitários de Animação
Use classes utilitárias do UnoCSS para interações simples (como hovers e redimensionamentos) onde a sobrecarga de uma transição SCSS completa é desnecessária:
- Use `transition-all duration-200 ease-in-out` para transições de hover padrão.
- Combine gatilhos de hover como `hover:scale-105 active:scale-95` para adicionar feedback tátil.

### 7. Desempenho e Limpeza de Recursos
- **Concorrência e Deslocamento de Layout:** Certifique-se de que os componentes sob transição possuam posicionamento absoluto ou isolado caso o `mode="out-in"` não possa ser utilizado, impedindo que elementos empurrem outros componentes da tela durante os ciclos de entrada/saída.
- **Limpeza de Listeners:** Se estiver utilizando ganchos JavaScript (`@before-enter`, `@enter`, etc.) integrados a bibliotecas de animação como `@vueuse/motion` ou GreenSock (GSAP), sempre limpe e destrua as instâncias de animação no gancho `onUnmounted`.

## Exemplos

### Exemplo 1: Transição de Modal Premium Padrão (SFC)
```vue
<template>
  <div class="modal-overlay" v-if="isOpen" @click="close">
    <transition name="modal-scale" appear>
      <div class="modal-content" @click.stop v-if="isOpen">
        <slot />
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';

defineProps<{
  isOpen: boolean;
}>();

const emit = defineEmits<{
  (e: 'close'): void;
}>();

const close = () => {
  emit('close');
};
</script>

<style scoped lang="scss">
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-primary, #ffffff);
  border-radius: 12px;
  padding: 24px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}

/* Animação de Escala e Esmaecimento */
.modal-scale-enter-active,
.modal-scale-leave-active {
  transition: opacity 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.modal-scale-enter-from,
.modal-scale-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(8px);
}
</style>
```

### Exemplo 2: Reordenação de Lista (Layout FLIP) com `<TransitionGroup>`
```vue
<template>
  <div class="list-wrapper">
    <transition-group name="list-flip" tag="ul" class="item-list">
      <li class="list-item" v-for="item in items" :key="item.id">
        <span>{{ item.name }}</span>
      </li>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { defineProps } from 'vue';

interface Item {
  id: number | string;
  name: string;
}

defineProps<{
  items: Item[];
}>();
</script>

<style scoped lang="scss">
.item-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.list-item {
  padding: 16px;
  background: var(--bg-card, #f8f9fa);
  border-radius: 8px;
  border: 1px solid var(--border-color, #e9ecef);
}

/* Estilos da Transição FLIP */
.list-flip-move {
  transition: transform 0.4s cubic-bezier(0.25, 1, 0.5, 1);
}

.list-flip-enter-active,
.list-flip-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.list-flip-enter-from,
.list-flip-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

/* Posicionamento absoluto na saída para garantir que o FLIP atue corretamente */
.list-flip-leave-active {
  position: absolute;
  width: 100%;
}
</style>
```

## Restrições
- **Não usar Options API:** Jamais declare `data()`, `methods` ou ganchos utilizando a estrutura de objeto da Options API.
- **Evitar Deslocamentos Visuais (Layout Shifts):** Nunca execute transições de substituição sem definir `mode="out-in"`.
- **Animações de Pintura Pesada Banidas:** Nunca anime propriedades que afetem as dimensões de bloco (como `width`, `height`, `top`, `left`, `margin`, `padding`, `border-width`) dentro de transições CSS. Prefira translações e escalas por `transform`.
- **Estilos Inline Proibidos:** Não configure tempos de duração ou dinâmicas de transição em atributos `:style` dinâmicos inline, a menos que sejam controlados via variáveis CSS.
- **Vazamento de Memória:** Certifique-se de limpar animações GSAP ou hooks JS nos componentes quando estes forem destruídos do DOM (gancho `onUnmounted`).
