---
name: adonisjs-brazilian-payments-asaas-integration-best-practices
description: "Use when configuring, debugging, or creating payment integrations with the Asaas gateway in AdonisJS v6. Triggers on files handling customer registrations, invoice generation (Pix, Boleto, Credit Card), webhook signature verification, subscription billing sync, and payment logging."
author: Johnattas Conrady Gomes Santana
---
# Integração de Pagamentos com Asaas no AdonisJS v6

## Objetivo
Padronizar, proteger e estruturar a integração com o gateway de pagamentos brasileiro **Asaas** em aplicações backend desenvolvidas com **AdonisJS v6** e **TypeScript**. Estabelecer padrões para clientes HTTP dedicados, tipagem estrita de payloads, geração e controle de cobranças (Pix, Boleto, Cartão de Crédito), assinaturas recorrentes, processamento assíncrono e idempotente de webhooks com BullMQ, e observabilidade com logging seguro.

---

## Instruções

### 1. Arquitetura de Serviços e Configuração de Ambiente
Centralize as credenciais e conexões com o Asaas em arquivos de configuração e serviços dedicados no AdonisJS:

* **Configuração de Ambiente (`start/env.ts` e `.env`):**
  Declare e valide as variáveis de ambiente necessárias via `@adonisjs/env`:
  ```typescript
  ASAAS_BASE_URL: Env.schema.string(), // 'https://api-sandbox.asaas.com' (sandbox) ou 'https://api.asaas.com' (produção)
  ASAAS_API_KEY: Env.schema.string(),  // Chave de API fornecida pelo Asaas ($aact_...)
  ASAAS_WEBHOOK_TOKEN: Env.schema.string(), // Token customizado para validação de webhooks
  ```

* **Arquivo de Configuração (`config/asaas.ts`):**
  ```typescript
  import env from '#start/env'

  export const asaasConfig = {
    baseUrl: env.get('ASAAS_BASE_URL', 'https://api-sandbox.asaas.com'),
    apiKey: env.get('ASAAS_API_KEY'),
    webhookToken: env.get('ASAAS_WEBHOOK_TOKEN'),
    timeoutMs: 15000,
  }
  ```

* **Cliente HTTP Base (`app/services/asaas_client.ts`):**
  Isole as chamadas HTTP em um cliente dedicado (usando `fetch` nativo do Node.js ou `axios`/`got`), injetando os headers obrigatórios:
  ```typescript
  import { asaasConfig } from '#config/asaas'
  import logger from '@adonisjs/core/services/logger'

  export class AsaasClient {
    private static baseUrl = asaasConfig.baseUrl.replace(/\/+$/, '')
    private static apiKey = asaasConfig.apiKey

    public static async request<T = any>(
      endpoint: string,
      options: RequestInit = {}
    ): Promise<T> {
      const url = `${this.baseUrl}/v3${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`
      const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'access_token': this.apiKey,
        ...(options.headers || {}),
      }

      const response = await fetch(url, {
        ...options,
        headers,
        signal: AbortSignal.timeout(asaasConfig.timeoutMs),
      })

      const data = await response.json().catch(() => null)

      if (!response.ok) {
        logger.error({ status: response.status, data, endpoint }, 'Falha na comunicação com Asaas')
        throw new Error(data?.errors?.[0]?.description || `Erro Asaas HTTP ${response.status}`)
      }

      return data as T
    }
  }
  ```

---

### 2. Gerenciamento e Deduplicação de Clientes (`/v3/customers`)
Antes de criar qualquer cobrança, o cliente deve estar cadastrado no Asaas. Evite duplicação de cadastros:

1. **Consulta Prévia:** Antes de chamar `POST /v3/customers`, consulte por CPF/CNPJ (`GET /v3/customers?cpfCnpj=...`) ou armazene o `asaas_customer_id` no modelo Lucid do cliente/empresa.
2. **Sincronização de Metadados:** Armazene identificadores internos (`externalReference`) no payload do Asaas para cruzamento de dados.
3. **Estrutura do Modelo:**
   ```typescript
   // Exemplo no Model Lucid
   @column()
   declare asaasCustomerId: string | null
   ```

---

### 3. Emissão de Cobranças (Pix, Boleto e Cartão de Crédito)
Mapeie a emissão de cobranças através de um serviço de domínio (`app/services/asaas_payment_service.ts`):

* **Armazenamento de Valores:**
  No banco de dados local, armazene sempre valores em centavos (`integer`) para precisão aritmética. Na comunicação com a API do Asaas, converta para decimal (`value: cents / 100`).

* **Cobrança via Pix (`billingType: 'PIX'`):**
  - Crie o pagamento via `POST /v3/payments`.
  - Obtenha o QR Code e a chave Copia e Cola via `GET /v3/payments/{id}/pixQrCode`.
  - Retorne os dados para renderização no frontend.

* **Cobrança via Boleto Bancário (`billingType: 'BOLETO'`):**
  - Defina `dueDate`, juros (`interest`), multa (`fine`) e desconto se aplicável.
  - Extraia `bankSlipUrl` (link do PDF) e `identificationField` (linha digitável) do retorno.

* **Cobrança via Cartão de Crédito (`billingType: 'CREDIT_CARD'`):**
  - Receba dados tokenizados pelo frontend ou objeto `creditCard` + `creditCardHolderInfo`.
  - Suporte parcelamento especificando `installmentCount` e `installmentValue`.
  - **Atenção:** Nunca persista dados do cartão (número completo ou CVV) no banco de dados local.

---

### 4. Assinaturas e Cobrança Recorrente (`/v3/subscriptions`)
Para modelos SaaS e planos com renovação automática:
* Utilize o endpoint `POST /v3/subscriptions`.
* Defina o ciclo de cobrança (`cycle: 'WEEKLY' | 'BIWEEKLY' | 'MONTHLY' | 'BIMONTHLY' | 'QUARTERLY' | 'SEMIANNUALLY' | 'YEARLY'`).
* Armazene `asaas_subscription_id` e controle o status da assinatura localmente (`ACTIVE`, `EXPIRED`, `OVERDUE`, `CANCELED`).

---

### 5. Recepção Segura e Processamento Assíncrono de Webhooks
Os webhooks do Asaas notificam mudanças de status (`PAYMENT_RECEIVED`, `PAYMENT_CONFIRMED`, `PAYMENT_OVERDUE`, etc.).

* **Endpoint de Webhook (`POST /api/webhooks/asaas`):**
  Crie um controller dedicado (`app/controllers/asaas_webhooks_controller.ts`):
  ```typescript
  import type { HttpContext } from '@adonisjs/core/http'
  import { asaasConfig } from '#config/asaas'
  import { ProcessAsaasWebhookJob } from '#jobs/process_asaas_webhook_job'
  import PaymentWebhook from '#models/payment_webhook'
  import logger from '@adonisjs/core/services/logger'

  export default class AsaasWebhooksController {
    public async handle({ request, response }: HttpContext) {
      // 1. Validação de segurança pelo header de token
      const token = request.header('asaas-access-token')
      if (token !== asaasConfig.webhookToken) {
        logger.warn({ tokenRecebido: token }, 'Tentativa de webhook com token inválido')
        return response.unauthorized({ message: 'Token de webhook inválido' })
      }

      const payload = request.body()
      const eventType = payload.event
      const paymentId = payload.payment?.id || payload.subscription?.id

      if (!eventType || !paymentId) {
        return response.badRequest({ message: 'Payload incompleto' })
      }

      // 2. Registro do evento bruto no banco (tabela payment_webhooks)
      const webhookRecord = await PaymentWebhook.create({
        gateway: 'asaas',
        eventId: payload.id || `${eventType}_${paymentId}_${Date.now()}`,
        eventType: eventType,
        paymentId: paymentId,
        payload: payload,
        status: 'pending',
      })

      // 3. Despacho do job em background (BullMQ)
      await ProcessAsaasWebhookJob.dispatch({ webhookId: webhookRecord.id })

      // 4. Resposta imediata 200 OK
      return response.ok({ received: true })
    }
  }
  ```

* **Idempotência Estrita no Job de Processamento:**
  No job BullMQ:
  - Verifique se a transação correspondente já atingiu o status final.
  - Utilize locks transacionais (`db.transaction()`) ao atualizar saldo, créditos ou planos do usuário.
  - Atualize o status do registro em `payment_webhooks` para `processed` ou `failed`.

---

### 6. Logging Seguro e Observabilidade
* Registre todas as requisições enviadas e eventos recebidos utilizando o logger nativo do AdonisJS (`@adonisjs/core/services/logger`).
* **Mascaramento:** Sanitização obrigatória de payloads para ocultar dados confidenciais (números de cartão, CVV, senhas e tokens).
* Utilize métricas e alertas para notificações com status `PAYMENT_REFUNDED`, `PAYMENT_CHARGEBACK_REQUESTED` ou `PAYMENT_DUNNING_RECEIVED`.

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** processe webhooks do Asaas de forma síncrona dentro do controller HTTP; sempre registre o evento e despache um job em background.
- **NÃO** ignore a validação do header de segurança `asaas-access-token` nas rotas de webhook.
- **NÃO** armazene números completos de cartão de crédito (PAN) ou códigos de segurança (CVV) no banco de dados da aplicação.
- **NÃO** deixe tokens, chaves de API (`ASAAS_API_KEY`) ou URLs de ambiente hardcoded no código.
- **NÃO** execute mutações de saldo ou liberação de serviços sem garantia de idempotência no processamento dos webhooks.
- **Comentários de código:** Todos os comentários em arquivos de código criados ou alterados devem estar estritamente em **Português do Brasil (pt-BR)**.
