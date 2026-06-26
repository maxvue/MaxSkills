---
name: vue-billing-subscription-headless-best-practices
description: Use when creating, reviewing, or refactoring Vue 3 frontend components, composables, or views for SaaS billing and subscription flows, including checkout modals, subscription state management, and plans display integrated with MaxComponentsUi. Triggers on useCheckout, useSubscription, plans modal, or billing-vue integrations.
---

## Objetivo
Fornecer diretrizes claras de arquitetura e implementação para integrar fluxos de faturamento (billing) e assinatura (subscription) SaaS no front-end Vue 3 usando os composables headless-first (`useCheckout` e `useSubscription`) do pacote `billing-vue`, compartilhando o estado globalmente via Pinia e entregando um design visual premium com `@maxvue/max-components-ui`.

## Instruções

## 1. Gerenciamento de Estado e `useSubscription`
* **Store Centralizada**: Não invoque `useSubscription()` diretamente em cada componente de página individual. Em vez disso, envolva-o em uma store do Pinia (ex: `useBillingStore` em `resources/Stores/billingStore.ts`).
* **Cache Reativo**: A store deve manter em cache o status da assinatura, planos e listas de faturas para evitar requisições redundantes ao backend.
* **Estados da Assinatura**: Mapeie e trate todos os estados padrão de assinatura definidos no backend:
  - `trialing`: O usuário está no período de testes. Permita acesso completo, mas exiba um banner discreto informando os dias restantes.
  - `active`: Assinatura totalmente paga. Estado ativo padrão.
  - `past_due`: Falha no pagamento. Exiba uma notificação de aviso não obstrutiva ou um banner de período de carência.
  - `grace`: Assinatura em período de carência antes da suspensão. Exiba um alerta para atualizar o pagamento.
  - `canceled`: Assinatura cancelada/encerrada. Bloqueie o acesso às funcionalidades principais imediatamente.
  - `incomplete`: Pagamento de configuração pendente. Direcione o usuário para a tela de checkout.

```typescript
// Exemplo: Padrão de Store Pinia para Faturamento
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useSubscription } from '@/composables/useSubscription'; // importado de billing-vue

export const useBillingStore = defineStore('billing', () => {
    const { subscription, loading, fetchSubscription } = useSubscription();
    const activeStates = ['active', 'trialing'];

    const isActive = computed(() => {
        return subscription.value && activeStates.includes(subscription.value.status);
    });

    const isPastDue = computed(() => {
        return subscription.value?.status === 'past_due';
    });

    return {
        subscription,
        loading,
        isActive,
        isPastDue,
        fetchSubscription
    };
});
```

## 2. Fluxos de Checkout Headless com `useCheckout`
* **Inicialização**: Use o composable `useCheckout` para gerenciar a criação da assinatura e a troca de planos.
* **Métodos de Pagamento**:
  - **Pix (Pagamento Instantâneo)**: Quando o checkout retornar uma transação Pix, exiba o QR Code claramente junto com um botão de "Copiar Código Pix" (Pix Copia e Cola). Garanta que o layout seja elegante usando painéis do tipo card.
  - **Cartão de Crédito**: Renderize os campos de entrada de cartão protegidos pela API do gateway de pagamento. Implemente a validação do lado do cliente utilizando padrões padrão.
* **Confirmação em Tempo Real (SSE/Transmissão)**: Em vez de fazer polling contínuo da API, utilize o `@adonisjs/transmit-client` ou Server-Sent Events (SSE) para escutar a transmissão de confirmação do webhook do backend. Mude automaticamente o modal de checkout para o estado "Sucesso" quando o evento de confirmação de pagamento for recebido no front-end.

## 3. Estilização da UI com `MaxComponentsUi` e SCSS
* **Estrutura SFC (Single-File Component)**: Todos os componentes de checkout e faturamento devem seguir rigidamente a ordem dos blocos SFC:
  1. `<template>`
  2. `<script setup lang="ts">`
  3. `<style scoped lang="scss">`
* **Formatação de Atributos em Linha Única**: No template, formate todos os componentes de UI do Vue mantendo os atributos em uma única linha. Não quebre os atributos em múltiplas linhas.
  - **Correto**: `<MaxModal :visible="showModal" @close="closeModal" title="Subscrição" width="600" />`
* **Variáveis de Tema**: Use variáveis CSS baseadas no tema (`var(--max-primary-500)`, `var(--background-200)`) para destacar os cards de plano, badges de status e tabelas de transações. Não utilize cores hexadecimais estáticas (hardcoded).
* **Apresentação Visual**: Renderize o histórico de faturamento usando componentes de tabela, exibindo colunas como `ID da Fatura`, `Data`, `Valor`, `Status` (Pago, Pendente, Falhou) e um link para download do PDF da fatura.

## 4. Proteção de Rotas e Bloqueios no Front-end (Enforcement)
* **Guarda de Rotas (Route Guards)**: Proteja as rotas que exigem assinatura ativa utilizando guardas de navegação do Vue Router. Valide o estado na store Pinia `useBillingStore` antes de permitir o acesso aos painéis de controle ou módulos de IA.
* **Tela de Bloqueio (Overlay)**: Se a assinatura do usuário estiver como `canceled` ou se estiver como `past_due` além do período de carência, exiba uma tela inteira de bloqueio (blocking overlay) ou redirecione-o para uma página de faturamento (`/billing`) que limite o acesso aos recursos do sistema até que o pagamento seja regularizado.

## Restrições
* **Composition API**: Você deve escrever o código do front-end usando `<script setup lang="ts">`. A Options API é estritamente proibida.
* **Sem CSS Puro**: Não escreva CSS vanilla; utilize SCSS com variáveis de tema ou UnoCSS.
* **Layout de Atributos**: Nunca quebre atributos de componentes Vue em múltiplas linhas dentro do `<template>`.
* **Sem importação direta do .env**: A biblioteca cliente `billing-vue` nunca deve ler chaves de API do gateway diretamente de variáveis de ambiente no front-end. Elas devem residir apenas no backend por questões de segurança.
* **Localização Brasileira**: Formate valores monetários usando `Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })` e formate datas usando DayJS ou Luxon em pt-BR.
