---
name: adonisjs-instagram-meta-token-renewal-best-practices
description: Use when designing, implementing, configuring, or debugging the automatic renewal of Meta/Instagram Graph API long-lived access tokens, managing OAuth2 token lifespans, scheduling token refresh cron jobs, or handling Meta OAuth authentication expiration in AdonisJS v6 applications.
author: Johnattas Conrady Gomes Santana
---
# Melhores Práticas para Renovação de Tokens da API da Meta e Instagram no AdonisJS

## Objetivo
Estabelecer diretrizes de codificação, padrões de arquitetura e padrões de implementação para verificar, validar, renovar e persistir de forma segura e em segundo plano os tokens de acesso de longa duração da Graph API da Meta/Instagram em aplicações AdonisJS v6.

> **Veja também:** para a troca inicial de tokens e os fluxos de publicação de mídia (contêineres, polling, publish), consulte `adonisjs-meta-graph-api-integration-best-practices`. Esta skill é a dona da renovação/refresh periódico via cron dos tokens de longa duração.

## Instruções

### 1. Armazenamento Seguro com Lucid ORM e Criptografia
* Nunca armazene tokens de acesso da Meta ou Instagram em texto simples (cleartext) no banco de dados.
* Implemente criptografia transparente no model Lucid `SocialMediaCredential`. Utilize as opções `prepare` e `consume` do decorator `@column()` combinadas com o serviço nativo de `encryption` do AdonisJS.
* Salve tanto a coluna `accessToken` criptografada quanto a coluna `tokenExpiresAt` do tipo datetime.

### 2. Regras de Expiração e Janela de Renovação
* Os tokens de acesso de longa duração da Meta possuem uma validade padrão de 60 dias.
* Calcule programaticamente a data de expiração como `DateTime.now().plus({ days: 60 })` caso a resposta do OAuth não retorne explicitamente um valor `expires_in`.
* Agende verificações diárias de renovação de tokens. Um token deve disparar a renovação automática se:
  - O token estiver ativo (`isActive = true`).
  - A data de expiração do token estiver dentro dos próximos 15 dias (`tokenExpiresAt <= DateTime.now().plus({ days: 15 })`).
  - Ou se o token não tiver data de expiração definida, mas tiver sido atualizado há mais de 45 dias.

### 3. Chamadas de API para Renovação Programática
Determine o tipo de token a partir de um campo explícito persistido na credencial (ex.: `provider` = `instagram` | `facebook`). **Não** infira o tipo pelo prefixo do valor do token (ex.: `startsWith('IG')`), pois é frágil e não confiável.

* **Para a Instagram API with Instagram Login (Graph API):**
  Execute uma requisição `GET` para:
  `https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token={long-lived-access-token}`
  > Observação: a antiga Instagram Basic Display API foi descontinuada pela Meta (dez/2024). Use a Instagram API com Instagram Login / Graph API.
* **Para a Graph API da Meta/Facebook:**
  Execute uma requisição `GET` para trocar/renovar o token usando:
  `https://graph.facebook.com/{version}/oauth/access_token?grant_type=fb_exchange_token&client_id={client-id}&client_secret={client-secret}&fb_exchange_token={existing-token}`
* Sempre valide a resposta da API. Extraia o novo `access_token` e o valor atualizado de `expires_in`.

### 4. Orquestração de Tarefas em Segundo Plano (Scheduler/BullMQ)
* Não realize a renovação de tokens de forma síncrona nas threads de requisição HTTP.
* Crie um comando Ace persistente (scheduler) ou um worker job no BullMQ (ex: `MetaTokenRenewalJob`) que seja executado diariamente.
* O job deve consultar todas as credenciais ativas prestes a expirar, chamar a API de renovação e atualizar o model dentro de uma transação de banco de dados.

### 5. Tratamento de Erros e Alertas via Eventos
* Envolva a requisição de renovação de API em um bloco `try/catch` robusto.
* Trate falhas de autorização com segurança. Se a Meta retornar um erro de autorização ou permissão (como erro de OAuthException código `190` - Token Inválido/Expirado, ou status HTTP 401/400):
  - Marque a credencial como inativa (`isActive = false`).
  - Limpe o token inválido se necessário para evitar novas tentativas desnecessárias.
  - Dispare um evento baseado em classe usando o emitter do Adonis v6: `emitter.emit(MetaTokenRenewalFailed, { credential, reason })`.
* Registre um listener carregado de forma preguiçosa (lazy-loaded listener) para o evento, com o objetivo de notificar o responsável pela conta para que refaça a autenticação manualmente.

## Examples

### Model Lucid com Criptografia Transparente
```typescript
import { DateTime } from 'luxon'
import { BaseModel, beforeCreate, column } from '@adonisjs/lucid/orm'
import encryption from '@adonisjs/core/services/encryption'
import { ulid } from 'ulid'

export default class SocialMediaCredential extends BaseModel {
  static table = 'calendar_social_media_credentials'
  static selfAssignPrimaryKey = true

  @beforeCreate()
  static assignUlid(model: SocialMediaCredential) {
    if (!model.id) model.id = ulid()
  }

  @column({ isPrimary: true })
  declare id: string

  @column()
  declare solarCompanyId: string

  @column()
  declare eventApiId: string

  @column()
  declare externalAccountId: string | null

  // Tipo de provedor persistido explicitamente ('instagram' | 'facebook'); não inferir pelo valor do token
  @column()
  declare provider: 'instagram' | 'facebook'

  // Criptografa o token transparentemente ao salvar, e descriptografa ao ler
  @column({
    serializeAs: null,
    prepare: (value: string | null) => value ? encryption.encrypt(value) : null,
    consume: (value: string | null) => value ? encryption.decrypt(value) : null
  })
  declare accessToken: string | null

  @column.dateTime()
  declare tokenExpiresAt: DateTime | null

  @column()
  declare isActive: boolean

  @column.dateTime({ autoCreate: true })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true })
  declare updatedAt: DateTime
}
```

### Serviço de Renovação Programática de Tokens
```typescript
import SocialMediaCredential from '#models/calendar/social_media_credential'
import { DateTime } from 'luxon'
import MetaTokenRenewalFailed from '#events/meta_token_renewal_failed'
import emitter from '@adonisjs/core/services/emitter'
import logger from '@adonisjs/core/services/logger'

export class MetaTokenRenewalService {
  /**
   * Renova o token de acesso de longa duração e trata os erros
   */
  public async renewToken(credential: SocialMediaCredential): Promise<void> {
    const originalToken = credential.accessToken
    if (!originalToken) return

    try {
      let renewalUrl = ''
      // Usa o tipo de provedor persistido explicitamente; nunca infere pelo valor do token
      const isInstagram = credential.provider === 'instagram'

      if (isInstagram) {
        renewalUrl = `https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=${originalToken}`
      } else {
        const clientId = process.env.META_CLIENT_ID
        const clientSecret = process.env.META_CLIENT_SECRET
        const version = process.env.META_GRAPH_VERSION || 'v20.0'
        renewalUrl = `https://graph.facebook.com/${version}/oauth/access_token?grant_type=fb_exchange_token&client_id=${clientId}&client_secret=${clientSecret}&fb_exchange_token=${originalToken}`
      }

      const response = await fetch(renewalUrl, { method: 'GET' })
      const data = await response.json() as any

      if (!response.ok || data.error) {
        const errorMsg = data.error?.message || 'A requisição de renovação de token falhou na Meta API'
        const errorCode = data.error?.code

        logger.error({ error: data.error, credentialId: credential.id }, 'Falha ao renovar o token na Meta Graph API')

        // Código 190 representa OAuthException (Token inválido ou expirado)
        if (response.status === 401 || response.status === 400 || errorCode === 190) {
          await this.handleFailedRenewal(credential, new Error(errorMsg))
        } else {
          throw new Error(errorMsg)
        }
        return
      }

      credential.accessToken = data.access_token
      credential.tokenExpiresAt = data.expires_in
        ? DateTime.now().plus({ seconds: data.expires_in })
        : DateTime.now().plus({ days: 60 })

      await credential.save()
      logger.info({ credentialId: credential.id }, 'Token de acesso da Meta/Instagram renovado com sucesso')
    } catch (error) {
      logger.error({ error, credentialId: credential.id }, 'Erro inesperado durante o processamento da renovação do token')
      throw error
    }
  }

  private async handleFailedRenewal(credential: SocialMediaCredential, error: Error): Promise<void> {
    credential.isActive = false
    await credential.save()

    // Dispara o evento para alertar o sistema que a ação do usuário é necessária (API do emitter do Adonis v6)
    await emitter.emit(MetaTokenRenewalFailed, { credential, reason: error.message })
  }
}
```

### Job do Worker Agendado (BullMQ / Scheduler)
```typescript
import SocialMediaCredential from '#models/calendar/social_media_credential'
import { MetaTokenRenewalService } from '#services/meta/meta_token_renewal_service'
import { DateTime } from 'luxon'
import logger from '@adonisjs/core/services/logger'

export default class MetaTokenRenewalJob {
  public static async execute() {
    logger.info('Iniciando verificação agendada de renovação de tokens Meta')
    const renewalService = new MetaTokenRenewalService()

    // Busca credenciais ativas cujos tokens expiram em breve (<= 15 dias) ou sem data de expiração definida
    const credentials = await SocialMediaCredential.query()
      .where('is_active', true)
      .where((query) => {
        query
          .where('token_expires_at', '<=', DateTime.now().plus({ days: 15 }).toSQL())
          .orWhereNull('token_expires_at')
      })

    for (const credential of credentials) {
      try {
        await renewalService.renewToken(credential)
      } catch (error) {
        logger.error({ error, credentialId: credential.id }, 'Falha ao renovar token para credencial')
      }
    }

    logger.info('Verificação agendada de renovação de tokens Meta concluída')
  }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Não** armazene tokens de acesso OAuth em texto simples. Sempre utilize ganchos do `@column()` em conjunto com `encryption.encrypt` para garantir a segurança dos dados.
* **Não** chame endpoints de renovação de token de forma síncrona dentro de controllers em requisições HTTP do usuário. Sempre delegue a execução para comandos cron ou tarefas de fila do BullMQ.
* **Não** tente renovar tokens infinitamente quando a Meta retornar erros de permissão ou autenticação (como erro de OAuthException código `190`). Defina imediatamente `isActive = false` e dispare `MetaTokenRenewalFailed` para evitar bloqueios por limites de requisições ou banimento de IP.
* **Não** insira credenciais do aplicativo Meta (Client ID, Client Secret, versões de API) diretamente no código-fonte. Recupere-as sempre das variáveis de ambiente via `process.env` ou pelo serviço Env do AdonisJS.
* **Não** execute o fluxo de renovação para credenciais que já estejam desativadas (`isActive = false`) ou sem token cadastrado.
