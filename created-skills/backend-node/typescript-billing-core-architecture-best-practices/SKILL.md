---
name: typescript-billing-core-architecture-best-practices
description: Use when designing, implementing, reviewing, or debugging core subscription billing engines, payment gateway interfaces (Efí/Gerencianet, Banco Inter), subscription state machines, or webhook parsers in pure TypeScript. Triggers on files modifying billing-core, payment gateway adapters, webhook validation, and idempotency logic without framework dependencies.
---

## Objetivo
Garantir a aplicação estrita de arquitetura limpa e princípios de design em TypeScript puro para o mecanismo de faturamento de assinaturas e gateways de pagamento no ecossistema Engeapp/SocialMediaApp, garantindo desacoplamento total de frameworks web (AdonisJS, NestJS) e runtimes de front-end (Vue.js).

## Instruções

## 1. Restrição de TypeScript Puro e Zero-Framework
* Toda a lógica central de faturamento deve residir em uma biblioteca TypeScript pura dedicada (`billing-core` / `@maxvue/max-banks`).
* **Sem Importações de Frameworks:** Absolutamente nenhuma importação de `@adonisjs/*`, `vue` ou qualquer outro framework é permitida nos pacotes `core` e `node`.
* **Sem Acesso a Variáveis de Ambiente:** Dentro da biblioteca, nunca leia `process.env` ou use provedores de configuração globalmente. Todas as configurações, certificados e credenciais devem ser explicitamente injetados pela aplicação consumidora durante a inicialização/boot.

## 2. Separação de Arquitetura em Camadas
Garanta a divisão estrita de responsabilidade de código entre os diretórios da biblioteca:
* **`core/` (Camada Isomórfica):**
  - Deve ser totalmente isomórfica (funciona em Node, navegador, runtimes edge).
  - Estritamente sem APIs nativas do Node.js (`node:*`, `fs`, `path`, etc.) ou dependências como Axios/Fetch que dependam de variáveis globais do Node.
  - Contém enums, tipos canônicos e a máquina de estados de assinaturas.
* **`node/` (Camada de Ambiente Node.js):**
  - Contém implementações que exigem APIs do Node.js (por exemplo, leitura de arquivos para certificados, configurações de cliente mTLS e operações criptográficas).
  - Implementa os clientes de gateway de pagamento, adaptadores de requisições HTTP e verificações de assinatura de webhook.

## 3. Design da Máquina de Estados de Assinatura
* Mantenha uma máquina de estados finitos robusta para as transições de status de assinatura usando:
  - **Status (`SubscriptionStatus`):** `incomplete` (pagamento inicial pendente), `trialing`, `active`, `past_due` (falha no pagamento, tentando novamente), `grace` (período de tolerância antes da suspensão) e `canceled` (estado terminal).
  - **Eventos (`SubscriptionEvent`):** `start_trial`, `payment_confirmed`, `payment_failed`, `grace_expired`, `cancel`.
* Utilize funções auxiliares de transição (`transition`, `canTransition`) para validar ações:
  - Se uma transição for inválida, lance um erro customizado `InvalidTransitionError`.
  - Exponha uma função `grantsAccess(status: SubscriptionStatus): boolean` que determina se o estado de assinatura concede acesso ativo à aplicação (`active`, `trialing` e `past_due` concedem acesso; `grace` e `canceled` não concedem).

## 4. Abstração Desacoplada de Gateway de Pagamento
* Todas as integrações de faturamento devem depender estritamente da interface `PaymentGateway`:
  ```typescript
  export interface PaymentGateway {
      readonly name: string;
      createPixCharge(input: CreatePixChargeInput): Promise<Charge>;
      getCharge(txid: string): Promise<Charge>;
      parseWebhook(payload: unknown): CanonicalWebhookEvent;
  }
  ```
* Implemente adaptadores de gateway concretos (por exemplo, `EfiGateway`, `InterGateway`) em conformidade com este contrato.
* Valores financeiros devem ser sempre representados como um número inteiro em centavos usando a estrutura `Money` (`{ amountCents: number, currency: 'BRL' }`) para evitar erros de cálculo de ponto flutuante.

## 5. Parser de Webhook e Regras de Idempotência
* A aplicação consumidora deve confiar no evento de webhook como a fonte da verdade para confirmações de pagamento.
* Use `parseWebhook` para traduzir payloads específicos de gateways para o formato canônico `CanonicalWebhookEvent` contendo uma `idempotencyKey` única e determinística (por exemplo, combinando o `txid` e o `endToEndId` do gateway).
* O backend consumidor deve processar esses eventos por meio de um job idempotente (por exemplo, usando BullMQ) consultando a `idempotencyKey` ou ID da transação para evitar cobranças duplas ou créditos duplicados.

## 6. Testes Unitários Isolados
* Os testes unitários para a lógica do `core` e transições devem ser totalmente isolados.
* Faça mock de todas as requisições HTTP externas e interfaces de rede.
* Não dependa de conexões de banco de dados, migrações ou variáveis de ambiente ativas durante a execução dos testes.

## Restrições
* Nunca importe provedores, models ou controllers específicos de frameworks dentro da biblioteca.
* Nunca coloque credenciais de pagamento ou buscas de variáveis de ambiente hardcoded.
* Nunca ignore a máquina de estados ao atualizar status de assinatura; sempre invoque a função `transition` para garantir o fluxo de ciclo de vida válido.
* Nunca permita transições a partir do estado terminal `canceled`.
