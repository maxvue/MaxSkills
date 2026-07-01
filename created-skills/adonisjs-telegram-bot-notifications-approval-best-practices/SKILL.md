---
name: adonisjs-telegram-bot-notifications-approval-best-practices
description: Use when implementing, configuring, or debugging Telegram Bot integrations, sending real-time channel notifications, handling Telegram webhooks, or designing interactive chat approvals (such as post validation buttons, system warnings, or queue alerts) in AdonisJS v6.
---

# Melhores Práticas para Notificações e Aprovações com Telegram Bot no AdonisJS v6

## Objetivo
Estabelecer diretrizes e padrões de implementação para envio de notificações assíncronas do Telegram, formatação de alertas ricos, tratamento seguro de webhooks do Telegram e implementação de aprovações interativas inline em um backend AdonisJS v6.

## Instruções

### 1. Validação de Configuração e Ambiente
* Defina as credenciais do Telegram em variáveis de ambiente.
* Valide as variáveis de ambiente no arquivo `start/env.ts` usando o VineJS:
  ```typescript
  TELEGRAM_BOT_TOKEN: Env.schema.string(),
  TELEGRAM_CHAT_ID: Env.schema.string.optional(), // ID padrão do chat/canal
  TELEGRAM_WEBHOOK_SECRET: Env.schema.string.optional(), // Token enviado pelo Telegram para verificar a autenticidade do webhook
  ```

### 2. Implementação do Serviço (`TelegramService`)
* Crie um serviço dedicado em `app/services/telegram_service.ts`.
* Use o `fetch` nativo do Node.js ou o `Axios` para enviar requisições para `https://api.telegram.org/bot<token>/`.
* Implemente um método de envio robusto com suporte a parse de Markdown/HTML e teclados inline (inline keyboards).
* Trate erros de limite de taxa da API (HTTP 429) extraindo o parâmetro `retry_after` para agendar novas tentativas.

```typescript
import env from '#start/env'
import logger from '@adonisjs/core/services/logger'

export default class TelegramService {
  private static getApiUrl(method: string) {
    const token = env.get('TELEGRAM_BOT_TOKEN')
    return `https://api.telegram.org/bot${token}/${method}`
  }

  /**
   * Escapa caracteres especiais para o formato MarkdownV2 do Telegram.
   */
  public static escapeMarkdownV2(text: string): string {
    return text.replace(/[_*[\]()~`>#+\-=|{}.!]/g, '\\$&')
  }

  /**
   * Envia mensagem de texto com botões opcionais de teclado inline.
   */
  public static async sendMessage(params: {
    chatId?: string
    text: string
    parseMode?: 'MarkdownV2' | 'HTML'
    inlineKeyboard?: Array<Array<{ text: string; callback_data?: string; url?: string }>>
  }) {
    const chatId = params.chatId || env.get('TELEGRAM_CHAT_ID')
    if (!chatId) {
      logger.warn('ID do Chat do Telegram não configurado.')
      return
    }

    const payload: Record<string, any> = {
      chat_id: chatId,
      text: params.text,
      parse_mode: params.parseMode || 'HTML',
    }

    if (params.inlineKeyboard) {
      payload.reply_markup = {
        inline_keyboard: params.inlineKeyboard,
      }
    }

    try {
      const response = await fetch(this.getApiUrl('sendMessage'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await response.json()

      if (!response.ok) {
        if (response.status === 429) {
          const retryAfter = data.parameters?.retry_after || 5
          logger.error(`Telegram rate limited. Tentar novamente após ${retryAfter}s.`)
          throw new Error(`TELEGRAM_RATE_LIMIT:${retryAfter}`)
        }
        logger.error({ data }, 'Falha ao enviar mensagem do Telegram')
        throw new Error(`Erro na API do Telegram: ${data.description || 'Erro desconhecido'}`)
      }

      return data
    } catch (error) {
      logger.error({ error }, 'Erro ao chamar a API do Telegram')
      throw error
    }
  }
}
```

### 3. Processamento Assíncrono de Fila (Integração com BullMQ)
* **Nunca chame APIs do Telegram de forma síncrona** durante o ciclo de requisição e resposta HTTP do cliente.
* Defina um job do BullMQ (ex: `TelegramNotificationJob`) para despachar as mensagens do Telegram.
* Ao receber um erro `TELEGRAM_RATE_LIMIT:x`, use o valor de `retry_after` (em segundos) para atrasar dinamicamente a nova tentativa do job.

```typescript
// Exemplo de trecho do processador de Job
import TelegramService from '#services/telegram_service'

export default class TelegramNotificationJob {
  public async handle(job: any) {
    const { chatId, text, parseMode, inlineKeyboard } = job.data
    try {
      await TelegramService.sendMessage({ chatId, text, parseMode, inlineKeyboard })
    } catch (error) {
      if (error.message.startsWith('TELEGRAM_RATE_LIMIT:')) {
        const seconds = parseInt(error.message.split(':')[1], 10)
        // Atrasa a execução do job no BullMQ
        await job.updateDelay(seconds * 1000)
        throw error // Lança o erro para disparar a lógica padrão de retentativa do BullMQ com o atraso atualizado
      }
      throw error
    }
  }
}
```

### 4. Retornos Interativos (Callbacks) e Segurança do Webhook
* Trate retornos de botões interativos (Inline Keyboards) expondo um endpoint de webhook (ex: `/api/webhooks/telegram`).
* **Shield CSRF — rota de webhook deve ser excepcionada:** O Shield protege POSTs com CSRF por padrão. O Telegram não envia `XSRF-TOKEN`, então a requisição seria rejeitada com 403 antes de chegar ao controller. Adicione o path em `config/shield.ts`:
  ```typescript
  // config/shield.ts
  csrf: {
    enabled: true,
    exceptRoutes: ['/api/webhooks/telegram'],
    // ...
  }
  ```
  A autenticidade é garantida pelo `X-Telegram-Bot-Api-Secret-Token`, não pelo CSRF.
* **Verificação de Token Secreto/Assinatura:**
  - Ao configurar o webhook via `setWebhook`, passe um token secreto aleatório no parâmetro `secret_token`.
  - No controller da sua rota no AdonisJS, verifique se o cabeçalho `X-Telegram-Bot-Api-Secret-Token` recebido coincide com a variável de ambiente `TELEGRAM_WEBHOOK_SECRET`.
  - Rejeite a requisição com uma resposta `403 Forbidden` se o token estiver ausente ou incorreto.
* **Limitações de Callback Query:**
  - O payload do campo `callback_data` possui um limite estrito de **64 bytes**. Estruture os dados de ação de forma compacta (ex: `appr:post_123` em vez de `{"action": "approve", "post_id": 123}`).
  - Responda à requisição do callback imediatamente usando `answerCallbackQuery` para evitar que o Telegram exiba um spinner de carregamento infinito na tela do usuário.

```typescript
import { HttpContext } from '@adonisjs/core/http'
import env from '#start/env'
import TelegramService from '#services/telegram_service'

export default class TelegramWebhooksController {
  public async handle({ request, response }: HttpContext) {
    const secretHeader = request.header('X-Telegram-Bot-Api-Secret-Token')
    const localSecret = env.get('TELEGRAM_WEBHOOK_SECRET')

    if (!localSecret || secretHeader !== localSecret) {
      return response.status(403).send('Forbidden: Token mismatch')
    }

    const update = request.body()
    
    // Verifica se a atualização é um clique em botão interativo (callback_query)
    if (update.callback_query) {
      const callbackQueryId = update.callback_query.id
      const data = update.callback_query.data // ex: "appr:post_123"
      
      // Executa lógica de negócio de forma assíncrona (ex: aprovar ou rejeitar)
      // ...

      // Sempre responda ao callback query imediatamente
      await fetch(`https://api.telegram.org/bot${env.get('TELEGRAM_BOT_TOKEN')}/answerCallbackQuery`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          callback_query_id: callbackQueryId,
          text: 'Processando requisição...', // Mensagem rápida mostrada ao usuário
        }),
      })
    }

    return response.status(200).send('OK')
  }
}
```

## Restrições
* Não exponha o token do bot ou segredos de webhook em repositórios públicos ou aplicações front-end.
* Não exceda os limites de taxa do Telegram (máximo de 30 mensagens por segundo em todos os chats, máximo de 1 mensagem por segundo em um chat específico).
* Nunca exceda o limite de **64 bytes** nos payloads de `callback_data`. Sempre comprima as chaves de ação.
* Ao usar `MarkdownV2`, certifique-se de que todas as strings de texto sejam escapadas utilizando `escapeMarkdownV2` para evitar erros de renderização.
