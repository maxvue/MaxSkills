---
name: adonisjs-google-business-profile-api-integration-best-practices
description: Use when implementing, configuring, reviewing, or debugging integrations with Google Business Profile (GBP / Google My Business) API v4 or Google Business Performance API in AdonisJS v6. Triggers on files managing Google OAuth 2.0 credentials, refreshing tokens, creating posts (local posts/updates, offers, events), uploading media to Google Business accounts, and handling API rate limits or webhook notifications.
---

# Boas Práticas de Integração da API Google Business Profile no AdonisJS

## Objetivo
Estabelecer padrões seguros, resilientes e robustos para integrar aplicações backend em AdonisJS v6 com a API v4 do Google Business Profile (GBP) e com a API do Google Business Performance. Isso inclui gerenciar credenciais offline do Google OAuth 2.0, criptografar tokens, realizar renovações automáticas, publicar atualizações locais (Novidades, Ofertas, Eventos), fazer upload de arquivos de mídia otimizados e gerenciar limites de requisição (rate limits) da API do Google usando sistemas de fila do BullMQ.

## Instruções

### 1. Handshake do Google OAuth 2.0 e Parâmetros de Consentimento
* **Acesso Offline (Offline Access)**: Ao iniciar o fluxo do Google OAuth via AdonisJS Ally ou autenticação manual, você deve solicitar explicitamente o acesso offline e forçar a tela de consentimento. Isso garante que o Google forneça um `refresh_token`, necessário para operações de longa duração.
* **Opções de Consentimento**:
  ```typescript
  // app/controllers/google_auth_controller.ts
  import { HttpContext } from '@adonisjs/core/http'

  export default class GoogleAuthController {
    async redirect({ ally }: HttpContext) {
      return ally
        .use('google')
        .redirect((request) => {
          request
            .param('access_type', 'offline')
            .param('prompt', 'consent')
            .scopes([
              'https://www.googleapis.com/auth/business.manage',
              'https://www.googleapis.com/auth/userinfo.profile',
              'https://www.googleapis.com/auth/userinfo.email'
            ])
        })
    }
  }
  ```

### 2. Armazenamento Seguro de Tokens e Lógica de Atualização (Refresh)
* **Criptografia de Tokens Confidenciais**: Nunca armazene o `refresh_token` em texto plano no banco de dados. Sempre criptografe-o usando o serviço de criptografia (`encryption`) do AdonisJS antes de salvá-lo.
* **Padrão de Renovação Automática**: Crie um serviço gerenciador de tokens dedicado para verificar a expiração. Renove o token de acesso caso ele esteja expirado ou prestes a expirar dentro de 5 minutos.
  ```typescript
  // app/services/google_token_service.ts
  import encryption from '@adonisjs/core/services/encryption'
  import env from '#start/env'
  import { DateTime } from 'luxon'
  import SocialMediaCredential from '#models/calendar/social_media_credential'

  export class GoogleTokenService {
    async getAccessToken(credential: SocialMediaCredential): Promise<string> {
      let accessToken = credential.accessToken
      let expiresAt = credential.tokenExpiresAt

      // Se o token estiver ausente, expirado ou prestes a expirar em 5 minutos
      if (!accessToken || !expiresAt || DateTime.now().plus({ minutes: 5 }) >= expiresAt) {
        // `params` é uma coluna JSONB no model (declarada com @column({ prepare/consume })
        // ou tipada como objeto). Garanta esse mapeamento no SocialMediaCredential.
        const encryptedRefresh = credential.params?.refreshToken
        if (!encryptedRefresh) {
          throw new Error(`Nenhum refresh token encontrado para a credencial: ${credential.id}`)
        }

        const decryptedRefresh = encryption.decrypt<string>(encryptedRefresh)
        
        // Solicita um novo token de acesso ao endpoint OAuth do Google
        const response = await fetch('https://oauth2.googleapis.com/token', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams({
            client_id: env.get('GOOGLE_CLIENT_ID'),
            client_secret: env.get('GOOGLE_CLIENT_SECRET'),
            refresh_token: decryptedRefresh,
            grant_type: 'refresh_token',
          }),
        })

        if (!response.ok) {
          const errBody = await response.text()
          throw new Error(`Falha ao renovar o token do Google: ${response.status} - ${errBody}`)
        }

        const data = await response.json() as { access_token: string; expires_in: number }
        accessToken = data.access_token
        expiresAt = DateTime.now().plus({ seconds: data.expires_in })

        // Salva o token de acesso atualizado no banco de dados
        credential.accessToken = accessToken
        credential.tokenExpiresAt = expiresAt
        await credential.save()
      }

      return accessToken
    }
  }
  ```

### 3. Serviço Centralizado do Google Business Profile
* **Arquitetura do Serviço**: Padronize as operações na classe `app/services/google_business_profile_service.ts`. Consolide a lógica para publicação e busca de métricas de desempenho.
* **Estrutura de Caminhos de Localização**: Os caminhos de recursos da API do Google My Business dependem dos IDs de conta e de local: `accounts/{accountId}/locations/{locationId}/localPosts`. Certifique-se de que o modelo de credenciais mapeie corretamente o `externalAccountId` (o identificador de Conta/Local do cliente).
* **Implementação de Tipos de Postagens do GBP**:
  ```typescript
  // app/services/google_business_profile_service.ts
  import logger from '@adonisjs/core/services/logger'
  import SocialMediaCredential from '#models/calendar/social_media_credential'
  import { GoogleTokenService } from './google_token_service.js'

  export class GoogleBusinessProfileService {
    private tokenService = new GoogleTokenService()

    async createLocalPost(
      credential: SocialMediaCredential,
      postData: {
        summary: string
        topicType: 'STANDARD' | 'EVENT' | 'OFFER'
        mediaUrl?: string
        eventData?: { title: string; startTime: string; endTime: string }
        offerData?: { couponCode?: string; redeemUrl?: string; termsConditions?: string }
      }
    ) {
      const token = await this.tokenService.getAccessToken(credential)
      const locationId = credential.externalAccountId // ex: accounts/123/locations/456
      // localPosts são servidos pela API v4 do Google My Business (mybusiness.googleapis.com).
      // O caminho do recurso já vem completo em externalAccountId: accounts/{id}/locations/{id}.
      const url = `https://mybusiness.googleapis.com/v4/${locationId}/localPosts`

      const payload: Record<string, any> = {
        languageCode: 'pt-BR',
        summary: postData.summary,
        topicType: postData.topicType,
      }

      // Adiciona mídia se estiver presente
      if (postData.mediaUrl) {
        payload.media = [{
          mediaFormat: 'PHOTO',
          sourceUrl: postData.mediaUrl,
        }]
      }

      // Preenche dados do Evento
      if (postData.topicType === 'EVENT' && postData.eventData) {
        payload.event = {
          title: postData.eventData.title,
          schedule: {
            startTime: postData.eventData.startTime,
            endTime: postData.eventData.endTime,
          },
        }
      }

      // Preenche dados da Oferta
      if (postData.topicType === 'OFFER' && postData.offerData) {
        payload.offer = {
          couponCode: postData.offerData.couponCode,
          redeemOnlineUrl: postData.offerData.redeemUrl,
          termsAndConditions: postData.offerData.termsConditions,
        }
      }

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        const errorMsg = await response.text()
        logger.error({ status: response.status, body: errorMsg }, 'GBP: Falha ao publicar postagem local')
        throw new Error(`Falha na publicação do Google Business Profile: ${response.status} - ${errorMsg}`)
      }

      return await response.json()
    }
  }
  ```

### 4. Requisitos e Tratamento de Mídia
* **Diretrizes para Imagens**: A API do Google Business Profile impõe regras rígidas para mídias. Certifique-se de que a validação atenda aos seguintes critérios:
  - **Formatos**: Apenas `JPG` ou `PNG` são suportados.
  - **Resolução**: O tamanho mínimo recomendado é 720px de largura por 720px de altura (preferência para proporção quadrada).
  - **Tamanho**: O tamanho máximo do arquivo é de `10MB` por imagem.
* **Fluxo de Upload Assíncrono**: A API do Google faz o download da imagem a partir da URL fornecida em `sourceUrl`. Certifique-se de que a URL da mídia seja acessível publicamente e hospedada em um CDN confiável (como URLs pré-assinadas do S3).

### 5. Processamento Assíncrono com Filas e Resiliência a Rate Limits
* **Nunca Execute na Thread HTTP principal**: Chamadas à API do Google Business Profile devem ser executadas de forma assíncrona por meio de jobs do BullMQ para evitar o bloqueio dos controllers HTTP.
* **Controle de Throttling e Retentativas (Backoff)**: Padronize políticas de retentativa com backoff exponencial para contornar problemas temporários de rede ou limites de requisições excedidos (erros `429 Quota Exceeded`).
  ```typescript
  // app/jobs/gbp_publish_job.ts
  import type { Job } from 'bullmq'
  import SocialMediaCredential from '#models/calendar/social_media_credential'
  import { GoogleBusinessProfileService } from '#services/google_business_profile_service'
  // gbpQueue deve ser declarado em app/services/queue_service.ts antes de importar:
  // export const gbpQueue = new Queue('gbp-publish', { connection: redis })
  import { gbpQueue } from '#services/queue_service'

  export interface GbpPublishData {
    credentialId: string
    summary: string
    topicType: 'STANDARD' | 'EVENT' | 'OFFER'
    mediaUrl?: string
    eventData?: { title: string; startTime: string; endTime: string }
    offerData?: { couponCode?: string; redeemUrl?: string; termsConditions?: string }
  }

  export default class GbpPublishJob {
    static readonly queueName = 'gbp-publish'

    static async dispatch(data: GbpPublishData) {
      await gbpQueue.add('publish-post', data, {
        attempts: 5,
        backoff: {
          type: 'exponential',
          delay: 10000, // atraso inicial de 10 segundos
        },
        removeOnComplete: { count: 50 },
        removeOnFail: { count: 100 },
      })
    }

    static async handle(job: Job<GbpPublishData>) {
      const { credentialId, ...postParams } = job.data
      const credential = await SocialMediaCredential.findOrFail(credentialId)
      const gbpService = new GoogleBusinessProfileService()

      await gbpService.createLocalPost(credential, postParams)
    }
  }
  ```

### 6. Processamento Resiliente de Webhooks e Notificações Pub/Sub
* **Padrão de Notificação**: Alterações no Google Business Profile (como novas avaliações, perguntas e respostas, atualizações de status de posts) são enviadas via webhooks do Google Cloud Pub/Sub.
* **Validação de Autenticidade**: Verifique a autenticidade das requisições recebidas comparando o token do Pub/Sub ou o parâmetro de assinatura antes do processamento.
* **Confirmação Imediata**: Sempre envie a notificação para uma fila em background e retorne imediatamente o status HTTP `200 OK` ao Google, evitando que o webhook envie tentativas repetidas desnecessariamente.

## Restrições
* **NÃO** execute operações das APIs do Google dentro do ciclo de vida das rotas HTTP dos controllers. Envie as operações para filas no BullMQ.
* **NÃO** salve o `refresh_token` do OAuth 2.0 em texto limpo no banco de dados. Você DEVE criptografá-lo usando o serviço `encryption` do AdonisJS.
* **NÃO** envie formatos de mídia não suportados (como WebP ou SVG) para os endpoints do Google Business Profile; valide estritamente que as imagens sejam JPG ou PNG e tenham menos de 10MB.
* **NÃO** execute chamadas de API sem verificação de expiração; sempre envolva as requisições na lógica automática de renovação do Token (Token Refresh).
