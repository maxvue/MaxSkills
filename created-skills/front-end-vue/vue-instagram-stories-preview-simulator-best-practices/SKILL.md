---
name: vue-instagram-stories-preview-simulator-best-practices
description: Use when creating, styling, modifying, or debugging the Instagram Stories preview simulator component in Vue 3 (SocialMediaApp). Triggers on components rendering 9:16 vertical layout, simulating story timing progress bars, handling navigation taps (left to go back, right to advance), displaying interactive story widgets (polls, questions, links, mentions), and validating story media aspect ratios.
---

# Boas Práticas do Simulador de Preview do Instagram Stories em Vue

## Objetivo
Fornecer diretrizes, padrões de arquitetura e lógica reativa para implementar um simulador interativo de Instagram Stories no front-end do SocialMediaApp usando Vue 3, utilizando componentes do design system, composables e gerenciamento de estado.

## Instruções

### 1. Arquitetura e Estrutura do Componente (SFC)
Sempre siga a estrutura oficial de componentes de arquivo único:
1. `<template>`: Estruture o container 9:16, as barras de progresso segmentadas, o container da mídia, os widgets e as sobreposições de navegação.
2. `<script setup lang="ts">`: Trate a lógica interativa, temporizadores, indexação do story ativo, estado do Pinia e manipuladores de toque/gesto.
3. `<style scoped lang="scss">`: Aplique estilização vertical estrita, animações para segmentos de progresso e posicionamento absoluto para stickers/widgets.

Lembre-se:
- Mantenha todos os parâmetros/atributos do template em uma única linha (estilo inline) na abertura da tag: `<Componente param1="..." param2="..." />`.
- Escreva comentários de código estritamente no idioma Português do Brasil (`pt-BR`).

### 2. Lógicas de Tempo e Navegação dos Stories
- **Barra de Progresso Segmentada:** Renderize uma série de barras de progresso superiores baseadas no total de stories. Use variáveis CSS para controlar a largura/animação com base no story ativo.
- **Temporizadores de Intervalo:** Use composables de `vue-max-use-development-best-practices` para gerenciar temporizadores (por exemplo, 5s para imagens, 15s para vídeos).
- **Toques de Navegação:**
  - Sobreponha áreas de toque invisíveis nas laterais esquerda (25% de largura) e direita (75% de largura) da tela.
  - O toque à esquerda aciona o story anterior ou reinicia o atual.
  - O toque à direita avança para o próximo story.
- **Gesto de Segurar para Pausar (Hold-to-Pause):** Detecte os eventos `pointerdown` e `pointerup`/`pointerleave` no container de mídia para pausar o temporizador enquanto o usuário pressiona, e retomar ao soltar.

### 3. Widgets Interativos (Stickers)
Renderize widgets personalizáveis sobrepostos com estilização precisa:
- **Link:** Renderize um selo em formato de cápsula com o nome da URL e um ícone de link.
- **Enquete:** Exiba uma pergunta com duas opções clicáveis (texto/cores personalizáveis).
- **Caixa de Pergunta:** Renderize uma caixa solicitando feedback com uma simulação de entrada de texto.
- **Menções e Hashtags:** Renderize selos de texto estilizados começando com `@` ou `#`.
- Gerencie o posicionamento dinâmico desses stickers (normalmente centralizados ou arrastáveis usando coordenadas de porcentagem/deslocamento do cliente).

### 4. Validação de Proporção de Mídia
- Valide os arquivos enviados pelo usuário para os stories antes de renderizá-los.
- Certifique-se de que a proporção da imagem/vídeo seja 9:16. Dispare avisos se a proporção desviar significativamente.
- Exemplo de código:
  ```typescript
  // Valida a proporção da imagem ou vídeo antes de exibir no preview
  const validateAspectRatio = (file: File): Promise<boolean> => {
    return new Promise((resolve) => {
      const url = URL.createObjectURL(file);
      if (file.type.startsWith('image/')) {
        const img = new Image();
        img.onload = () => {
          const ratio = img.width / img.height;
          // Proporção ideal de 9:16 é ~0.5625
          resolve(Math.abs(ratio - 0.5625) < 0.05);
        };
        img.src = url;
      } else {
        const video = document.createElement('video');
        video.onloadedmetadata = () => {
          const ratio = video.videoWidth / video.videoHeight;
          resolve(Math.abs(ratio - 0.5625) < 0.05);
        };
        video.src = url;
      }
    });
  };
  ```

### 5. Integração com Design System e Estado
- Utilize `<MaxButton>`, `<MaxGrid>`, `<MaxCard>` e outros componentes de UI do design system quando apropriado.
- Vincule o estado (lista de stories, índice do story ativo atual, status de reprodução/pausa) a uma store dedicada do Pinia.

## Restrições
- **NÃO** utilize Options API. Sempre utilize `<script setup lang="ts">`.
- **NÃO** escreva estilos em CSS puro ou Tailwind CSS. SCSS é obrigatório.
- **NÃO** escreva comentários de código em inglês. Todos os comentários de código devem ser em Português do Brasil (`pt-BR`).
- **NÃO** quebre os parâmetros do template em várias linhas. Mantenha todos os atributos na mesma linha.
- **NÃO** use alertas nativos do navegador (`alert`) para avisos. Utilize componentes locais de notificação de UI.
