---
name: vue-instagram-stories-sticker-editor-best-practices
description: Use when building, modifying, styling, or debugging the Instagram Stories sticker editor UI, managing draggable and resizable stickers (polls, questions, mentions, links, location) on canvas elements, validating story aspects (9:16), or calculating normalized coordinate objects for Meta Graph API integration.
---

# Boas Práticas do Editor de Stickers de Instagram Stories no Vue

## Objetivo
Padronizar a implementação de um editor visual interativo de stickers para Instagram Stories em Vue 3 (Composition API), garantindo interações precisas de arrastar e soltar (drag-and-drop), redimensionamento, rotação, validação de áreas seguras (safe zones) e cálculo de coordenadas normalizadas para os payloads de publicação da Meta Graph API.

## Instruções

### 1. Proporção do Canvas e Áreas Seguras (Safe Zones)
* Manter uma **proporção exata de 9:16** (ex: largura: 360px, altura: 640px) no container do editor.
* Implementar uma área segura superior (topo de 15% / ~96px) e uma área segura inferior (base de 15% / ~96px).
* Sinalizar visualmente ou bloquear os stickers para que não sejam posicionados de forma definitiva dentro destas áreas seguras, evitando colisão com elementos nativos da UI do Instagram (cabeçalho/rodapé).

### 2. Interatividade de Arrastar, Redimensionar e Rotacionar
* Utilizar variáveis reativas para o estado do sticker ativo: `x`, `y`, `width`, `height` e `rotation`.
* Implementar guias de encaixe magnético (snapping guides) para alinhamento central horizontal e vertical que aparecem quando um sticker está em um intervalo de 5px do eixo central.
* Centralizar eventos de mouse/toque usando os wrappers de interação expostos via `@maxvue/max-use` (auto-import, ex.: `useDraggable`) para manipular as coordenadas de forma suave. Evite importar `@vueuse/core` diretamente — use os helpers do `MaxUse`.

### 3. Normalização de Coordenadas
* Converter coordenadas locais do container em pixels para decimais relativos (0.0 a 1.0) e a rotação para graus (0 a 360) para compatibilidade com a Meta Graph API.
* Sempre recalcular e serializar as coordenadas antes de persistir:
  ```typescript
  const normalizedX = sticker.x / canvas.width
  const normalizedY = sticker.y / canvas.height
  const normalizedWidth = sticker.width / canvas.width
  const normalizedHeight = sticker.height / canvas.height
  ```
* Padronizar o esquema JSON que representa a lista de stickers:
  ```typescript
  interface StorySticker {
    id: string
    type: 'poll' | 'question' | 'mention' | 'link' | 'location'
    x: number // 0.0 a 1.0
    y: number // 0.0 a 1.0
    width: number // 0.0 a 1.0
    height: number // 0.0 a 1.0
    rotation: number // graus, 0 a 360
    properties: Record<string, any> // texto, URL, opções, etc.
  }
  ```

### 4. Gerenciamento de Estado e Persistência com MaxPinia
* Centralizar o estado de UI em uma store `useStickerEditorStore` (sticker ativo, alças, seleção). O estado puramente visual/efêmero pode ser uma store Pinia local.
* Toda leitura e persistência do payload normalizado (a lista final de stickers do Story) DEVE passar por uma store `@maxvue/max-pinia`, que cuida do GET inicial e do auto-save (debounced) no backend Adonis. Não faça `axios.get`/`axios.post` manual nem salve por submit.
* As rotas são caminhos string `/api/...` resolvidos por `apiGetRoute`/`apiPostRoute` do `@maxvue/max-use` (sem `route()`/Ziggy). Ex.: `apiGetRoute('/api/stories/{id}/stickers')`.
* Expor actions limpas na store de UI: `addSticker`, `removeSticker`, `updateStickerPosition` e `selectSticker`; ao mutar a lista normalizada na store MaxPinia, o salvamento ocorre automaticamente.
* Manter uma separação clara entre o sticker ativo sendo editado (estado da UI) e a lista serializada final dos stickers do Story (persistida via store MaxPinia).

### 5. UI e Estilos (UnoCSS)
* Usar propriedades de transformação CSS (`translate` e `rotate`) para renderizar os stickers no canvas.
* Renderizar alças de transformação interativas (alças de redimensionamento nos quatro cantos e uma alça de rotação no topo) apenas ao redor do sticker ativo selecionado.
* Integrar formulários de edição dos detalhes do sticker (como opções da enquete ou URLs do link) usando a biblioteca de componentes de design system local `MaxComponentsUi`.

## Restrições
* NÃO defina valores fixos de pixel do canvas no payload final enviado para a Meta Graph API. Sempre converta para valores decimais relativos (normalizados).
* NÃO bloqueie a thread principal de renderização com detecções complexas de colisão em tempo real; utilize debouncing ou atualizações via `requestAnimationFrame`.
* NÃO misture coordenadas locais da UI em pixels diretamente com as coordenadas de persistência. Sempre isole o estado local do estado persistido em decimais.
* NÃO use Tailwind CSS. Use exclusivamente UnoCSS com `presetMaxUno` (modo attributify) e os componentes `MaxComponentsUi`.
* NÃO faça GET/save manual do payload de stickers. A leitura inicial e o salvamento passam obrigatoriamente por uma store `@maxvue/max-pinia`.
