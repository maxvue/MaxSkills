---
name: vue-instagram-feed-grid-simulator-best-practices
description: Use when building, modifying, styling, or debugging the Instagram profile feed grid simulator UI in Vue 3, managing the 3x3 post grid preview, handling media aspect ratio containers, implementing drag-and-drop reordering for scheduled posts, or integrating with @maxvue/max-pinia stores for calendar events.
---

# Boas Práticas para o Simulador de Grade de Feed do Instagram em Vue

## Objetivo
Padronizar a implementação da interface do usuário para o simulador de grade de feed de perfil do Instagram em Vue 3 usando Composition API, TypeScript, SCSS e UnoCSS. Isso inclui a criação de um grid 3x3 responsivo, controle de proporção de aspecto de imagens, renderização de marcadores de tipo de postagem (ex: Reels, Carrossel), implementação de reordenação por arrastar e soltar (drag-and-drop) para postagens agendadas, e integração com stores `@maxvue/max-pinia` (com auto-save) e pacotes do ecossistema Engeapp.

## Instruções

### 1. Arquitetura e Estrutura do Componente
* **Ordem de Blocos SFC**: Defina os blocos Single-File Component exatamente nesta ordem: `<template>`, `<script setup lang="ts">` e depois `<style lang="scss" scoped>`.
* **Comentários em Português do Brasil**: Todos os comentários inline e documentação nos componentes Vue devem ser escritos em **Português do Brasil (pt-BR)**.
* **Atributos Inline no Template**: Mantenha todos os atributos de tags HTML e componentes em uma única linha no template, evitando formatação multilinha para as tags.
* **Integração com MaxComponentsUi**: Reutilize os componentes da biblioteca [MaxComponentsUi](file:///home/johnattas/GitHub/MaxComponentsUi) sempre que possível. Estes componentes são registrados via `unplugin-vue-components` e usados diretamente no template **sem import manual** (auto-import obrigatório):
  * Utilize [MaxButton.vue](file:///home/johnattas/GitHub/MaxComponentsUi/src/components/MaxButton.vue) para botões.
  * Utilize [MaxUserAvatar.vue](file:///home/johnattas/GitHub/MaxComponentsUi/src/components/MaxUserAvatar.vue) para avatares de usuário.
  * Utilize [MaxIcon.vue](file:///home/johnattas/GitHub/MaxComponentsUi/src/components/MaxIcon.vue) para exibição de ícones.

### 2. Layout do Grid do Instagram 3x3 e Proporções de Imagem
* **Grid de 3 Colunas**: Aloque as postagens em um container com grid CSS configurado com exatamente 3 colunas: `grid-template-columns: repeat(3, 1fr)`.
* **Restrição de Proporção (Aspect Ratio)**: Garanta que os cards das publicações permaneçam estritamente quadrados utilizando `aspect-ratio: 1 / 1`. Aplique `object-fit: cover` nas imagens ou vídeos para que a mídia não sofra distorções.
* **Marcadores Visuais do Tipo de Post**: Posicione os indicadores no canto superior direito de cada card de postagem usando `position: absolute`:
  * **Carrossel**: Use um ícone de páginas/slides (ex: `iconoir:multiple-pages` ou `lucide:layers`).
  * **Reels/Vídeo**: Use um ícone de vídeo/reprodução (ex: `iconoir:play` ou `lucide:clapperboard-play`).
  * **Imagem**: Sem overlay ou ícone simples de imagem.

### 3. Integração de Arrastar e Soltar (Drag-and-Drop)
* **VueDraggableNext**: Integre a funcionalidade de ordenação usando a biblioteca `vue-draggable-next`, seguindo as diretrizes descritas na skill [vue-draggable-next-best-practices](file:///home/johnattas/GitHub/Skills/created-skills/frontEnd/vue-draggable-next-best-practices/SKILL.md).
* **Vinculação Reativa**: Vincule a lista de posts reativa ao componente utilizando `<draggable v-model="posts" item-key="id" ...>` em uma única linha.
* **Slot de Item**: Utilize o slot `#item` desestruturando `{ element }` para renderizar os cards de mídia do feed.
* **Persistência da Ordenação**: Capture o evento `@change` para refletir a nova ordem no estado da store `@maxvue/max-pinia`. NÃO faça requisições `axios` manuais nem chame endpoints de salvamento diretamente: ao mutar o array reativo da store (`store.posts`), o MaxPinia dispara o auto-save (debounced) para `/api/...` automaticamente. Basta mapear os IDs e posições para o estado da store.

### 4. Sincronização com Stores MaxPinia
* **Integração com Stores `@maxvue/max-pinia`**:
  * Toda leitura e escrita de dados de página passa por uma store `@maxvue/max-pinia` — nunca via GET/POST manual. As stores usam helpers `apiGetRoute`/`apiPostRoute` do `@maxvue/max-use` que resolvem para caminhos string `/api/...` (não existe `route()`/Ziggy).
  * Sincronize com uma store de eventos de calendário (ex.: `useCalendarEventStore`) para gerenciar o estado da publicação selecionada no simulador. O GET inicial dos posts agendados é feito pela store, e qualquer mutação no estado é persistida automaticamente pelo auto-save do MaxPinia.
  * Recupere e atualize a lista de pautas e agendamentos por meio de uma store dedicada (ex.: `useSocialMediaThemesStore`), também ancorada em `@maxvue/max-pinia`.
* **Simulação de Uploads Temporários**: Permita que o usuário simule a pré-visualização de imagens rascunho (não agendadas no banco) gerando URLs locais temporárias via `URL.createObjectURL(file)` e atualizando o estado reativo local antes de consolidar o agendamento final no calendário.

---

## Exemplos

### Componente de Grid de Perfil Simulado (`InstagramGridSimulator.vue`)
```vue
<template>
  <div class="instagram-simulator-container">
    <div class="profile-header-preview" flex items-center mb-20>
      <MaxUserAvatar :imageUrl="props.clientAvatar" :name="props.clientName" size="xlarge" />
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
              <MaxIcon icon="iconoir:heart" size="1.1" mr-5 />
              <span>{{ element.likes ?? 0 }}</span>
            </div>
            <div class="overlay-stat" flex items-center>
              <MaxIcon icon="iconoir:chat-bubble" size="1.1" mr-5 />
              <span>{{ element.comments_count ?? 0 }}</span>
            </div>
          </div>
        </div>
      </template>
    </draggable>
    <div class="loader-state" flex items-center justify-center p-10 v-if="isSaving">
      <MaxIcon icon="loading" size="1.5" mr-10 />
      <span>Sincronizando feed...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
// `ref`/`watch` são auto-importados (unplugin-auto-import).
// MaxUserAvatar e MaxIcon são auto-registrados (unplugin-vue-components) — sem import manual.
// O componente da lib é o default export, registrado globalmente como <draggable>.
import VueDraggableNext from 'vue-draggable-next';

// Define a estrutura de um post no simulador do Instagram
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

const emit = defineEmits<{
  reordered: [posts: InstagramSimulatedPost[]];
}>();

const posts = ref<InstagramSimulatedPost[]>([...props.initialPosts]);
// Reflete o estado de salvamento exposto pela store @maxvue/max-pinia (auto-save).
const isSaving = ref<boolean>(false);

// Sincroniza a reatividade interna caso os posts iniciais mudem
watch(() => props.initialPosts, (newVal) => {
  posts.value = [...newVal];
}, { deep: true });

// Define o ícone com base no tipo de mídia do post
const getIndicatorIcon = (type: 'image' | 'video' | 'carousel'): string => {
  if (type === 'video') return 'iconoir:play';
  if (type === 'carousel') return 'iconoir:multiple-pages';
  return '';
};

// Dispara a reordenação das datas e propaga a nova ordem ao pai.
// A persistência é feita ao mutar o estado da store @maxvue/max-pinia,
// cujo auto-save (debounced) envia para /api/... automaticamente — sem axios manual.
const onGridReorder = () => {
  emit('reordered', posts.value);
};
</script>

<style lang="scss" scoped>
.instagram-simulator-container {
  max-width: 935px;
  margin: 0 auto;
  padding: 20px;
  background-color: var(--background-0);

  .profile-header-preview {
    border-bottom: 1px solid var(--surface-border);
    padding-bottom: 20px;
  }

  .instagram-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 28px; /* Espaçamento padrão do feed desktop do Instagram */

    @media (max-width: 768px) {
      gap: 3px; /* Espaçamento no mobile */
    }
  }

  .post-grid-card {
    position: relative;
    aspect-ratio: 1 / 1;
    width: 100%;
    overflow: hidden;
    background-color: var(--surface-card);
    cursor: grab;

    &:active {
      cursor: grabbing;
    }

    .post-media {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }

    .post-type-indicator {
      position: absolute;
      top: 10px;
      right: 10px;
      z-index: 5;
      filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.4));
    }

    .hover-overlay {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: rgba(0, 0, 0, 0.3);
      color: #ffffff;
      opacity: 0;
      transition: opacity 0.2s ease;
      pointer-events: none;
      z-index: 4;
    }

    &:hover .hover-overlay {
      opacity: 1;
    }

    .overlay-stat {
      font-size: 1rem;
      font-weight: 600;
    }
  }

  .grid-ghost {
    opacity: 0.4;
    border: 2px dashed var(--primary-color);
  }

  .grid-dragging {
    opacity: 0.9;
    transform: scale(1.02);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
  }
}
</style>
```

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **PROIBIDO uso de Tailwind CSS**: Deve-se utilizar SCSS com escopo fechado (`scoped`) ou as classes utilitárias customizadas do UnoCSS.
* **PROIBIDO manipulação direta do DOM por seletores**: Utilize sempre referências do template do Vue (`ref="el"`) em vez de seletores do document como `document.querySelector`.
* **PROIBIDO Tags com Atributos Multilinha**: A abertura de tags HTML e os parâmetros de componentes Vue devem ser declarados em uma única linha no template.
* **Ordem Estrita de SFC**: Os blocos do arquivo Vue devem seguir a sequência de ordem: `<template>` -> `<script setup lang="ts">` -> `<style lang="scss" scoped>`.
* **Manter Zona de Segurança das Imagens**: No layout do grid 3x3, garanta que outros elementos visuais customizados (como caixas de seleção ou marcadores de rascunho) não ocultem os indicadores de tipo de post ou distorçam o formato do grid.
* **Comentários de Código em pt-BR**: Qualquer comentário inserido nos blocos de script e estilo do componente deve estar no idioma Português do Brasil.
