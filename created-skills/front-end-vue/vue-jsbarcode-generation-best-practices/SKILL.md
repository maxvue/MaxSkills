---
name: vue-jsbarcode-generation-best-practices
description: Use when creating, rendering, or debugging barcode generation in frontend Vue 3 components using the jsbarcode library. Triggers on rendering SVG/Canvas barcodes, barcode value reactive updates, ITF or CODE128 format configurations, and dynamic scaling/zooming of barcode elements.
---

## Objetivo
Padronizar a renderização, manipulação reativa e prevenção de erros na geração de códigos de barras em componentes Vue 3 utilizando a biblioteca `jsbarcode` dentro do ecossistema Engeapp.

## Instruções

## 1. Declaração do Template
* Prefira elementos `<svg>` a `<canvas>` para garantir que as linhas do código de barras sejam vetoriais, nítidas em telas de alta densidade (Retina/DPI) e escalem perfeitamente.
* Mantenha os atributos inline e em uma única linha dentro do bloco de template:
  ```html
  <svg ref="barcodeElement" class="barcode-svg" />
  ```

## 2. Lógica e Estrutura do Componente
* Sempre utilize a Composition API do Vue 3 com `<script setup lang="ts">`.
* Referencie os elementos do DOM usando `useTemplateRef` (Vue 3.5+) ou a tipagem padrão de `ref`:
  ```typescript
  const barcodeElement = ref<SVGElement | null>(null);
  ```
* Todos os comentários do código dentro dos templates ou scripts devem estar no idioma Português do Brasil (`pt-BR`) para manter a consistência do repositório.

## 3. Renderização Reativa com Watchers
* Os valores de códigos de barras costumam ser carregados de forma assíncrona. Não dependa unicamente do ciclo de vida `onMounted` para renderização.
* Configure um bloco de `watch` para monitorar tanto o valor do código de barras quanto a referência do elemento do DOM. Use o `nextTick` para garantir que o DOM esteja completamente montado e pronto antes de chamar o renderizador.
  ```typescript
  watch([() => props.value, barcodeElement], async ([newValue, newEl]) => {
      if (newValue && newEl) {
          await nextTick();
          generateBarcode();
      }
  }, { immediate: true });
  ```

## 4. Prevenção de Erros e Validação
* A biblioteca `jsbarcode` lança exceções graves quando recebe valores inválidos (por exemplo, tamanho ímpar de caracteres para o formato ITF/Interleaved 2 of 5, ou caracteres não suportados).
* Sempre envolva a chamada do `JsBarcode()` em um bloco `try/catch` para evitar a quebra da execução de scripts e falhas na aplicação.
* Gerencie estados de erro e emita eventos (`success`, `error`) para notificar o componente pai sobre o resultado do processo, permitindo que a aplicação exiba elementos alternativos (fallbacks) como o valor bruto legível caso a renderização falhe.

## 5. Escalonamento e Responsividade (Zoom Mobile)
* Leitores físicos de código de barras exigem espaçamentos precisos entre as barras para realizar a leitura de forma correta.
* Para escalar o código de barras em telas pequenas de smartphones sem prejudicar a leitura:
  - Envolva o SVG do código de barras em um contêiner adequado.
  - Implemente um comportamento de zoom que amplie o elemento aplicando a transformação CSS `transform: scale(scaleFactor)` combinada com `transform-origin: center` ou `top left`.
  - Calcule o fator de escala dinamicamente: `(larguraDaJanela - margem) / larguraDoCodigo`. Utilize funções auxiliares da biblioteca `@vueuse/core`, como `useWindowSize` e `useElementSize`.

## Restrições
* Nunca execute a função `JsBarcode()` sem envolvê-la em uma estrutura de tratamento de erros `try/catch`.
* Não utilize valores estáticos ou formatos fixados diretamente no código. Garanta que sejam dinâmicos através de Props do Vue ou variáveis reativas.
* Jamais utilize a Options API ou JavaScript comum sem tipagem TypeScript (`lang="ts"`).
* Evite o uso de estilos em linha para dimensionamento personalizado; utilize blocos SCSS escopados (`scoped`).

# Exemplos

Abaixo encontra-se a estrutura padrão de um componente Vue 3 SFC pronto para produção, utilizando Composition API, TypeScript e SCSS escopado.

```vue
<template>
  <div class="barcode-container">
    <div :class="['barcode-wrapper', { 'is-zoomed': isZoomed }]" :style="wrapperStyle" @click="toggleZoom">
      <!-- Tag inline mantendo os atributos em uma única linha conforme os padrões -->
      <svg ref="barcodeElement" class="barcode-svg" />
    </div>
    
    <div v-if="hasError" class="barcode-error-fallback">
      <span class="error-text">Não foi possível gerar o código de barras.</span>
      <span class="raw-value">{{ value }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue';
import JsBarcode from 'jsbarcode';
import { useElementSize, useWindowSize } from '@vueuse/core';

// Definição das propriedades do componente com TypeScript
interface Props {
  value: string;
  format?: 'ITF' | 'CODE128' | 'CODE39' | 'EAN13';
  lineColor?: string;
  width?: number;
  height?: number;
  displayValue?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  format: 'ITF',
  lineColor: '#2f4155',
  width: 1.65,
  height: 60,
  displayValue: false
});

// Emissão de eventos para controle do componente pai
const emit = defineEmits<{
  (e: 'success'): void;
  (e: 'error', error: any): void;
}>();

// Referência reativa para o elemento SVG do código de barras
const barcodeElement = ref<SVGElement | null>(null);
const hasError = ref<boolean>(false);

// Zoom e controle responsivo
const isZoomed = ref<boolean>(false);
const scale = ref<number>(1);

const { width: windowWidth } = useWindowSize();
const { width: barcodeWidth } = useElementSize(barcodeElement);

// Estilo dinâmico para aplicar escala CSS baseada no zoom
const wrapperStyle = computed(() => {
  return {
    transform: `scale(${scale.value})`,
    transformOrigin: 'center center'
  };
});

// Alterna o zoom ajustando a escala dinamicamente para ocupar a largura da tela
const toggleZoom = (): void => {
  isZoomed.value = !isZoomed.value;
  if (isZoomed.value && barcodeWidth.value > 0) {
    // Deduz 40px para margens de segurança nas laterais da tela do celular
    scale.value = (windowWidth.value - 40) / barcodeWidth.value;
  } else {
    scale.value = 1;
  }
};

// Gera o código de barras de forma segura
const generateBarcode = (): void => {
  if (!barcodeElement.value || !props.value) {
    return;
  }

  try {
    hasError.value = false;
    JsBarcode(barcodeElement.value, props.value, {
      format: props.format,
      lineColor: props.lineColor,
      width: props.width,
      height: props.height,
      displayValue: props.displayValue
    });
    emit('success');
  } catch (error) {
    hasError.value = true;
    console.error('[JsBarcode] Erro ao renderizar o código de barras:', error);
    emit('error', error);
  }
};

// Monitora alterações no valor do código de barras ou no elemento DOM
watch(
  [() => props.value, () => props.format, barcodeElement],
  async ([newValue, newFormat, newEl]) => {
    if (newValue && newEl) {
      await nextTick();
      generateBarcode();
    }
  },
  { immediate: true }
);
</script>

<style scoped lang="scss">
.barcode-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  overflow: hidden;

  .barcode-wrapper {
    transition: transform 0.3s ease;
    cursor: pointer;
    max-width: 100%;
    display: flex;
    justify-content: center;

    &.is-zoomed {
      z-index: 50;
      position: relative;
    }

    .barcode-svg {
      display: block;
      height: auto;
    }
  }

  .barcode-error-fallback {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem;
    border: 1px dashed var(--red-500, #ef4444);
    border-radius: 0.5rem;
    background-color: var(--red-50, #fef2f2);
    color: var(--red-700, #b91c1c);
    text-align: center;
    font-family: sans-serif;

    .error-text {
      font-size: 0.875rem;
      font-weight: 500;
    }

    .raw-value {
      margin-top: 0.25rem;
      font-size: 0.75rem;
      font-family: monospace;
      letter-spacing: 0.05em;
    }
  }
}
</style>
```
