---
name: vue-instagram-comments-moderation-inbox-best-practices
description: Use when building, modifying, reviewing, or styling the Instagram comments and direct messages (DM) moderation inbox interface in Vue 3 (an EngeApp feature), handling real-time updates from Server-Sent Events (SSE), implementing AI-generated reply suggestions, managing moderation actions (like, reply, hide, delete comments), or structuring custom scrollbars and grid systems for interactive panels.
---

## Objetivo
Padronizar o design, a experiência do usuário (UX) e a implementação técnica da interface de caixa de entrada (Inbox) para moderação de comentários e DMs do Instagram no Vue 3, utilizando MaxComponentsUi, MaxUse, sincronização em tempo real via SSE e respostas assistidas por IA.

## Instruções

### 1. Layout de Grid e Estrutura de Painéis
Estruture a caixa de entrada usando um layout de duas colunas otimizado para ergonomia e produtividade:
- Use `MaxGrid` e `MaxGridCols` para dividir a tela em:
  - **Painel Esquerdo (30-40% de largura):** Lista de conversas ou visão geral dos posts. Exibe os itens de conversa com indicadores de lido/não lido, avatares dos remetentes, prévia do texto e carimbo de data/hora via `useTimeAgo`.
  - **Painel Direito (60-70% de largura):** Visualização detalhada do histórico de mensagens / árvore de comentários e a caixa de ferramentas de interação.
- Aplique barras de rolagem personalizadas (`overflow-y-auto`) utilizando classes CSS com estilos modernos.
- Use `<div>` + SCSS (não existe componente de card genérico no MaxComponentsUi) para criar painéis visualmente premium.

### 2. Ingestão em Tempo Real (Laravel Reverb + Echo)
Use o `@laravel/echo-vue` (Echo já configurado no bootstrap via `configureEcho`, apontando para o Laravel Reverb) para manter a linha de comentários atualizada sem recarregamento manual de página:
- Assine o canal de moderação com `useEcho` e escute o evento de atualização de comentários/mensagens em tempo real:
  ```typescript
  import { useEcho } from '@laravel/echo-vue'

  const { listen } = useEcho(`instagram.moderation.${clientId}`, 'InstagramCommentUpdated', (data: { commentId: string; text: string; action: string }) => {
    // Atualiza reativamente a store @maxvue/max-pinia (mescla o novo comentário/mensagem na coleção)
  })
  ```
- **Limpeza:** O `useEcho` faz o unsubscribe automaticamente no `onUnmounted` do componente. Para pausar/retomar manualmente, use os controles `leave()`/`listen()` retornados pelo composable.

### 3. Sugestões de Respostas Geradas por IA
Melhore o fluxo de trabalho de moderação utilizando sugestões de IA integradas:
- Use `MaxLoaderAi` para indicar quando a IA no backend está elaborando recomendações de resposta.
- Exiba as sugestões em um card visual distinto abaixo da caixa de chat.
- Implemente uma ação de clique único para preencher a caixa de entrada de comentário principal com o rascunho sugerido pela IA, permitindo que o moderador revise e edite antes de enviar.

### 4. Ações Rápidas de Moderação
Exponha gatilhos de ação rápida para moderação de comentários do Instagram:
- Implemente botões para ações de **Curtir (Coração)**, **Ocultar/Exibir** e **Excluir** usando `MaxIconButton` com os ícones correspondentes (`mdi:heart-outline`, `mdi:eye-off-outline`, `mdi:trash-can-outline`).
- Trate os estados de carregamento reativamente usando referências booleanas para cada requisição de ação.
- **Despache as ações via store `@maxvue/max-pinia`:** mutações na coleção de comentários/mensagens (curtir, ocultar/exibir, excluir) devem alterar o estado da store, que persiste automaticamente no backend Laravel 13 (auto-save debounced) através de `apiPostRoute`/`apiGetRoute` resolvendo caminhos string `/api/...`. NÃO faça requisições Axios REST manuais para dados de página.

### 5. Diretrizes de Código e Templates
- Sempre use a Composition API (`<script setup lang="ts">`) e SCSS (`<style scoped lang="scss">`).
- Mantenha todos os atributos do template HTML em uma única linha (sem formatação multilinha para atributos de elementos/componentes nos templates).
  - *Exemplo:* `<MaxButton class="btn-primary" :loading="isSubmitting" @click="submit" />`

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **PROIBIDO Options API:** Não utilize a Options API do Vue sob nenhuma circunstância.
- **Realtime padronizado:** Use sempre `@laravel/echo-vue` (`useEcho`) sobre o Laravel Reverb para novas integrações em tempo real. Não instancie `laravel-echo` cru nem misture outros clientes de socket — o Echo já vem configurado no bootstrap da app.
- **PROIBIDO Desvios de Layout (Layout Shifts):** Garanta que as atualizações de altura do scroll ocorram de forma suave ao carregar novas mensagens ou comentários dinamicamente, preservando a posição de rolagem do usuário caso ele tenha rolado para cima.
