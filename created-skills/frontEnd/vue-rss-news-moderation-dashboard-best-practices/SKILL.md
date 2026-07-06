---
name: vue-rss-news-moderation-dashboard-best-practices
description: Use ao implementar, estilizar ou depurar o painel de moderação de notícias RSS (TabNewsItems.vue) do EngeApp em Vue 3. Cobre a store Pinia useSocialMediaNewsStore (axios + rotas Ziggy news.index/approve/reprove/refresh/agent.keywords), abas pendente/arquivada via prop archived, agrupamento por palavra-chave, aprovar criando Tema editorial e feedback via Toast.
---

## Objetivo
Padronizar a arquitetura e a UX do painel de moderação de notícias RSS do EngeApp — o componente `resources/Vue/Sections/SocialMedia/TabNewsItems.vue` e sua store `resources/Stores/calendar/useSocialMediaNews.Store.ts`. As notícias são importadas do Google News RSS (comando `social-media:fetch-news`), entram como `pending`, e o gestor aprova (gerando um Tema editorial) ou arquiva cada uma.

Grave a verdade-base do fluxo antes de mexer, porque a implementação é enxuta e específica: cards de texto puro (sem imagens), abas controladas pelo pai via prop, store Pinia pura com axios, e feedback via `Toast`. Não invente imagens, busca de texto, animação otimista nem cache MaxPinia — nada disso existe aqui.

## Verdade-base do fluxo (confirme sempre no código)

- **Componente:** `TabNewsItems.vue`, `<script setup lang="ts">`. Recebe `defineProps<{ archived?: boolean }>()` e emite `theme-created`. O pai (página) decide qual aba renderizar passando `archived`; o componente NÃO tem abas internas nem `ref` de status.
- **Status reais:** `type NewsStatus = 'pending' | 'approved' | 'reproved'`. A aba "arquivadas" mostra os `reproved`. Não existe status `archived`, e não há aba de `approved` — aprovar remove o item da lista e cria um `SocialMediaTheme`.
- **Store:** `useSocialMediaNewsStore`, `defineStore('social.media.news.store', ...)`. É **Pinia pura** (setup store), sem `isCached`, sem `options`, sem auto-save. Faz `axios` direto contra nomes de rota Ziggy resolvidos por `route()`.
- **Cards:** texto puro — `source`, `published_at`, `title`, `keywords`, `description`, mais link externo (`item.url`). Não há `<img>`, `imageUrl`, fallback de imagem nem `handleImageError`. A interface `SocialMediaNewsItem` não tem campo de imagem.
- **Backend:** EngeApp é **Laravel 13**; a geração/IA usa o pacote `laravel/ai`. Não existe Vercel AI SDK aqui, nem card inline "Sugerir Tema" — o Tema nasce como efeito de `approve`.

## Instruções

### 1. Abas controladas pela prop `archived`
Não crie abas internas nem um `activeStatus = ref()`. O componente é uma "view" de uma lista; o pai troca de aba re-renderizando com outra prop:

```typescript
const props = defineProps<{ archived?: boolean }>();

const items     = computed<SocialMediaNewsItem[]>(() => props.archived ? store.archived : store.pending);
const isLoading = computed(() => props.archived ? store.loadingArchived : store.loadingPending);
```

Carregue no `onMounted` chamando `reload()`, que despacha `store.loadPending()` ou `store.loadArchived()` conforme a prop. O painel de palavras-chave e as ações de moderação só aparecem quando `!archived`.

### 2. Store Pinia pura com axios + rotas Ziggy
Toda leitura/gravação deste fluxo usa `axios` diretamente com **nomes de rota Ziggy** via `route(...)` (Ziggy está configurado). Esta store NÃO usa `@maxvue/max-pinia`, `isCached`, `apiGetRoute` nem `apiPostRoute` — replicar o padrão MaxPinia aqui está errado.

```typescript
export const useSocialMediaNewsStore = defineStore('social.media.news.store', () => {
    const pending  = ref<SocialMediaNewsItem[]>([]);
    const archived = ref<SocialMediaNewsItem[]>([]);
    const loadingPending  = ref(false);
    const loadingArchived = ref(false);
    const processingId    = ref<string | null>(null);

    async function loadPending(): Promise<void> {
        loadingPending.value = true;
        try {
            const { data } = await axios.get(route('news.index'), { params: { status: 'pending' } });
            pending.value = data;
        } finally {
            loadingPending.value = false;
        }
    }

    async function approve(id: string): Promise<{ theme: any }> {
        processingId.value = id;
        try {
            const { data } = await axios.post(route('news.approve', { news: id }));
            pending.value = pending.value.filter(n => n.id !== id); // remoção real fica na store
            return data; // { theme }
        } finally {
            processingId.value = null;
        }
    }
    // reprove → route('news.reprove', { news: id })
    // saveKeywords → route('news.agent.keywords', { agent: agentId }) via axios.patch
    // refresh → route('news.refresh')
    return { pending, archived, loadingPending, loadingArchived, processingId,
             loadPending, loadArchived, approve, reprove, saveKeywords, refresh };
});
```

Rotas Ziggy reais usadas: `news.index` (com `params.status`), `news.approve` (param `news`), `news.reprove` (param `news`), `news.agent.keywords` (param `agent`, `PATCH`), `news.refresh`.

### 3. Ação de moderação: sem otimismo com timeout, remoção na store
Não faça `items[index].isLeaving = true` + `splice` + `setTimeout(300)` nem rollback via `reload()` — nada disso existe. O padrão real é: o handler do componente chama o método da store (que faz o axios e já remove o item da lista com `filter`), e o feedback vem de `Toast`. O loading por item é derivado de `store.processingId === item.id`.

```typescript
async function handleApprove(id: string): Promise<void> {
    try {
        const result = await store.approve(id);
        themesStore.themes.unshift(result.theme); // aprovar CRIA um Tema editorial
        Toast.show({ severity: 'success', title: 'Tema criado!', message: 'A notícia foi aprovada e um tema pendente foi criado.' });
        emit('theme-created');
    } catch (e) {
        console.error('[handleApprove] erro ao aprovar notícia:', e);
        Toast.show({ severity: 'error', title: 'Erro', message: 'Não foi possível aprovar a notícia.' });
    }
}
```

`handleReprove(id)` chama `store.reprove(id)` (move para `archived`) e mostra `Toast`. Nos botões, ligue o loading a `store.processingId === item.id` e as ações via `:action`:

```html
<MaxButton icon="mdi:check-circle-outline" label="Aprovar · Criar Tema" size="small" :loading="store.processingId === item.id" :action="() => handleApprove(item.id)" />
```

### 4. Agrupamento por palavra-chave (não é busca de texto)
Não existe input de busca, `refDebounced`, filtro `computed` por texto digitado nem parâmetro `search` reativo na store. A organização real é por **palavras-chave** do agente: `displayGroups` ordena as notícias por data e as agrupa segundo `agentStore.data?.news_keywords`, com um grupo "Outros" para o restante. Na aba arquivada, tudo vai num grupo único.

```typescript
const displayGroups = computed<NewsGroup[]>(() => {
    const sorted = sortByDate(items.value);
    if (props.archived || !sorted.length) return [{ keyword: null, label: '', items: sorted }];
    const keywords = agentStore.data?.news_keywords ?? [];
    // ...agrupa por keyword incluída em item.keywords, dedup por id, resto em "Outros"
});
```

O painel de palavras-chave (aba pendente) permite adicionar/remover chips localmente e persistir via `store.saveKeywords(agentId, localKeywords)` (rota `news.agent.keywords`), com `keywordsDirty` controlando o botão "Salvar".

### 5. Importação e atualização em tempo real (Echo)
Para reimportar notícias, chame `store.refresh()` (dispara o job de importação no backend) e informe o usuário com `Toast` de que a atualização virá automaticamente. A chegada das novas notícias é notificada por WebSocket com `useEcho` de `@laravel/echo-vue`, no canal `live.company.${companyId}`, evento `SocialMediaNewsImported`; ao receber, recarregue com `store.loadPending()` e mostre `Toast` com a contagem.

```typescript
useEcho(`live.company.${companyId}`, 'SocialMediaNewsImported', (payload: { count: number }) => {
    store.loadPending();
    Toast.show({ severity: 'success', title: 'Notícias atualizadas!', message: `${payload.count} nova(s) notícia(s) importada(s).` });
});
```

### 6. Componentes, estilo e atributos
- Use apenas `Composition API` (`<script setup lang="ts">`).
- Componentes da UI vêm de `@maxvue/max-components-ui` (`MaxButton`, `MaxIcon`, `Toast`); tooltips via diretiva `v-tooltip.top`. Não use PrimeVue cru nem `<button>` nativo para ações de UI padronizadas (o input inline de keyword e os micro-botões de chip são exceções intencionais já presentes no arquivo).
- O estilo real é `<style lang="scss">` **NÃO escopado**, com classes CSS nomeadas (`news-card`, `news-grid`, `news-keyword-chip`, ...) usadas via `class="..."` no template, e tokens de tema `var(--background-*)`, `var(--primary-color)`, `var(--text-color)`. Não converta para UnoCSS attributify nem imponha `scoped` — isso contradiz o componente que a skill documenta.
- Mantenha os atributos de cada elemento/componente do template em uma única linha.
- Comentários de código em pt-BR.

## Restrições
- **Idioma:** Comunique-se com o humano sempre em Português (pt-BR), independentemente do idioma do corpo da skill.
- **PROIBIDO Options API.**
- **PROIBIDO inventar recursos ausentes:** não adicione imagens/fallback, busca de texto com debounce, animação otimista com `setTimeout`, cache MaxPinia (`isCached`/`options`) ou Vercel AI SDK — nada disso existe neste fluxo.
- **PROIBIDO UI de bloqueio síncrono:** nunca congele a tela durante aprovar/arquivar/importar; use os loaders localizados (`store.processingId`, `store.loadingPending/loadingArchived`, `refreshing`, `savingKeywords`) e feedback via `Toast`.
- **Estados vazios/carregando:** sempre trate `isLoading` e lista vazia com mensagens próprias (pendentes vs. arquivadas), como no componente real.
</content>
</invoke>
