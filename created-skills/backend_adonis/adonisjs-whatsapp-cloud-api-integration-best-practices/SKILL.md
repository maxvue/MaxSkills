---
name: adonisjs-whatsapp-cloud-api-integration-best-practices
description: Use when configuring, reviewing, or debugging WhatsApp Cloud API integrations and Webhook reception in AdonisJS. Triggers on WhatsApp service development, sending template messages, managing webhook verification, verifying X-Hub-Signature-256, and offloading webhook payloads to BullMQ jobs in Node.js.
---

# Melhores Práticas para Integração da WhatsApp Cloud API no AdonisJS

## Objetivo
Fornecer diretrizes seguras, performáticas e resilientes para a integração com a WhatsApp Cloud API e o processamento de payloads de webhook no AdonisJS v6. O objetivo principal é garantir respostas instantâneas à Meta (respeitando o limite de timeout de 3 segundos) por meio de delegação assíncrona para filas, certificar a autenticidade dos payloads e manter registros robustos de auditoria.

## Instruções

### 1. Configuração de Ambiente e Variáveis
* Configure de forma segura as credenciais do WhatsApp utilizando variáveis de ambiente. Acesse-as por meio da camada de configuração do AdonisJS.
* Variáveis necessárias no arquivo `.env`:
  ```env
  WHATSAPP_TOKEN=seu_token_de_acesso_permanente
  WHATSAPP_PHONE_NUMBER_ID=seu_id_do_numero_de_telefone
  WHATSAPP_BUSINESS_ACCOUNT_ID=seu_id_da_conta_whatsapp_business
  WHATSAPP_WEBHOOK_VERIFY_TOKEN=seu_token_customizado_de_verificacao_do_webhook
  WHATSAPP_APP_SECRET=seu_segredo_do_app_da_meta
  WHATSAPP_GRAPH_VERSION=v24.0
  ```
* Registre estas variáveis em `start/env.ts` para validação estrita dos tipos.

### 2. Serviço de Integração Dedicado
* Crie uma classe de serviço dedicada (`WhatsAppService`) para isolar o transporte HTTP externo.
* Utilize a API nativa `fetch` para realizar requisições para a API do Meta Graph.
* Implemente métodos estruturados para o envio de mensagens de texto e de mensagens interativas baseadas em templates.
* Exemplo de implementação do `WhatsAppService`:
  ```typescript
  import logger from '@adonisjs/core/services/logger'
  import env from '#start/env'

  export interface WhatsAppMessagePayload {
    messaging_product: 'whatsapp'
    to: string
    type: 'text' | 'template'
    text?: { body: string }
    template?: {
      name: string
      language: { code: string }
      components: any[]
    }
  }

  export class WhatsAppService {
    private baseUrl = 'https://graph.facebook.com/'
    private token: string
    private phoneNumberId: string
    private version: string

    constructor() {
      this.token = env.get('WHATSAPP_TOKEN', '')
      this.phoneNumberId = env.get('WHATSAPP_PHONE_NUMBER_ID', '')
      this.version = env.get('WHATSAPP_GRAPH_VERSION', 'v24.0')
    }

    private getRequestUrl(): string {
      return `${this.baseUrl}${this.version}/${this.phoneNumberId}/messages`
    }

    async sendText(to: string, body: string): Promise<Record<string, any>> {
      return this.send({
        messaging_product: 'whatsapp',
        to,
        type: 'text',
        text: { body },
      })
    }

    async sendTemplate(
      to: string,
      templateName: string,
      languageCode: string = 'pt_BR',
      components: any[] = []
    ): Promise<Record<string, any>> {
      return this.send({
        messaging_product: 'whatsapp',
        to,
        type: 'template',
        template: {
          name: templateName,
          language: { code: languageCode },
          components,
        },
      })
    }

    private async send(payload: WhatsAppMessagePayload): Promise<Record<string, any>> {
      if (!this.token || !this.phoneNumberId) {
        throw new Error('As credenciais do serviço WhatsApp não estão configuradas.')
      }

      try {
        const response = await fetch(this.getRequestUrl(), {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.token}`,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: JSON.stringify(payload),
        })

        const data = await response.json() as Record<string, any>

        if (!response.ok) {
          logger.warn({ payload, status: response.status, response: data }, 'WhatsAppService: Falha no envio da mensagem')
        }

        return data
      } catch (error: any) {
        logger.error({ payload, error: error.message }, 'WhatsAppService: Ocorreu um erro no transporte')
        return { error: error.message }
      }
    }
  }
  ```

### 3. Endpoint de Webhook Seguro (Controller)
* **Validação do GET:** Confirme que as requisições de assinatura da Meta batem com o `WHATSAPP_WEBHOOK_VERIFY_TOKEN` e retorne o texto bruto do `hub_challenge`.
* **Segurança do POST (X-Hub-Signature-256):** Sempre verifique a assinatura HMAC SHA-256 enviada pela Meta no cabeçalho `X-Hub-Signature-256` utilizando o `WHATSAPP_APP_SECRET` para prevenir requisições forjadas (spoofing). Calcule o HMAC sobre o corpo **bruto** (`request.raw()`) — o body parser deve preservar o rawBody — e compare em tempo constante com `crypto.timingSafeEqual`, nunca com igualdade de string.
* **Ingestão Rápida:** Salve o payload bruto no model `Webhook` imediatamente para construir o histórico de auditoria e, em seguida, enfileire uma tarefa do BullMQ passando apenas o ID do registro inserido.
* Exemplo de implementação do `WhatsAppWebhookController`:
  ```typescript
  import crypto from 'node:crypto'
  import type { HttpContext } from '@adonisjs/core/http'
  import logger from '@adonisjs/core/services/logger'
  import env from '#start/env'
  import Webhook from '#models/webhook'
  import WhatsAppWebhookJob from '#jobs/whatsapp_webhook_job'

  export default class WhatsAppWebhookController {
    // Validação da inscrição (GET)
    async verify({ request, response }: HttpContext) {
      const mode = request.input('hub.mode')
      const token = request.input('hub.verify_token')
      const challenge = request.input('hub.challenge')

      if (mode === 'subscribe' && token === env.get('WHATSAPP_WEBHOOK_VERIFY_TOKEN')) {
        return response.status(200).send(String(challenge))
      }

      return response.status(403).send('Forbidden: Incompatibilidade de token')
    }

    // Recebimento de eventos (POST)
    async handle({ request, response }: HttpContext) {
      const signature = request.header('X-Hub-Signature-256')
      const rawBody = request.raw()

      if (!signature || !rawBody) {
        return response.status(401).send('Unauthorized: Assinatura ou corpo ausente')
      }

      // Validação do X-Hub-Signature-256
      const appSecret = env.get('WHATSAPP_APP_SECRET', '')
      const elements = signature.split('=')
      const signatureHash = elements[1] ?? ''

      const expectedHash = crypto
        .createHmac('sha256', appSecret)
        .update(rawBody)
        .digest('hex')

      // Comparação em tempo constante para evitar timing attacks
      const signatureBuffer = Buffer.from(signatureHash, 'hex')
      const expectedBuffer = Buffer.from(expectedHash, 'hex')

      if (
        signatureBuffer.length !== expectedBuffer.length ||
        !crypto.timingSafeEqual(signatureBuffer, expectedBuffer)
      ) {
        logger.warn('WhatsAppWebhook: Falha na verificação de assinatura')
        return response.status(401).send('Unauthorized: Incompatibilidade de assinatura')
      }

      // Persistência do payload exato que foi assinado (rawBody).
      // NÃO use request.all(): com bodyparser json.convertEmptyStringsToNull=true,
      // strings vazias viram null e divergem dos bytes verificados na assinatura.
      const payload = JSON.parse(rawBody)
      const webhook = await Webhook.create({
        payload: payload ?? null,
        parameters: request.params() ?? null,
        ip: request.ip(),
        routeName: 'api.whatsapp.webhook',
      })

      logger.info({ webhook_id: webhook.id }, 'WhatsAppWebhook: Payload recebido com sucesso')

      // Dispara o Job no BullMQ e responde em menos de 3s
      await WhatsAppWebhookJob.dispatch(webhook.id)

      return response.status(200).send('EVENT_RECEIVED')
    }
  }
  ```

### 4. Processamento em Background (BullMQ)
* Processe os payloads de forma assíncrona dentro do executor de jobs do BullMQ (`WhatsAppWebhookJob`).
* Extraia os objetos de mensagem e campos de alteração (como `messages` ou `statuses`).
* **Atualização de Status de Envio:** Atualize o estado local das mensagens (`sent`, `delivered`, `read`) com base no ID da mensagem do WhatsApp (`wamid`).
* **Idempotência:** Garanta que cada evento de webhook seja processado uma única vez através da validação do ID do evento ou carimbo de data/hora (timestamp) no banco de dados.
* Atualize o campo `processedAt` do webhook original para indicar conclusão.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* NÃO execute fluxos de negócios complexos, gravações lentas em banco de dados ou chamadas síncronas de processamento HTTP de mensagens dentro do controller do Webhook.
* NÃO confie em payloads de webhook sem realizar a validação prévia do cabeçalho `X-Hub-Signature-256` utilizando o App Secret.
* NÃO armazene chaves, tokens ou segredos de API diretamente nos arquivos de código do repositório; use sempre arquivos de ambiente `.env` e a camada de config.
* NÃO utilize chaves primárias inteiras e auto-incrementais para a tabela de logs de webhook (`Webhook`); prefira `ULID` ou `UUID`.
* NÃO negligencie o registro de logs e metadados de erros da API de mensagens do WhatsApp em caso de falhas de envio.
