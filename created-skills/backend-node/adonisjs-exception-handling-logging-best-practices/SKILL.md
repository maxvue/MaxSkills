---
name: adonisjs-exception-handling-logging-best-practices
description: Use when configuring global or custom exception handlers in AdonisJS v6, defining custom HTTP response formats, handling validation errors, logging info or debug data using the AdonisJS Logger (pino), or integrating third-party monitoring tools.
---

## Objetivo
Estabelecer padrões robustos e convenções de codificação para gerenciar o tratamento de exceções, formatação de erros de validação e logs de auditoria em aplicações AdonisJS v6, garantindo depurabilidade adequada, respostas de erro limpas para os clientes e segurança absoluta contra vazamentos de informações em produção.

## Instruções

## 1. Tratador Global de Exceções (`app/exceptions/handler.ts`)

O AdonisJS usa uma classe centralizada para capturar e processar todas as exceções não tratadas. Configure seu tratador para retornar formatos de erro JSON consistentes ao lidar com requisições de API, preservando as páginas de status para requisições HTML.

```typescript
import app from '@adonisjs/core/services/app'
import { type HttpContext, ExceptionHandler } from '@adonisjs/core/http'
import type { StatusPageRange, StatusPageRenderer } from '@adonisjs/core/types/http'
import { errors as vErrors } from '@vinejs/vine'

export default class HttpExceptionHandler extends ExceptionHandler {
  /**
   * No modo debug, o tratador de exceções exibirá erros detalhados
   * com stack traces formatados (apenas em desenvolvimento).
   */
  protected debug = !app.inProduction

  /**
   * As páginas de status renderizam templates HTML personalizados para códigos de status HTTP específicos.
   */
  protected renderStatusPages = app.inProduction

  protected statusPages: Record<StatusPageRange, StatusPageRenderer> = {
    '404': (error, { view }) => {
      return view.render('pages/errors/not_found', { error })
    },
    '500..599': (error, { view }) => {
      return view.render('pages/errors/server_error', { error })
    },
  }

  /**
   * O método handle intercepta todas as exceções e retorna a resposta ao cliente.
   */
  async handle(error: any, ctx: HttpContext) {
    const isJsonRequest = ctx.request.accepts(['html', 'json']) === 'json' || ctx.request.url().startsWith('/api')

    if (isJsonRequest) {
      return this.handleJsonResponse(error, ctx)
    }

    return super.handle(error, ctx)
  }

  /**
   * Formata uma resposta de erro JSON consistente para os consumidores da API.
   */
  private async handleJsonResponse(error: any, ctx: HttpContext) {
    const status = error.status || 500
    const code = error.code || 'E_INTERNAL_SERVER_ERROR'
    
    // Formata os erros de validação do VineJS explicitamente
    if (error instanceof vErrors.E_VALIDATION_ERROR) {
      return ctx.response.status(error.status).send({
        errors: error.messages.map((message: any) => ({
          field: message.field,
          rule: message.rule,
          message: message.message,
        })),
      })
    }

    const responsePayload: any = {
      error: {
        code,
        message: error.message || 'Ocorreu um erro inesperado.',
      },
    }

    // Inclui stack trace apenas em desenvolvimento
    if (this.debug) {
      responsePayload.error.stack = error.stack
    }

    return ctx.response.status(status).send(responsePayload)
  }

  /**
   * O método report envia exceções para serviços externos de relatório/monitoramento.
   * Evite enviar erros de negócio comuns (4xx) para o monitoramento externo.
   */
  async report(error: any, ctx: HttpContext) {
    if (!this.shouldReport(error)) {
      return
    }

    // Integração com serviços externos como Sentry, Bugsnag, Datadog
    if (app.inProduction) {
      ctx.logger.error({ err: error, requestId: ctx.request.id() }, error.message)
      
      // Exemplo Sentry:
      // Sentry.captureException(error)
    } else {
      await super.report(error, ctx)
    }
  }

  /**
   * Determina se o erro deve ser reportado ao monitoramento externo.
   */
  private shouldReport(error: any): boolean {
    const status = error.status || 500
    // Ignora o log de erros de validação (422) ou erros de autenticação (401, 403)
    return status >= 500
  }
}
```

## 2. Erros de Validação e Formatos

Os erros de validação do VineJS usam como padrão o código `E_VALIDATION_ERROR` com o status `422`. O formato deve ser padronizado globalmente no tratador de exceções conforme demonstrado acima, garantindo que todos os erros de API retornem um array `errors`.

### Mensagens de Validação Personalizadas
Sempre especifique mensagens de validação claras em seus esquemas de validação:

```typescript
import vine from '@vinejs/vine'

export const createUserValidator = vine.compile(
  vine.object({
    email: vine.string().email().normalizeEmail(),
    password: vine.string().minLength(8),
  })
)

createUserValidator.messagesProvider = new vine.SimpleMessagesProvider({
  'email.required': 'O campo e-mail é obrigatório.',
  'email.email': 'O endereço de e-mail é inválido.',
  'password.minLength': 'A senha deve ter pelo menos 8 caracteres.',
})
```

## 3. Criando Exceções Personalizadas

Use exceções personalizadas para falhas de regras de negócio. Isso isola a lógica de resposta de erro dos controllers.
Gere uma exceção usando o Ace: `node ace make:exception AccountSuspendedException`

```typescript
import { Exception } from '@adonisjs/core/exceptions'
import { HttpContext } from '@adonisjs/core/http'

export default class AccountSuspendedException extends Exception {
  static status = 403
  static code = 'E_ACCOUNT_SUSPENDED'

  constructor(message = 'Sua conta foi suspensa.') {
    super(message)
  }

  /**
   * Método opcional handle para definir a capacidade de auto-renderização.
   * O AdonisJS chama este método automaticamente ao retornar as respostas.
   */
  async handle(error: this, ctx: HttpContext) {
    const isJsonRequest = ctx.request.accepts(['html', 'json']) === 'json' || ctx.request.url().startsWith('/api')

    if (isJsonRequest) {
      return ctx.response.status(error.status).send({
        error: {
          code: error.code,
          message: error.message,
        },
      })
    }

    return ctx.view.render('pages/errors/forbidden', { error })
  }
}
```

## 4. Práticas de Registro de Logs Estruturados

Sempre use logs estruturados em vez de strings simples para suportar a indexação em ferramentas de agregação de logs (ex: Kibana, Loki, Datadog).

### Usando o Logger Contextual
Prefira usar `ctx.logger` dentro das requisições HTTP em vez do serviço global `Logger`. O logger de contexto HTTP inclui metadados importantes, como o ID da requisição.

```typescript
import { HttpContext } from '@adonisjs/core/http'

export default class PostController {
  async store({ request, response, logger }: HttpContext) {
    logger.info({ payload: request.body() }, 'Criando novo post')

    try {
      // Lógica de negócios
      return response.created({ success: true })
    } catch (error) {
      logger.error({ err: error }, 'Falha ao criar o post')
      throw error // Propaga para o Exception Handler
    }
  }
}
```

### Referência de Níveis de Log
- **trace**: Eventos muito ruidosos (parâmetros de consulta de banco de dados, payload bruto de sockets).
- **debug**: Informações úteis para desenvolvedores durante a depuração local.
- **info**: Marcos importantes do sistema (pagamentos bem-sucedidos, logins de usuários, sucesso de implantação).
- **warn**: Ocorreu algo inesperado, mas o sistema se recuperou (ex: limite de taxa atingido, tentativa de login malsucedida).
- **error**: A operação do sistema falhou (tempo limite da API externa, erro de conexão com o banco de dados).
- **fatal**: O aplicativo inteiro não pode continuar rodando (porta já em uso, variáveis de ambiente obrigatórias ausentes).

## 5. Segurança & Mascaramento de Dados Sensíveis (Pino Redact)

Evite registrar credenciais, cartões de crédito ou cabeçalhos de autenticação em produção. Configure o mascaramento de logs em `config/logger.ts`.

```typescript
import env from '#start/env'
import app from '@adonisjs/core/services/app'
import { defineConfig, syncDestination, targets } from '@adonisjs/core/logger'

const loggerConfig = defineConfig({
  default: 'app',
  loggers: {
    app: {
      enabled: true,
      name: env.get('APP_NAME'),
      level: env.get('LOG_LEVEL'),
      desination: !app.inProduction ? await syncDestination() : undefined,
      
      // Oculta chaves confidenciais na saída dos logs
      redact: {
        paths: [
          'password',
          'password_confirmation',
          'confirmPassword',
          'creditCard',
          'token',
          'headers.authorization',
          'payload.password',
        ],
        censor: '***MASKED***',
      },

      transport: {
        targets: [targets.file({ destination: 1 })],
      },
    },
  },
})

export default loggerConfig
```

## Restrições

- **Sem Vazamento de Dados Sensíveis**: Nunca exiba stack traces (`error.stack`) ou detalhes de erros brutos de SQL diretamente nas respostas HTTP em produção.
- **Sem Logs com o Console**: Sempre use `ctx.logger` ou o serviço global `Logger`. NÃO use `console.log`, `console.error` ou outros comandos globais de saída do Javascript.
- **Sem Blocos Try-Catch Vazios**: Não capture exceções para silenciá-las de forma oculta (`catch (e) {}`). Sempre registre o erro usando o logger ou relance a exceção.
- **Não Registre Logs Repetidamente**: Se você registrar um erro em um serviço, não o registre novamente dentro do controller ou do tratador de exceções. Registre apenas uma vez na fronteira apropriada.
- **Nunca Exiba Credenciais Brutas**: Mascare campos sensíveis usando a opção `redact` em `config/logger.ts` e verifique os payloads de log dinamicamente.
