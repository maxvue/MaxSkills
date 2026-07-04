---
name: vue-social-post-preview-simulator-best-practices
description: Use when designing, building, styling, or debugging Vue 3 components, views, or composables for social media post/preview simulators in the SocialMediaApp/EngeApp front-end. Covers feed/timeline cards (Facebook, Threads, Instagram feed grid, Google Business Profile) and vertical 9:16 video/story previews (Instagram Stories, Instagram Reels, TikTok, YouTube Shorts). Triggers on components like FacebookPostPreview, ThreadsPostPreview, InstagramGridSimulator, GoogleBusinessPostPreview, ReelsSimulator, TikTokVideoPreview, YouTubeShortsPreview, StoriesSimulator; image-grid collages, link preview cards, character-limit validators (500 Threads / 1500 GBP), CTA button mappers, 9:16 video player wrappers, native UI overlays (action sidebars, like/comment/share/save), safe-zone overlay helpers, story progress bars and tap navigation, drag-and-drop feed reordering, and aspect-ratio validation.
---

# Boas Práticas para Simuladores de Pré-visualização de Posts em Redes Sociais (Vue)

## Objetivo
Padronizar a implementação de componentes de simulação/pré-visualização (preview) de posts de redes sociais no front-end (SocialMediaApp/EngeApp), em alta fidelidade e reatividade, com Vue 3 (Composition API), TypeScript, UnoCSS (modo **attributify**, `presetMaxUno`) e as bibliotecas locais `@maxvue/max-components-ui` (MaxComponentsUi), `@maxvue/max-use` (MaxUse) e `@maxvue/max-pinia` (MaxPinia).

Os simuladores se dividem em duas **variantes de formato**:
- **(A) Card de feed/timeline:** Facebook, Threads, Instagram (grade de feed), Google Business Profile.
- **(B) Vídeo/story vertical 9:16:** Instagram Stories, Instagram Reels, TikTok, YouTube Shorts.

Stack-alvo: Laravel 13 (PHP) + Vue Router (SPA pura) + Vite. SEM Inertia, SEM Tailwind. Realtime via **Laravel Reverb** com `@laravel/echo-vue` (`import Echo`/`useEcho`); persistência em MySQL exposta por `/api/...`.

## Instruções Gerais (todas as variantes)

### 1. Estrutura e Configuração do Componente (SFC)
- Use sempre Single-File Components na ordem **obrigatória**: `<template>` → `<script setup lang="ts">` → `<style scoped lang="scss">`.
- Defina interfaces TypeScript **estritas** para os dados do post, anexos de mídia, previews de link, CTAs, metadados de oferta/evento e fatias de encadeamento.
- Mantenha todos os atributos de tags/componentes em **uma única linha** no `<template>` (`<Componente param1="..." param2="..." />`). NÃO quebre atributos em múltiplas linhas.
- Comentários de código (script/style/template) estritamente em **Português do Brasil (pt-BR)**.

### 2. Integração com Bibliotecas Locais (MaxComponentsUi / MaxUse)
- Use componentes do MaxComponentsUi no lugar de tags nativas: `MaxButton`/`MaxIconButton` (em vez de `<button>`), `MaxIcon` (ícones), `MaxTitle1`/`MaxTitle2` (títulos, via props `:h1`/`:h2` — não existe um `MaxTitle` genérico com `:level`, nem `MaxText`; para texto simples use `<span>`/`<p>` com tokens de tema), `MaxUserAvatar` (avatares), `MaxModal`, `MaxGrid` quando aplicável (não existe um `MaxCard` genérico — use `<div>` + SCSS).
- Componentes do MaxComponentsUi são auto-registrados via `unplugin-vue-components` — **sem import manual** no template.
- `ref`, `computed`, `watch` etc. são auto-importados via `unplugin-auto-import` — **sem import manual**.
- `useTimeAgo` (e demais composables do `@maxvue/max-use`): instancie o composable **uma única vez** no `setup`, passando um `ref`/`computed` reativo com a data. **Nunca** instancie dentro de um `computed` — `useTimeAgo` cria um efeito interno e seria recriado a cada recálculo (vazamento/efeitos duplicados).

### 3. Gerenciamento de Estado — MaxPinia (CRÍTICO)
- **TODO GET de dados de página** (peça de conteúdo, lista de posts agendados, dados do canal/cliente, stories) DEVE passar por uma store `@maxvue/max-pinia`. NÃO faça requisições `axios`/`fetch` manuais.
- As stores resolvem rotas como **caminhos string** via helpers `apiGetRoute`/`apiPostRoute` do `@maxvue/max-use`, que retornam `/api/...`. NÃO existe `route()`/Ziggy.
- **Salvamento automático:** ao mutar o estado reativo da store (ex.: reordenar `store.posts`, editar a peça de conteúdo), o MaxPinia dispara o **auto-save (debounced)** para `/api/...`. NÃO chame endpoints de salvamento manualmente.
- Use stores dedicadas por domínio (ex.: `useCalendarEventStore` para agendamentos, `useSocialMediaThemesStore` para pautas).
- **Estado puramente local de UI** do simulador (índice de story ativo, play/pause, mudo, expansão de legenda, exibição de Safe Zones, `showFullText`, índice de carrossel) pode permanecer como `ref` local — não precisa de store. Estado de preview de vídeo pode ser sincronizado com a store apenas se múltiplas telas precisarem reagir.
- **Uploads temporários (rascunho):** para pré-visualizar mídia ainda não persistida, gere URLs locais com `URL.createObjectURL(file)` e atualize o estado reativo local antes de consolidar o agendamento na store.

### 4. Estilização (UnoCSS attributify + tokens de tema)
- Use UnoCSS no modo **attributify** com `presetMaxUno`: utilitários como atributos (`flex items-center gap-2`), não em `class="..."`.
- **NÃO** use classes no estilo Tailwind (`bg-white`, `dark:bg-zinc-900`, `text-blue-600`, `zinc-900`, `amber-500`, etc.). Use os tokens de tema (`bg-surface`, `text-default`, `text-muted`, `border-base`, `text-danger`, `text-warning`, `text-primary`, `text-success`), que já suportam claro/escuro nativamente.
- Cores de marca específicas de cada rede (ex.: azul Google `#1a73e8`, vermelho YouTube `#ff0000`, rosa TikTok `#ff0050`) são exceção aceitável quando a fidelidade visual exige a cor exata da rede — preferencialmente isoladas no bloco `<style scoped lang="scss">`, não como utilitários hardcoded espalhados.
- SCSS escopado (`scoped`) é obrigatório para layout complexo (containers 9:16, posicionamento absoluto de overlays, animações). NÃO escreva CSS puro global nem Tailwind.

---

## Variante A — Card de Feed / Timeline

### Especificações por rede

| Rede | Largura típica | Limite de texto | Elementos de UI distintos |
|------|----------------|-----------------|---------------------------|
| Facebook | `max-w-xl` | "Ver mais" > 300 chars | Cabeçalho com ícone de privacidade (`mdi:earth`); grade de mídia 1–5+; link card; barra Curtir/Comentar/Compartilhar |
| Threads | `max-w-xl` | 500 chars (divide em thread) | Linha conectora vertical entre posts; barra Curtir/Responder/Repostar/Compartilhar; carrossel |
| Instagram (grade de feed) | `935px` container | — | Grid 3×3 `aspect-ratio: 1/1`; indicadores de tipo (Reels/Carrossel); drag-and-drop |
| Google Business Profile | `650px` desktop / `420px` mobile | ~220 visível / 1500 total | Tipos NEWS/OFFER/EVENT; badges; cupom; CTA arredondado azul |

### Facebook — grade de mídia e link card
- Cabeçalho: avatar circular, nome da página, tempo relativo (`useTimeAgo`) e ícone de privacidade (`mdi:earth`).
- Texto com "Ver mais" se > 300 caracteres.
- **Grade de mídia (1 a 5+ imagens):**
  - 1: largura total com `max-h` limite.
  - 2: lado a lado.
  - 3: principal à esquerda + duas empilhadas à direita.
  - 4: principal superior + três menores abaixo (ou 2×2).
  - 5+: colagem com overlay `+X` na última imagem quando houver mais de 5.
- **Link card** (quando há URL e nenhuma mídia física): miniatura no topo, domínio canônico em caixa alta/cinza, título e descrição.
- **Barra de ações:** Curtir (`mdi:thumb-up-outline`/`mdi:thumb-up`), Comentar (`mdi:comment-outline`), Compartilhar (`mdi:share-outline`).

```vue
<template>
  <div class="facebook-preview-card" border="~ base rounded-lg" max-w-xl bg-surface text-default shadow-sm>
    <!-- Cabeçalho do Post -->
    <div flex items-center justify-between p-3 pb-2>
      <div flex items-center gap-2>
        <img :src="pageAvatar || '/default-avatar.png'" alt="Avatar" w-10 h-10 rounded-full object-cover />
        <div flex flex-col>
          <span font-semibold text-sm hover:underline cursor-pointer leading-tight>{{ pageName || 'Nome da Página' }}</span>
          <div flex items-center gap-1 text-xs text-muted mt-0.5>
            <span>{{ formattedTime }}</span>
            <span>•</span>
            <MaxIcon icon="mdi:earth" size="0.9rem" text-muted />
          </div>
        </div>
      </div>
      <MaxIconButton icon="mdi:dots-horizontal" size="1.2" />
    </div>

    <!-- Conteúdo do Texto -->
    <div px-3 pb-2 text-sm leading-relaxed whitespace-pre-wrap select-text>
      <span>
        <span>{{ displayedText }}</span>
        <MaxButton v-if="hasMoreText && !showFullText" variant="text" text-primary font-semibold ml-1 @click="showFullText = true">Ver mais</MaxButton>
      </span>
    </div>

    <!-- Mídia (Grade de Imagens / Collage) -->
    <div v-if="mediaUrls && mediaUrls.length > 0" class="media-collage" border="y base" bg-muted overflow-hidden>
      <!-- 1 Imagem -->
      <div v-if="mediaUrls.length === 1" w-full flex justify-center max-h="450px">
        <img :src="mediaUrls[0]" alt="Post Media" w-full object-cover max-h="450px" />
      </div>
      <!-- 2 Imagens -->
      <div v-else-if="mediaUrls.length === 2" grid grid-cols-2 gap-1 h="300px">
        <img v-for="(img, idx) in mediaUrls" :key="idx" :src="img" alt="Post Media" w-full h-full object-cover />
      </div>
      <!-- 3 Imagens -->
      <div v-else-if="mediaUrls.length === 3" grid grid-cols-2 gap-1 h="320px">
        <img :src="mediaUrls[0]" alt="Post Media" w-full h-full object-cover row-span-2 />
        <div grid grid-rows-2 gap-1 h-full>
          <img :src="mediaUrls[1]" alt="Post Media" w-full h-full object-cover />
          <img :src="mediaUrls[2]" alt="Post Media" w-full h-full object-cover />
        </div>
      </div>
      <!-- 4 Imagens -->
      <div v-else-if="mediaUrls.length === 4" grid grid-cols-2 gap-1 h="340px">
        <img :src="mediaUrls[0]" alt="Post Media" w-full h-full object-cover />
        <div grid grid-cols-3 gap-1 col-span-2 h="120px" mt-1>
          <img v-for="idx in [1, 2, 3]" :key="idx" :src="mediaUrls[idx]" alt="Post Media" w-full h-full object-cover />
        </div>
      </div>
      <!-- 5 ou mais Imagens -->
      <div v-else grid grid-cols-6 gap-1 h="350px">
        <img :src="mediaUrls[0]" alt="Post Media" col-span-3 h-full object-cover />
        <img :src="mediaUrls[1]" alt="Post Media" col-span-3 h-full object-cover />
        <div col-span-6 grid grid-cols-3 gap-1 h="120px" mt-1>
          <img :src="mediaUrls[2]" alt="Post Media" w-full h-full object-cover />
          <img :src="mediaUrls[3]" alt="Post Media" w-full h-full object-cover />
          <div relative w-full h-full>
            <img :src="mediaUrls[4]" alt="Post Media" w-full h-full object-cover opacity-70 />
            <div v-if="mediaUrls.length > 5" absolute inset-0 bg="black/60" flex items-center justify-center text-white font-bold text-lg>
              +{{ mediaUrls.length - 4 }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Preview de Link Externo -->
    <a v-else-if="linkPreview" :href="linkPreview.url" target="_blank" class="link-preview-card" block border="y base" bg-muted transition-colors>
      <img v-if="linkPreview.image" :src="linkPreview.image" alt="Thumbnail" w-full h-64 object-cover />
      <div p-3>
        <span text-xs text-muted uppercase tracking-wider>{{ linkPreview.domain }}</span>
        <MaxTitle2 :h1="linkPreview.title" text-sm font-semibold mt-1 text-default line-clamp-1 />
        <p text-xs text-muted mt-1 line-clamp-2>{{ linkPreview.description }}</p>
      </div>
    </a>

    <!-- Barra de Ações -->
    <div flex items-center justify-between border="t base" mx-3 py-1 mt-2 text-xs text-muted>
      <MaxButton variant="text" flex-1 flex justify-center items-center gap-1.5 py-2 font-medium :class="{ 'text-primary': isLiked }" @click="toggleLike">
        <MaxIcon :icon="isLiked ? 'mdi:thumb-up' : 'mdi:thumb-up-outline'" size="1.1rem" />
        <span>Curtir</span>
      </MaxButton>
      <MaxButton variant="text" flex-1 flex justify-center items-center gap-1.5 py-2 font-medium>
        <MaxIcon icon="mdi:comment-outline" size="1.1rem" />
        <span>Comentar</span>
      </MaxButton>
      <MaxButton variant="text" flex-1 flex justify-center items-center gap-1.5 py-2 font-medium>
        <MaxIcon icon="mdi:share-outline" size="1.1rem" />
        <span>Compartilhar</span>
      </MaxButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTimeAgo } from '@maxvue/max-use';

interface LinkPreview {
  url: string;
  title: string;
  description: string;
  domain: string;
  image?: string;
}

const props = defineProps<{
  pageName?: string;
  pageAvatar?: string;
  text?: string;
  mediaUrls?: string[];
  linkPreview?: LinkPreview;
  publishDate?: Date | string;
}>();

const isLiked = ref<boolean>(false);
const showFullText = ref<boolean>(false);

// useTimeAgo instanciado UMA única vez no setup com um ref reativo; nunca dentro de um computed.
const publishRef = computed<Date>(() => new Date(props.publishDate ?? Date.now()));
const timeAgo = useTimeAgo(publishRef);
const formattedTime = computed<string>(() => {
  if (!props.publishDate) return 'Agora mesmo';
  return timeAgo.value;
});

const hasMoreText = computed<boolean>(() => (props.text || '').length > 300);
const displayedText = computed<string>(() => {
  const textStr = props.text || '';
  if (!hasMoreText.value || showFullText.value) return textStr;
  return textStr.slice(0, 300) + '...';
});

const toggleLike = (): void => { isLiked.value = !isLiked.value; };
</script>

<style scoped lang="scss">
.facebook-preview-card {
  font-family: SFProText-Regular, Helvetica, Arial, sans-serif;
  img { user-select: none; }
}
</style>
```

### Threads — limite de 500 chars e divisão em encadeamento
- Layout: avatar à esquerda; nome + conteúdo à direita. **Linha conectora vertical** entre posts encadeados.
- Barra de ações: Curtir (`mdi:heart-outline`), Responder (`mdi:comment-outline`), Repostar (`mdi:repeat`), Compartilhar (`mdi:send-outline`).
- **Limite de 500 caracteres:** contagem em tempo real com indicador que muda de cor (`text-muted` → `text-warning` > 450 → `text-danger` > 500). Se exceder 500, divida automaticamente nos limites de palavra e exiba como sequência de posts conectados.
- Mídia: imagem/vídeo único arredondado (`rounded-xl`), carrossel com paginador, ou link card. Mantenha os utilitários em attributify (o exemplo abaixo usa tokens de tema, não paleta crua).

```vue
<template>
  <div class="threads-preview-container" flex flex-col gap-4 p-4 border="~ base rounded-2xl" max-w-xl bg-surface text-default>
    <div v-for="(post, index) in threadPosts" :key="index" class="thread-item" flex gap-3 relative>
      <!-- Linha conectora vertical para posts encadeados -->
      <div v-if="threadPosts.length > 1 && index < threadPosts.length - 1" absolute left-6 top-12 bottom-0 w-0.5 bg-muted></div>

      <!-- Avatar -->
      <div flex flex-col items-center>
        <img :src="avatarUrl || '/default-avatar.png'" alt="Avatar" w-12 h-12 rounded-full object-cover />
      </div>

      <!-- Conteúdo do Post -->
      <div flex-1 flex flex-col gap-1 pb-4>
        <div flex items-center justify-between>
          <span font-semibold text-sm hover:underline cursor-pointer>{{ username || 'usuario_threads' }}</span>
          <div flex items-center gap-2 text-xs text-muted>
            <span>{{ formattedTime }}</span>
            <MaxIcon icon="mdi:dots-horizontal" cursor-pointer />
          </div>
        </div>

        <p text-sm leading-relaxed whitespace-pre-wrap select-text>{{ post.text }}</p>

        <!-- Preview de Mídia -->
        <div v-if="post.media && post.media.length > 0" class="media-container" mt-2 rounded-xl overflow-hidden border="~ base" max-h-80 bg-muted flex justify-center items-center>
          <div v-if="post.media.length > 1" relative w-full>
            <img :src="post.media[activeMediaIndex]" alt="Preview" w-full h-80 object-cover />
            <span absolute top-2 right-2 bg="black/60" text-white text-xs px-2 py-1 rounded-full>{{ activeMediaIndex + 1 }}/{{ post.media.length }}</span>
          </div>
          <img v-else :src="post.media[0]" alt="Preview" w-full max-h-80 object-cover />
        </div>

        <!-- Preview de Link -->
        <a v-if="post.linkPreview && (!post.media || post.media.length === 0)" :href="post.linkPreview.url" target="_blank" mt-2 flex flex-col rounded-xl overflow-hidden border="~ base" hover:bg-muted transition-colors>
          <img v-if="post.linkPreview.image" :src="post.linkPreview.image" alt="Thumbnail" w-full h-40 object-cover />
          <div p-3 flex flex-col gap-1>
            <span text-xs text-muted uppercase tracking-wider>{{ post.linkPreview.domain }}</span>
            <span text-sm font-semibold line-clamp-1>{{ post.linkPreview.title }}</span>
            <span text-xs text-muted line-clamp-2>{{ post.linkPreview.description }}</span>
          </div>
        </a>

        <!-- Barra de Ações -->
        <div flex gap-4 mt-3 text-muted>
          <MaxButton variant="text" hover:text-danger transition-colors><MaxIcon icon="mdi:heart-outline" size="1.1" /></MaxButton>
          <MaxButton variant="text" hover:text-primary transition-colors><MaxIcon icon="mdi:comment-outline" size="1.1" /></MaxButton>
          <MaxButton variant="text" hover:text-success transition-colors><MaxIcon icon="mdi:repeat" size="1.1" /></MaxButton>
          <MaxButton variant="text" hover:text-primary transition-colors><MaxIcon icon="mdi:send-outline" size="1.1" /></MaxButton>
        </div>
      </div>
    </div>

    <!-- Validador visual do limite de caracteres -->
    <div flex items-center justify-between border="t base" pt-3 mt-1 text-xs>
      <span :class="textLengthClass">{{ rawText.length }}/500 caracteres</span>
      <span v-if="rawText.length > 500" text-danger font-medium>O texto será dividido em {{ threadPosts.length }} posts.</span>
    </div>
  </div>
</template>

<script setup lang="ts">
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

const props = defineProps<{
  rawText: string;
  mediaUrls?: string[];
  linkPreview?: LinkPreview;
  username?: string;
  avatarUrl?: string;
  publishDate?: Date | string;
}>();

const activeMediaIndex = ref<number>(0);

// Tempo relativo via composable (instanciado uma vez no setup).
const publishRef = computed<Date>(() => new Date(props.publishDate ?? Date.now()));
const timeAgo = useTimeAgo(publishRef);
const formattedTime = computed<string>(() => props.publishDate ? timeAgo.value : 'Agora mesmo');

// Cor dinâmica conforme a contagem de caracteres (tokens de tema).
const textLengthClass = computed<string>(() => {
  if (props.rawText.length > 500) return 'text-danger font-bold';
  if (props.rawText.length > 450) return 'text-warning font-semibold';
  return 'text-muted';
});

// Divide o texto em fatias caso ultrapasse o limite do Threads (500 caracteres).
const threadPosts = computed<PostSlice[]>(() => {
  const text = props.rawText || '';
  if (text.length <= 500) {
    return [{ text, media: props.mediaUrls, linkPreview: props.linkPreview }];
  }

  const slices: PostSlice[] = [];
  let remainingText = text;

  while (remainingText.length > 0) {
    let sliceLength = 500;
    if (remainingText.length > 500) {
      const subStr = remainingText.slice(0, 500);
      const lastSpace = Math.max(subStr.lastIndexOf(' '), subStr.lastIndexOf('\n'));
      if (lastSpace > 400) sliceLength = lastSpace;
    }
    const currentText = remainingText.slice(0, sliceLength).trim();
    slices.push({ text: currentText });
    remainingText = remainingText.slice(sliceLength).trim();
  }

  // Mídias e links associados apenas ao post inicial do encadeamento.
  if (slices.length > 0) {
    slices[0].media = props.mediaUrls;
    slices[0].linkPreview = props.linkPreview;
  }
  return slices;
});

import { useTimeAgo } from '@maxvue/max-use';
</script>

<style scoped lang="scss">
.threads-preview-container {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  .thread-item { transition: all 0.2s ease-in-out; }
}
</style>
```

### Instagram — grade de feed 3×3 com drag-and-drop
- Container `935px`; grid `repeat(3, 1fr)`; cards quadrados (`aspect-ratio: 1/1`, `object-fit: cover`).
- Indicadores de tipo no canto superior direito (`position: absolute`): Carrossel (`iconoir:multiple-pages`), Reels/Vídeo (`iconoir:play`), Imagem (sem overlay).
- **Drag-and-drop** com `vue-draggable-next` (ver skill `vue-draggable-next-best-practices`): importe e registre localmente o componente sob o nome `draggable` (`import { VueDraggableNext as draggable } from 'vue-draggable-next'`); use `<draggable v-model="posts" item-key="id" ...>` em uma linha, slot `#item` com `{ element }`.
- **Persistência:** capture `@change` e reflita a nova ordem no estado da store `@maxvue/max-pinia`. NÃO faça `axios` manual — mutar `store.posts` dispara o auto-save (debounced) para `/api/...`.

```vue
<template>
  <div class="instagram-simulator-container">
    <div class="profile-header-preview" flex items-center mb-20>
      <MaxUserAvatar :imageUrl="props.clientAvatar" :name="props.clientName" />
      <div class="profile-info-meta" ml-15>
        <span class="username" text-lg font-bold>{{ props.clientUsername }}</span>
        <div class="stats-counter" flex gap-15 mt-5>
          <span><strong>{{ posts.length }}</strong> publicações</span>
          <span><strong>12.5k</strong> seguidores</span>
        </div>
      </div>
    </div>
    <draggable v-model="posts" item-key="id" ghost-class="grid-ghost" drag-class="grid-dragging" @change="onGridReorder" class="instagram-grid">
      <template #item="{ element }">
        <div class="post-grid-card">
          <img :src="element.media_url || '/placeholder.png'" class="post-media" alt="Instagram Post" />
          <div class="post-type-indicator" v-if="element.media_type">
            <MaxIcon :icon="getIndicatorIcon(element.media_type)" size="1.2" color="#ffffff" />
          </div>
          <div class="hover-overlay" flex items-center justify-center>
            <div class="overlay-stat" flex items-center mr-10>
              <MaxIcon icon="iconoir:heart" size="1.1" mr-5 /><span>{{ element.likes ?? 0 }}</span>
            </div>
            <div class="overlay-stat" flex items-center>
              <MaxIcon icon="iconoir:chat-bubble" size="1.1" mr-5 /><span>{{ element.comments_count ?? 0 }}</span>
            </div>
          </div>
        </div>
      </template>
    </draggable>
    <div class="loader-state" flex items-center justify-center p-10 v-if="isSaving">
      <MaxIcon icon="loading" size="1.5" mr-10 /><span>Sincronizando feed...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
// Registro local: renomeia o componente da lib para <draggable> no template deste componente.
import { VueDraggableNext as draggable } from 'vue-draggable-next';

interface InstagramSimulatedPost {
  id: string;
  media_url: string;
  media_type: 'image' | 'video' | 'carousel';
  likes?: number;
  comments_count?: number;
  scheduled_at: string;
}

const props = defineProps<{
  clientName: string;
  clientUsername: string;
  clientAvatar?: string;
  initialPosts: InstagramSimulatedPost[];
}>();

const emit = defineEmits<{ reordered: [posts: InstagramSimulatedPost[]] }>();

const posts = ref<InstagramSimulatedPost[]>([...props.initialPosts]);
// Reflete o estado de salvamento exposto pela store @maxvue/max-pinia (auto-save).
const isSaving = ref<boolean>(false);

watch(() => props.initialPosts, (newVal) => { posts.value = [...newVal]; }, { deep: true });

const getIndicatorIcon = (type: 'image' | 'video' | 'carousel'): string => {
  if (type === 'video') return 'iconoir:play';
  if (type === 'carousel') return 'iconoir:multiple-pages';
  return '';
};

// A persistência é feita ao mutar o estado da store @maxvue/max-pinia (auto-save debounced) — sem axios manual.
const onGridReorder = () => { emit('reordered', posts.value); };
</script>

<style lang="scss" scoped>
.instagram-simulator-container {
  max-width: 935px;
  margin: 0 auto;
  padding: 20px;
  background-color: var(--background-0);

  .profile-header-preview { border-bottom: 1px solid var(--surface-border); padding-bottom: 20px; }

  .instagram-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 28px; /* Espaçamento padrão do feed desktop do Instagram */
    @media (max-width: 768px) { gap: 3px; }
  }

  .post-grid-card {
    position: relative;
    aspect-ratio: 1 / 1;
    width: 100%;
    overflow: hidden;
    background-color: var(--surface-card);
    cursor: grab;
    &:active { cursor: grabbing; }

    .post-media { width: 100%; height: 100%; object-fit: cover; }
    .post-type-indicator { position: absolute; top: 10px; right: 10px; z-index: 5; filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4)); }
    .hover-overlay { position: absolute; inset: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.3); color: #fff; opacity: 0; transition: opacity 0.2s ease; pointer-events: none; z-index: 4; }
    &:hover .hover-overlay { opacity: 1; }
    .overlay-stat { font-size: 1rem; font-weight: 600; }
  }

  .grid-ghost { opacity: 0.4; border: 2px dashed var(--primary-color); }
  .grid-dragging { opacity: 0.9; transform: scale(1.02); box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15); }
}
</style>
```

> **Zona de segurança das imagens:** no grid 3×3, garanta que marcadores customizados (caixas de seleção, badges de rascunho) não ocultem os indicadores de tipo nem distorçam o formato.

### Google Business Profile — NEWS / OFFER / EVENT + CTA
- Suporte a três tipos: **Novidades** (texto até 1500 chars + mídia opcional), **Oferta** (título em destaque, validade, cupom com borda pontilhada e ação de cópia, link de Termos em `MaxModal`) e **Evento** (título + período com horas + badge de calendário).
- **Mapeador de CTA:** `BOOK`→Reservar, `ORDER_ONLINE`→Pedir on-line, `BUY`→Comprar, `LEARN_MORE`→Saiba mais, `SIGN_UP`→Cadastrar-se, `CALL_NOW`→Ligar agora (link `tel:`). Sem CTA selecionado: oculte o botão.
- Viewport alternável desktop (`650px`) / mobile (`420px`). Tipografia `Roboto, Arial, sans-serif`. Botão CTA azul Google (`#1a73e8` / hover `#1557b0`, `rounded-full`, branco semibold). Mídia 4:3 ou 16:9 com leve zoom no hover. Truncamento de texto ~220 chars visíveis com "Mais".

```vue
<template>
  <div class="google-preview-container" flex="~ col" gap-4 p-4 bg-muted rounded-xl border="~ base">
    <!-- Alternador Desktop / Mobile -->
    <div flex="~" items-center justify-between border-b="~ base" pb-3>
      <span text-xs text-muted font-semibold uppercase tracking-wider>Visualização Prévia</span>
      <div flex="~" bg-surface p-0.5 rounded-lg>
        <MaxButton :variant="!isMobile ? 'outlined' : 'text'" size="sm" icon="mdi:desktop-mac" @click="isMobile = false">Desktop</MaxButton>
        <MaxButton :variant="isMobile ? 'outlined' : 'text'" size="sm" icon="mdi:cellphone" @click="isMobile = true">Mobile</MaxButton>
      </div>
    </div>

    <!-- Card de Post no Padrão do Google -->
    <div :max-w="isMobile ? '420px' : '650px'" class="gbp-post-card" w-full mx-auto bg-surface border="~ base" rounded-lg shadow-sm overflow-hidden text-default transition-all duration-300>
      <!-- Cabeçalho -->
      <div flex="~" items-center gap-3 p-4>
        <img :src="businessAvatar || '/default-business.png'" alt="Avatar" w-10 h-10 rounded-full border="~ base" object-cover />
        <div flex="~ col">
          <span font-medium text-sm text-default leading-tight>{{ businessName || 'Nome da Empresa' }}</span>
          <span text-xs text-muted mt-0.5>{{ formattedTime }}</span>
        </div>
      </div>

      <!-- Imagem de Destaque com badge -->
      <div v-if="imageUrl" class="media-container" relative aspect="4/3" w-full bg-muted overflow-hidden border-b="~ base">
        <img :src="imageUrl" alt="Post Media" w-full h-full object-cover transition-transform duration-300 hover:scale-105 />
        <span v-if="postType === 'OFFER'" absolute top-3 left-3 class="gbp-badge-offer" text-xs font-semibold px-2.5 py-1 rounded flex="~" items-center gap-1 shadow-sm>
          <MaxIcon icon="mdi:tag-outline" size="0.9rem" /><span>Oferta</span>
        </span>
        <span v-else-if="postType === 'EVENT'" absolute top-3 left-3 class="gbp-badge-event" text-xs font-semibold px-2.5 py-1 rounded flex="~" items-center gap-1 shadow-sm>
          <MaxIcon icon="mdi:calendar-star" size="0.9rem" /><span>Evento</span>
        </span>
      </div>

      <div p-4 flex="~ col" gap-3>
        <!-- Títulos Especiais -->
        <div v-if="postType === 'OFFER' && offerTitle" flex="~ col">
          <MaxTitle1 :h1="offerTitle" class="gbp-offer-title" font-bold leading-snug />
          <span text-xs text-muted font-medium mt-1 flex="~" items-center gap-1>
            <MaxIcon icon="mdi:clock-outline" size="0.8rem" /><span>Validade: {{ offerDates }}</span>
          </span>
        </div>
        <div v-else-if="postType === 'EVENT' && eventTitle" flex="~ col">
          <MaxTitle1 :h1="eventTitle" class="gbp-event-title" font-bold leading-snug />
          <span text-xs text-muted font-medium mt-1 flex="~" items-center gap-1>
            <MaxIcon icon="mdi:calendar-clock" size="0.8rem" /><span>Horário: {{ eventDates }}</span>
          </span>
        </div>

        <!-- Texto / Descrição -->
        <p v-if="description" text-sm text-default leading-relaxed whitespace-pre-line>
          {{ displayedDescription }}
          <MaxButton v-if="hasLongText && !showFullText" variant="link" size="sm" @click="showFullText = true">Mais</MaxButton>
        </p>

        <!-- Detalhes da Oferta -->
        <div v-if="postType === 'OFFER' && (couponCode || terms)" flex="~ col" gap-2 mt-1 p-3 bg-muted rounded-lg border="~ dashed base">
          <div v-if="couponCode" flex="~" items-center justify-between>
            <div flex="~" items-center gap-1.5 text-xs text-default>
              <MaxIcon icon="mdi:ticket-percent" text-primary size="1rem" />
              <span>Código: <code font-mono bg-surface px-1.5 py-0.5 rounded text-sm font-semibold select-all>{{ couponCode }}</code></span>
            </div>
            <MaxButton variant="link" size="sm" @click="simulateCopy">Copiar</MaxButton>
          </div>
          <MaxModal v-if="terms" title="Termos e Condições">
            <template #button>
              <MaxButton variant="link" size="sm">Ver termos e condições</MaxButton>
            </template>
            <p text-xs text-muted leading-relaxed>{{ terms }}</p>
          </MaxModal>
        </div>

        <!-- Botão de CTA -->
        <div v-if="ctaType && ctaLabel" flex="~" justify-end mt-2 pt-2 border-t="~ base">
          <a :href="ctaUrl" @click.prevent="handleCtaClick" class="google-cta-btn" text-xs font-semibold px-5 py-2.5 rounded-full transition-colors flex="~" items-center gap-1.5 shadow-sm>
            <MaxIcon v-if="ctaType === 'CALL_NOW'" icon="mdi:phone" size="0.9rem" /><span>{{ ctaLabel }}</span>
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTimeAgo } from '@maxvue/max-use';
import { Toast } from '@maxvue/max-components-ui';

type GbpPostType = 'NEWS' | 'OFFER' | 'EVENT';
type GbpCtaType = 'BOOK' | 'ORDER_ONLINE' | 'BUY' | 'LEARN_MORE' | 'SIGN_UP' | 'CALL_NOW';

interface Props {
  businessName?: string;
  businessAvatar?: string;
  postType?: GbpPostType;
  description?: string;
  imageUrl?: string;
  publishDate?: Date | string;
  offerTitle?: string;
  startDate?: string;
  endDate?: string;
  couponCode?: string;
  terms?: string;
  eventTitle?: string;
  ctaType?: GbpCtaType;
  ctaTargetUrl?: string;
}

const props = withDefaults(defineProps<Props>(), { postType: 'NEWS', description: '' });

const isMobile = ref<boolean>(false);
const showFullText = ref<boolean>(false);

// useTimeAgo instanciado uma vez, reagindo à fonte reativa.
const publishDateRef = computed<Date>(() => new Date(props.publishDate ?? Date.now()));
const timeAgo = useTimeAgo(publishDateRef);
const formattedTime = computed<string>(() => props.publishDate ? timeAgo.value : 'Agora mesmo');

// Limite do Google ~220 caracteres visíveis no snippet.
const hasLongText = computed<boolean>(() => props.description.length > 220);
const displayedDescription = computed<string>(() => {
  if (!hasLongText.value || showFullText.value) return props.description;
  return props.description.slice(0, 220) + '...';
});

const offerDates = computed<string>(() => {
  if (!props.startDate && !props.endDate) return 'Período não definido';
  const start = props.startDate ? new Date(props.startDate).toLocaleDateString('pt-BR') : '';
  const end = props.endDate ? new Date(props.endDate).toLocaleDateString('pt-BR') : 'Sem data de término';
  return start ? `${start} - ${end}` : end;
});

const eventDates = computed<string>(() => {
  if (!props.startDate && !props.endDate) return 'Data não definida';
  const options: Intl.DateTimeFormatOptions = { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' };
  const start = props.startDate ? new Date(props.startDate).toLocaleString('pt-BR', options) : '';
  const end = props.endDate ? new Date(props.endDate).toLocaleString('pt-BR', options) : 'Sem data de término';
  return start ? `${start} - ${end}` : end;
});

const ctaLabel = computed<string>(() => {
  if (!props.ctaType) return '';
  const labelMap: Record<GbpCtaType, string> = {
    BOOK: 'Reservar', ORDER_ONLINE: 'Pedir on-line', BUY: 'Comprar',
    LEARN_MORE: 'Saiba mais', SIGN_UP: 'Cadastrar-se', CALL_NOW: 'Ligar agora'
  };
  return labelMap[props.ctaType];
});

const ctaUrl = computed<string>(() => {
  if (props.ctaType === 'CALL_NOW') return 'tel:+5511999999999';
  return props.ctaTargetUrl || '#';
});

const simulateCopy = (): void => {
  Toast.show({ title: `[Simulador] Código do cupom "${props.couponCode}" copiado!`, severity: 'info' });
};

const handleCtaClick = (): void => {
  if (props.ctaType === 'CALL_NOW') Toast.show({ title: '[Simulador] Ação "Ligar agora" disparada.', severity: 'info' });
  else Toast.show({ title: `[Simulador] CTA "${ctaLabel.value}" redirecionando para: ${ctaUrl.value}`, severity: 'info' });
};
</script>

<style scoped lang="scss">
.gbp-post-card {
  font-family: Roboto, Arial, sans-serif;
  .media-container img { user-select: none; -webkit-user-drag: none; }
  .google-cta-btn { user-select: none; text-decoration: none; background-color: #1a73e8; color: #fff; &:hover { background-color: #1557b0; } }
  .gbp-offer-title { color: #1a73e8; }
  .gbp-event-title { color: #b06000; }
}
.gbp-badge-offer { background-color: #e8f0fe; color: #1a73e8; }
.gbp-badge-event { background-color: #fef7e0; color: #b06000; }
</style>
```

---

## Variante B — Vídeo / Story Vertical 9:16

### Especificações por rede

| Rede | `max-width` desktop | Safe zones (topo / direita / base) | UI distinta |
|------|---------------------|-------------------------------------|-------------|
| Instagram Reels | `400px` (711px alt.) | 12% / 18% / 30% | Avatar+Seguir, Curtir/Comentar/Compartilhar/Opções, áudio em vinil |
| Instagram Stories | 9:16 | barras de progresso segmentadas | Toque navega (esq. 25% / dir. 75%), hold-to-pause, widgets (enquete/pergunta/link/menção) |
| TikTok | `360px` (ou 400px) | 12% / 18% / 28% | Avatar+botão `+`, Curtir/Comentar/Salvar/Compartilhar, disco de música girando, marquee |
| YouTube Shorts | `360px` (ou 400px) | 10% / 18% / 33% | Inscrever-se (vermelho), Curtir/Não gostei/Comentar/Compartilhar/Remix, disco de áudio |

### Regras comuns 9:16
- Container com `aspect-ratio: 9 / 16`, fundo preto `#000` para letterboxing, `border-radius` e sombra. `object-fit: cover` no `<video>`.
- Limites máximos no desktop para emular celular (ver tabela).
- **Overlays nativos** com `position: absolute` sobre o vídeo: barra de ações vertical à direita (`MaxIconButton` + contadores simulados), bloco de perfil/legenda no canto inferior esquerdo, banner de música com marquee. Use `pointer-events: none` no container de overlay e `pointer-events: auto` nos elementos interativos.
- **Expansão de legenda:** trunque > 80 caracteres com botão "mais" reativo (`isExpanded`).
- **Play/Pause:** clique no `<video>` alterna `togglePlay`; exiba indicador central temporário (`showPlayOverlay`, ~500–600ms).
- Vídeo HTML5 com `muted`/`loop`/`autoplay` conforme a rede.

### Assistente Visual de Safe Zones (toggle `showSafeZones`)
Alerta criadores sobre "zonas mortas" onde a UI nativa cobre conteúdo. Quando ativo, sobreponha camadas semitransparentes vermelhas/tracejadas nas margens. Use os percentuais por rede da tabela acima (são padrões críticos — não os ignore).

```vue
<template>
  <div class="vertical-simulator">
    <!-- Container do dispositivo 9:16 -->
    <div class="device-container" :class="{ 'show-safe-zones': showSafeZones }">
      <!-- Player de vídeo nativo HTML5 -->
      <video ref="videoRef" :src="videoUrl" :muted="isMuted" class="video-player" loop @click="togglePlay" />

      <!-- Feedback central de play/pause -->
      <div v-if="showPlayOverlay" class="play-overlay">
        <MaxIconButton :icon="isPlaying ? 'mdi:play' : 'mdi:pause'" size="3" />
      </div>

      <!-- Guias visuais de Safe Zone (percentuais variam por rede) -->
      <div v-if="showSafeZones" class="safe-zone-overlay">
        <div class="safe-zone top-zone"><span>Área Restrita: Topo</span></div>
        <div class="safe-zone right-zone"><span>Área Restrita: Ações</span></div>
        <div class="safe-zone bottom-zone"><span>Área Restrita: Legenda</span></div>
      </div>

      <!-- UI Nativa (overlays) -->
      <div class="native-ui">
        <!-- Barra de ações lateral direita -->
        <div class="actions-sidebar">
          <!-- Bloco do perfil com botão de seguir (TikTok usa "+", Reels/Shorts variam) -->
          <div class="profile-container">
            <img :src="channelAvatarUrl" class="creator-avatar" alt="Avatar" />
            <MaxButton class="follow-btn" label="+" />
          </div>
          <div class="action-item">
            <MaxIconButton :icon="isLiked ? 'mdi:heart' : 'mdi:heart-outline'" :class="{ 'liked': isLiked }" @action="toggleLike" />
            <span>{{ isLiked ? '12.4K' : '12.3K' }}</span>
          </div>
          <div class="action-item">
            <MaxIconButton icon="mdi:comment-processing-outline" /><span>856</span>
          </div>
          <div class="action-item">
            <MaxIconButton :icon="isBookmarked ? 'mdi:bookmark' : 'mdi:bookmark-outline'" :class="{ 'bookmarked': isBookmarked }" @action="toggleBookmark" />
            <span>{{ isBookmarked ? '432' : '431' }}</span>
          </div>
          <div class="action-item"><MaxIconButton icon="mdi:share" /><span>192</span></div>
          <!-- Disco de música giratório (presente quando reproduzindo) -->
          <div class="music-disc-wrapper" :class="{ 'is-playing': isPlaying }">
            <img :src="channelAvatarUrl" alt="Música" class="music-disc" />
          </div>
        </div>

        <!-- Conteúdo inferior esquerdo: usuário + legenda + música -->
        <div class="content-overlay">
          <span class="user-handle">@{{ channelHandle }}</span>
          <div class="caption-wrapper">
            <p class="caption-text">
              {{ isExpanded ? captionText : truncatedCaption }}
              <span v-if="captionText.length > 80 && !isExpanded" class="more-btn" @click="isExpanded = true">mais</span>
            </p>
          </div>
          <div class="music-track-info">
            <MaxIcon icon="mdi:music" size="1rem" class="music-icon" />
            <div class="track-marquee-container">
              <span class="track-marquee">Som original - {{ channelHandle }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// `ref`/`computed` auto-importados; MaxIcon/MaxIconButton auto-registrados.
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
const isBookmarked = ref<boolean>(false);
const showSafeZones = ref<boolean>(false);
const isExpanded = ref<boolean>(false);
const showPlayOverlay = ref<boolean>(false);

// Trunca a legenda caso exceda o limite visual padrão (80 chars).
const truncatedCaption = computed<string>(() => {
  if (props.captionText.length <= 80) return props.captionText;
  return props.captionText.substring(0, 80) + '...';
});

// Alterna reprodução e dispara feedback visual.
const togglePlay = (): void => {
  if (!videoRef.value) return;
  if (videoRef.value.paused) { videoRef.value.play(); isPlaying.value = true; }
  else { videoRef.value.pause(); isPlaying.value = false; }
  triggerPlayOverlay();
};

const toggleLike = (): void => { isLiked.value = !isLiked.value; };
const toggleBookmark = (): void => { isBookmarked.value = !isBookmarked.value; };

const triggerPlayOverlay = (): void => {
  showPlayOverlay.value = true;
  setTimeout(() => { showPlayOverlay.value = false; }, 600);
};
</script>

<style scoped lang="scss">
.vertical-simulator {
  display: flex;
  justify-content: center;
  align-items: center;

  .device-container {
    position: relative;
    width: 100%;
    max-width: 360px; /* TikTok/Shorts; use 400px para Reels */
    aspect-ratio: 9 / 16;
    background-color: #000;
    overflow: hidden;
    border-radius: 16px;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.6);

    .video-player { width: 100%; height: 100%; object-fit: cover; }

    .play-overlay { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); pointer-events: none; z-index: 10; opacity: 0.8; }

    .safe-zone-overlay {
      position: absolute; inset: 0; pointer-events: none; z-index: 5;
      .safe-zone {
        position: absolute; background-color: rgba(239, 68, 68, 0.25);
        border: 1px dashed rgba(239, 68, 68, 0.6); color: #fff; font-size: 11px;
        display: flex; align-items: center; justify-content: center;
        font-weight: 600; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8);
      }
      /* Percentuais variam por rede — Reels 12/18/30, TikTok 12/18/28, Shorts 10/18/33 */
      .top-zone { top: 0; left: 0; width: 100%; height: 12%; }
      .right-zone { top: 12%; right: 0; width: 18%; height: 60%; }
      .bottom-zone { bottom: 0; left: 0; width: 100%; height: 28%; }
    }

    .native-ui {
      position: absolute; inset: 0; pointer-events: none;
      display: flex; flex-direction: column; justify-content: flex-end;
      padding: 16px; z-index: 4;
      background: linear-gradient(to top, rgba(0, 0, 0, 0.6) 0%, rgba(0, 0, 0, 0) 30%);

      .actions-sidebar {
        position: absolute; right: 8px; bottom: 30px;
        display: flex; flex-direction: column; align-items: center; gap: 18px; pointer-events: auto;

        .profile-container {
          position: relative; width: 44px; height: 44px; margin-bottom: 8px;
          .creator-avatar { width: 100%; height: 100%; border-radius: 50%; border: 2px solid #fff; object-fit: cover; }
          .follow-btn {
            position: absolute; bottom: -5px; left: 50%; transform: translateX(-50%);
            background-color: #ff0050; color: #fff; border: none; width: 18px; height: 18px;
            border-radius: 50%; font-size: 14px; font-weight: bold;
            display: flex; align-items: center; justify-content: center; cursor: pointer;
          }
        }

        .action-item {
          display: flex; flex-direction: column; align-items: center;
          color: #fff; font-size: 11px; text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8); gap: 2px;
          .liked { color: #ff0050; }
          .bookmarked { color: #facd3b; }
        }

        .music-disc-wrapper {
          width: 38px; height: 38px; border-radius: 50%; background-color: #111;
          display: flex; align-items: center; justify-content: center; border: 4px solid #222;
          .music-disc { width: 22px; height: 22px; border-radius: 50%; object-fit: cover; }
          &.is-playing { animation: spin-disc 4s linear infinite; }
        }
      }

      .content-overlay {
        max-width: 76%; color: #fff; display: flex; flex-direction: column; gap: 6px;
        pointer-events: auto; text-shadow: 0 1px 2px rgba(0, 0, 0, 0.6);
        .user-handle { font-weight: 700; font-size: 14px; }
        .caption-wrapper .caption-text {
          font-size: 13px; line-height: 1.4;
          .more-btn { font-weight: bold; cursor: pointer; margin-left: 4px; color: #ccc; text-decoration: underline; }
        }
        .music-track-info {
          display: flex; align-items: center; gap: 8px; font-size: 12px;
          .music-icon { flex-shrink: 0; }
          .track-marquee-container {
            overflow: hidden; white-space: nowrap; width: 140px;
            .track-marquee { display: inline-block; padding-left: 100%; animation: marquee-scroll 10s linear infinite; }
          }
        }
      }
    }
  }
}

@keyframes spin-disc { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes marquee-scroll { 0% { transform: translate3d(0, 0, 0); } 100% { transform: translate3d(-100%, 0, 0); } }
</style>
```

> **Particularidades:** YouTube Shorts substitui o botão de seguir por **Inscrever-se** vermelho (`#ff0000`, hover `#cc0000`, `border-radius: 18px`), adiciona **Não gostei** (`mdi:thumb-down-outline`) e **Remix** (`mdi:repeat`), e usa Curtir como joinha (`mdi:thumb-up-outline`/`mdi:thumb-up`); banner de música em pílula com fundo `rgba(255,255,255,0.15)`. Instagram Reels usa avião de papel (`mdi:share-variant-outline`) e gradiente mais alto. TikTok usa o disco de álbum no canto e o botão `+` rosa.

### Instagram Stories — barras de progresso, navegação por toque e widgets
- **Barras de progresso segmentadas** no topo (uma por story); controle de largura/animação por variáveis CSS com base no story ativo.
- **Temporizadores** (5s imagens, 15s vídeos) via composables do `@maxvue/max-use`.
- **Navegação por toque:** áreas invisíveis sobrepostas — esquerda (25%) volta/reinicia, direita (75%) avança.
- **Hold-to-pause:** `pointerdown` pausa o timer; `pointerup`/`pointerleave` retoma.
- **Widgets/stickers** com posicionamento absoluto (coordenadas em %): Link (cápsula com ícone), Enquete (pergunta + duas opções), Caixa de Pergunta (input simulado), Menções/Hashtags (`@`/`#`).
- **Validação de proporção 9:16** antes de renderizar (avise se desviar; use componentes de notificação locais, nunca `alert()`):

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

---

## Restrições (todas as variantes)
- **NÃO** use Options API. Sempre `<script setup lang="ts">`.
- **NÃO** use Tailwind CSS nem a paleta crua estilo Tailwind (`bg-white`, `dark:bg-zinc-900`, `zinc-900`, `amber-500`, `red-500`). Use UnoCSS attributify com tokens de tema do `presetMaxUno` (claro/escuro nativos). SCSS escopado é obrigatório para layout/animações. Cores de marca da rede são exceção quando a fidelidade exige.
- **NÃO** quebre atributos do template em várias linhas — mantenha-os em uma única linha.
- **NÃO** faça GET/POST manual (`axios`/`fetch`) para dados de página nem salvamentos manuais — use stores `@maxvue/max-pinia` (auto-save debounced) com rotas string `/api/...`. NÃO use `route()`/Ziggy.
- **NÃO** manipule o DOM por seletores (`document.querySelector`) — use `ref` de template.
- **NÃO** use `alert()` nativo — use o helper `Toast` do `@maxvue/max-components-ui` (ex.: `Toast.show({ title, severity })`).
- **NÃO** ignore as Safe Zones (9:16) nem os limites de caracteres (500 Threads, ~220/1500 GBP, 300 Facebook, 80 legenda vertical).
- Todos os comentários de código em **pt-BR**.

## Skills relacionadas
- `vue-draggable-next-best-practices` — drag-and-drop na grade do Instagram.
- Stores e cache: padrões `@maxvue/max-pinia` (GET + auto-save).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
