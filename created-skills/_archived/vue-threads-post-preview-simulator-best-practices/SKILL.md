---
name: vue-threads-post-preview-simulator-best-practices
description: Use when designing, building, styling, or debugging Vue 3 components, composables, or views for simulating and previewing Threads posts (including text-only threads, single/multiple image attachments, video, or link previews). Triggers on components like ThreadsPostPreview, post length validations (500 character limit), and Threads thread-reply mockup simulators.
---

# Boas Práticas para Pré-visualização e Simulador de Postagens no Threads

## Objetivo
Fornecer um conjunto padronizado de boas práticas e diretrizes de implementação para a criação de componentes de simulação e pré-visualização (preview) de postagens do Threads em Vue 3, com alta fidelidade e reatividade, utilizando UnoCSS, TypeScript e as bibliotecas de componentes locais (`MaxComponentsUi` e `MaxUse`).

## Instruções

### 1. Estrutura e Configuração do Componente
- Sempre utilize Componentes de Arquivo Único (SFC) seguindo a ordem correta de blocos: `<template>`, `<script setup lang="ts">` e `<style lang="scss">` ou classes utilitárias do UnoCSS.
- Defina uma interface TypeScript estrita para a estrutura dos dados da postagem, garantindo a tipagem segura.
- Utilize propriedades computadas (`computed`) do Vue para derivar estilos, indicadores de limite de caracteres e arrays de divisão do encadeamento (threads).

### 2. Layout e Estética Nativa (Estilização do Threads)
- **Layout de Perfil:** Renderize o avatar do perfil do usuário à esquerda, o nome de usuário na linha superior e o conteúdo do post à direita do avatar.
- **Linha Conectora:** Se um encadeamento tiver respostas ou for dividido em vários posts, renderize uma linha vertical fina (conector) que vai do avatar do perfil atual até o avatar do próximo post.
- **Ícones de Ação:** Forneça a barra de ações padrão do Threads (Curtir, Responder, Repostar, Compartilhar) logo abaixo do conteúdo, usando componentes `MaxIcon`:
  - Curtir (Like): `mdi:heart-outline`
  - Responder (Reply): `mdi:comment-outline` ou `mdi:message-outline`
  - Repostar (Repost): `mdi:repeat`
  - Compartilhar (Share): `mdi:send-outline`

### 3. Limite de Caracteres e Divisão em Vários Posts
- O Threads impõe um **limite de 500 caracteres** por postagem.
- Implemente a contagem de caracteres em tempo real. Mostre um indicador de progresso circular ou um selo que mude de cor (ex: cinza -> laranja -> vermelho) à medida que a contagem se aproxima de 500.
- **Simulador de divisão automática de threads:** Se o texto inserido exceder 500 caracteres, divida automaticamente o texto nos limites das palavras (ou a cada 500 caracteres) e exiba no simulador como uma sequência de posts conectados.

### 4. Visualizações Prévias de Mídia e Links
- **Imagem/Vídeo Único:** Exiba em um contêiner responsivo com cantos arredondados (`border-radius: 12px` / `rounded-xl`) e uma altura máxima para evitar quebras abruptas de layout.
- **Carrosséis (Múltiplas Imagens):** Renderize as imagens usando rolagem horizontal com snap ou um contêiner de carrossel com botões de paginação.
- **Cartão de Pré-visualização de Link (Link Preview):** Se uma URL for detectada em um post de apenas texto, renderize um cartão rico com:
  - Miniatura do link (imagem no topo ou na lateral dependendo do tamanho)
  - Domínio canônico (ex: `github.com`)
  - Título do artigo e uma breve descrição
- **Sobreposição em Vídeo:** Inclua um botão/indicador de play/pause sobreposto para arquivos de vídeo.

### 5. Integração com Bibliotecas Locais
- Use `MaxIcon` para todos os ícones da interface.
- Integre os composables do `MaxUse` (como auxiliares para leitura de arquivos locais para base64 ou URLs de objeto temporárias para renderização imediata).
- Mantenha os atributos dos componentes em uma única linha (estilo inline) no bloco `<template>`, conforme as diretrizes do projeto.

---

## Restrições
- **NÃO** defina cores fixas (hardcoded) nem use a paleta crua do tipo Tailwind (`zinc-900`, `amber-500`, `red-500`, etc.). Use exclusivamente os tokens de cor do tema `presetMaxUno`/Aura (ex.: `bg-surface`, `text-muted`, `border-base`, `text-danger`, `text-warning`), que já suportam os modos claro e escuro nativamente.
- **NÃO** use Options API. Sempre utilize `<script setup lang="ts">`.
- **NÃO** ignore o indicador de limite de 500 caracteres; o simulador precisa avisar visualmente se a validação do backend for rejeitar a publicação.
- Todos os comentários do código em arquivos Vue devem ser escritos estritamente em **Português do Brasil (pt-BR)**.

---

## Exemplos

### ThreadsPostPreview.vue
Aqui está um exemplo de alta fidelidade de um componente de pré-visualização do Threads usando Composition API, TypeScript e auxiliares locais:

```vue
<template>
  <div class="threads-preview-container flex flex-col gap-4 p-4 border border-base rounded-2xl max-w-xl bg-surface text-base">
    <div v-for="(post, index) in threadPosts" :key="index" class="thread-item flex gap-3 relative">
      <!-- Linha conectora vertical para posts encadeados -->
      <div v-if="threadPosts.length > 1 && index < threadPosts.length - 1" class="absolute left-6 top-12 bottom-0 w-0.5 bg-base-muted"></div>

      <!-- Avatar da Conta -->
      <div class="flex flex-col items-center">
        <img :src="avatarUrl || '/default-avatar.png'" alt="Avatar" class="w-12 h-12 rounded-full object-cover" />
      </div>

      <!-- Conteúdo do Post -->
      <div class="flex-1 flex flex-col gap-1 pb-4">
        <!-- Nome de usuário e tempo decorrido -->
        <div class="flex items-center justify-between">
          <span class="font-semibold text-sm hover:underline cursor-pointer">{{ username || 'usuario_threads' }}</span>
          <div class="flex items-center gap-2 text-xs text-muted">
            <span>{{ timeAgo }}</span>
            <MaxIcon icon="mdi:dots-horizontal" class="cursor-pointer" />
          </div>
        </div>

        <!-- Texto do post -->
        <p class="text-sm leading-relaxed whitespace-pre-wrap select-text">{{ post.text }}</p>

        <!-- Preview de Mídia -->
        <div v-if="post.media && post.media.length > 0" class="media-container mt-2 rounded-xl overflow-hidden border border-base max-h-80 bg-surface-muted flex justify-center items-center">
          <!-- Carrossel de imagens -->
          <div v-if="post.media.length > 1" class="carousel-wrapper w-full relative">
            <img :src="post.media[activeMediaIndex]" alt="Preview" class="w-full h-80 object-cover" />
            <span class="absolute top-2 right-2 bg-overlay text-on-overlay text-xs px-2 py-1 rounded-full">{{ activeMediaIndex + 1 }}/{{ post.media.length }}</span>
          </div>
          <!-- Imagem única -->
          <img v-else :src="post.media[0]" alt="Preview" class="w-full max-h-80 object-cover" />
        </div>

        <!-- Preview de Link Rich Card (se houver e não houver mídia física) -->
        <a v-if="post.linkPreview && (!post.media || post.media.length === 0)" :href="post.linkPreview.url" target="_blank" class="link-preview-card mt-2 flex flex-col rounded-xl overflow-hidden border border-base hover:bg-surface-muted transition-colors">
          <img v-if="post.linkPreview.image" :src="post.linkPreview.image" alt="Thumbnail" class="w-full h-40 object-cover" />
          <div class="p-3 flex flex-col gap-1">
            <span class="text-xs text-muted uppercase tracking-wider">{{ post.linkPreview.domain }}</span>
            <span class="text-sm font-semibold line-clamp-1">{{ post.linkPreview.title }}</span>
            <span class="text-xs text-muted line-clamp-2">{{ post.linkPreview.description }}</span>
          </div>
        </a>

        <!-- Barra de Ações -->
        <div class="action-bar flex gap-4 mt-3 text-muted">
          <button class="hover:text-danger transition-colors"><MaxIcon icon="mdi:heart-outline" size="1.1" /></button>
          <button class="hover:text-primary transition-colors"><MaxIcon icon="mdi:comment-outline" size="1.1" /></button>
          <button class="hover:text-success transition-colors"><MaxIcon icon="mdi:repeat" size="1.1" /></button>
          <button class="hover:text-primary transition-colors"><MaxIcon icon="mdi:send-outline" size="1.1" /></button>
        </div>
      </div>
    </div>

    <!-- Validador visual do limite de caracteres -->
    <div class="validation-bar flex items-center justify-between border-t border-base pt-3 mt-1 text-xs">
      <span :class="textLengthClass">{{ rawText.length }}/500 caracteres</span>
      <span v-if="rawText.length > 500" class="text-danger font-medium">O texto será dividido em {{ threadPosts.length }} posts.</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';

// Definição das interfaces para tipagem estrita
interface LinkPreview {
  url: string;
  title: string;
  description: string;
  image?: string;
  domain: string;
}

interface PostSlice {
  text: string;
  media?: string[];
  linkPreview?: LinkPreview;
}

// Props recebidas pelo componente
const props = defineProps<{
  rawText: string;
  mediaUrls?: string[];
  linkPreview?: LinkPreview;
  username?: string;
  avatarUrl?: string;
  timeAgo?: string;
}>();

// Índice ativo para navegação de imagens em carrossel
const activeMediaIndex = ref<number>(0);

// Computed para cor dinâmica de acordo com a quantidade de caracteres
const textLengthClass = computed<string>(() => {
  if (props.rawText.length > 500) return 'text-danger font-bold';
  if (props.rawText.length > 450) return 'text-warning font-semibold';
  return 'text-muted';
});

// Computed que divide o texto em fatias caso ultrapasse o limite do Threads (500 caracteres)
const threadPosts = computed<PostSlice[]>(() => {
  const text = props.rawText || '';
  if (text.length <= 500) {
    return [{
      text,
      media: props.mediaUrls,
      linkPreview: props.linkPreview
    }];
  }

  const slices: PostSlice[] = [];
  let remainingText = text;

  while (remainingText.length > 0) {
    let sliceLength = 500;
    if (remainingText.length > 500) {
      // Quebra no espaço ou quebra de linha mais próxima do fim da fatia
      const subStr = remainingText.slice(0, 500);
      const lastSpace = Math.max(subStr.lastIndexOf(' '), subStr.lastIndexOf('\n'));
      if (lastSpace > 400) {
        sliceLength = lastSpace;
      }
    }

    const currentText = remainingText.slice(0, sliceLength).trim();
    slices.push({ text: currentText });
    remainingText = remainingText.slice(sliceLength).trim();
  }

  // Mídias e links associados apenas ao post inicial do encadeamento
  if (slices.length > 0) {
    slices[0].media = props.mediaUrls;
    slices[0].linkPreview = props.linkPreview;
  }

  return slices;
});
</script>

<style scoped lang="scss">
.threads-preview-container {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  
  .thread-item {
    transition: all 0.2s ease-in-out;
  }
}
</style>
```
