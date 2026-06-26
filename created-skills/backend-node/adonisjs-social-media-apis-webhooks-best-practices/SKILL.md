---
name: adonisjs-social-media-apis-webhooks-best-practices
description: Use when receiving INBOUND social media webhooks (Meta / Instagram Graph) in AdonisJS — verifying hub_verify_token challenge requests, fast-persisting raw payloads to an audit table, returning 200 within Meta's 3-second limit by delegating to async BullMQ jobs, and normalizing incoming comment/event payloads. For outbound publishing and token management, see adonisjs-meta-graph-api-integration-best-practices.
---

# Melhores Práticas para APIs de Mídias Sociais e Webhooks no AdonisJS

## Objetivo
Estabelecer uma integração segura, performática e resiliente com APIs de mídias sociais (como Meta Graph API e Instagram Graph API) e sistemas de ingestão de webhooks no AdonisJS v6. Os principais objetivos são evitar os limites rígidos de timeout de 3 segundos da Meta via delegação para filas assíncronas e manter logs robustos e trilhas de auditoria no banco de dados.

## Instruções

### 1. Verificação Segura do Webhook (Requisição GET)
* Ao receber requisições de verificação de plataformas externas (por exemplo, o fluxo de `hub_verify_token` da Meta), compare os tokens de forma segura utilizando variáveis de ambiente.
* Responda imediatamente com o token de desafio (`hub_challenge`) quando a verificação for bem-sucedida, ou retorne o status `403 Forbidden`.
* Exemplo de manipulador de verificação:
  ```typescript
  import type { HttpContext } from '@adonisjs/core/http'

  export default class MetaWebhookController {
    async index({ request, response }: HttpContext) {
      if (request.method() === 'GET' && request.input('hub_challenge')) {
        const token = process.env.META_WEBHOOK_TOKEN

        if (request.input('hub_verify_token') === token) {
          return response.status(200).send(String(request.input('hub_challenge')))
        }
        return response.status(403).send('Token inválido')
      }
      // A lógica do POST entra aqui...
    }
  }
  ```

### 2. Ingestão Rápida e Delegação Assíncrona (Requisição POST)
* **Restrição de Timeout dos Webhooks da Meta:** A Meta espera uma resposta `200 OK` em menos de 3 segundos. Para evitar timeouts, NÃO processe a lógica de negócios do webhook de forma síncrona dentro do ciclo de requisição HTTP.
* **Persistência Imediata:** Persista o payload bruto do webhook imediatamente no banco de dados (por exemplo, utilizando um modelo `Webhook` com chave primária ULID) para estabelecer uma trilha de auditoria.
* **Despacho para Fila:** Enfileire um job em segundo plano usando um gerenciador de filas (como o BullMQ), passando apenas o ID do registro do webhook criado, e retorne a resposta HTTP (por exemplo, `response.json(false)` ou `response.status(200)`) imediatamente.
* Exemplo de Ingestão:
  ```typescript
  import Webhook from '#models/webhook'
  import MetaWebhookJob from '#jobs/meta_webhook_job'

  // Dentro do método do seu controller (POST)
  const webhook = await Webhook.create({
    payload: request.all() ?? null,
    parameters: request.params() ?? null,
    ip: request.ip(),
    routeName: 'api.meta.webhook',
  })

  logger.info({ webhook_id: webhook.id }, 'MetaWebhook: Evento recebido')

  // Despacha o job de forma assíncrona usando BullMQ
  await MetaWebhookJob.dispatch(webhook.id)

  return response.json(false)
  ```

### 3. Processamento de Job Assíncrono e Normalização
* Busque o registro do webhook bruto no handler do job em segundo plano.
* Itere pelos payloads (por exemplo, a estrutura aninhada da Meta `payload.entry` -> `entry.changes`).
* **Camada de Normalização:** Mapeie o payload específico da plataforma (Facebook, Instagram, etc.) para um formato de objeto interno padronizado.
* **Correlação de Dados:** Consulte o modelo de destino (por exemplo, `CalendarEvent`) usando IDs externos (por exemplo, `external_post_id`) para associar comentários ou métricas aos registros locais.
* **Atualizações Idempotentes:** Salve os comentários ou webhooks usando `updateOrCreate` (por exemplo, em `SocialMediaComment` por `externalCommentId`) para lidar com segurança com possíveis entregas duplicadas de webhooks.
* Atualize as colunas de status do webhook bruto (`processedAt` ou `errorWebhook`) assim que o processamento for concluído ou falhar.

### 4. Logging e Monitoramento
* Utilize logs estruturados (por exemplo, o Logger do AdonisJS) para rastrear eventos com campos de contexto como `webhook_id`, `comment_id` ou `event_id`.
* Registre logs com marcações claras para ingestão, processamento e resolução dos payloads dos webhooks.

## Restrições
* NÃO execute lógica de negócios demorada, downloads de mídia, geração de IA ou chamadas pesadas de API externa diretamente no controller do receptor de webhook.
* NÃO confie em payloads de webhooks recebidos sem verificar a assinatura da requisição (por exemplo, assinatura HMAC-SHA256 nos cabeçalhos) ou confirmar a integridade do payload antes de agir sobre ele.
* NÃO utilize IDs inteiros autoincrementais para registros de Webhooks; sempre utilize `ulid()` ou `uuid()` para evitar a enumeração de IDs.
* NÃO deixe de registrar o payload bruto no banco de dados. Sem ele, a depuração de webhooks com falhas em produção se torna impossível.
