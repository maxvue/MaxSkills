---
name: vue-splitpanes-layouts-best-practices
description: Use when designing, implementing, or debugging resizable panel layouts, split view containers, or multi-pane sidebars using the splitpanes library in Vue 3 frontend components.
---

# Diretrizes e Boas Práticas de Layouts com Splitpanes no Vue

## Objetivo
Fornecer diretrizes sólidas e padrões consistentes para o uso da biblioteca `splitpanes` no desenvolvimento de layouts redimensionáveis no frontend Vue 3 do Engeapp, garantindo responsividade, alta performance, consistência visual e persistência de estado.

## Instruções

### 1. Estrutura SFC e Configuração
- Sempre use a Composition API com `<script setup lang="ts">`.
- Use `lang="scss"` para estilos.
- Siga estritamente a ordem dos blocos SFC: `<template>`, `<script setup>`, e então `<style scoped lang="scss">`.
- Mantenha os atributos dos componentes Vue na mesma linha no bloco `<template>` (estilo inline, sem quebra de linhas para atributos).

### 2. Inicialização dos Componentes
- Importe `Splitpanes` e `Pane` do pacote `splitpanes`.
- Certifique-se de que o container pai do `<splitpanes>` tenha uma altura definida (ex: `height: 100%` ou `height: 100vh`) e `overflow: hidden`, pois o splitpanes calcula o tamanho relativo ao pai.
- Defina explicitamente os tamanhos (em porcentagem) para cada elemento `<pane>`.

### 3. Persistência de Estado
- Utilize o `useLocalStorage` do `@vueuse/core` ou um utilitário de storage próprio do projeto para persistir o tamanho dos painéis.
- Vincule os tamanhos persistidos à propriedade `:size` de cada `<pane>`.
- Escute o evento `@resized` no componente `<splitpanes>` para atualizar os tamanhos no storage após a interação do usuário.

### 4. Estilização Personalizada (SCSS)
- Sobrescreva os estilos padrão das divisórias (splitters) para alinhar ao design premium e moderno do Engeapp (suporte a Dark Mode, transições suaves, cores harmoniosas).
- Adicione micro-animações nas divisórias durante o hover/arraste para uma experiência premium.

## Examples

### Layout com Painel Lateral Persistido e Área Principal
```vue
<template>
  <div class="layout-container">
    <splitpanes class="default-theme" @resized="handleResized">
      <pane :size="paneSizes[0]" min-size="15" max-size="40">
        <aside class="sidebar-content">
          <!-- Conteúdo da barra lateral -->
          <h3>Painel Lateral</h3>
        </aside>
      </pane>
      <pane :size="paneSizes[1]">
        <main class="main-content">
          <!-- Conteúdo principal -->
          <h1>Área Principal</h1>
        </main>
      </pane>
    </splitpanes>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Splitpanes, Pane } from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';

// Interface para definir tamanhos dos painéis
interface PaneState {
  size: number;
}

// Persistência reativa usando LocalStorage
const STORAGE_KEY = 'engeapp-pane-sizes';
const defaultSizes = [25, 75];

const getStoredSizes = (): number[] => {
  const stored = localStorage.getItem(STORAGE_KEY);
  return stored ? JSON.parse(stored) : defaultSizes;
};

const paneSizes = ref<number[]>(getStoredSizes());

// Atualiza o estado persistido após o usuário terminar o redimensionamento
const handleResized = (panes: PaneState[]) => {
  paneSizes.value = panes.map((p) => p.size);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(paneSizes.value));
};
</script>

<style scoped lang="scss">
.layout-container {
  width: 100%;
  height: 100%;
  overflow: hidden;
  display: flex;
  background-color: var(--bg-primary);

  .sidebar-content,
  .main-content {
    width: 100%;
    height: 100%;
    padding: 1.5rem;
    overflow-y: auto;
  }
}

// Estilização personalizada das divisórias (Gutters)
:deep(.splitpanes__splitter) {
  background-color: var(--border-color, #e2e8f0);
  position: relative;
  transition: background-color 0.2s ease;
  width: 6px !important;

  &:hover {
    background-color: var(--color-primary, #3b82f6);
  }

  &::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 2px;
    height: 20px;
    background-color: var(--text-muted, #94a3b8);
    border-radius: 1px;
    transition: background-color 0.2s;
  }

  &:hover::before {
    background-color: #ffffff;
  }
}
</style>
```

## Restrições
- Sob nenhuma circunstância utilize a Options API.
- Não quebre atributos/parâmetros de componentes Vue em múltiplas linhas dentro do `<template>`.
- Não estilize o componente splitpanes usando estilos inline; sempre utilize SCSS no bloco `<style scoped lang="scss">`.
- Nunca deixe de importar o arquivo de estilo padrão (`splitpanes.css` ou equivalente).
- Os comentários do código dos componentes devem sempre ser escritos no idioma Português do Brasil (pt-BR).
