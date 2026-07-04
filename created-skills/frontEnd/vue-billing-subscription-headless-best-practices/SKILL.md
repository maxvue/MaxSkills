---
name: vue-billing-subscription-headless-best-practices
description: Use when creating, reviewing, or refactoring Vue 3 frontend components, stores, or views for SaaS billing and subscription flows, including checkout modals, subscription state management via @maxvue/max-pinia stores, and plans display integrated with @maxvue/max-components-ui. Triggers on billing store, subscription state, checkout flow, or plans modal work.
---

## Objetivo
Fornecer diretrizes claras de arquitetura e implementação para integrar fluxos de faturamento (billing) e assinatura (subscription) SaaS no front-end Vue 3, compartilhando o estado globalmente via store `@maxvue/max-pinia` (que faz os GETs cacheados e o auto-save ao backend Laravel) e entregando um design visual premium com `@maxvue/max-components-ui`.

## Instruções

## 1. Gerenciamento de Estado via Store `@maxvue/max-pinia`
* **Store Centralizada**: Não faça `fetch`/`axios` manual em cada componente de página. Em vez disso, defina uma store `@maxvue/max-pinia` (ex: `useBillingStore` em `resources/Stores/billingStore.ts`) que carrega os dados via caminho string `/api/...` (resolvido por `apiGetRoute` do `@maxvue/max-use`).
* **GET cacheado + auto-save**: TODO GET de status de assinatura, planos e faturas DEVE passar pela store MaxPinia, que mantém cache reativo e evita requisições redundantes. Alterações feitas no estado são salvas automaticamente no backend (auto-save/debounced); não escreva POSTs manuais de salvamento por submit.
* **Estados da Assinatura**: Mapeie e trate todos os estados padrão de assinatura definidos no backend:
  - `trialing`: O usuário está no período de testes. Permita acesso completo, mas exiba um banner discreto informando os dias restantes.
  - `active`: Assinatura totalmente paga. Estado ativo padrão.
  - `past_due`: Falha no pagamento. Exiba uma notificação de aviso não obstrutiva ou um banner de período de carência.
  - `grace`: Assinatura em período de carência antes da suspensão. Exiba um alerta para atualizar o pagamento.
  - `canceled`: Assinatura cancelada/encerrada. Bloqueie o acesso às funcionalidades principais imediatamente.
  - `incomplete`: Pagamento de configuração pendente. Direcione o usuário para a tela de checkout.

```typescript
// Exemplo: Store @maxvue/max-pinia para Faturamento
// O GET do status/planos/faturas passa pela store (cache + auto-save via plugin).
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface Subscription {
    status: 'trialing' | 'active' | 'past_due' | 'grace' | 'canceled' | 'incomplete';
}

export const useBillingStore = defineStore('billing', () => {
    const isCached = ref(true);
    const data = ref<Subscription | null>(null);

    // GET automático via plugin; route é caminho string /api/... (a store chama apiGetRoute internamente); sem rotas nomeadas estilo Ziggy.
    const options = computed(() => ({
        get: { route: '/api/billing/subscription' },
    }));

    // `data` é populado/cacheado pela store MaxPinia.
    const isActive = computed(
        () => !!data.value && ['active', 'trialing'].includes(data.value.status),
    );
    const isPastDue = computed(() => data.value?.status === 'past_due');

    return { data, isCached, options, isActive, isPastDue };
});
```

## 2. Fluxos de Checkout Headless
* **Inicialização**: Gerencie a criação da assinatura e a troca de planos através da store MaxPinia, disparando a ação via caminho string `/api/...` (ex: `apiPostRoute('/api/billing/checkout')`). Não faça `axios.post` manual.
* **Métodos de Pagamento**:
  - **Pix (Pagamento Instantâneo)**: Quando o checkout retornar uma transação Pix, exiba o QR Code claramente junto com um botão de "Copiar Código Pix" (Pix Copia e Cola). Garanta que o layout seja elegante usando painéis do tipo card.
  - **Cartão de Crédito**: Renderize os campos de entrada de cartão protegidos pela API do gateway de pagamento. Implemente a validação do lado do cliente utilizando padrões padrão.
* **Confirmação em Tempo Real (WebSocket)**: Em vez de fazer polling contínuo da API, utilize **Laravel Reverb + `@laravel/echo-vue`** (`useEcho`) para escutar o evento de confirmação disparado pelo webhook do backend. Mude automaticamente o modal de checkout para o estado "Sucesso" quando o evento de confirmação de pagamento for recebido no front-end.

## 3. Estilização da UI com `MaxComponentsUi` e SCSS
* **Estrutura SFC (Single-File Component)**: Todos os componentes de checkout e faturamento devem seguir rigidamente a ordem dos blocos SFC:
  1. `<template>`
  2. `<script setup lang="ts">`
  3. `<style scoped lang="scss">`
* **Formatação de Atributos em Linha Única**: No template, formate todos os componentes de UI do Vue mantendo os atributos em uma única linha. Não quebre os atributos em múltiplas linhas.
  - **Correto**: `<MaxModal ref="modalRef" title="Subscrição" subTitle="Gerencie seu plano" width="600" />` — o `MaxModal` NÃO tem prop `visible` nem evento `@close`; ele é controlado pelo próprio botão/slot embutido ou imperativamente por um template ref chamando os métodos expostos `show()` / `hide()` / `toggle()`.
* **Variáveis de Tema**: Use variáveis CSS baseadas no tema (`var(--max-primary-500)`, `var(--background-200)`) para destacar os cards de plano, badges de status e tabelas de transações. Não utilize cores hexadecimais estáticas (hardcoded).
* **Apresentação Visual**: Renderize o histórico de faturamento usando componentes de tabela, exibindo colunas como `ID da Fatura`, `Data`, `Valor`, `Status` (Pago, Pendente, Falhou) e um link para download do PDF da fatura.

## 4. Proteção de Rotas e Bloqueios no Front-end (Enforcement)
* **Guarda de Rotas (Route Guards)**: Proteja as rotas que exigem assinatura ativa utilizando guardas de navegação do Vue Router. Valide o estado na store Pinia `useBillingStore` antes de permitir o acesso aos painéis de controle ou módulos de IA.
* **Tela de Bloqueio (Overlay)**: Se a assinatura do usuário estiver como `canceled` ou se estiver como `past_due` além do período de carência, exiba uma tela inteira de bloqueio (blocking overlay) ou redirecione-o para uma página de faturamento (`/billing`) que limite o acesso aos recursos do sistema até que o pagamento seja regularizado.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Composition API**: Você deve escrever o código do front-end usando `<script setup lang="ts">`. A Options API é estritamente proibida.
* **Sem CSS Puro**: Não escreva CSS vanilla; utilize SCSS com variáveis de tema ou UnoCSS.
* **Layout de Atributos**: Nunca quebre atributos de componentes Vue em múltiplas linhas dentro do `<template>`.
* **Sem importação direta do .env**: O front-end nunca deve ler chaves de API do gateway diretamente de variáveis de ambiente. Elas devem residir apenas no backend Laravel por questões de segurança.
* **Localização Brasileira**: Formate valores monetários usando `Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })` e formate datas usando DayJS ou Luxon em pt-BR.
