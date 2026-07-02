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
- Use `MaxButton` para os botões de ação e `MaxTitle`/`MaxText` (ou equivalentes do `MaxComponentsUi`) para títulos e textos do card, em vez de tags HTML nativas (`<button>`, `<h3>`, `<h4>`).
- Use `useTimeAgo` da biblioteca `MaxUse` para calcular tempos relativos das publicações. Instancie o composable **uma única vez** no `setup` (passando um `ref` reativo com a data), nunca dentro de um `computed` — `useTimeAgo` cria um efeito interno e não deve ser recriado a cada recálculo.
- Alinhe a tipografia e o estilo usando UnoCSS no modo **attributify** (`presetMaxUno`): utilitários como atributos (`flex items-center gap-2`), não em `class="..."`. Não use classes no estilo Tailwind (`bg-white`, `dark:bg-zinc-900`, etc.).

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** use a Options API. Sempre use `<script setup lang="ts">`.
- **NÃO** defina cores de tema estáticas diretamente no código ("hardcoded"). Use os tokens/utilitários de tema do `presetMaxUno` (UnoCSS attributify) com suporte nativo a modo claro e escuro. **NÃO** use classes no estilo Tailwind (`bg-white`, `dark:bg-zinc-900`, `text-blue-600`, etc.).
- **NÃO** quebre os atributos do template em várias linhas. Mantenha-os em uma única linha.
- Todos os comentários de código nos arquivos Vue devem ser escritos em **Português do Brasil (pt-BR)**.

---

## Exemplos

### FacebookPostPreview.vue
Aqui está um exemplo de alta fidelidade de um componente de visualização do Facebook usando Composition API, TypeScript e as bibliotecas locais:

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
      <MaxText>
        <span>{{ displayedText }}</span>
        <MaxButton v-if="hasMoreText && !showFullText" variant="text" text-primary font-semibold ml-1 @click="showFullText = true">Ver mais</MaxButton>
      </MaxText>
    </div>

    <!-- Mídia (Grade de Imagens / Collage) -->
    <div v-if="mediaUrls && mediaUrls.length > 0" class="media-collage" border="y base" bg-muted overflow-hidden>
      <!-- Exibição de 1 Imagem -->
      <div v-if="mediaUrls.length === 1" w-full flex justify-center max-h="450px">
        <img :src="mediaUrls[0]" alt="Post Media" w-full object-cover max-h="450px" />
      </div>

      <!-- Exibição de 2 Imagens -->
      <div v-else-if="mediaUrls.length === 2" grid grid-cols-2 gap-1 h="300px">
        <img v-for="(img, idx) in mediaUrls" :key="idx" :src="img" alt="Post Media" w-full h-full object-cover />
      </div>

      <!-- Exibição de 3 Imagens -->
      <div v-else-if="mediaUrls.length === 3" grid grid-cols-2 gap-1 h="320px">
        <img :src="mediaUrls[0]" alt="Post Media" w-full h-full object-cover row-span-2 />
        <div grid grid-rows-2 gap-1 h-full>
          <img :src="mediaUrls[1]" alt="Post Media" w-full h-full object-cover />
          <img :src="mediaUrls[2]" alt="Post Media" w-full h-full object-cover />
        </div>
      </div>

      <!-- Exibição de 4 Imagens -->
      <div v-else-if="mediaUrls.length === 4" grid grid-cols-2 gap-1 h="340px">
        <img :src="mediaUrls[0]" alt="Post Media" w-full h-full object-cover />
        <div grid grid-cols-3 gap-1 col-span-2 h="120px" mt-1>
          <img v-for="idx in [1, 2, 3]" :key="idx" :src="mediaUrls[idx]" alt="Post Media" w-full h-full object-cover />
        </div>
      </div>

      <!-- Exibição de 5 ou mais Imagens -->
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

    <!-- Preview de Link Externo (se houver e não houver mídias carregadas) -->
    <a v-else-if="linkPreview" :href="linkPreview.url" target="_blank" class="link-preview-card" block border="y base" bg-muted transition-colors>
      <img v-if="linkPreview.image" :src="linkPreview.image" alt="Thumbnail" w-full h-64 object-cover />
      <div p-3>
        <span text-xs text-muted uppercase tracking-wider>{{ linkPreview.domain }}</span>
        <MaxTitle :level="4" text-sm font-semibold mt-1 text-default line-clamp-1>{{ linkPreview.title }}</MaxTitle>
        <MaxText text-xs text-muted mt-1 line-clamp-2>{{ linkPreview.description }}</MaxText>
      </div>
    </a>

    <!-- Barra de Ações (Curtir, Comentar, Compartilhar) -->
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

// Formatador de data usando composable local.
// useTimeAgo é instanciado UMA única vez no setup com um ref reativo;
// nunca dentro de um computed, pois cria um efeito interno.
const publishRef = computed<Date>(() => new Date(props.publishDate ?? Date.now()));
const timeAgo = useTimeAgo(publishRef);
const formattedTime = computed<string>(() => {
  if (!props.publishDate) return 'Agora mesmo';
  return timeAgo.value;
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
