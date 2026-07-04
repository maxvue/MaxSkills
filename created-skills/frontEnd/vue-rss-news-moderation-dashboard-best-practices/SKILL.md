---
name: vue-rss-news-moderation-dashboard-best-practices
description: Use when implementing, modifying, styling, or debugging RSS news moderation dashboard components or views in Vue 3 (EngeApp). Triggers on news items filter, approve/disapprove actions, tab/category navigation, search queries for news, and UI/UX improvements on TabNewsItems component.
---

## Objetivo
Padronizar a arquitetura, a experiência do usuário (UX) e a implementação técnica do painel de moderação de notícias RSS (`TabNewsItems`) no Vue 3, garantindo o carregamento resiliente de recursos externos, transições suaves de estado, feedback imediato das ações, filtragem de busca no cliente/servidor e integração semântica com IA.

## Instruções

### 1. Navegação por Abas e Filtragem de Status
Organize o fluxo de trabalho de moderação usando uma estrutura de abas baseada em status:
- Implemente abas para os estados **Pendente**, **Aprovado** e **Arquivado**.
- Vincule o estado da aba ativa reativamente para disparar a filtragem:
  ```typescript
  type ModerationStatus = 'pending' | 'approved' | 'archived'
  const activeStatus = ref<ModerationStatus>('pending')
  ```
- Anime os indicadores de aba ativa com transições suaves de deslizamento usando transições CSS/UnoCSS (ex: `transition-all duration-300 ease-in-out`).

### 2. Tratamento Resiliente de Imagens (Padrão de Fallback)
Imagens externas de feeds RSS são frequentemente instáveis. Sempre implemente o tratamento de fallback para imagens:
- Use um marcador de posição (placeholder) de fallback padrão quando a imagem do item RSS estiver ausente, falhar ao carregar ou retornar um erro/404.
- Crie um manipulador de erro de carregamento de imagem para alternar para o fallback reativamente:
  ```html
  <!-- Estilize via atributos attributify do UnoCSS (presetMaxUno) + tokens de tema, não via class="..." cru -->
  <img :src="item.imageUrl || defaultFallbackUrl" @error="handleImageError" w-full h-48 object-cover rounded-lg />
  ```
  ```typescript
  const defaultFallbackUrl = '/images/news-fallback.jpg'
  const handleImageError = (event: Event) => {
    const target = event.target as HTMLImageElement
    if (target.src !== defaultFallbackUrl) {
      target.src = defaultFallbackUrl
    }
  }
  ```

### 3. Feedback Visual Imediato e Micro-animações
Garanta uma experiência fluida para o usuário fornecendo feedback visual tátil instantâneo nas decisões de moderação:
- Aplique utilitários de animação do UnoCSS como atributos attributify (ex.: `animate-fade-out` ou `scale-95 duration-200`), ligados dinamicamente via `:class`/`:animate-fade-out` quando um item for aprovado ou arquivado — nunca como strings `class="..."` cruas de Tailwind.
- Atualize de forma otimista o estado da lista na interface do usuário imediatamente quando um botão de ação for clicado. A persistência NÃO usa Axios cru: toda leitura/gravação de dados de página passa por uma store `@maxvue/max-pinia`, que faz o auto-save (debounced) no backend. Para ações pontuais de comando (aprovar/arquivar), dispare o método da store que resolve o caminho via `apiPostRoute`:
  ```typescript
  import { useNewsModerationStore } from '~/stores/newsModeration'

  const newsStore = useNewsModerationStore()

  const approveItem = async (itemId: string) => {
    // 1. Atualização otimista da UI: desliza/esmaece o item
    const index = newsStore.items.findIndex(item => item.id === itemId)
    if (index !== -1) {
      newsStore.items[index].isLeaving = true
      setTimeout(() => {
        newsStore.items.splice(index, 1)
      }, 300) // deve corresponder à duração da animação
    }

    // 2. Persistência via store MaxPinia (sem Axios manual);
    //    a store resolve a rota string /api/... . Em caso de falha, o rollback é
    //    feito AQUI (no componente), chamando reload() na instância da store.
    try {
      await newsStore.approve(itemId)
    } catch {
      await newsStore.reload() // reload só é acessível na instância da store
    }
  }
  ```
  A store é uma SETUP store do `@maxvue/max-pinia` (`isCached` + `options`). O comando de aprovar usa `apiPostRoute` do `@maxvue/max-use` (chamada imperativa — executa a requisição e retorna o payload direto). O `reload()` é injetado pelo `@maxvue/max-pinia` **na instância** da store, não é uma variável do escopo da setup — então o rollback é feito pelo chamador via `newsStore.reload()` (como acima), e não dentro da setup:
  ```typescript
  // stores/newsModeration.ts
  import { defineStore } from 'pinia'
  import { ref, computed } from 'vue'
  import { apiPostRoute } from '@maxvue/max-use'

  export const useNewsModerationStore = defineStore('news.moderation', () => {
    const isCached = ref(true)
    const items = ref<any[]>([])
    // Parâmetro de busca reativo: alterá-lo dispara automaticamente novo GET pela store.
    const search = ref('')

    // route é caminho string /api/...; a store chama apiGetRoute internamente.
    // options.get.data é reativo — o GET refaz sozinho quando search muda.
    const options = computed(() => ({
      get: { route: '/api/news/moderation', data: { search: search.value } },
      id: 'news-moderation',
    }))

    async function approve(itemId: string) {
      // Chamada imperativa de comando (não é config de store): dispara o POST.
      // Deixe o erro propagar — o rollback (reload) é feito pelo chamador na instância.
      await apiPostRoute(`/api/news/moderation/${itemId}/approve`)
    }

    return { isCached, items, search, options, approve }
  })
  ```
  > `reload()` é injetado pelo `@maxvue/max-pinia` **na instância** da store (ex.: `newsStore.reload()`); NÃO é uma variável do escopo da setup — referenciá-lo bare dentro da setup lança `ReferenceError`. Use-o a partir do componente.
  > A chave do cache vem de `options.id` (o `@maxvue/max-pinia` não lê `options.key`).

### 4. Filtragem Híbrida no Lado do Cliente e do Servidor
Combine a busca instantânea de texto no cliente com a filtragem dinâmica via API no backend:
- Implemente a filtragem no lado do cliente na lista de notícias carregada atualmente usando uma propriedade computada (`computed`) para obter resultados instantâneos conforme o usuário digita.
- Utilize debounce nos termos de busca (ex: usando `refDebounced` do MaxUse (`@maxvue/max-use`, que reexporta o VueUse) com atraso de 300ms) antes de pedir uma nova carga ao backend. A busca no servidor é feita pela store MaxPinia (que faz o GET via `apiGetRoute` resolvendo o caminho string `/api/...`), nunca por `axios.get` manual:
  ```typescript
  import { refDebounced } from '@maxvue/max-use'
  import { useNewsModerationStore } from '~/stores/newsModeration'

  const newsStore = useNewsModerationStore()
  const searchInput = ref('')
  const debouncedSearch = refDebounced(searchInput, 300)

  watch(debouncedSearch, (newQuery) => {
    // Atualiza o parâmetro reativo da store (options.get.data). Como ele é reativo,
    // o @maxvue/max-pinia reexecuta o GET (/api/...) e atualiza o cache automaticamente.
    // Se precisar forçar a revalidação, chame newsStore.reload().
    newsStore.search = newQuery
  })
  ```

### 5. Prompt Semântico de IA para Sugestões Editoriais
Integre sugestões de IA de forma dinâmica na tela de moderação para auxiliar os criadores de conteúdo:
- Forneça um card inline com ações como "Sugerir Tema Editorial" ou "Gerar Rascunho do Post" ao lado ou dentro da visualização de detalhes da notícia.
- Envie o título e a prévia do conteúdo do item de notícia para o endpoint de IA no backend, que roteia a geração pelo **Vercel AI SDK** (provider Gemini via Vercel AI SDK), produzindo classificações de tópicos estruturadas, ângulos para publicações ou rascunhos de posts. A chamada parte de um método da store MaxPinia (`apiPostRoute('/api/news/.../ai-suggest')`), não de Axios cru.
- Renderize os resultados em um card envolto por `MaxLoaderAi`, permitindo a cópia com um clique ou a inserção direta nas ferramentas de agendamento/redação.

### 6. Sintaxe de Componentes e Diretrizes de Atributos
- Sempre use a Composition API do Vue 3 (`<script setup lang="ts">`) and SCSS escopados (`<style scoped lang="scss">`).
- Mantenha todos os atributos do template HTML em uma única linha (sem quebras de linha para múltiplos atributos de um elemento ou componente no template).
  - *Exemplo:* `<MaxButton class="btn-primary" :loading="isSubmitting" @click="submit" />`

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **PROIBIDO Options API:** Não utilize a Options API sob nenhuma circunstância.
- **PROIBIDO Pré-visualizações em Branco:** Não permita que falhas no carregamento de imagens externas de RSS causem espaços vazios ou ícones de imagens quebradas; o uso de imagens de fallback é obrigatório.
- **PROIBIDO UI de Bloqueio Síncrono:** Nunca congele a tela de moderação ou bloqueie outras interações enquanto aguarda a resposta das APIs de aprovação/arquivamento. Use atualizações otimistas da UI e loaders localizados.
