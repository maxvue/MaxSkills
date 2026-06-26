---
name: vue-facebook-post-preview-simulator-best-practices
description: Use when designing, building, styling, or debugging Vue 3 components, views, or composables related to the Facebook post preview simulator. Triggers on components like FacebookPostPreview, FacebookSimulator, layouts supporting single/multiple image attachments, link cards, video players, page header mockups, and interaction bars (Like, Comment, Share) in SocialMediaApp.
---

# Melhores Práticas para o Simulador e Visualizador de Post do Facebook

## Objetivo
Fornecer um conjunto padronizado de melhores práticas e diretrizes de implementação para a criação de componentes reativos e de alta fidelidade para simulação e visualização de posts do Facebook no Vue 3, utilizando UnoCSS, TypeScript e as bibliotecas de interface locais (`MaxComponentsUi` e `MaxUse`).

## Instruções

### 1. Estrutura e Configuração de Componentes
- Use sempre Single-File Components (SFC) seguindo a ordem correta de blocos: `<template>`, `<script setup lang="ts">` e `<style scoped lang="scss">`.
- Defina interfaces TypeScript estritas para a estrutura de dados do post, anexos de mídia e visualizações de link para garantir a segurança de tipos.
- Mantenha os atributos dos componentes em linha única no bloco `<template>`, conforme as diretrizes do Vue local (ex: `<Componente param1="..." param2="..." />`).

### 2. Estética e Layout do Feed do Facebook
- **Mockup do Cabeçalho da Página:** Renderize o avatar da página à esquerda (imagem circular), o nome da página, o carimbo de data/hora da publicação do post (usando o composable `useTimeAgo` da biblioteca `MaxUse`) e o ícone de privacidade (globo público) ao lado.
- **Conteúdo do Post:** Renderize o texto do post com um botão "Ver mais" se o texto ultrapassar 300 caracteres.
- **Layout de Grade de Mídia (1 a 5 imagens):**
  - **1 Imagem:** Exibição em largura total com altura máxima limite.
  - **2 Imagens:** Divisão lado a lado.
  - **3 Imagens:** Uma imagem principal à esquerda/topo e duas menores à direita/baixo.
  - **4 Imagens:** Uma imagem principal superior e três imagens menores divididas abaixo, ou grade 2x2.
  - **5 Imagens:** Colagem padrão do Facebook (duas colunas principais, onde um dos lados contém 3 imagens menores empilhadas, exibindo uma sobreposição de `+X` na última imagem se houver mais de 5 imagens no total).
- **Card de Visualização de Link (Link Preview):** Se uma URL for anexada e nenhuma imagem física for enviada, renderize um card de visualização grande contendo:
  - Imagem em miniatura em alta resolução no topo
  - Domínio canônico na parte inferior em cinza e letras maiúsculas
  - Título e descrição do artigo
- **Barra de Ações/Interação:** Renderize os botões de ação do Facebook (Curtir, Comentar, Compartilhar) usando os componentes `MaxIconButton` ou `MaxIcon`:
  - Curtir: `mdi:thumb-up-outline` (ou preenchido quando curtido)
  - Comentar: `mdi:comment-outline`
  - Compartilhar: `mdi:share-outline`

### 3. Integração com Bibliotecas Locais
- Use `MaxIcon` ou `MaxIconButton` para todos os ícones da interface.
- Use `useTimeAgo` da biblioteca `MaxUse` para calcular tempos relativos das publicações.
- Alinhe a tipografia e o estilo com as classes utilitárias do UnoCSS.

---

## Restrições
- **NÃO** use a Options API. Sempre use `<script setup lang="ts">`.
- **NÃO** defina cores de tema estáticas diretamente no código ("hardcoded"). Use variáveis CSS ou classes de tema do UnoCSS com suporte nativo a modo claro e escuro.
- **NÃO** quebre os atributos do template em várias linhas. Mantenha-os em uma única linha.
- Todos os comentários de código nos arquivos Vue devem ser escritos em **Português do Brasil (pt-BR)**.

---

## Exemplos

### FacebookPostPreview.vue
Aqui está um exemplo de alta fidelidade de um componente de visualização do Facebook usando Composition API, TypeScript e as bibliotecas locais:

```vue
<template>
  <div class="facebook-preview-card border border-zinc-200 dark:border-zinc-800 rounded-lg max-w-xl bg-white dark:bg-zinc-900 text-zinc-900 dark:text-zinc-100 shadow-sm">
    <!-- Cabeçalho do Post -->
    <div class="flex items-center justify-between p-3 pb-2">
      <div class="flex items-center gap-2">
        <img :src="pageAvatar || '/default-avatar.png'" alt="Avatar" class="w-10 h-10 rounded-full object-cover" />
        <div class="flex flex-col">
          <span class="font-semibold text-sm hover:underline cursor-pointer leading-tight">{{ pageName || 'Nome da Página' }}</span>
          <div class="flex items-center gap-1 text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
            <span>{{ formattedTime }}</span>
            <span>•</span>
            <MaxIcon icon="mdi:earth" size="0.9rem" class="text-zinc-500" />
          </div>
        </div>
      </div>
      <MaxIconButton icon="mdi:dots-horizontal" size="1.2" />
    </div>

    <!-- Conteúdo do Texto -->
    <div class="px-3 pb-2 text-sm leading-relaxed whitespace-pre-wrap select-text">
      <p>
        <span>{{ displayedText }}</span>
        <button v-if="hasMoreText && !showFullText" @click="showFullText = true" class="text-blue-600 dark:text-blue-400 font-semibold hover:underline ml-1">Ver mais</button>
      </p>
    </div>

    <!-- Mídia (Grade de Imagens / Collage) -->
    <div v-if="mediaUrls && mediaUrls.length > 0" class="media-collage border-y border-zinc-200 dark:border-zinc-800 bg-zinc-100 dark:bg-zinc-950 overflow-hidden">
      <!-- Exibição de 1 Imagem -->
      <div v-if="mediaUrls.length === 1" class="w-full flex justify-center max-h-[450px]">
        <img :src="mediaUrls[0]" alt="Post Media" class="w-full object-cover max-h-[450px]" />
      </div>

      <!-- Exibição de 2 Imagens -->
      <div v-else-if="mediaUrls.length === 2" class="grid grid-cols-2 gap-1 h-[300px]">
        <img v-for="(img, idx) in mediaUrls" :key="idx" :src="img" alt="Post Media" class="w-full h-full object-cover" />
      </div>

      <!-- Exibição de 3 Imagens -->
      <div v-else-if="mediaUrls.length === 3" class="grid grid-cols-2 gap-1 h-[320px]">
        <img :src="mediaUrls[0]" alt="Post Media" class="w-full h-full object-cover row-span-2" />
        <div class="grid grid-rows-2 gap-1 h-full">
          <img :src="mediaUrls[1]" alt="Post Media" class="w-full h-full object-cover" />
          <img :src="mediaUrls[2]" alt="Post Media" class="w-full h-full object-cover" />
        </div>
      </div>

      <!-- Exibição de 4 Imagens -->
      <div v-else-if="mediaUrls.length === 4" class="grid grid-cols-2 gap-1 h-[340px]">
        <img :src="mediaUrls[0]" alt="Post Media" class="w-full h-full object-cover" />
        <div class="grid grid-cols-3 gap-1 col-span-2 h-[120px] mt-1">
          <img v-for="idx in [1, 2, 3]" :key="idx" :src="mediaUrls[idx]" alt="Post Media" class="w-full h-full object-cover" />
        </div>
      </div>

      <!-- Exibição de 5 ou mais Imagens -->
      <div v-else class="grid grid-cols-6 gap-1 h-[350px]">
        <img :src="mediaUrls[0]" alt="Post Media" class="col-span-3 h-full object-cover" />
        <img :src="mediaUrls[1]" alt="Post Media" class="col-span-3 h-full object-cover" />
        <div class="col-span-6 grid grid-cols-3 gap-1 h-[120px] mt-1">
          <img :src="mediaUrls[2]" alt="Post Media" class="w-full h-full object-cover" />
          <img :src="mediaUrls[3]" alt="Post Media" class="w-full h-full object-cover" />
          <div class="relative w-full h-full">
            <img :src="mediaUrls[4]" alt="Post Media" class="w-full h-full object-cover opacity-70" />
            <div v-if="mediaUrls.length > 5" class="absolute inset-0 bg-black/60 flex items-center justify-center text-white font-bold text-lg">
              +{{ mediaUrls.length - 4 }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Preview de Link Externo (se houver e não houver mídias carregadas) -->
    <a v-else-if="linkPreview" :href="linkPreview.url" target="_blank" class="link-preview-card block border-y border-zinc-200 dark:border-zinc-800 bg-zinc-50 dark:bg-zinc-950 hover:bg-zinc-100 dark:hover:bg-zinc-900 transition-colors">
      <img v-if="linkPreview.image" :src="linkPreview.image" alt="Thumbnail" class="w-full h-64 object-cover" />
      <div class="p-3">
        <span class="text-xs text-zinc-500 uppercase tracking-wider">{{ linkPreview.domain }}</span>
        <h4 class="text-sm font-semibold mt-1 text-zinc-900 dark:text-zinc-100 line-clamp-1">{{ linkPreview.title }}</h4>
        <p class="text-xs text-zinc-400 mt-1 line-clamp-2">{{ linkPreview.description }}</p>
      </div>
    </a>

    <!-- Barra de Ações (Curtir, Comentar, Compartilhar) -->
    <div class="flex items-center justify-between border-t border-zinc-100 dark:border-zinc-800 mx-3 py-1 mt-2 text-xs text-zinc-500 dark:text-zinc-400">
      <button @click="toggleLike" class="flex-1 flex justify-center items-center gap-1.5 py-2 hover:bg-zinc-50 dark:hover:bg-zinc-800 rounded transition-colors font-medium" :class="{ 'text-blue-600 dark:text-blue-400': isLiked }">
        <MaxIcon :icon="isLiked ? 'mdi:thumb-up' : 'mdi:thumb-up-outline'" size="1.1rem" />
        <span>Curtir</span>
      </button>
      
      <button class="flex-1 flex justify-center items-center gap-1.5 py-2 hover:bg-zinc-50 dark:hover:bg-zinc-800 rounded transition-colors font-medium">
        <MaxIcon icon="mdi:comment-outline" size="1.1rem" />
        <span>Comentar</span>
      </button>
      
      <button class="flex-1 flex justify-center items-center gap-1.5 py-2 hover:bg-zinc-50 dark:hover:bg-zinc-800 rounded transition-colors font-medium">
        <MaxIcon icon="mdi:share-outline" size="1.1rem" />
        <span>Compartilhar</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useTimeAgo } from '@maxvue/max-use'; // Importação do composable do ecossistema local

// Interfaces para os dados do componente
interface LinkPreview {
  url: string;
  title: string;
  description: string;
  domain: string;
  image?: string;
}

// Props tipadas com TypeScript
const props = defineProps<{
  pageName?: string;
  pageAvatar?: string;
  text?: string;
  mediaUrls?: string[];
  linkPreview?: LinkPreview;
  publishDate?: Date | string;
}>();

// Estado reativo interno
const isLiked = ref<boolean>(false);
const showFullText = ref<boolean>(false);

// Formatador de data usando composable local
const formattedTime = computed<string>(() => {
  if (!props.publishDate) return 'Agora mesmo';
  return useTimeAgo(new Date(props.publishDate)).value;
});

// Lógica de truncamento de texto longo
const hasMoreText = computed<boolean>(() => {
  return (props.text || '').length > 300;
});

const displayedText = computed<string>(() => {
  const textStr = props.text || '';
  if (!hasMoreText.value || showFullText.value) return textStr;
  return textStr.slice(0, 300) + '...';
});

// Ações do usuário
const toggleLike = (): void => {
  isLiked.value = !isLiked.value;
};
</script>

<style scoped lang="scss">
.facebook-preview-card {
  font-family: SFProText-Regular, Helvetica, Arial, sans-serif;
  
  img {
    user-select: none;
  }
}
</style>
```
