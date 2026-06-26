---
name: vue-lottie-animations-best-practices
description: Use when implementing, managing, or optimizing Lottie animations in Vue 3 using the @lottiefiles/dotlottie-vue library. Triggers on adding interactive animation files, controlling playback via state, and optimizing performance.
---

## Objetivo
Fornecer instruções claras, boas práticas e padrões de código para integrar, gerenciar e otimizar animações Lottie no Vue 3 utilizando a biblioteca oficial `@lottiefiles/dotlottie-vue` no ecossistema Engeapp.

## Instruções

### 1. Importação da Biblioteca
Sempre importe o `DotLottieVue` da biblioteca oficial:
```typescript
import { DotLottieVue } from '@lottiefiles/dotlottie-vue';
```

### 2. Estrutura de Componente Single File (SFC)
Sempre utilize a Composition API (`<script setup lang="ts">`) e SCSS (`lang="scss"`). Mantenha a ordem dos blocos do SFC como: `<template>`, `<script>` e `<style>`.

### 3. Restrição de Atributos Inline
Dentro do bloco `<template>`, formate o componente `<DotLottieVue>` mantendo todos os seus atributos/propriedades em uma única linha (sem quebras de linha nos atributos).
```vue
<template>
  <div class="lottie-wrapper">
    <DotLottieVue style="height: 250px; width: 250px;" autoplay loop src="https://lottie.host/example.lottie" />
  </div>
</template>
```

### 4. Otimização de Formato
- Prefira arquivos no formato `.lottie` em vez dos arquivos Lottie tradicionais em `.json`.
- Arquivos `.lottie` são arquivos compactados (zip) que compilam todos os recursos (incluindo imagens rasterizadas e fontes) dentro de um único arquivo leve, reduzindo drasticamente os tempos de carregamento e o processamento de CPU.

### 5. Controle Programático (Gerenciamento de Instância)
Para controlar a reprodução programaticamente (ex: play, pause, stop, definir velocidade), vincule um `ref` ao componente e extraia a instância usando `getDotLottieInstance()` dentro de `onMounted` ou em gatilhos de ação:
```vue
<template>
  <div class="animation-control-container">
    <DotLottieVue ref="playerRef" style="height: 300px; width: 300px;" src="/animations/loading.lottie" />
    <button @click="togglePlayback">Alternar Play/Pause</button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { DotLottieVue } from '@lottiefiles/dotlottie-vue';

// Referência ao elemento do player
const playerRef = ref<any>(null);
const dotLottie = ref<any>(null);
const isPlaying = ref<boolean>(false);

onMounted(() => {
  if (playerRef.value) {
    // Acessa a instância interna da biblioteca dotlottie-web
    dotLottie.value = playerRef.value.getDotLottieInstance();
    
    // Registra listeners de eventos da biblioteca
    dotLottie.value.addEventListener('play', () => {
      isPlaying.value = true;
    });
    dotLottie.value.addEventListener('pause', () => {
      isPlaying.value = false;
    });
  }
});

// Controle programático de execução
const togglePlayback = () => {
  if (!dotLottie.value) {
    return;
  }
  
  if (dotLottie.value.is_playing()) {
    dotLottie.value.pause();
  } else {
    dotLottie.value.play();
  }
};
</script>
```

### 6. Interação Nativa com Hover
Para interações simples de reprodução ao passar o mouse, utilize a propriedade nativa `playOnHover`:
```vue
<template>
  <DotLottieVue playOnHover style="height: 100px; width: 100px;" src="/animations/button-feedback.lottie" />
</template>
```

### 7. Performance e Carregamento Lento (Lazy Loading)
Evite renderizar e executar animações que estão fora da tela. Envolva o player em um container de carregamento lento ou renderize condicionalmente usando `v-if` com uma verificação de interseção:
```vue
<template>
  <div ref="targetContainer" class="lazy-animation-container">
    <DotLottieVue v-if="isVisible" style="height: 400px; width: 400px;" autoplay loop src="/animations/banner.lottie" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { DotLottieVue } from '@lottiefiles/dotlottie-vue';

const targetContainer = ref<HTMLElement | null>(null);
const isVisible = ref<boolean>(false);
let observer: IntersectionObserver | null = null;

onMounted(() => {
  observer = new IntersectionObserver(([entry]) => {
    // Define a visibilidade com base na interseção na tela
    isVisible.value = entry.isIntersecting;
  }, { threshold: 0.1 });

  if (targetContainer.value) {
    observer.observe(targetContainer.value);
  }
});

onUnmounted(() => {
  if (observer) {
    observer.disconnect();
  }
});
</script>
```

## Restrições
- **NUNCA** utilize a Options API. Sempre utilize `<script setup lang="ts">` com a Composition API.
- **NUNCA** quebre os atributos de `<DotLottieVue>` em várias linhas dentro do `<template>`. Mantenha-os todos na mesma linha.
- **NUNCA** carregue recursos pesados de animação na inicialização sem lazy loading.
- Todos os comentários adicionados no código gerado pelo agente **DEVEM** ser escritos em Português do Brasil (pt-BR).
