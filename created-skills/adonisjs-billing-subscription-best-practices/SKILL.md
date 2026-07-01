---
name: adonisjs-billing-subscription-best-practices
description: Use when designing, implementing, configuring, or debugging SaaS subscription models, recurring billing, or payment gateway integrations (Efí, Banco Inter) in AdonisJS. Triggers on setting up billing-core, billing-adonis adapter, migrations, subscription state machines, webhook handling via BullMQ jobs, and billing enforcement middlewares.
---

# Boas Práticas de Faturamento e Assinatura no AdonisJS

## Objetivo
Estabelecer uma arquitetura de faturamento e assinaturas modular, desacoplada e segura no AdonisJS v6. Suporta múltiplos gateways (Efí, Banco Inter) usando um núcleo unificado baseado em TypeScript, garante a idempotência nos webhooks por meio do processamento com BullMQ e impõe controles de acesso aos inquilinos (tenants) no nível da empresa solar.

## Instruções

### 1. Arquitetura Modular Desacoplada
Organize a lógica de pagamento e faturamento em três camadas principais:
* **`billing-core` (Camada de Domínio)**: Pacote TypeScript puro contendo drivers de gateway, DTOs e contratos de interface. Absolutamente nenhuma dependência direta do AdonisJS.
  * Defina uma interface comum `PaymentGateway` contendo métodos como `createCustomer`, `createSubscription`, `cancelSubscription` e `handleWebhook`.
  * Instancie os drivers (ex: `EfiGateway`, `InterGateway`) usando um padrão de fábrica (factory pattern), mantendo singletons para os clientes de API.
* **`billing-adonis` (Adaptador do Framework)**: Contém Service Providers, models/migrations de banco de dados, controllers para endpoints de webhook e middlewares de rota.
* **`billing-vue` (Camada Frontend)**: Componentes Vue 3 e elementos de interface headless-first para renderizar telas de pagamento e gerenciar checkouts. O status do plano atual e demais dados de página DEVEM ser lidos e atualizados através de uma store `@maxvue/max-pinia` (com cache e auto-save/debounced), NUNCA via fetch manual de status. Rotas são caminhos string `/api/...` resolvidos por `apiGetRoute`/`apiPostRoute` do `@maxvue/max-use`.

### 2. Esquema de Banco de Dados e Mapeamento Lucid ORM
Implemente tabelas usando ULID como chaves primárias. Estruture os relacionamentos cuidadosamente em torno do model de Tenant (ex: `SolarCompany`):

* **`plans`**: Armazena o catálogo de planos (`id`, `name`, `price`, `interval`, `gateway_plan_id`).
* **`subscriptions`**: Rastreia os estados ativos de faturamento recorrente (`id`, `solar_company_id`, `plan_id`, `status`, `current_period_end`, `gateway_subscription_id`).
  * Defina estados padrão de assinatura: `pending`, `trialing`, `active`, `past_due`, `canceled`.
* **`invoices`**: Registra as tentativas de cobrança (`id`, `subscription_id`, `amount`, `status`, `payment_method`, `due_date`, `paid_at`).
* **`webhook_events`**: Armazena os payloads brutos dos webhooks recebidos do gateway para evitar a execução duplicada de eventos (`id` [ID do evento no gateway], `gateway`, `payload`, `processed_at`).

Exemplo do model de assinatura:
```typescript
import { DateTime } from 'luxon'
import { BaseModel, beforeCreate, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import { ulid } from 'ulid'
import SolarCompany from '#models/solar_company'
import Plan from '#models/plan'

export default class Subscription extends BaseModel {
  static selfAssignPrimaryKey = true

  @beforeCreate()
  static assignUlid(model: Subscription) {
    if (!model.id) model.id = ulid()
  }

  @column({ isPrimary: true })
  declare id: string

  @column()
  declare solarCompanyId: string

  @column()
  declare planId: string

  @column()
  declare status: 'pending' | 'trialing' | 'active' | 'past_due' | 'canceled'

  @column.dateTime()
  declare currentPeriodEnd: DateTime

  @column()
  declare gatewaySubscriptionId: string

  @belongsTo(() => SolarCompany)
  declare solarCompany: BelongsTo<typeof SolarCompany>

  @belongsTo(() => Plan)
  declare plan: BelongsTo<typeof Plan>
}
```

### 3. Idempotência de Webhooks e Delegação para Fila
Sempre trate os eventos de webhook de pagamento recebidos de forma assíncrona para garantir alta disponibilidade e confiabilidade:
1. **Registre Imediatamente**: Valide a assinatura recebida, salve o payload bruto na tabela `webhook_events` e verifique se o ID do evento já existe para evitar o processamento duplicado.
2. **Responda Rápido**: Retorne uma resposta HTTP `200 OK` para o gateway de pagamento imediatamente.
3. **Processe na Fila**: Dispare um job em segundo plano usando BullMQ (ex: `ProcessWebhookJob`) contendo o ID do evento registrado para realizar as alterações reais de estado (atualizar o status da assinatura, emitir faturas, enviar e-mails de notificação).

Exemplo de estrutura de Controller:
```typescript
import { HttpContext } from '@adonisjs/core/http'
import WebhookEvent from '#models/webhook_event'
import ProcessWebhookJob from '#jobs/process_webhook_job'

export default class WebhooksController {
  async handle({ request, response }: HttpContext) {
    const gateway = request.param('gateway')
    const payload = request.body()
    const eventId = request.header('X-Gateway-Event-Id') || payload.event_id

    if (!eventId) {
      return response.badRequest({ error: 'Missing event identifier' })
    }

    // 1. Verificar assinatura do gateway ANTES de qualquer operação no banco
    // (implementação varia por gateway — exemplo para HMAC genérico):
    const rawBody = request.raw() ?? ''
    const gatewaySignature = request.header('X-Gateway-Signature') ?? ''
    const expectedSig = 'sha256=' + crypto
      .createHmac('sha256', env.get('PAYMENT_GATEWAY_WEBHOOK_SECRET'))
      .update(rawBody)
      .digest('hex')
    if (!crypto.timingSafeEqual(Buffer.from(gatewaySignature), Buffer.from(expectedSig))) {
      return response.unauthorized({ error: 'Invalid webhook signature' })
    }

    // 2. Verificar idempotência
    const existing = await WebhookEvent.find(eventId)
    if (existing) {
      return response.ok({ status: 'already_received' })
    }

    // 3. Persistir o evento após validação
    const event = await WebhookEvent.create({
      id: eventId,
      gateway,
      payload,
    })

    // Delegar processamento para o job BullMQ
    await ProcessWebhookJob.dispatch(event.id)

    return response.ok({ status: 'queued' })
  }
}
```

### 4. Middleware de Enforcement de Faturamento
Proteja as rotas da aplicação verificando o status de faturamento do Tenant atual usando um middleware HTTP:
* Extraia o contexto da empresa solar atual.
* Verifique se `SolarCompany.isActive` é verdadeiro e se há uma `Subscription` ativa ou em período de testes (`trialing`) que não tenha expirado.
* Conceda um período de carência (ex: 3 dias) para estados de inadimplência (`past_due`) antes de bloquear o acesso completamente.
* Se não estiver autorizado, interrompa a requisição e retorne um status HTTP `402 Payment Required` personalizado ou redirecione para a página de faturamento/checkout.

```typescript
import type { HttpContext } from '@adonisjs/core/http'
import type { NextFn } from '@adonisjs/core/types/http'

export default class BillingEnforcementMiddleware {
  async handle(ctx: HttpContext, next: NextFn) {
    const { auth, response } = ctx
    const user = auth.user
    
    if (!user || !user.solarCompanyId) {
      return next()
    }

    await user.load('solarCompany', (query) => {
      query.preload('subscriptions', (subQuery) => {
        subQuery.where('status', 'active').orWhere('status', 'trialing')
      })
    })

    const company = user.solarCompany
    const hasActiveSub = company.subscriptions.length > 0

    if (!company.isActive || !hasActiveSub) {
      return response.paymentRequired({
        message: 'Acesso suspenso. Assinatura ativa necessária.',
        code: 'BILLING_SUSPENDED'
      })
    }

    return next()
  }
}
```

### 5. Integração Segura de Pagamentos (Efí, Banco Inter)
* Armazene todos os certificados (arquivos `.pem` / `.key`) e segredos de cliente (client secrets) de forma segura em storage/app/certificates ou diretórios de ambiente privados.
* Nunca envie certificados para o controle de versão. Refira-se aos caminhos no `.env`.
* Envolva com segurança as respostas do cliente de pagamento em blocos try/catch, lançando exceções de domínio normalizadas personalizadas (ex: `PaymentGatewayException`).

## Restrições
* NUNCA execute requisições de API de gateways de terceiros de forma síncrona dentro do ciclo de requisição/resposta HTTP principal para webhooks. Use o BullMQ.
* NUNCA codifique credenciais ou conteúdos de arquivos de certificado de forma estática (hardcoded). Sempre faça referência a eles via `env` (variáveis de ambiente) ou um arquivo de configuração dedicado de billing (ex: `#config/billing`).
* NUNCA use IDs numéricos auto-incrementáveis para planos, assinaturas, faturas ou logs de eventos de webhook. Use ULIDs.
* NUNCA execute atualizações de faturamento sem realizar verificações de idempotência nas tabelas de `webhook_events` primeiro.
* NUNCA verifique o status de faturamento diretamente em todos os controllers de rota. Use um middleware `BillingEnforcementMiddleware` unificado.
