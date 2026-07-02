---
name: adonisjs-brazilian-payments-asaas-integration-best-practices
description: Use when configuring, debugging, or creating payment integrations with the Asaas gateway in AdonisJS v6. Triggers on files handling customer registrations, invoice generation (Pix, Boleto, Credit Card), webhook signature verification, subscription billing sync, and payment logging.
---

# Boas Práticas de Integração do Gateway de Pagamentos Asaas no AdonisJS

## Objetivo
Estabelecer uma integração de pagamentos segura, resiliente e altamente modular com o gateway Asaas (API v3) no backend AdonisJS v6. Isso inclui a configuração do cliente HTTP, definição de modelos de banco de dados utilizando ULIDs, verificação de assinaturas de webhook e delegação do tratamento de eventos para filas do BullMQ.

## Instruções

### 1. Cliente HTTP e Configuração de Serviço
Implemente uma classe de serviço isolada para interagir com a API v3 do Asaas. Evite wrappers de bibliotecas de terceiros desatualizadas; prefira o `fetch` nativo do Node ou uma instância limpa do Axios. (Observação: `@adonisjs/http-client` é voltado a testes, não a chamadas HTTP de produção.)

* **Autenticação da API**: Use o cabeçalho `access_token` para enviar as credenciais.
* **Configuração de Ambiente**: Defina as variáveis de configuração no arquivo `start/env.ts` e no arquivo `#config/asaas.ts`.

Exemplo de configuração do Asaas:
```typescript
// start/env.ts
import { Env } from '@adonisjs/core/env'

export default await Env.create(new URL('../', import.meta.url), {
  ASAAS_API_KEY: Env.schema.string(),
  ASAAS_WEBHOOK_TOKEN: Env.schema.string(),
  ASAAS_API_URL: Env.schema.string({ format: 'url' }),
})

// config/asaas.ts
import env from '#start/env'

export default {
  apiKey: env.get('ASAAS_API_KEY'),
  webhookToken: env.get('ASAAS_WEBHOOK_TOKEN'),
  apiUrl: env.get('ASAAS_API_URL'),
}
```

Exemplo do wrapper de Serviço:
```typescript
import axios from 'axios'
import config from '#config/asaas'

export default class AsaasService {
  private static client = axios.create({
    baseURL: config.apiUrl,
    headers: {
      'access_token': config.apiKey,
      'Content-Type': 'application/json',
    },
  })

  static async createCustomer(data: { name: string; cpfCnpj: string; email: string }) {
    const response = await this.client.post('/customers', data)
    return response.data
  }

  static async createPayment(data: {
    customer: string
    billingType: 'PIX' | 'BOLETO' | 'CREDIT_CARD'
    value: number
    dueDate: string
    description?: string
  }) {
    const response = await this.client.post('/payments', data)
    return response.data
  }
}
```

### 2. Modelos de Banco de Dados e Lucid ORM
Utilize ULIDs para todos os modelos relacionados a faturamento e pagamentos. Mapeie corretamente os relacionamentos entre inquilinos (`SolarCompany` ou `User`) com `AsaasCustomer` e `AsaasInvoice`.

* **`AsaasCustomer`**: Vincula um inquilino/usuário local ao ID do cliente no Asaas.
* **`AsaasInvoice`**: Rastreia os status das transações (`PENDING`, `RECEIVED`, `CONFIRMED`, `OVERDUE`, `REFUNDED`).

Exemplo de implementação do Model:
```typescript
import { DateTime } from 'luxon'
import { BaseModel, beforeCreate, column, belongsTo } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import { ulid } from 'ulid'
import SolarCompany from '#models/solar_company'

export default class AsaasCustomer extends BaseModel {
  static table = 'asaas_customers'
  static selfAssignPrimaryKey = true

  @beforeCreate()
  static assignUlid(model: AsaasCustomer) {
    if (!model.id) model.id = ulid()
  }

  @column({ isPrimary: true })
  declare id: string

  @column()
  declare solarCompanyId: string

  @column()
  declare asaasCustomerId: string

  @column.dateTime({ autoCreate: true })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true })
  declare updatedAt: DateTime

  @belongsTo(() => SolarCompany)
  declare solarCompany: BelongsTo<typeof SolarCompany>
}
```

### 3. Autenticação e Validação de Webhooks
Proteja o endpoint do webhook contra chamadas não autorizadas validando o cabeçalho `asaas-access-token`.

* **Validação de Assinatura**: Compare o valor recebido no cabeçalho `asaas-access-token` com o token `ASAAS_WEBHOOK_TOKEN` configurado no ambiente usando comparação estrita.
* **Rapidez do Controller**: Salve o payload recebido imediatamente no banco de dados e responda com `200 OK` antes de fazer qualquer processamento pesado.

Exemplo de rotas e validação do webhook:
```typescript
// start/routes.ts
import router from '@adonisjs/core/services/router'
const AsaasWebhooksController = () => import('#controllers/asaas_webhooks_controller')

router.post('/webhooks/asaas', [AsaasWebhooksController, 'handle']).as('webhooks.asaas')

// app/controllers/asaas_webhooks_controller.ts
import type { HttpContext } from '@adonisjs/core/http'
import config from '#config/asaas'
import Webhook from '#models/webhook'
import AsaasWebhookJob from '#jobs/asaas_webhook_job'

export default class AsaasWebhooksController {
  async handle({ request, response }: HttpContext) {
    const signature = request.header('asaas-access-token')

    if (!signature || signature !== config.webhookToken) {
      return response.unauthorized({ error: 'Assinatura do webhook inválida' })
    }

    const payload = request.all()
    const eventId = payload.event

    // Cria registro persistente do webhook para auditoria e processamento
    const webhook = await Webhook.create({
      payload,
      routeName: 'webhooks.asaas',
      ip: request.ip(),
    })

    // Dispara o job em background via BullMQ
    await AsaasWebhookJob.dispatch(webhook.id)

    return response.ok({ received: true })
  }
}
```

### 4. Processamento Assíncrono com Filas (BullMQ)
Todo o processamento pesado de webhooks (atualizações de assinaturas, liberação de acessos, envio de e-mails) deve ser processado em background.

* **Idempotência**: Verifique se o evento já foi processado através do ID do webhook recebido no banco de dados para evitar duplicidade de faturamento.
* **Tratamento de Eventos**: Implemente um `AsaasWebhookJob` dedicado para interpretar cada tipo de evento (`PAYMENT_RECEIVED`, `PAYMENT_OVERDUE`, `PAYMENT_DELETED`).

Exemplo de estrutura do Job:
```typescript
import type { Job } from 'bullmq'
import { DateTime } from 'luxon'
import logger from '@adonisjs/core/services/logger'
import Webhook from '#models/webhook'
import { webhooksQueue } from '#services/queue_service'

export interface AsaasWebhookJobData {
  webhookId: string
}

export default class AsaasWebhookJob {
  static readonly queueName = 'webhooks'

  static async dispatch(webhookId: string) {
    await webhooksQueue.add('asaas_process', { webhookId })
  }

  static async handle(job: Job<AsaasWebhookJobData>) {
    const webhook = await Webhook.find(job.data.webhookId)
    if (!webhook || webhook.processedAt) return

    const payload = webhook.payload ?? {}
    const eventType = payload.event
    const paymentData = payload.payment

    logger.info({ webhookId: webhook.id, eventType }, 'Processando evento do Webhook Asaas')

    switch (eventType) {
      case 'PAYMENT_RECEIVED':
      case 'PAYMENT_CONFIRMED':
        // Atualiza fatura local e libera acessos do plano/assinatura
        break
      case 'PAYMENT_OVERDUE':
        // Bloqueia conta ou altera status da assinatura para past_due
        break
      default:
        logger.warn({ eventType }, 'Tipo de evento Asaas não tratado')
    }

    await webhook.merge({ processedAt: DateTime.now() }).save()
  }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* NUNCA execute chamadas síncronas de gravação na API do Asaas dentro do ciclo de vida HTTP do endpoint de webhook. Sempre use BullMQ.
* NUNCA aceite pacotes de webhook do Asaas sem validar o cabeçalho `asaas-access-token`.
* NUNCA utilize chaves numéricas autoincrementais para chaves primárias dos models de relacionamento com o Asaas; sempre utilize chaves de tipo ULID.
* NUNCA coloque tokens ou segredos de ambiente diretamente no código; use sempre `Env.schema`.
* NUNCA exponha credenciais ou arquivos de certificados brutos no repositório.
