---
name: vue-html-to-image-export-best-practices
description: Use when exporting Vue 3 DOM elements, charts, or diagrams to images (PNG, JPEG, SVG) using html-to-image or html2canvas. Triggers on DOM capture configuration, handling device pixel ratio scaling, hidden element rendering, and image downloads.
---

# Boas Práticas para Exportação de HTML para Imagem no Vue

## Objetivo
Estabelecer diretrizes e padrões de alta qualidade para exportação de elementos HTML, gráficos (Chart.js) e diagramas (Vue Flow) como imagens de alta definição (PNG, JPEG, SVG) diretamente no navegador utilizando `html-to-image` e `html2canvas` no Vue 3.

## Instruções
1. **Seleção de Biblioteca**:
   - Prefira `html-to-image` para estruturas modernas baseadas em SVG/DOM, maior fidelidade de estilos CSS e melhor performance.
   - Utilize `html2canvas` ao realizar capturas de operações complexas de canvas ou capturas de tela cheia que envolvam deslocamentos de rolagem (scroll).

2. **Composition API & Composables**:
   - Implemente helpers de captura reativa utilizando a Composition API do Vue 3 (ex: `useHtmlToImage`).
   - Defina uma referência para o elemento DOM alvo: `const elementRef = ref<HTMLElement | null>(null)`.

3. **Configuração de Resolução de Captura (Alta Definição)**:
   - Evite imagens borradas em telas de alta densidade de pixels (telas Retina) configurando o `pixelRatio` ou fatores de escala.
   - Para `html2canvas`:
     ```typescript
     const canvas = await html2canvas(element, {
       scale: window.devicePixelRatio || 2,
       useCORS: true,
       // NÃO use allowTaint: true ao exportar — um canvas "tainted" não pode ser
       // convertido em imagem (toDataURL/toBlob lançam SecurityError).
       logging: false
     });
     ```
   - Para `html-to-image`:
     ```typescript
     const dataUrl = await toPng(element, {
       pixelRatio: window.devicePixelRatio || 2,
       cacheBust: true,
       style: {
         transform: 'scale(1)',
         transformOrigin: 'top left'
       }
     });
     ```

4. **Tratamento de Fontes Customizadas e Imagens Externas (CORS)**:
   - Sempre configure `useCORS: true` ou equivalente para permitir o carregamento de imagens de domínios externos.
   - Garanta que fontes customizadas da web estejam completamente carregadas antes de iniciar a captura.
   - Evite erros de segurança (tainted canvas) realizando o proxy de ativos externos ou convertendo-os previamente em Base64/Data URLs.

5. **Renderização de Elementos Ocultos ou Fora da Tela (Off-Screen)**:
   - Para capturar um elemento que está oculto (`v-show` ou `v-if`), renderize-o fora da tela usando posicionamento absoluto (`position: absolute; left: -9999px;`) ou através de um container temporário fora da área visível antes de disparar a captura, em vez de depender de atualizações imediatas do ciclo de vida do DOM.

6. **Boas Práticas em Componentes Vue**:
   - Sempre utilize `<script setup lang="ts">` e `<style scoped lang="scss">` para os Single-File Components (SFC).
   - Escreva todos os comentários do código no idioma Português do Brasil (pt-BR).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- Nunca execute a captura diretamente em elementos descarregados do DOM (`v-if="false"`). Sempre valide se a referência do elemento não é nula antes de prosseguir.
- Não utilize dimensões de pixel absolutas e fixas para capturas, preservando o comportamento responsivo dos componentes.
- Não ignore as configurações de CORS; falhas de CORS causarão exceções de segurança ("Tainted canvases may not be exported").
- Evite bloquear a thread principal do navegador; sempre utilize operações assíncronas (async/await) e forneça feedback ao usuário através de indicadores de carregamento (ex: variáveis reativas `isLoading` ou lojas de loading).
