---
name: adonisjs-sentry-monitoring-best-practices
description: Use when setting up, configuring, or debugging Sentry error monitoring and performance tracking in AdonisJS v6. Triggers on Sentry initialization, configuring the HttpExceptionHandler to report to Sentry, capturing errors in BullMQ workers, attaching request context (user, URL, IP), or tracing database queries and transactions.
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Fornecer diretrizes claras e padrões de código estritos para a integração do Sentry v8/v9 em aplicações AdonisJS v6. Isso inclui a captura de exceções HTTP não tratadas, enriquecimento do contexto com metadados de usuário e requisição, reporte de falhas em filas em background (BullMQ), rastreamento de performance de consultas ao banco (Lucid ORM) e conformidade com padrões de segurança para evitar vazamento de dados em produção.

## Instruções

## 1. Instalação e Configuração Básica
Para iniciar o monitoramento de erros, instale o SDK oficial do Sentry para Node.js:
```bash
npm install @sentry/node
```

Adicione o DSN do Sentry e as variáveis de ambiente ao schema de validação em `start/env.ts` (o módulo é importado em outros arquivos pelo alias `#start/env`):
```typescript
// start/env.ts
export default await Env.create(new URL('../', import.meta.url), {
  SENTRY_DSN: Env.schema.string.optional(),
})
```

Crie um arquivo de configuração em `config/sentry.ts`:
```typescript
import env from '#start/env'

const sentryConfig = {
  dsn: env.get('SENTRY_DSN'),
  environment: env.get('NODE_ENV'),
  enabled: env.get('NODE_ENV') === 'production' || !!env.get('SENTRY_DSN'),
  tracesSampleRate: 1.0,
}

export default sentryConfig
```

## 2. Inicialização Antecipada via instrument.ts
A auto-instrumentação do Sentry v8+ (HTTP, `pg`, etc.) depende de monkey-patching que precisa ocorrer **antes** de qualquer outro import/boot da aplicação. Inicializar na fase `register` de um provider é tarde demais, pois os módulos core já foram carregados. O padrão correto é um arquivo `instrument.ts` carregado primeiro:

```typescript
// start/instrument.ts
import env from '#start/env'
import * as Sentry from '@sentry/node'

if (env.get('NODE_ENV') === 'production' || env.get('SENTRY_DSN')) {
  Sentry.init({
    dsn: env.get('SENTRY_DSN'),
    environment: env.get('NODE_ENV'),
    tracesSampleRate: 1.0,
    // Integração automática de tracing para Node HTTP e bancos de dados (padrão na v8+)
  })
}
```

Carregue-o como o **primeiro** import no entrypoint, antes do bootstrap do Adonis:
```typescript
// bin/server.ts (topo absoluto do arquivo, antes de qualquer outro import)
import './start/instrument.js'
// ...demais imports e ignitor
```

Alternativamente, use a flag `--import` do Node para garantir a precedência:
```bash
node --import ./start/instrument.js bin/server.js
```

## 3. Capturar Exceções no HttpExceptionHandler
Conecte o Sentry ao reporter global de exceções localizado em `app/exceptions/handler.ts`. Ignore erros em ambiente de desenvolvimento local e erros padrão de HTTP 4xx (como validação ou autenticação).

> **Veja também:** a estrutura do `handler.ts`, o método `shouldReport()` e o logging estruturado com Pino ficam em `adonisjs-exception-handling-logging-best-practices`. Esta skill cobre apenas a camada Sentry sobre esse handler.

```typescript
import app from '@adonisjs/core/services/app'
import { type HttpContext, ExceptionHandler } from '@adonisjs/core/http'
import * as Sentry from '@sentry/node'

export default class HttpExceptionHandler extends ExceptionHandler {
  // Delega ao `shouldReport` da base: erros com estes status não são reportados (evita ruído 4xx)
  protected ignoreStatuses = [401, 403, 404, 422]

  async report(error: any, ctx: HttpContext) {
    if (!this.shouldReport(error)) {
      return
    }

    if (app.inProduction) {
      Sentry.withScope((scope) => {
        // Vincula o contexto do usuário se autenticado
        if (ctx.auth && ctx.auth.user) {
          scope.setUser({
            id: String(ctx.auth.user.id),
            email: ctx.auth.user.email || undefined,
            username: ctx.auth.user.username || undefined,
          })
        }

        // Vincula metadados detalhados da requisição
        scope.setExtra('request', {
          id: ctx.request.id(),
          url: ctx.request.url(true),
          method: ctx.request.method(),
          ip: ctx.request.ip(),
          headers: this.sanitizeHeaders(ctx.request.headers()),
          queries: ctx.request.qs(),
          params: ctx.request.params(),
        })

        Sentry.captureException(error)
      })
    }

    await super.report(error, ctx)
  }

  private sanitizeHeaders(headers: Record<string, any>): Record<string, any> {
    const sanitized = { ...headers }
    const sensitiveHeaders = ['authorization', 'cookie', 'x-csrf-token']
    for (const key of sensitiveHeaders) {
      if (sanitized[key]) {
        sanitized[key] = '[REDACTED]'
      }
    }
    return sanitized
  }
}
```

## 4. Monitoramento de Filas em Segundo Plano (BullMQ)
Ao utilizar o BullMQ para tarefas assíncronas, intercepte falhas e reporte-as ao Sentry. Use os listeners de eventos do worker para capturar exceções:

```typescript
import * as Sentry from '@sentry/node'
import { Worker } from 'bullmq'

// Ao definir workers:
const worker = new Worker('my-queue', async (job) => {
  // Lógica de execução do job
})

worker.on('failed', (job, err) => {
  Sentry.withScope((scope) => {
    scope.setTag('system', 'bullmq')
    scope.setTag('queue', job?.queueName || 'unknown')
    scope.setTag('job_name', job?.name || 'unknown')
    scope.setExtra('job_id', job?.id)
    scope.setExtra('job_data', job?.data)
    
    Sentry.captureException(err)
  })
})
```

## 5. Rastreamento de Banco de Dados e Lucid ORM
Para rastreamento de performance, o Sentry se conecta automaticamente a drivers nativos como `pg` ou `mysql2` na inicialização. Para instrumentar manualmente consultas lentas, escute o evento `db:query` no emitter. **Requisito:** habilite `debug: true` em `config/database.ts` (globalmente ou por conexão) para que o Lucid emita o evento `db:query`.

```typescript
import emitter from '@adonisjs/core/services/emitter'
import * as Sentry from '@sentry/node'

// Escutar o evento `db:query` para capturar consultas lentas
// Payload (DbQueryEventNode): { connection, model?, ddl?, duration?: [number, number], method, sql, bindings?, inTransaction? }
emitter.on('db:query', (query) => {
  const duration = query.duration
  const durationMs = Array.isArray(duration) ? (duration[0] * 1000 + duration[1] / 1e6) : duration

  // Captura no Sentry se a query exceder 1000ms
  if (durationMs > 1000) {
    Sentry.withScope((scope) => {
      scope.setTag('database', 'slow_query')
      scope.setExtra('sql', query.sql)
      scope.setExtra('bindings', query.bindings)
      scope.setExtra('duration_ms', durationMs)
      Sentry.captureMessage(`Slow DB Query: ${query.sql.substring(0, 100)}...`, 'warning')
    })
  }
})
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Não Envie Erros 4xx:** Evite o envio de erros 400, 401, 403, 404 e 422 para o Sentry para evitar ruído. Apenas capture códigos de status >= 500 ou exceções não tratadas.
- **Redação Rígida de Dados Sensíveis:** Sempre remova ou oculte cabeçalhos de autorização, cookies, senhas e tokens antes de enviar os metadados da requisição.
- **Inicialização Antecipada:** Certifique-se de que o `Sentry.init` seja executado em `start/instrument.ts`, carregado como o primeiríssimo import do entrypoint (ou via `node --import`), antes de qualquer módulo core de HTTP/banco. A fase `register` de um provider é tarde demais para a auto-instrumentação.
- **Não Silencie Erros:** A captura de erros no Sentry não deve ocultar a exceção na aplicação. Certifique-se de que o handler de exceções ou worker de fila registre a falha e se comporte de acordo.
