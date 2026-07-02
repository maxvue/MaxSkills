---
name: vue-youtube-shorts-preview-simulator-best-practices
description: Use when designing, building, styling, or debugging Vue 3 components, views, or composables related to the YouTube Shorts video preview simulator. Triggers on components like YouTubeShortsPreview, ShortsSimulator, vertical video player wrappers (9:16 aspect ratio), YouTube application UI overlay mockups (channel logo, channel name, subscribe button, description, action sidebar icons for Like, Dislike, Comments, Share, Remix), and safe zones layout guides (non-overlapping areas).
---

# Boas Práticas do Simulador de Pré-visualização do YouTube Shorts em Vue

## Objetivo
Fornecer diretrizes, padrões de arquitetura e lógica reativa para construir e manter um simulador interativo de pré-visualização de vídeo vertical 9:16 que representa a interface mobile do YouTube Shorts no frontend do EngeApp, utilizando a biblioteca unificada MaxComponentsUi, auxiliares do MaxUse e práticas padrão da Composition API do Vue 3.

## Instruções

### 1. Estrutura e Configuração do Componente (SFC)
Siga rigorosamente a ordem de estrutura do Single-File Component (SFC):
1. `<template>`: Envolve o container do vídeo 9:16, indicadores nativos de sobreposição do YouTube, a barra lateral de ações, detalhes do canal, controles personalizados (reproduzir/pausar/mutar) e guias visuais ativáveis de Safe Zone.
2. `<script setup lang="ts">`: Gerencia a vinculação de referência do vídeo, alternância do estado de reprodução, alternância do estado de mudo, alternância de expansão da legenda, contadores fictícios de interação (curtir, comentar) e exibição das guias de Safe Zone.
3. `<style scoped lang="scss">`: Define as restrições de layout, posicionamento absoluto para as sobreposições, animações ativas (como o disco giratório do áudio) e os estilos visuais para as áreas restritas.

Lembre-se:
- Mantenha todos os parâmetros/atributos do template em uma única linha (estilo inline) na abertura de tags: `<Componente param1="..." param2="..." />`.
- Escreva todos os comentários do código estritamente em Português do Brasil (`pt-BR`).

### 2. Layout, Proporção e Responsividade (9:16)
- **Proporção 9:16:** Garanta que o container do player de vídeo imponha uma proporção rígida de `aspect-ratio: 9 / 16`.
- **Restrições de tamanho no Desktop:** Aplique limites máximos de tela no desktop (ex: `max-width: 360px; max-height: 640px;` ou `max-width: 400px; max-height: 711px;`) para emular fielmente as telas de celulares.
- **Letterboxing:** Use um fundo preto sólido (`#000`) para o container. Vídeos com proporções diferentes de 9:16 devem ser centralizados e ajustados via `object-fit: cover` ou `object-fit: contain` conforme os requisitos do produto.

### 3. Elementos de Sobreposição da UI do YouTube Shorts
Replique com fidelidade a interface oficial do YouTube Shorts para celular para ajudar os criadores a testarem possíveis problemas de sobreposição de elementos:
- **Barra Lateral de Ações (Coluna Vertical Direita):**
  - Botão Curtir (`MaxIconButton` com ícone de joinha/thumbs-up) + contador fictício.
  - Botão Não Gostei (`MaxIconButton` com ícone de joinha invertido) + texto "Não gostei".
  - Botão Comentários (`MaxIconButton` com ícone de balão de diálogo) + contador fictício.
  - Botão Compartilhar (`MaxIconButton` com ícone de seta/compartilhamento) + texto "Compartilhar".
  - Botão Remix (`MaxIconButton` com ícone de loop/remix) + texto "Remix".
  - Miniatura do disco do áudio musical girando no canto inferior direito quando o vídeo estiver sendo reproduzido.
- **Informações do Canal e Legenda (Sobreposições Inferiores Esquerdas):**
  - Avatar do Canal (formato circular), Handle (`@handle`) e o botão vermelho "Inscrever-se".
  - Legenda/Descrição com hashtags. Se o texto exceder 80 caracteres, trunque-o e adicione o botão "mais" para expandir o texto de forma reativa.
  - Banner da faixa musical exibindo o título da música com um efeito de texto rolante (marquee) ao lado de um ícone de nota musical.
- **Controles de Vídeo:**
  - Elemento `<video>` HTML5 padrão com atributos de mudo, reprodução contínua (loop) e reprodução automática (autoplay).
  - Indicador central de Reproduzir/Pausar. Clicar em qualquer lugar sobre o player de vídeo deve pausar/retomar a reprodução e exibir brevemente um feedback visual na tela.

### 4. Guia Visual de Safe Zone (Grade de Sobreposição)
Adicione um assistente visual para guiar os criadores na colocação de legendas ou logotipos sem sofrer problemas de sobreposição com a UI oficial. Destaque as "zonas mortas" da interface nativa usando camadas semitransparentes vermelhas ou bordas tracejadas:
- **Limite Superior da Safe Zone (Cabeçalho):** Topo 10% (onde residem os ícones de pesquisa e botões de voltar).
- **Limite Inferior da Safe Zone (Legenda e Canal):** Base 33% (reservado para o avatar do canal, botão inscrever-se, descrição e banner da música).
- **Limite Lateral Direito da Safe Zone (Coluna de Ações):** Lateral Direita 18% (reservado para os botões verticais da barra de ações).
- **Implementação:** Forneça um estado reativo alternável (`showSafeZones`). Quando ativo, renderize sobreposições semitransparentes com rótulos de aviso indicando as zonas bloqueadas.

Exemplo de Código:
```vue
<template>
  <div class="shorts-simulator">
    <!-- Container principal que simula o dispositivo mobile -->
    <div class="device-container" :class="{ 'show-safe-zones': showSafeZones }">
      <!-- Player de vídeo nativo HTML5 -->
      <video ref="videoRef" :src="videoUrl" :muted="isMuted" class="video-player" loop @click="togglePlay" />

      <!-- Feedback visual rápido ao pausar ou reproduzir -->
      <div v-if="showPlayOverlay" class="play-overlay">
        <MaxIconButton :icon="isPlaying ? 'mdi:play' : 'mdi:pause'" size="3" />
      </div>

      <!-- Guias Visuais das Zonas de Risco (Safe Zones) -->
      <div v-if="showSafeZones" class="safe-zone-overlay">
        <div class="safe-zone top-zone"><span>Área Ocupada: Topo (10%)</span></div>
        <div class="safe-zone right-zone"><span>Área Ocupada: Ações (18%)</span></div>
        <div class="safe-zone bottom-zone"><span>Área Ocupada: Legendas/Canal (33%)</span></div>
      </div>

      <!-- Camada de Interface Nativa (Overlays) -->
      <div class="native-ui">
        <!-- Barra de Ações Lateral Direita -->
        <div class="actions-sidebar">
          <div class="action-item">
            <MaxIconButton :icon="isLiked ? 'mdi:thumb-up' : 'mdi:thumb-up-outline'" @click="toggleLike" />
            <span>{{ isLiked ? '1.3K' : '1.2K' }}</span>
          </div>
          <div class="action-item">
            <MaxIconButton icon="mdi:thumb-down-outline" />
            <span>Não gostei</span>
          </div>
          <div class="action-item">
            <MaxIconButton icon="mdi:comment-text-outline" />
            <span>412</span>
          </div>
          <div class="action-item">
            <MaxIconButton icon="mdi:share-outline" />
            <span>Compartilhar</span>
          </div>
          <div class="action-item">
            <MaxIconButton icon="mdi:repeat" />
            <span>Remix</span>
          </div>
          <!-- Miniatura do Áudio Giratória -->
          <div class="music-thumbnail" :class="{ 'is-playing': isPlaying }">
            <img :src="channelAvatarUrl" alt="Áudio" class="audio-disc" />
          </div>
        </div>

        <!-- Informações do Canal e Legenda no Canto Inferior Esquerdo -->
        <div class="channel-overlay">
          <div class="channel-details">
            <img :src="channelAvatarUrl" class="channel-avatar" alt="Avatar" />
            <span class="channel-handle">@{{ channelHandle }}</span>
            <button class="subscribe-btn">Inscrever-se</button>
          </div>
          <div class="caption-container">
            <p class="caption">
              {{ isExpanded ? captionText : truncatedCaption }}
              <span v-if="captionText.length > 80 && !isExpanded" class="more-btn" @click="isExpanded = true">mais</span>
            </p>
          </div>
          <div class="music-track">
            <MaxIcon icon="mdi:music" size="1.2rem" />
            <div class="track-text-wrapper">
              <span class="track-text">Som original - {{ channelHandle }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// `ref` e `computed` são auto-importados via unplugin-auto-import; não importe manualmente.

const props = defineProps<{
  videoUrl: string;
  captionText: string;
  channelHandle: string;
  channelAvatarUrl: string;
}>();

const videoRef = ref<HTMLVideoElement | null>(null);
const isPlaying = ref<boolean>(false);
const isMuted = ref<boolean>(true);
const isLiked = ref<boolean>(false);
const showSafeZones = ref<boolean>(false);
const isExpanded = ref<boolean>(false);
const showPlayOverlay = ref<boolean>(false);

// Abrevia a legenda para manter a consistência visual caso seja longa
const truncatedCaption = computed<string>(() => {
  if (props.captionText.length <= 80) return props.captionText;
  return props.captionText.substring(0, 80) + '...';
});

// Controla a reprodução do vídeo
const togglePlay = (): void => {
  if (!videoRef.value) return;
  if (videoRef.value.paused) {
    videoRef.value.play();
    isPlaying.value = true;
  } else {
    videoRef.value.pause();
    isPlaying.value = false;
  }
  triggerPlayOverlay();
};

// Controla o estado de curtir
const toggleLike = (): void => {
  isLiked.value = !isLiked.value;
};

// Exibe feedback temporário na tela ao alternar play/pause
const triggerPlayOverlay = (): void => {
  showPlayOverlay.value = true;
  setTimeout(() => {
    showPlayOverlay.value = false;
  }, 600);
};
</script>

<style scoped lang="scss">
.shorts-simulator {
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: transparent;

  .device-container {
    position: relative;
    width: 100%;
    max-width: 360px;
    aspect-ratio: 9 / 16;
    background-color: #000;
    overflow: hidden;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);

    .video-player {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .play-overlay {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      pointer-events: none;
      z-index: 10;
    }

    .safe-zone-overlay {
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 5;

      .safe-zone {
        position: absolute;
        background-color: rgba(220, 38, 38, 0.25);
        border: 1px dashed rgba(220, 38, 38, 0.6);
        color: #fff;
        font-size: 11px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 500;
      }

      .top-zone {
        top: 0;
        left: 0;
        width: 100%;
        height: 10%;
      }

      .right-zone {
        top: 10%;
        right: 0;
        width: 18%;
        height: 57%;
      }

      .bottom-zone {
        bottom: 0;
        left: 0;
        width: 100%;
        height: 33%;
      }
    }

    .native-ui {
      position: absolute;
      inset: 0;
      pointer-events: none;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding: 16px;
      z-index: 3;
      background: linear-gradient(to top, rgba(0, 0, 0, 0.7) 0%, rgba(0, 0, 0, 0) 35%);

      .actions-sidebar {
        position: absolute;
        right: 8px;
        bottom: 40px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 16px;
        pointer-events: auto;

        .action-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          color: #fff;
          font-size: 11px;
          text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
        }

        .music-thumbnail {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          overflow: hidden;
          border: 2px solid #fff;
          display: flex;
          align-items: center;
          justify-content: center;

          .audio-disc {
            width: 100%;
            height: 100%;
            object-fit: cover;
          }

          &.is-playing {
            animation: spin 3s linear infinite;
          }
        }
      }

      .channel-overlay {
        max-width: 78%;
        color: #fff;
        pointer-events: auto;
        display: flex;
        flex-direction: column;
        gap: 8px;

        .channel-details {
          display: flex;
          align-items: center;
          gap: 8px;

          .channel-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            border: 1px solid #fff;
          }

          .channel-handle {
            font-weight: 600;
            font-size: 13px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
          }

          .subscribe-btn {
            background-color: #ff0000;
            color: #fff;
            border: none;
            padding: 4px 10px;
            font-size: 11px;
            font-weight: 600;
            border-radius: 18px;
            cursor: pointer;
            transition: background-color 0.2s;

            &:hover {
              background-color: #cc0000;
            }
          }
        }

        .caption-container {
          .caption {
            font-size: 12px;
            line-height: 1.4;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);

            .more-btn {
              font-weight: bold;
              cursor: pointer;
              margin-left: 4px;
              text-decoration: underline;
            }
          }
        }

        .music-track {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 11px;
          background-color: rgba(255, 255, 255, 0.15);
          padding: 4px 8px;
          border-radius: 12px;
          width: fit-content;
          max-width: 100%;

          .track-text-wrapper {
            overflow: hidden;
            white-space: nowrap;
            width: 120px;

            .track-text {
              display: inline-block;
              padding-left: 100%;
              animation: marquee 8s linear infinite;
            }
          }
        }
      }
    }
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes marquee {
  0% { transform: translate3d(0, 0, 0); }
  100% { transform: translate3d(-100%, 0, 0); }
}
</style>
```

### 5. Integração com Design System e Estado
- Utilize `<MaxIconButton>` para as ações da barra lateral vertical.
- Obtenha as informações do canal/cliente ativo dinamicamente a partir de uma store `@maxvue/max-pinia` (todo dado de página vem da store; o GET ao backend é feito pela store via caminho string `/api/...`, não por axios manual). Use esses dados para preencher `channelHandle` e `channelAvatarUrl`.
- Estados puramente locais de UI (reprodução, silenciamento, expansão de legenda, exibição de Safe Zones) podem permanecer como `ref` locais no componente — não precisam de store. Já os dados persistidos do canal/mídia devem vir da store `@maxvue/max-pinia`, que cuida do salvamento automático (auto-save/debounced) ao serem alterados.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** utilize Options API. Sempre utilize `<script setup lang="ts">`.
- **NÃO** escreva estilos em CSS puro ou Tailwind CSS. SCSS é obrigatório.
- **NÃO** escreva os comentários do código em inglês. Todos os comentários de código devem ser em Português do Brasil (`pt-BR`).
- **NÃO** quebre atributos/parâmetros do template em várias linhas. Mantenha os atributos na mesma linha.
- **NÃO** ignore as delimitações da Safe Zone. O topo (10%), a base (33%) e a lateral direita (18%) são áreas inseguras que cobrem elementos cruciais e legendas.
