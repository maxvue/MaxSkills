---
name: vue-google-business-profile-post-preview-simulator-best-practices
description: Use when designing, building, styling, or debugging Vue 3 components, views, or composables related to the Google Business Profile (GBP / Google My Business) post and update preview simulator. Triggers on components like GoogleBusinessPostPreview, GoogleBusinessSimulator, layouts supporting news/offers/events post types, call-to-action buttons (Learn More, Sign Up, Buy, Call Now), date picker event offsets, and desktop/mobile search result mockups in SocialMediaApp.
---

# Boas Práticas para Simulador e Pré-visualização de Posts do Google Business Profile

## Objetivo
Fornecer diretrizes, especificações de design system e padrões de implementação para a criação de componentes de pré-visualização de postagens do Google Business Profile (GBP) reativos e de alta fidelidade em Vue 3. Isso garante que os profissionais de marketing vejam uma réplica exata de como suas atualizações locais (Novidades, Ofertas, Eventos) aparecerão na Busca do Google (desktop/mobile) e no Google Maps antes de programar o envio.

## Instruções

### 1. Estrutura e Configuração do Componente
- **Componentes Single-File (SFC):** Siga a estrutura de blocos obrigatória do Vue: `<template>`, `<script setup lang="ts">` e `<style scoped lang="scss">`.
- **Tipagem TypeScript:** Defina interfaces estritas para os modelos de postagem, opções de CTA, metadados de ofertas (cupom, termos) e horários de eventos.
- **Layout de Atributos:** Formate os componentes Vue mantendo todas as propriedades em uma única linha no template (ex: `<Component param1="value" param2="value" />`). Não quebre os atributos em várias linhas.

### 2. Tipos de Post do GBP e Lógica de Renderização
Certifique-se de que o simulador suporte três modos distintos de postagens do Google Business Profile:
1. **Novidades (What's New):**
   - Renderiza uma descrição/texto (máx. 1500 caracteres) e uma única imagem ou vídeo opcional.
   - Mostra o botão de CTA selecionado no rodapé.
2. **Oferta (Offer):**
   - Requer um **Título da Oferta** (exibido em negrito, caixa alta ou badge de destaque).
   - Mostra um **Período de Validade** (data de início até data de término).
   - Renderiza um container para o **Código do Cupom** (com borda pontilhada, simulação de ação de cópia e ícone de cupom).
   - Renderiza o link de **Termos e Condições** que abre um modal/popup simulado quando clicado.
3. **Evento (Event):**
   - Requer um **Título do Evento**.
   - Mostra o **Período do Evento** (formato: "Data de Início - Data de Término", incluindo as horas).
   - Renderiza uma badge de evento ou ícone de calendário.

### 3. Ações de Call-to-Action (CTA)
Implemente um mapeador dinâmico de botões para as ações suportadas pelo GBP:
- `BOOK`: "Reservar"
- `ORDER_ONLINE`: "Pedir on-line"
- `BUY`: "Comprar"
- `LEARN_MORE`: "Saiba mais"
- `SIGN_UP`: "Cadastrar-se"
- `CALL_NOW`: "Ligar agora" -> renderiza como um link telefônico `tel:`.
- Se nenhum CTA for selecionado, oculte o botão de ação por completo.

### 4. Layout & Estética (Estilo Google Local Search)
- **Simulação de Viewport:** Ofereça suporte para alternar entre a barra lateral de pesquisa no desktop (`max-w-[650px]`) e o feed de pesquisa no mobile (`max-w-[420px]`).
- **Cabeçalho:** Renderize o Nome da Empresa (negrito, cinza escuro), o Avatar da Empresa (circular) e o tempo relativo da publicação (ex: "Agora mesmo" ou tempo relativo usando o composable `useTimeAgo`).
- **Container de Mídia:** Mantenha uma proporção de aspecto 4:3 ou 16:9 para a imagem do post com um efeito suave de zoom ao passar o mouse.
- **Tipografia:** Siga a tipografia padrão do Google: `Roboto`, `arial`, sans-serif.
- **Estilo do Botão de CTA:** Botão azul arredondado padrão do Google (`bg-[#1a73e8]`, hover `bg-[#1557b0]`, inteiramente arredondado/rounded-full, texto branco, semibold).

---

## Restrições
- **NÃO** utilize a Options API. Sempre utilize `<script setup lang="ts">`.
- **NÃO** escreva estilos fora de blocos SCSS escopados (`scoped`).
- **NÃO** escreva comentários de código em inglês. Todos os comentários inline dentro dos templates/scripts do Vue devem ser escritos em **Português do Brasil (pt-BR)**.
- **NÃO** duplique cores CSS; utilize as variáveis de design do projeto ou variáveis de tema nativas do UnoCSS.

---

## Examples (Exemplos)

### GoogleBusinessPostPreview.vue
Aqui está uma implementação de alta fidelidade do componente de pré-visualização do GBP em Vue 3:

```vue
<template>
  <div class="google-preview-container flex flex-col gap-4 p-4 bg-zinc-50 dark:bg-zinc-950 rounded-xl border border-zinc-200 dark:border-zinc-800">
    <!-- Alternador de Visualização (Desktop / Mobile) -->
    <div class="flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800 pb-3">
      <span class="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Visualização Prévia</span>
      <div class="flex bg-zinc-200 dark:bg-zinc-800 p-0.5 rounded-lg">
        <button @click="isMobile = false" :class="[!isMobile ? 'bg-white dark:bg-zinc-700 shadow-sm text-blue-600' : 'text-zinc-600 dark:text-zinc-400']" class="px-3 py-1 text-xs font-medium rounded-md transition-all flex items-center gap-1">
          <MaxIcon icon="mdi:desktop-mac" size="0.9rem" />
          <span>Desktop</span>
        </button>
        <button @click="isMobile = true" :class="[isMobile ? 'bg-white dark:bg-zinc-700 shadow-sm text-blue-600' : 'text-zinc-600 dark:text-zinc-400']" class="px-3 py-1 text-xs font-medium rounded-md transition-all flex items-center gap-1">
          <MaxIcon icon="mdi:cellphone" size="0.9rem" />
          <span>Mobile</span>
        </button>
      </div>
    </div>

    <!-- Card de Post no Padrão do Google -->
    <div :class="[isMobile ? 'max-w-[420px]' : 'max-w-[650px]']" class="gbp-post-card w-full mx-auto bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg shadow-sm overflow-hidden text-[#202124] dark:text-[#e8eaed] transition-all duration-300">
      <!-- Cabeçalho do Card (Local / Perfil) -->
      <div class="flex items-center gap-3 p-4">
        <img :src="businessAvatar || '/default-business.png'" alt="Avatar" class="w-10 h-10 rounded-full border border-zinc-200 dark:border-zinc-700 object-cover" />
        <div class="flex flex-col">
          <span class="font-medium text-sm text-[#202124] dark:text-[#e8eaed] leading-tight">{{ businessName || 'Nome da Empresa' }}</span>
          <span class="text-xs text-[#70757a] dark:text-[#9aa0a6] mt-0.5">{{ formattedTime }}</span>
        </div>
      </div>

      <!-- Imagem de Destaque -->
      <div v-if="imageUrl" class="media-container relative aspect-[4/3] w-full bg-zinc-100 dark:bg-zinc-950 overflow-hidden border-b border-zinc-100 dark:border-zinc-800">
        <img :src="imageUrl" alt="Post Media" class="w-full h-full object-cover transition-transform duration-300 hover:scale-105" />
        
        <!-- Badge de Oferta ou Evento sobreposta -->
        <span v-if="postType === 'OFFER'" class="absolute top-3 left-3 bg-[#e8f0fe] dark:bg-blue-950/60 text-[#1a73e8] dark:text-blue-300 text-xs font-semibold px-2.5 py-1 rounded flex items-center gap-1 shadow-sm">
          <MaxIcon icon="mdi:tag-outline" size="0.9rem" />
          <span>Oferta</span>
        </span>
        <span v-else-if="postType === 'EVENT'" class="absolute top-3 left-3 bg-[#fef7e0] dark:bg-amber-950/60 text-[#b06000] dark:text-amber-300 text-xs font-semibold px-2.5 py-1 rounded flex items-center gap-1 shadow-sm">
          <MaxIcon icon="mdi:calendar-star" size="0.9rem" />
          <span>Evento</span>
        </span>
      </div>

      <!-- Área de Informações Específicas do Tipo de Post -->
      <div class="p-4 flex flex-col gap-3">
        <!-- 1. Títulos Especiais (Oferta / Evento) -->
        <div v-if="postType === 'OFFER' && offerTitle" class="flex flex-col">
          <h3 class="text-lg font-bold text-[#1a73e8] dark:text-blue-400 leading-snug">{{ offerTitle }}</h3>
          <span class="text-xs text-[#70757a] dark:text-[#9aa0a6] font-medium mt-1 flex items-center gap-1">
            <MaxIcon icon="mdi:clock-outline" size="0.8rem" />
            <span>Validade: {{ offerDates }}</span>
          </span>
        </div>

        <div v-else-if="postType === 'EVENT' && eventTitle" class="flex flex-col">
          <h3 class="text-lg font-bold text-[#b06000] dark:text-amber-400 leading-snug">{{ eventTitle }}</h3>
          <span class="text-xs text-[#70757a] dark:text-[#9aa0a6] font-medium mt-1 flex items-center gap-1">
            <MaxIcon icon="mdi:calendar-clock" size="0.8rem" />
            <span>Horário: {{ eventDates }}</span>
          </span>
        </div>

        <!-- 2. Texto do Post / Descrição -->
        <p v-if="description" class="text-sm text-[#3c4043] dark:text-[#bdc1c6] leading-relaxed whitespace-pre-line">
          {{ displayedDescription }}
          <button v-if="hasLongText && !showFullText" @click="showFullText = true" class="text-[#1a73e8] dark:text-blue-400 font-medium hover:underline ml-1">Mais</button>
        </p>

        <!-- 3. Detalhes Adicionais da Oferta (Cupom / Termos) -->
        <div v-if="postType === 'OFFER' && (couponCode || terms)" class="offer-details flex flex-col gap-2 mt-1 p-3 bg-zinc-50 dark:bg-zinc-800/40 rounded-lg border border-dashed border-zinc-300 dark:border-zinc-700">
          <div v-if="couponCode" class="flex items-center justify-between">
            <div class="flex items-center gap-1.5 text-xs text-[#3c4043] dark:text-[#bdc1c6]">
              <MaxIcon icon="mdi:ticket-percent" class="text-[#1a73e8]" size="1rem" />
              <span>Código: <code class="font-mono bg-zinc-200 dark:bg-zinc-700 px-1.5 py-0.5 rounded text-sm font-semibold select-all">{{ couponCode }}</code></span>
            </div>
            <button @click="simulateCopy" class="text-xs text-[#1a73e8] dark:text-blue-400 font-semibold hover:underline">Copiar</button>
          </div>
          <button v-if="terms" @click="showTermsModal = true" class="text-xs text-[#70757a] dark:text-[#9aa0a6] text-left hover:underline w-fit">Ver termos e condições</button>
        </div>

        <!-- 4. Botão de Call to Action (CTA) -->
        <div v-if="ctaType && ctaLabel" class="flex justify-end mt-2 pt-2 border-t border-zinc-100 dark:border-zinc-800">
          <a :href="ctaUrl" @click.prevent="handleCtaClick" class="google-cta-btn bg-[#1a73e8] hover:bg-[#1557b0] text-white text-xs font-semibold px-5 py-2.5 rounded-full transition-colors flex items-center gap-1.5 shadow-sm">
            <MaxIcon v-if="ctaType === 'CALL_NOW'" icon="mdi:phone" size="0.9rem" />
            <span>{{ ctaLabel }}</span>
          </a>
        </div>
      </div>
    </div>

    <!-- Modal Simulado de Termos da Oferta -->
    <div v-if="showTermsModal" class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-zinc-900 rounded-lg p-5 max-w-sm w-full border border-zinc-200 dark:border-zinc-800 shadow-xl">
        <h4 class="text-sm font-bold border-b pb-2 mb-3">Termos e Condições</h4>
        <p class="text-xs text-zinc-600 dark:text-zinc-400 leading-relaxed mb-4">{{ terms }}</p>
        <div class="flex justify-end">
          <button @click="showTermsModal = false" class="bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 text-xs font-semibold px-4 py-2 rounded transition-colors">Fechar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useTimeAgo } from '@maxvue/max-use'; // Helper de data e reatividade da biblioteca local

// Define os tipos aceitos para postagem
type GbpPostType = 'NEWS' | 'OFFER' | 'EVENT';
type GbpCtaType = 'BOOK' | 'ORDER_ONLINE' | 'BUY' | 'LEARN_MORE' | 'SIGN_UP' | 'CALL_NOW';

// Props tipadas com TypeScript
interface Props {
  businessName?: string;
  businessAvatar?: string;
  postType?: GbpPostType;
  description?: string;
  imageUrl?: string;
  publishDate?: Date | string;
  // Propriedades de Oferta
  offerTitle?: string;
  startDate?: string;
  endDate?: string;
  couponCode?: string;
  terms?: string;
  // Propriedades de Evento
  eventTitle?: string;
  // Configuração do CTA
  ctaType?: GbpCtaType;
  ctaTargetUrl?: string;
}

const props = withDefaults(defineProps<Props>(), {
  postType: 'NEWS',
  description: ''
});

// Estados internos de interface
const isMobile = ref<boolean>(false);
const showFullText = ref<boolean>(false);
const showTermsModal = ref<boolean>(false);

// Formatador de tempo relativo
const formattedTime = computed<string>(() => {
  if (!props.publishDate) return 'Agora mesmo';
  return useTimeAgo(new Date(props.publishDate)).value;
});

// Validador de truncamento de texto longo (limite do Google de cerca de 220 caracteres visíveis no snippet)
const hasLongText = computed<boolean>(() => {
  return props.description.length > 220;
});

const displayedDescription = computed<string>(() => {
  if (!hasLongText.value || showFullText.value) return props.description;
  return props.description.slice(0, 220) + '...';
});

// Agrupamento visual das datas da oferta
const offerDates = computed<string>(() => {
  if (!props.startDate && !props.endDate) return 'Período não definido';
  const start = props.startDate ? new Date(props.startDate).toLocaleDateString('pt-BR') : '';
  const end = props.endDate ? new Date(props.endDate).toLocaleDateString('pt-BR') : 'Sem data de término';
  return start ? `${start} - ${end}` : end;
});

// Agrupamento visual das datas do evento
const eventDates = computed<string>(() => {
  if (!props.startDate && !props.endDate) return 'Data não definida';
  const options: Intl.DateTimeFormatOptions = { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' };
  const start = props.startDate ? new Date(props.startDate).toLocaleString('pt-BR', options) : '';
  const end = props.endDate ? new Date(props.endDate).toLocaleString('pt-BR', options) : 'Sem data de término';
  return start ? `${start} - ${end}` : end;
});

// Mapeamento de rótulos do botão de CTA
const ctaLabel = computed<string>(() => {
  if (!props.ctaType) return '';
  const labelMap: Record<GbpCtaType, string> = {
    BOOK: 'Reservar',
    ORDER_ONLINE: 'Pedir on-line',
    BUY: 'Comprar',
    LEARN_MORE: 'Saiba mais',
    SIGN_UP: 'Cadastrar-se',
    CALL_NOW: 'Ligar agora'
  };
  return labelMap[props.ctaType];
});

// Trata a URL de destino baseando-se no tipo do CTA
const ctaUrl = computed<string>(() => {
  if (props.ctaType === 'CALL_NOW') {
    return 'tel:+5511999999999'; // Simula ligação para número de teste
  }
  return props.ctaTargetUrl || '#';
});

// Simulação das ações do usuário no preview
const simulateCopy = (): void => {
  alert(`[Simulador] Código do cupom "${props.couponCode}" copiado para a área de transferência!`);
};

const handleCtaClick = (): void => {
  if (props.ctaType === 'CALL_NOW') {
    alert('[Simulador] Ação "Ligar agora" disparada. Iniciando chamada telefônica...');
  } else {
    alert(`[Simulador] Ação de CTA "${ctaLabel.value}" redirecionando para: ${ctaUrl.value}`);
  }
};
</script>

<style scoped lang="scss">
.gbp-post-card {
  font-family: Roboto, Arial, sans-serif;
  
  .media-container {
    img {
      user-select: none;
      -webkit-user-drag: none;
    }
  }

  .google-cta-btn {
    user-select: none;
    text-decoration: none;
  }
}
</style>
```
