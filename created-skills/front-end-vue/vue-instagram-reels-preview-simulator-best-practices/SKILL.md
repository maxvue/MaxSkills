---
name: vue-instagram-reels-preview-simulator-best-practices
description: Use when creating, modifying, styling, or debugging the Instagram Reels and TikTok vertical video preview simulator component in Vue 3 (SocialMediaApp). Triggers on components rendering 9:16 vertical video layout, simulating player controls, handling video play/pause states, showing native social media overlays (username, caption, action buttons like like/comment/share), and demonstrating safe zones (safe area overlay helper) where text or critical visual content must not be obscured by the native UI.
---

# Boas Práticas do Simulador de Preview do Instagram Reels & TikTok em Vue

## Objetivo
Fornecer diretrizes, padrões estruturais e lógica reativa para construir e manter um simulador interativo de visualização de vídeo vertical no formato 9:16 que represente o Instagram Reels e o TikTok dentro do front-end do SocialMediaApp, utilizando componentes unificados do MaxComponentsUi, helpers do MaxUse e as práticas padrões de Composition API do Vue 3.

## Instruções

### 1. Estrutura e Configuração do Componente (SFC)
Siga estritamente a ordem oficial de estrutura de Componentes de Arquivo Único (SFC):
1. `<template>`: Estruture o container de proporção de tela 9:16, o elemento de vídeo, as sobreposições de UI nativa, o indicador visual de feedback de reprodução/pausa e os guias visuais ativáveis de Safe Zones (Áreas Seguras).
2. `<script setup lang="ts">`: Implemente a reatividade do componente, o gerenciamento de referências do elemento de vídeo, a alternância de play/pause, a lógica de expansão da legenda, controle de volume e controle do estado de exibição das Safe Zones.
3. `<style scoped lang="scss">`: Aplique formatação SCSS para as restrições do container 9:16, posicionamento absoluto das sobreposições de UI, ícones personalizados e estilização visual das Safe Zones.

Lembre-se:
- Mantenha todos os parâmetros/atributos do template em uma única linha (estilo inline) na abertura da tag: `<Componente param1="..." param2="..." />`.
- Escreva todos os comentários de código estritamente no idioma Português do Brasil (`pt-BR`).

### 2. Layout, Proporção de Tela e Responsividade (9:16)
- **Proporção de Tela 9:16:** Garanta que o container de exibição do vídeo imponha uma proporção rígida de `aspect-ratio: 9 / 16`.
- **Limites de Dimensões Máximas:** Defina limites máximos para desktops (ex: `max-width: 400px; max-height: 711px;`) para emular telas de smartphones com precisão sem estourar a tela do navegador no desktop.
- **Fundo e Redimensionamento:** Aplique um fundo preto (`#000`) atrás do vídeo para lidar com barras pretas (letterboxing) caso o usuário envie um vídeo com proporção diferente de 9:16.

### 3. Elementos de Sobreposição da UI Nativa das Redes Sociais
Replique a sobreposição oficial da interface do Instagram Reels para ajudar os usuários a identificar possíveis problemas de sobreposição:
- **Informações do Perfil (Canto Inferior Esquerdo):** Avatar do perfil, nome do usuário (`@username`) seguido pela legenda.
- **Expansão da Legenda ("Ver mais"):** Implemente uma alternância reativa para a legenda. Se a legenda tiver mais de 80 caracteres, trunque-a e exiba o botão "mais". Quando clicado, expanda para exibir o texto completo sobre o container do vídeo.
- **Botões de Ação (Coluna Vertical Lateral Direita):** Foto do perfil (com botão de seguir), Curtir (coração), Comentar (balão), Compartilhar (avião de papel) e Opções (três pontos). Exiba contadores simulados realistas abaixo de cada ação.
- **Informações de Áudio (Linha Inferior Esquerda):** Renderize um título de música em rolagem com um ícone de vinil girando ou nota musical.

### 4. Assistente Visual de Áreas Seguras (Safe Zone Overlay)
Forneça um assistente visual para alertar criadores de conteúdo sobre zonas onde eles NÃO devem posicionar textos críticos, gráficos importantes ou chamadas para ação (CTAs):
- **Limite Superior da Safe Zone (Header):** Primeiros 12% da altura (reservados para busca, botão de voltar e filtros de categoria).
- **Limite Inferior da Safe Zone (Legenda e Perfil):** Últimos 25% a 30% da altura (reservados para legenda, nome do usuário e barra de áudio).
- **Limite Lateral Direito da Safe Zone (Coluna de Ação):** Últimos 15% a 20% da largura na lateral direita (reservados para os botões de ação).
- **Implementação:** Adicione um botão de alternância (toggle) visual. Quando ativado, sobreponha camadas vermelhas/laranjas semitransparentes ou linhas pontilhadas nessas margens para destacar visualmente as "zonas mortas".

Exemplo de Código:
```vue
<template>
  <div class="reels-simulator">
    <!-- Container principal do emulador de celular -->
    <div class="device-container" :class="{ 'show-safe-zones': showSafeZones }">
      <!-- Elemento de Vídeo Nativo -->
      <video ref="videoRef" :src="videoUrl" class="video-player" @click="togglePlay" />

      <!-- Ícone indicador de play/pause no centro -->
      <div v-if="showPlayOverlay" class="play-overlay">
        <MaxIconButton icon="mdi:play" size="3" />
      </div>

      <!-- Guia Visual de Safe Zone -->
      <div v-if="showSafeZones" class="safe-zone-overlay">
        <div class="safe-zone top-zone"><span>Área Restrita: Topo</span></div>
        <div class="safe-zone right-zone"><span>Área Restrita: Ações</span></div>
        <div class="safe-zone bottom-zone"><span>Área Restrita: Legenda</span></div>
      </div>

      <!-- UI Nativa do Instagram Reels (Overlays) -->
      <div class="native-ui">
        <!-- Coluna de Ações à Direita -->
        <div class="actions-sidebar">
          <div class="action-item"><MaxIconButton icon="mdi:heart-outline" /><span>1.2K</span></div>
          <div class="action-item"><MaxIconButton icon="mdi:comment-outline" /><span>340</span></div>
          <div class="action-item"><MaxIconButton icon="mdi:share-variant-outline" /></div>
          <div class="action-item"><MaxIconButton icon="mdi:dots-horizontal" /></div>
        </div>

        <!-- Informações do Perfil e Legenda no Canto Inferior Esquerdo -->
        <div class="profile-info">
          <div class="user-details">
            <span class="username">@canal_teste</span>
            <button class="follow-btn">Seguir</button>
          </div>
          <p class="caption">
            {{ isExpanded ? captionText : truncatedCaption }}
            <span v-if="captionText.length > 80 && !isExpanded" class="more-btn" @click="isExpanded = true">mais</span>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

const props = defineProps<{
  videoUrl: string;
  captionText: string;
}>();

const videoRef = ref<HTMLVideoElement | null>(null);
const showSafeZones = ref<boolean>(false);
const isExpanded = ref<boolean>(false);
const showPlayOverlay = ref<boolean>(false);

// Trunca a legenda caso exceda o limite visual padrão
const truncatedCaption = computed<string>(() => {
  if (props.captionText.length <= 80) return props.captionText;
  return props.captionText.substring(0, 80) + '...';
});

// Alterna o estado de reprodução do vídeo
const togglePlay = (): void => {
  if (!videoRef.value) return;
  if (videoRef.value.paused) {
    videoRef.value.play();
    triggerPlayOverlay();
  } else {
    videoRef.value.pause();
    triggerPlayOverlay();
  }
};

// Exibe brevemente o feedback de play/pause no centro do vídeo
const triggerPlayOverlay = (): void => {
  showPlayOverlay.value = true;
  setTimeout(() => {
    showPlayOverlay.value = false;
  }, 500);
};
</script>

<style scoped lang="scss">
.reels-simulator {
  display: flex;
  justify-content: center;
  align-items: center;

  .device-container {
    position: relative;
    width: 100%;
    max-width: 400px;
    aspect-ratio: 9 / 16;
    background-color: #000;
    overflow: hidden;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);

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
      animation: ping 0.5s ease-out;
    }

    .safe-zone-overlay {
      position: absolute;
      inset: 0;
      pointer-events: none;

      .safe-zone {
        position: absolute;
        background-color: rgba(239, 68, 68, 0.25);
        border: 1px dashed rgba(239, 68, 68, 0.5);
        color: #fff;
        font-size: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
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
        height: 58%;
      }

      .bottom-zone {
        bottom: 0;
        left: 0;
        width: 100%;
        height: 30%;
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
      background: linear-gradient(to top, rgba(0, 0, 0, 0.6) 0%, rgba(0, 0, 0, 0) 40%);

      .actions-sidebar {
        position: absolute;
        right: 8px;
        bottom: 120px;
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
          font-size: 12px;
        }
      }

      .profile-info {
        max-width: 80%;
        color: #fff;
        pointer-events: auto;
        display: flex;
        flex-direction: column;
        gap: 8px;

        .user-details {
          display: flex;
          align-items: center;
          gap: 8px;

          .username {
            font-weight: 600;
            font-size: 14px;
          }

          .follow-btn {
            background: transparent;
            border: 1px solid #fff;
            color: #fff;
            padding: 2px 8px;
            font-size: 11px;
            border-radius: 4px;
            cursor: pointer;
          }
        }

        .caption {
          font-size: 13px;
          line-height: 1.4;

          .more-btn {
            font-weight: bold;
            cursor: pointer;
            margin-left: 4px;
            opacity: 0.8;
          }
        }
      }
    }
  }
}
</style>
```

### 5. Integração com o Design System e Gerenciamento de Estado
- Utilize `<MaxIconButton>` para os elementos de interação da barra lateral vertical.
- Utilize helpers do `vue-max-use-development-best-practices` para rastrear fatores de escala vertical ou orientação da tela, se necessário.
- Sincronize o estado de reprodução ativa (reproduzindo, progresso, duração atual) com o painel de pré-visualização do calendário ou com a store correspondente do Pinia para validações editoriais.

## Restrições
- **NÃO** utilize Options API. Sempre utilize `<script setup lang="ts">`.
- **NÃO** escreva estilos em CSS puro ou Tailwind CSS. SCSS é obrigatório.
- **NÃO** escreva comentários de código em inglês. Todos os comentários de código devem ser em Português do Brasil (`pt-BR`).
- **NÃO** quebre os parâmetros do template em várias linhas. Mantenha todos os atributos na mesma linha.
- **NÃO** ignore as margens da Safe Zone. A interface de Reels pode variar sutilmente, mas os limites inferiores (30%), superiores (12%) e direito (18%) são padrões críticos a serem respeitados.
