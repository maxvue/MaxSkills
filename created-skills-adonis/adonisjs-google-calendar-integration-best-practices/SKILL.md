---
name: adonisjs-google-calendar-integration-best-practices
description: Use when implementing, reviewing, or debugging Google Calendar API integrations, OAuth 2.0 flows for Google services, syncing events between local databases and Google Calendars, or handling Google Calendar webhook channel renewals and push notifications in AdonisJS v6. Triggers on files modifying GoogleCalendarService, GoogleCalendarController, calendar sync jobs, and Google OAuth credentials config.
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Integração do Google Calendar no AdonisJS

## Objetivo
Fornecer regras estritas, padrões de configuração e modelos de código para integrar a API do Google Calendar de forma segura e eficiente em aplicações backend AdonisJS v6, com foco no tratamento do fluxo OAuth 2.0, expiração/renovação de tokens, sincronização bidirecional, operações assíncronas com BullMQ, notificações por webhook e controle de concorrência.

## Instruções

### 1. Handshake do Google OAuth 2.0 e Armazenamento Seguro de Tokens
* Configure o driver Google Ally ou construa manualmente o fluxo OAuth usando a biblioteca oficial `google-auth-library`.
* Sempre solicite `access_type: 'offline'` e `prompt: 'consent'` nos parâmetros de autorização para garantir que o Google retorne um `refresh_token` de longa duração.
* Mapeie colunas do banco de dados no modelo de credenciais (ex: `GoogleCalendarCredential`, vinculado ao usuário/técnico que agenda visitas e instalações fotovoltaicas) para armazenar:
  - `accessToken`: O token de acesso temporário.
  - `tokenExpiresAt`: Data/Hora em que o token de acesso expira (mapeado com `DateTime` do Luxon).
  - `refreshToken`: **DEVE** ser criptografado no banco de dados. Use o serviço de criptografia (`encryption`) do AdonisJS. Armazene-o em uma coluna dedicada `refresh_token` (não em um campo genérico `params`).
* Exemplo de lógica para armazenamento seguro e renovação de token:
  ```typescript
  import { google } from 'googleapis'
  import encryption from '@adonisjs/core/services/encryption'
  import { DateTime } from 'luxon'
  import env from '#start/env'
  import GoogleCalendarCredential from '#models/calendar/google_calendar_credential'

  export class GoogleTokenService {
    private oauth2Client = new google.auth.OAuth2(
      env.get('GOOGLE_CLIENT_ID'),
      env.get('GOOGLE_CLIENT_SECRET'),
      env.get('GOOGLE_REDIRECT_URL')
    )

    async getAuthenticatedClient(credential: GoogleCalendarCredential) {
      const encryptedRefresh = credential.refreshToken
      if (!encryptedRefresh) {
        throw new Error('Refresh token não encontrado para a credencial: ' + credential.id)
      }

      const decryptedRefreshToken = encryption.decrypt<string>(encryptedRefresh)

      // Forneça o refresh_token e o access_token/expiry atuais ao cliente.
      // A google-auth-library moderna renova o access_token automaticamente
      // quando ele está ausente ou expirado (não use refreshAccessToken(), que é legado).
      this.oauth2Client.setCredentials({
        refresh_token: decryptedRefreshToken,
        access_token: credential.accessToken ?? undefined,
        expiry_date: credential.tokenExpiresAt?.toMillis() ?? undefined,
      })

      // Persiste os tokens sempre que a biblioteca emitir um access_token renovado.
      this.oauth2Client.on('tokens', async (tokens) => {
        if (tokens.access_token) {
          credential.accessToken = tokens.access_token
        }
        if (tokens.expiry_date) {
          credential.tokenExpiresAt = DateTime.fromMillis(tokens.expiry_date)
        }
        // O Google só reenvia refresh_token em consentimentos novos; preserve o existente.
        if (tokens.refresh_token) {
          credential.refreshToken = encryption.encrypt(tokens.refresh_token)
        }
        await credential.save()
      })

      // getAccessToken() força a renovação se necessário e dispara o evento 'tokens'.
      await this.oauth2Client.getAccessToken()

      return this.oauth2Client
    }
  }
  ```

### 2. Interações Centralizadas com a API do Google Calendar
* Centralize todas as interações de calendário em `app/services/google_calendar_service.ts`.
* Evite criar novos clientes de autenticação diretamente dentro de controllers ou jobs; em vez disso, obtenha o cliente HTTP autenticado por meio do serviço de tokens.
* Mapeie os parâmetros de eventos de forma estrita (ex: resumo, descrição, datas de início/fim com fusos horários).
* Trate as respostas da API do Google Calendar de forma adequada, rastreando erros específicos como 404 (calendário não encontrado) ou 403 (limites de taxa/rate limits).

### 3. Sincronização Assíncrona via Jobs do BullMQ
* **NUNCA** execute chamadas à API do Google Calendar dentro do ciclo de vida das requisições HTTP (controllers).
* Despatche um job do BullMQ (ex: `GoogleCalendarSyncJob`) para mutações de saída:
  - `insert`: Adiciona um evento local ao Google Calendar, armazenando o `google_event_id` retornado.
  - `update`: Atualiza um evento existente no Google Calendar usando o `google_event_id` mapeado.
  - `delete`: Remove o evento do Google Calendar.
* Configure a fila do BullMQ com retentativas exponenciais (exponential backoff) para lidar com falhas temporárias de rede ou limites de taxa da API.
  ```typescript
  // app/jobs/google_calendar_sync_job.ts
  import type { Job } from 'bullmq'
  import { googleCalendarSyncQueue } from '#services/queue_service'
  import { GoogleCalendarService } from '#services/google_calendar_service'

  export interface SyncJobData {
    eventId: string
    action: 'insert' | 'update' | 'delete'
    googleEventId?: string
    credentialId: string
  }

  export default class GoogleCalendarSyncJob {
    static readonly queueName = 'google-calendar-sync'

    static async dispatch(data: SyncJobData) {
      await googleCalendarSyncQueue.add('sync', data, {
        attempts: 5,
        backoff: {
          type: 'exponential',
          delay: 5000,
        },
        removeOnComplete: { count: 100 },
        removeOnFail: { count: 500 },
      })
    }

    static async handle(job: Job<SyncJobData>) {
      const { eventId, action, googleEventId, credentialId } = job.data
      const calendarService = new GoogleCalendarService()
      await calendarService.sync(eventId, action, googleEventId, credentialId)
    }
  }
  ```

### 4. Receptor de Webhook Push e Renovação de Canais de Webhook
* Exponha uma rota POST `/webhooks/google/calendar` para receber notificações de push do Google.
* Inspecione os cabeçalhos da requisição:
  - `x-goog-channel-id`: Identifica o listener do canal local.
  - `x-goog-resource-id`: Identifica o recurso do Google Calendar.
  - `x-goog-resource-state`: Estado da ação (`exists`, `not_exists`, `sync`).
* Transfira o processamento das notificações de webhook para um job em segundo plano (`GoogleWebhookProcessorJob`) para responder ao Google imediatamente com um status `200 OK`.
* Mantenha um comando Ace (`node ace google:channels:renew`) para rodar via agendador de tarefas, renovando os canais antes de expirarem (as assinaturas de webhook do Google duram no máximo 30 dias).

### 5. Idempotência e Prevenção de Loops de Sincronização
* Para evitar loops infinitos (Atualização Local ➔ Sincronização com o Google ➔ Notificação via Webhook ➔ Atualização Local), aplique travas (locking) baseadas no Redis:
  ```typescript
  import redis from '@adonisjs/redis/services/main'

  const lockKey = `lock:calendar:sync:${eventId}`
  // Tenta adquirir a trava por 10 segundos
  const acquired = await redis.set(lockKey, 'true', 'EX', 10, 'NX')

  if (!acquired) {
    // Sincronização já em andamento, descarta a ação duplicada
    return
  }

  try {
    // Prossegue com a sincronização
  } finally {
    await redis.del(lockKey)
  }
  ```
* Rastreie timestamps da última sincronização (`synchronized_at` ou `sync_version`) no banco de dados local e compare-os com o timestamp `updated` do evento retornado pelo Google.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* NÃO execute chamadas à API do Google Calendar dentro de controllers HTTP do AdonisJS. Todas as chamadas de API devem passar por jobs do BullMQ.
* NÃO armazene o `refresh_token` em texto limpo. Sempre criptografe-o usando o serviço de criptografia (`encryption`) do AdonisJS.
* NÃO inicialize `google.calendar` sem passar um cliente OAuth válido que trate a autorrenovação do token de acesso.
* NÃO ignore o travamento via Redis ao atualizar eventos a partir de webhooks para evitar recursões de loop de sincronização infinito.
* NÃO ignore o cabeçalho de verificação do Webhook do Google (`x-goog-channel-token`) se for usado para verificar a autenticidade das mensagens do webhook.
