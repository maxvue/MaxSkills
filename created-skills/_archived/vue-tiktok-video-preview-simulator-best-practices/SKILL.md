---
name: vue-tiktok-video-preview-simulator-best-practices
description: Use when designing, building, styling, or debugging Vue 3 components, views, or composables related to the TikTok video preview simulator. Triggers on components like TikTokVideoPreview, TikTokSimulator, vertical video player wrappers (9:16 aspect ratio), TikTok application UI overlay mockups (user avatar, follow button, description, music disc, actions sidebar for Like, Comments, Share, Bookmark), and safe zones layout guides (non-overlapping areas) in the front-end.
---

# Boas Práticas do Simulador de Preview de Vídeo do TikTok em Vue

## Objetivo
Fornecer diretrizes, padrões arquiteturais e lógica reativa para construir e manter um simulador interativo de preview de vídeo vertical 9:16 que represente a interface móvel do TikTok dentro do front-end do projeto, utilizando o MaxComponentsUi unificado, helpers do MaxUse e práticas padrão da Composition API do Vue 3.

## Instruções

### 1. Estrutura do Componente e Configuração (SFC)
Siga rigorosamente a ordem da estrutura do Single-File Component (SFC):
1. `<template>`: Envolve o container de vídeo 9:16, indicadores de sobreposição nativos do TikTok, a barra lateral de ações à direita, detalhes do usuário e legenda no canto inferior esquerdo, controles personalizados e guias visuais de Zona Segura alternáveis.
2. `<script setup lang="ts">`: Gerencia a vinculação da referência do vídeo, alternância do estado de reprodução/pausa, alternância do estado de mudo, alternância de expansão da legenda, contadores de interação simulados (curtidas, comentários, salvamentos) e exibição das guias de zona segura.
3. `<style scoped lang="scss">`: Define as restrições de layout, posicionamento absoluto para as sobreposições, animações ativas (como o disco de música giratório) e os estilos visuais para as zonas restritas.

Lembre-se:
- Mantenha todos os parâmetros/atributos do template em uma única linha (estilo inline) na abertura das tags: `<Componente param1="..." param2="..." />`.
- Escreva todos os comentários de código estritamente em português brasileiro (`pt-BR`).

### 2. Layout, Proporção de Tela e Responsividade (9:16)
- **Proporção 9:16:** Certifique-se de que o container do player de vídeo aplique estritamente a propriedade `aspect-ratio: 9 / 16`.
- **Restrições de tamanho no Desktop:** Aplique limites máximos para visualização em desktop (ex: `max-width: 360px; max-height: 640px;` ou `max-width: 400px; max-height: 711px;`) para simular fielmente telas de dispositivos móveis.
- **Letterboxing:** Use um fundo preto sólido (`#000`) para o container. Vídeos com proporções diferentes de 9:16 devem ser centralizados e dimensionados via `object-fit: cover` ou `object-fit: contain` dependendo dos requisitos.

### 3. Elementos de Sobreposição da Interface do TikTok
Replique com precisão a interface do aplicativo móvel do TikTok para ajudar os criadores a testar possíveis sobreposições:
- **Barra Lateral de Ações (Coluna Vertical Direita):**
  - Avatar do perfil (formato circular) com um pequeno botão "+" rosa/vermelho de seguir sobreposto na parte inferior central do círculo do avatar.
  - Botão Curtir (`MaxIconButton` com ícone de coração) + contador simulado.
  - Botão Comentários (`MaxIconButton` com ícone de balão de diálogo) + contador simulado.
  - Botão Salvar/Favorito (`MaxIconButton` com ícone de bandeira/marcador) + contador simulado.
  - Botão Compartilhar (`MaxIconButton` com ícone de seta de compartilhamento) + contador simulado.
  - Miniatura do álbum da faixa de música girando no canto inferior direito quando o vídeo estiver sendo reproduzido.
- **Informações do Canal e Legenda (Sobreposições Inferior-Esquerda):**
  - Nome de usuário (`@usuario`) em negrito.
  - Legenda/Descrição com hashtags. Se o texto ultrapassar 80 caracteres, trunque-o e adicione um botão "mais" para expandir o texto de forma reativa.
  - Banner da música exibindo o título da música acompanhado de um efeito de rolagem de texto (marquee) e um ícone de nota musical.
- **Controles de Vídeo:**
  - Elemento `<video>` HTML5 padrão com as opções muted, loop e autoplay.
  - Indicador centralizado de Reproduzir/Pausar. Clicar em qualquer lugar no player de vídeo deve alternar a reprodução e acionar um breve indicador visual na tela.

### 4. Assistente Visual de Zona Segura (Grade de Sobreposição)
Adicione um assistente visual para orientar os criadores sobre onde posicionar legendas ou logotipos sem que ocorram problemas de sobreposição. Destaque as "zonas mortas" da interface nativa utilizando sobreposições semitransparentes ou bordas vermelhas tracejadas:
- **Limite Superior da Zona Segura (Cabeçalho):** Topo de 12% (onde ficam as abas "Seguindo / Para você" e os ícones de busca).
- **Limite da Zona Segura Lateral Direita (Coluna de Ações):** Direita de 18% (reservada para os ícones da barra lateral de ações e o disco de música giratório).
- **Limite Inferior da Zona Segura (Legenda e Perfil):** Base de 28% (reservada para o nome de usuário, descrição e informações da música).
- **Implementação:** Disponibilize um estado reativo alternável (`showSafeZones`). Quando ativo, exiba sobreposições semitransparentes com etiquetas de aviso indicando as áreas bloqueadas.

### 5. Exemplo de Código

```vue
<template>
  <div class="tiktok-simulator">
    <!-- Container do dispositivo que aplica a proporção de tela vertical 9:16 -->
    <div class="device-container" :class="{ 'show-safe-zones': showSafeZones }">
      <!-- Player de vídeo nativo HTML5 com clique para reproduzir/pausar -->
      <video ref="videoRef" :src="videoUrl" :muted="isMuted" class="video-player" loop @click="togglePlay" />

      <!-- Ícone indicador central de play/pause com efeito de exibição rápida -->
      <div v-if="showPlayOverlay" class="play-overlay">
        <MaxIconButton :icon="isPlaying ? 'mdi:play' : 'mdi:pause'" size="3" />
      </div>

      <!-- Camada de Zonas de Risco de Sobreposição (Safe Zones) -->
      <div v-if="showSafeZones" class="safe-zone-overlay">
        <div class="safe-zone top-zone"><span>Navegação / Abas (12%)</span></div>
        <div class="safe-zone right-zone"><span>Ações e Disco (18%)</span></div>
        <div class="safe-zone bottom-zone"><span>Perfil, Legenda e Áudio (28%)</span></div>
      </div>

      <!-- Interface Nativa Simulada do TikTok -->
      <div class="native-ui">
        <!-- Barra de Ações Lateral Direita (Avatar, Like, Comentário, Favorito, Compartilhar, Disco) -->
        <div class="actions-sidebar">
          <!-- Bloco do Perfil do Criador com botão de Seguir (+) -->
          <div class="profile-container">
            <img :src="channelAvatarUrl" class="creator-avatar" alt="Avatar" />
            <button class="follow-btn">+</button>
          </div>

          <!-- Ação Curtir -->
          <div class="action-item">
            <MaxIconButton :icon="isLiked ? 'mdi:heart' : 'mdi:heart-outline'" class="icon-like" :class="{ 'liked': isLiked }" @action="toggleLike" />
            <span>{{ isLiked ? '12.4K' : '12.3K' }}</span>
          </div>

          <!-- Ação Comentários -->
          <div class="action-item">
            <MaxIconButton icon="mdi:comment-processing-outline" class="icon-comment" />
            <span>856</span>
          </div>

          <!-- Ação Salvar/Favorito -->
          <div class="action-item">
            <MaxIconButton :icon="isBookmarked ? 'mdi:bookmark' : 'mdi:bookmark-outline'" class="icon-bookmark" :class="{ 'bookmarked': isBookmarked }" @action="toggleBookmark" />
            <span>{{ isBookmarked ? '432' : '431' }}</span>
          </div>

          <!-- Ação Compartilhar -->
          <div class="action-item">
            <MaxIconButton icon="mdi:share" class="icon-share" />
            <span>192</span>
          </div>

          <!-- Miniatura do Disco de Música Giratório -->
          <div class="music-disc-wrapper" :class="{ 'is-playing': isPlaying }">
            <img :src="channelAvatarUrl" alt="Música" class="music-disc" />
          </div>
        </div>

        <!-- Detalhes do Conteúdo no Canto Inferior Esquerdo (Usuário, Legenda, Música) -->
        <div class="content-overlay">
          <!-- Nome do Usuário TikTok com @ -->
          <span class="user-handle">@{{ channelHandle }}</span>

          <!-- Legenda do vídeo com toggle de expansão (mais) -->
          <div class="caption-wrapper">
            <p class="caption-text">
              {{ isExpanded ? captionText : truncatedCaption }}
              <span v-if="captionText.length > 80 && !isExpanded" class="more-btn" @click="isExpanded = true">mais</span>
            </p>
          </div>

          <!-- Detalhe da faixa musical simulando rolagem horizontal -->
          <div class="music-track-info">
            <MaxIcon icon="mdi:music" size="1rem" class="music-icon" />
            <div class="track-marquee-container">
              <span class="track-marquee">Som original - {{ channelHandle }} - @{{ channelHandle }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

// Definição das propriedades do simulador
const props = defineProps<{
  videoUrl: string;
  captionText: string;
  channelHandle: string;
  channelAvatarUrl: string;
}>();

// Referência para o elemento HTML5 de vídeo
const videoRef = ref<HTMLVideoElement | null>(null);

// Estados reativos locais de controle
const isPlaying = ref<boolean>(false);
const isMuted = ref<boolean>(true);
const isLiked = ref<boolean>(false);
const isBookmarked = ref<boolean>(false);
const showSafeZones = ref<boolean>(false);
const isExpanded = ref<boolean>(false);
const showPlayOverlay = ref<boolean>(false);

// Computada para truncar a legenda caso seja muito longa
const truncatedCaption = computed<string>(() => {
  if (props.captionText.length <= 80) return props.captionText;
  return props.captionText.substring(0, 80) + '...';
});

// Função para reproduzir/pausar o vídeo e animar o feedback na tela
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

// Alterna o estado de curtida
const toggleLike = (): void => {
  isLiked.value = !isLiked.value;
};

// Alterna o estado de favorito/salvo
const toggleBookmark = (): void => {
  isBookmarked.value = !isBookmarked.value;
};

// Exibe brevemente o feedback de play/pause sobreposto ao vídeo
const triggerPlayOverlay = (): void => {
  showPlayOverlay.value = true;
  setTimeout(() => {
    showPlayOverlay.value = false;
  }, 600);
};
</script>

<style scoped lang="scss">
.tiktok-simulator {
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
    border-radius: 16px;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6);

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
      opacity: 0.8;
    }

    .safe-zone-overlay {
      position: absolute;
      inset: 0;
      pointer-events: none;
      z-index: 5;

      .safe-zone {
        position: absolute;
        background-color: rgba(239, 68, 68, 0.25);
        border: 1px dashed rgba(239, 68, 68, 0.6);
        color: #fff;
        font-size: 11px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
      }

      .top-zone {
        top: 0;
        left: 0;
        width: 100%;
        height: 12%;
      }

      .right-zone {
        top: 12%;
        right: 0;
        width: 18%;
        height: 60%;
      }

      .bottom-zone {
        bottom: 0;
        left: 0;
        width: 100%;
        height: 28%;
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
      z-index: 4;
      background: linear-gradient(to top, rgba(0, 0, 0, 0.6) 0%, rgba(0, 0, 0, 0) 30%);

      .actions-sidebar {
        position: absolute;
        right: 8px;
        bottom: 30px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 18px;
        pointer-events: auto;

        .profile-container {
          position: relative;
          width: 44px;
          height: 44px;
          margin-bottom: 8px;

          .creator-avatar {
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 2px solid #fff;
            object-fit: cover;
          }

          .follow-btn {
            position: absolute;
            bottom: -5px;
            left: 50%;
            transform: translateX(-50%);
            background-color: #ff0050;
            color: #fff;
            border: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            font-size: 14px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
          }
        }

        .action-item {
          display: flex;
          flex-direction: column;
          align-items: center;
          color: #fff;
          font-size: 11px;
          text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8);
          gap: 2px;

          .icon-like.liked {
            color: #ff0050;
          }

          .icon-bookmark.bookmarked {
            color: #facd3b;
          }
        }

        .music-disc-wrapper {
          width: 38px;
          height: 38px;
          border-radius: 50%;
          background-color: #111;
          display: flex;
          align-items: center;
          justify-content: center;
          border: 4px solid #222;

          .music-disc {
            width: 22px;
            height: 22px;
            border-radius: 50%;
            object-fit: cover;
          }

          &.is-playing {
            animation: spin-disc 4s linear infinite;
          }
        }
      }

      .content-overlay {
        max-width: 76%;
        color: #fff;
        display: flex;
        flex-direction: column;
        gap: 6px;
        pointer-events: auto;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);

        .user-handle {
          font-weight: 700;
          font-size: 14px;
        }

        .caption-wrapper {
          .caption-text {
            font-size: 13px;
            line-height: 1.4;

            .more-btn {
              font-weight: bold;
              cursor: pointer;
              margin-left: 4px;
              color: #ccc;
              text-decoration: underline;
            }
          }
        }

        .music-track-info {
          display: flex;
          align-items: center;
          gap: 8px;
          font-size: 12px;

          .music-icon {
            flex-shrink: 0;
          }

          .track-marquee-container {
            overflow: hidden;
            white-space: nowrap;
            width: 140px;

            .track-marquee {
              display: inline-block;
              padding-left: 100%;
              animation: marquee-scroll 10s linear infinite;
            }
          }
        }
      }
    }
  }
}

@keyframes spin-disc {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes marquee-scroll {
  0% { transform: translate3d(0, 0, 0); }
  100% { transform: translate3d(-100%, 0, 0); }
}
</style>
```

### 6. Integração com Design System e Estado
- Utilize `<MaxIconButton>` para as ações padrão do painel lateral (Likes, Comentários, Salvar, Compartilhar).
- Vincule as informações ativas do usuário dinamicamente a partir de `vue-tenant-client-context-best-practices` para preencher automaticamente os parâmetros (`channelHandle` e `channelAvatarUrl`).
- Integre o estado de reprodução do vídeo com a store do Pinia utilizando as diretrizes de `vue-max-pinia-integration-best-practices` caso seja necessária a sincronização entre múltiplas telas (como a edição de detalhes e a visualização prévia).

## Restrições
- **NÃO** utilize Options API. Sempre utilize `<script setup lang="ts">`.
- **NÃO** escreva estilos em CSS puro ou Tailwind CSS. SCSS é obrigatório.
- **NÃO** escreva comentários do código Vue em inglês. Todos os comentários de código devem ser em português brasileiro (`pt-BR`).
- **NÃO** quebre parâmetros ou atributos do template em várias linhas. Mantenha todos os atributos na mesma linha.
- **NÃO** ignore as dimensões das Zonas Seguras. O topo (12%), a base (28%) e a direita (18%) são regiões críticas onde elementos de sobreposição do TikTok ocultarão legendas ou artes visuais importantes.
