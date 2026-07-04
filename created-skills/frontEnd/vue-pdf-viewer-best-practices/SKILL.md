---
name: vue-pdf-viewer-best-practices
description: Use when embedding, rendering, or customizing PDF documents in the Vue 3 frontend using the vue-pdf-embed or pdfjs-dist libraries. Triggers on PDF component integration, page rendering, page navigation, loading status, scale/rotation configurations, worker configuration, and memory cleanup.
---

# Boas Práticas de Visualização de PDF no Vue 3

## Objetivo
Fornecer diretrizes sólidas, arquiteturas otimizadas e padrões estruturados para renderização de PDF reativa, de alta performance e livre de vazamentos de memória (memory leaks) usando `vue-pdf-embed` e `pdfjs-dist` (PDF.js) no front-end Vue 3 do Engeapp.

## Instruções

### 1. Utilizando `vue-pdf-embed` (Componente de Alto Nível)

#### Importação e Configuração Básica
Sempre importe o componente e, se necessário, importe as camadas de CSS correspondentes (camada de texto e camada de anotações) para garantir o alinhamento visual e funcionamento corretos.

```typescript
import VuePdfEmbed from 'vue-pdf-embed'
// Importe os arquivos CSS apenas se estiver usando text-layer or annotation-layer
import 'vue-pdf-embed/dist/styles/annotationLayer.css'
import 'vue-pdf-embed/dist/styles/textLayer.css'
```

**Segurança de Tipagem em Vinculação de Props**: Certifique-se de passar props booleanas de forma dinâmica utilizando o prefixo `:`.
*   **Correto:** `:text-layer="false"` ou `:annotation-layer="true"`
*   **Incorreto:** `text-layer="false"` (passa a string `"false"`, que é avaliada como verdadeira/truthy)

#### Tratamento de Eventos e Status de Carregamento
Implemente um feedback robusto durante as fases de carregamento e renderização do PDF. Capture falhas utilizando eventos de erro para evitar que a interface trave silenciosamente.

```vue
<template>
  <div class="pdf-viewer-container">
    <div v-if="isLoading" class="loading-spinner">Carregando PDF...</div>
    <div v-if="errorMessage" class="error-banner">{{ errorMessage }}</div>
    <VuePdfEmbed :source="pdfSource" :page="currentPage" :scale="pdfScale" :rotation="pdfRotation" @loaded="onPdfLoaded" @rendered="onPdfRendered" @loading-failed="onPdfLoadFailed" @rendering-failed="onPdfRenderFailed" />
  </div>
</template>

<script setup lang="ts">
import VuePdfEmbed from 'vue-pdf-embed'
// `ref`, `computed` etc. são auto-importados (unplugin-auto-import) — não importe de 'vue' manualmente.

const pdfSource = ref<string>('/api/document/datasheet/123')
const currentPage = ref<number>(1)
const pdfScale = ref<number>(1.0)
const pdfRotation = ref<number>(0)

const isLoading = ref<boolean>(true)
const errorMessage = ref<string | null>(null)
const totalPages = ref<number>(0)

const onPdfLoaded = (pdfDocument: any) => {
  isLoading.value = false
  totalPages.value = pdfDocument.numPages
  errorMessage.value = null
}

const onPdfRendered = () => {
  isLoading.value = false
}

const onPdfLoadFailed = (error: Error) => {
  isLoading.value = false
  errorMessage.value = 'Falha ao carregar o documento PDF. Por favor, tente novamente.'
  console.error('Erro de carregamento do PDF:', error)
}

const onPdfRenderFailed = (error: Error) => {
  isLoading.value = false
  errorMessage.value = 'Falha ao renderizar as páginas do PDF.'
  console.error('Erro de renderização do PDF:', error)
}
</script>
```

#### Reatividade Dinâmica (Escala, Rotação e Responsividade)
Para tornar o visualizador de PDF responsivo a diferentes tamanhos de container ou tela:
1.  Use um `ResizeObserver` ou o `useResizeObserver` do MaxUse (`@maxvue/max-use`, que reexporta o VueUse) para monitorar as alterações de largura do container.
2.  Vincule a largura calculada à propriedade `:width` do `VuePdfEmbed`.

```typescript
// `ref` é auto-importado (unplugin-auto-import).
// `useResizeObserver` vem do MaxUse (@maxvue/max-use), que reexporta o VueUse — não use
// `new ResizeObserver` manual: o composable já desconecta a observação no unmount.
import { useResizeObserver } from '@maxvue/max-use'

const containerRef = ref<HTMLElement | null>(null)
const pdfWidth = ref<number>(800)

useResizeObserver(containerRef, (entries) => {
  for (const entry of entries) {
    // Deixe uma margem de segurança (ex: 16px) para evitar barras de rolagem
    pdfWidth.value = Math.max(150, entry.contentRect.width - 16)
  }
})
```

### 2. Utilizando `pdfjs-dist` (Renderização de Baixo Nível)

#### Configuração do Worker
Sempre carregue o worker do PDF.js a partir da distribuição local em `node_modules` ou de uma CDN externa que coincida exatamente com a versão instalada da biblioteca.

```typescript
import * as pdfjsLib from 'pdfjs-dist';

// Configura o caminho do worker usando a resolução de assets do Vite via URL
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url
).toString();
```

#### Diretrizes de Estado Reativo & Vue Wrapper
**Aviso Crítico de Performance**: NÃO armazene as instâncias de documentos ou páginas do `pdfjs` dentro de um objeto reativo padrão (`ref` ou `reactive`). A reatividade profunda do Vue degrada drasticamente a performance e pode corromper os estados internos do PDF.js. Use `shallowRef` ou mantenha as referências em variáveis comuns.

```typescript
// `shallowRef` é auto-importado (unplugin-auto-import) — não importe de 'vue' manualmente.
const pdfDoc = shallowRef<pdfjsLib.PDFDocumentProxy | null>(null);
```

#### Carregando o PDF
Gerencie os status de carregamento dinamicamente usando `pdfjsLib.getDocument` passando uma URL, ArrayBuffer ou Blob.

Resolva os cmaps a partir do pacote local via Vite (`import.meta.url`), garantindo que a versão coincida sempre com a `pdfjs-dist` instalada — nunca fixe a versão na URL.

```typescript
// Resolve os cmaps empacotados em node_modules; a versão acompanha a instalada.
const cMapUrl = new URL('pdfjs-dist/cmaps/', import.meta.url).toString();

const loadingTask = pdfjsLib.getDocument({
  url: pdfUrl,
  cMapUrl,
  cMapPacked: true,
});
pdfDoc.value = await loadingTask.promise;
```

#### Renderizando Páginas no Canvas
Recupere o objeto da página e calcule a viewport. Monitore e cancele tarefas de renderização ativas se o usuário mudar de página rapidamente, evitando a poluição do canvas.

```typescript
let currentRenderTask: pdfjsLib.RenderTask | null = null;

async function renderPage(pageNum: number, scale: number = 1.5) {
  if (!pdfDoc.value) return;
  
  const page = await pdfDoc.value.getPage(pageNum);
  const canvas = canvasRef.value;
  if (!canvas) return;
  
  const context = canvas.getContext('2d');
  if (!context) return;
  
  // Cancela a tarefa anterior se estiver em execução
  if (currentRenderTask) {
    currentRenderTask.cancel();
  }
  
  const viewport = page.getViewport({ scale });
  canvas.height = viewport.height;
  canvas.width = viewport.width;
  
  const renderContext = {
    canvasContext: context,
    viewport: viewport,
  };
  
  currentRenderTask = page.render(renderContext);
  try {
    await currentRenderTask.promise;
  } catch (error: any) {
    if (error.name !== 'RenderingCancelledException') {
      console.error('Erro de renderização do PDF:', error);
    }
  }
}
```

### 3. Gerenciamento de Memória & Limpeza

Destrua adequadamente os objetos do PDF.js e fluxos de URL quando o componente for desmontado.
- Sempre desconecte/remova a observação das instâncias de `ResizeObserver`.
- Garanta que todas as URLs de objetos geradas via `URL.createObjectURL(file)` sejam revogadas com `URL.revokeObjectURL(url)`.
- Limpe o canvas, cancele tarefas de renderização ativas e invoque `destroy()` na instância do documento.

```typescript
// `onUnmounted` é auto-importado (unplugin-auto-import) — não importe de 'vue' manualmente.
// O `useResizeObserver` do MaxUse já limpa a observação sozinho no unmount.
onUnmounted(() => {
  if (currentRenderTask) {
    currentRenderTask.cancel();
  }
  if (pdfDoc.value) {
    pdfDoc.value.destroy();
  }
  // URL.revokeObjectURL(url) se tiver sido criado
});
```

### 4. Testes e Mocking (VuePdfEmbed)
Mocke o componente `VuePdfEmbed` nos testes unitários para evitar erros do motor de layout no jsdom/happy-dom.

```typescript
import { mount } from '@vue/test-utils'
import { describe, it, expect, vi } from 'vitest'
import DocumentViewer from './DocumentViewer.vue'

vi.mock('vue-pdf-embed', () => ({
  default: {
    name: 'VuePdfEmbed',
    template: '<div class="mock-vue-pdf-embed" data-testid="pdf-embed"><slot /></div>',
    props: ['source', 'page', 'scale', 'width', 'rotation', 'textLayer', 'annotationLayer'],
    emits: ['loaded', 'rendered', 'loading-failed', 'rendering-failed']
  }
}))

// testes...
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Apenas Composition API:** Sempre use `<script setup lang="ts">`.
- **TypeScript & SCSS:** Todas as seções de script devem usar TypeScript (`lang="ts"`) e a estilização deve usar SCSS (`lang="scss"`). A ordem dos elementos no arquivo SFC deve ser: `<template>`, `<script>`, `<style>`.
- **Restrições de Reatividade:** NUNCA associe proxies de documentos ou páginas do PDF.js diretamente a refs profundamente reativos do Vue (`ref()` ou `reactive()`). Use sempre `shallowRef()`.
- **Cancelamento de Renderização:** NUNCA tente renderizar uma página em um canvas sem antes checar se hay uma tarefa de renderização ativa no mesmo canvas. Sempre cancele-a primeiro.
- **Revogação de Recursos:** NUNCA deixe referências do `URL.createObjectURL` ativas depois que o componente for desmontado; sempre execute `URL.revokeObjectURL`.
- **URLs de CMAP:** NÃO defina URLs de CMAP diretamente no código (hardcoded). Use uma CDN que corresponda à versão exata ou empacote os cmaps.
- **Formatação de Atributos em Linha Única:** Mantenha todos os atributos/parâmetros de componentes Vue na mesma linha no template.
- **Sem Dimensões Estáticas no Código:** Evite definir larguras estáticas de forma direta (como `width="800px"`).
