---
name: adonisjs-bullmq-best-practices
description: Use when configuring, creating, auditing, or debugging background jobs, queues, or workers with BullMQ in AdonisJS v6. Covers Redis connection setup, queue services, job/worker structure, sandboxed CPU-bound workers, graceful shutdown, retries and exponential backoff, failure handling and worker event listeners, job idempotency and deduplication via deterministic jobId, distributed Redis locks (ioredis), Lucid ORM transactions in jobs/webhook processors, and multi-tenant job isolation (tenant context propagation, AsyncLocalStorage, per-tenant concurrency/throttling, structured tenant logging). Triggers on Redis connections for queues, sandboxed workers, retry/backoff config, error categorization, webhook deduplication, setting jobIds, distributed locks, transaction-wrapped DB writes in jobs, tenantId payloads, and per-tenant rate limiting.
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de BullMQ no AdonisJS v6

## Objetivo
Fornecer regras rígidas, padrões de configuração e modelos de código para um sistema de filas resiliente com BullMQ em aplicações backend AdonisJS v6: otimizando conexões Redis, isolando tarefas pesadas, garantindo retentativas/tolerância a falhas, idempotência/deduplicação, transações ACID e isolamento multi-tenant.

> Escopo do projeto: backend AdonisJS v6 + PostgreSQL (Lucid ORM). Realtime via Transmit (SSE) — quando um job precisar empurrar progresso ao front, emita por Transmit. No front, todo GET/save passa por stores `@maxvue/max-pinia`; jobs nunca são disparados por requisições/salvamentos manuais paralelos ao MaxPinia. Sem Inertia, Ziggy, Sanctum, Horizon ou Reverb.

## Instruções

### 1. Configuração da Conexão Redis (`config/redis.ts`)
* Estabeleça conexões dedicadas e estáveis com o Redis utilizando `maxRetriesPerRequest: null` dentro das opções de `connection` para evitar falhas em loops de conexão do BullMQ.
  ```typescript
  import env from '#start/env'

  const redisConfig = {
    connection: {
      host: env.get('REDIS_HOST'),
      port: env.get('REDIS_PORT'),
      password: env.get('REDIS_PASSWORD') || undefined,
      maxRetriesPerRequest: null,
    },
  } as const

  export default redisConfig
  ```

### 2. Serviço de Instanciação de Filas (`app/services/queue_service.ts`)
* Centralize todas as instanciações de `Queue` em um único arquivo de serviço.
* Reaproveite a conexão padrão do Redis de `#config/redis` em vez de gerar novas conexões por fila.
  ```typescript
  import { Queue } from 'bullmq'
  import redisConfig from '#config/redis'

  const { connection } = redisConfig

  export const proposalGenerationQueue = new Queue('proposal-generation', { connection })
  export const energyReportQueue = new Queue('energy-report', { connection })
  export const inverterSyncQueue = new Queue('inverter-sync', { connection })
  export const webhooksQueue = new Queue('webhooks', { connection })
  ```

### 3. Estrutura de Definição de Jobs (`app/jobs/`)
* Defina cada job em sua própria classe sob `app/jobs/`.
* Mantenha `queueName` como string estática `readonly`.
* Implemente `static async dispatch(...)` para enfileirar jobs, incluindo opções de tentativas, backoff e gerenciamento de memória.
* Implemente `static async handle(job: Job<T>)` com a execução, delegando lógica complexa para Services da camada de negócio.
* Exponha uma interface TypeScript explícita para `JobData`.
  ```typescript
  import type { Job } from 'bullmq'
  import { energyReportQueue } from '#services/queue_service'
  import { EnergyReportService } from '#services/energy_report_service'

  export interface EnergyReportJobData {
    plantId: string
  }

  export default class EnergyReportJob {
    static readonly queueName = 'energy-report'

    static async dispatch(plantId: string) {
      await energyReportQueue.add('generate', { plantId }, {
        attempts: 3,
        backoff: { type: 'exponential', delay: 5000 },
        removeOnComplete: { count: 100 },
        removeOnFail: { count: 500 },
      })
    }

    static async handle(job: Job<EnergyReportJobData>) {
      const service = new EnergyReportService()
      await service.generateForPlant(job.data.plantId)
    }
  }
  ```

### 4. Comando Ace para os Workers (`commands/worker.ts`)
* Instancie os workers dentro de um Comando Ace usando `{ startApp: true, staysAlive: true }` para carregar o container do AdonisJS e manter o processo vivo.
* Registre listeners de eventos `failed` e `error` (ver Seção 6) e use `this.app.terminating(...)` para encerramento gracioso aguardando `worker.close()`.
  ```typescript
  import { BaseCommand } from '@adonisjs/core/ace'
  import type { CommandOptions } from '@adonisjs/core/types/ace'
  import { Worker } from 'bullmq'
  import redisConfig from '#config/redis'
  import EnergyReportJob from '#jobs/energy_report_job'
  import logger from '@adonisjs/core/services/logger'

  export default class WorkerCommand extends BaseCommand {
    static commandName = 'worker'
    static description = 'Inicia os workers do BullMQ'
    static options: CommandOptions = { startApp: true, staysAlive: true }

    async run() {
      const { connection } = redisConfig

      const worker = new Worker(
        EnergyReportJob.queueName,
        async (job) => EnergyReportJob.handle(job),
        { connection }
      )

      worker.on('failed', (job, err) => {
        logger.error(
          { err, jobId: job?.id, queueName: EnergyReportJob.queueName },
          `Job falhou após ${job?.attemptsMade} tentativas: ${err.message}`
        )
      })
      worker.on('error', (err) => {
        logger.error({ err }, `Erro global do worker: ${err.message}`)
      })

      this.app.terminating(async () => {
        await worker.close()
      })
    }
  }
  ```

### 5. Workers Isolados (Sandboxed) para tarefas CPU-bound
* Para tarefas pesadas de CPU (geração de PDF, processamento de imagens de telhados/datasheets de módulos), use Sandboxed Workers referenciando um arquivo processor externo, para não bloquear o event loop principal do Node.
  * O processor file deve exportar como `default` uma função `async (job) => { ... }`, sem dependências do contexto HTTP:
    ```typescript
    // app/jobs/processors/pdf_report_processor.ts
    import type { Job } from 'bullmq'

    export default async function (job: Job<{ plantId: string }>) {
      const { PdfReportService } = await import('#services/pdf_report_service')
      const service = new PdfReportService()
      return service.render(job.data.plantId)
    }
    ```
  * Registre o Sandboxed Worker passando o caminho absoluto do arquivo `.js` compilado:
    ```typescript
    import { fileURLToPath } from 'node:url'
    import { Worker } from 'bullmq'

    const processorPath = fileURLToPath(
      new URL('../app/jobs/processors/pdf_report_processor.js', import.meta.url)
    )

    new Worker('pdf-report', processorPath, { connection })
    ```

### 6. Resiliência: Retentativas, Backoff e Categorização de Erros
* Sempre defina política de retentativa com **backoff exponencial** no `dispatch` (não confie nos padrões). Use `attempts` tipicamente entre 3 e 5, e `removeOnComplete`/`removeOnFail` com `count`/`age` para evitar inchaço do Redis.
  ```typescript
  import { fetchNewsQueue } from '#services/queue_service'

  export default class FetchNewsJob {
    static readonly queueName = 'fetch-news'

    static async dispatch(solarCompanyId: string) {
      await fetchNewsQueue.add(
        'fetch',
        { solarCompanyId },
        {
          attempts: 3,
          backoff: { type: 'exponential', delay: 2000 }, // 2s, 4s, 8s...
          removeOnComplete: { count: 100, age: 24 * 3600 },
          removeOnFail: { count: 500, age: 7 * 24 * 3600 },
        }
      )
    }
  }
  ```
* No `handle`, diferencie erros **temporários** (timeouts, rate limit → deixe propagar para o BullMQ retentar) de **permanentes** (validação, recurso inválido → `await job.discard()` para impedir novas tentativas, depois relance um erro para marcar como `failed` e disparar alertas).
  ```typescript
  import type { Job } from 'bullmq'
  import { Exception } from '@adonisjs/core/exceptions'

  export default class FetchNewsJob {
    static async handle(job: Job<FetchNewsJobData>) {
      try {
        const service = new NewsFetchService()
        await service.fetchForCompany(job.data.solarCompanyId)
      } catch (error) {
        if (error.status === 404 || error.code === 'E_VALIDATION_ERROR') {
          // Permanente: impede retentativas (discard) e marca como failed (throw)
          await job.discard()
          throw new Exception('Erro permanente. Descartando tentativas do job.', {
            status: 400,
            code: 'E_JOB_FATAL_ERROR',
          })
        }
        // Temporário: relança para acionar a retentativa com backoff
        throw error
      }
    }
  }
  ```
* Registre listeners `failed` e `error` no comando Ace (ver Seção 4) para métricas/alertas (ex: Sentry). Uma falha de job não deve derrubar o processo do worker.

### 7. Idempotência e Deduplicação via `jobId`
Ao disparar jobs onde o processamento duplicado deve ser evitado (webhooks de pagamento, callbacks de gateway, telemetria de inversores/equipamentos), defina um `jobId` **determinístico** combinando um prefixo de domínio com um identificador único do payload (ex: `webhook:inverter:evt_12345`). Se um job com aquele `jobId` já estiver em `waiting`, `delayed` ou `active`, o BullMQ ignora o novo enfileiramento.
```typescript
import { webhooksQueue } from '#services/queue_service'

export default class WebhookJob {
  static readonly queueName = 'webhooks'

  static async dispatch(webhookId: string, externalEventId: string) {
    const jobId = `webhook:inverter:${externalEventId}`

    await webhooksQueue.add(
      'process',
      { webhookId },
      {
        jobId,
        removeOnComplete: { age: 3600 },  // 1 hora
        removeOnFail: { age: 86400 },     // 24h para depuração
        attempts: 3,
        backoff: { type: 'exponential', delay: 5000 },
      }
    )
  }
}
```

### 8. Locks Distribuídos com Redis (ioredis)
O `jobId` não protege contra dois jobs idênticos executando simultaneamente em workers diferentes (ou após a remoção do primeiro). Para isso, adquira um lock distribuído no início do handler. Como o projeto não usa `@adonisjs/redis`, instancie o cliente `Redis` do `ioredis` com a conexão compartilhada.
```typescript
import { Redis } from 'ioredis'
import redisConfig from '#config/redis'

const redis = new Redis(redisConfig.connection)

/** NX: define só se não existir. PX: expiração em ms. */
export async function acquireLock(key: string, value: string, ttlMs: number): Promise<boolean> {
  const result = await redis.set(key, value, 'PX', ttlMs, 'NX')
  return result === 'OK'
}

/** Libera atomicamente via Lua: só quem adquiriu pode liberar. */
export async function releaseLock(key: string, value: string): Promise<boolean> {
  const luaScript = `
    if redis.call('get', KEYS[1]) == ARGV[1] then
      return redis.call('del', KEYS[1])
    else
      return 0
    end
  `
  const result = (await redis.eval(luaScript, 1, key, value)) as number
  return result === 1
}
```
```typescript
import type { Job } from 'bullmq'
import logger from '@adonisjs/core/services/logger'
import { acquireLock, releaseLock } from '#helpers/lock_helper'

export default class WebhookJob {
  static async handle(job: Job<{ webhookId: string }>) {
    const { webhookId } = job.data
    const lockKey = `lock:webhook:${webhookId}`
    const lockValue = `job:${job.id}:${Date.now()}`

    const acquired = await acquireLock(lockKey, lockValue, 30000)
    if (!acquired) {
      logger.warn({ webhookId }, 'Webhook já em processamento por outro worker. Pulando.')
      return
    }

    try {
      // operações de banco envolvidas em transação (Seção 9)
    } finally {
      await releaseLock(lockKey, lockValue)
    }
  }
}
```

### 9. Transações Lucid ORM (PostgreSQL)
Toda inserção/alteração/exclusão dentro de um job ou processador de webhook deve estar envolvida em uma transação ACID do Lucid, para evitar gravações parciais em reexecução.
* Envolva em `db.transaction()`.
* Passe `{ client: trx }` a todas as consultas/criações; use `model.useTransaction(trx)` ao salvar instâncias existentes.
```typescript
import { DateTime } from 'luxon'
import db from '@adonisjs/lucid/services/db'
import Webhook from '#models/webhook'
import InverterReading from '#models/inverter_reading'

await db.transaction(async (trx) => {
  const webhook = await Webhook.query({ client: trx }).where('id', webhookId).first()
  if (!webhook || webhook.processedAt) {
    return // já processado ou inexistente
  }

  await InverterReading.updateOrCreate(
    { externalReadingId: reading.externalReadingId },
    { ...reading },
    { client: trx }
  )

  webhook.useTransaction(trx)
  webhook.processedAt = DateTime.now()
  await webhook.save()
})
```

### 10. Isolamento Multi-Tenant
#### 10.1. Payload com `tenantId` obrigatório (`app/jobs/`)
Todo job em contexto multi-tenant deve exigir `tenantId` na interface do payload, propagando o contexto do despacho até a execução.
```typescript
export interface BaseTenantJobData {
  tenantId: string // integradorId ou clientId conforme o escopo de isolamento
}

export interface MyTenantJobData extends BaseTenantJobData {
  usinaId: string
  action: 'generate' | 'publish'
}
```

#### 10.2. Captura do contexto no despacho
Ao despachar durante uma requisição HTTP ativa, recupere o tenant do `TenantService` (que usa `AsyncLocalStorage`) e serialize-o no payload.
```typescript
import { TenantService } from '#services/tenant_service'
import GenerateReportJob from '#jobs/generate_report_job'

export default class UsinaReportController {
  async handle({ request, response }: HttpContext) {
    const usinaId = request.input('usinaId')
    const tenantId = TenantService.getRequiredTenantId()

    await GenerateReportJob.dispatch({ tenantId, usinaId, action: 'generate' })

    return response.ok({ message: 'Relatório de geração solar agendado' })
  }
}
```

#### 10.3. Restauração do contexto no worker
Workers rodam fora do ciclo HTTP, então o contexto do tenant se perde. O processador deve ler o `tenantId` do payload e envolver o handler em `TenantService.run()`.
```typescript
import { Worker, Job } from 'bullmq'
import { TenantService } from '#services/tenant_service'
import redisConfig from '#config/redis'
import GenerateReportJob from '#jobs/generate_report_job'

const { connection } = redisConfig

const reportWorker = new Worker(
  GenerateReportJob.queueName,
  async (job: Job) => {
    const { tenantId } = job.data
    if (!tenantId) {
      throw new Error(`Job ${job.id} falhou: tenantId ausente no payload`)
    }
    return await TenantService.run(tenantId, async () => {
      return await GenerateReportJob.handle(job)
    })
  },
  { connection }
)
```

#### 10.4. Limitação de Concorrência por Tenant (Throttling)
Para evitar que um tenant monopolize os workers:
* **Opção A — Filas dedicadas por tenant.** Este projeto usa **BullMQ open-source** (não BullMQ Pro). No OSS não existe rate-limiting por grupo (`limiter.groupKey`); o `limiter` aplica teto **global** à fila inteira. Para isolamento por tenant, crie filas dedicadas (`generate-report:${tenantId}`) com worker/limiter próprio:
  ```typescript
  const worker = new Worker(
    'high-throughput-queue',
    async (job) => { /* ... */ },
    {
      connection,
      limiter: { max: 100, duration: 1000 }, // teto GLOBAL, não por tenant
      concurrency: 10,
    }
  )
  ```
  Quando uma fila por tenant for inviável (muitos tenants), prefira a Opção B (controle por aplicação).
* **Opção B — Controle na camada de aplicação com Redis.** Verifique cotas do tenant ou crie locks de concorrência (Seção 8) em um Service antes de chamadas pesadas de IA/APIs externas.

#### 10.5. Logs Estruturados Multi-Tenant
Injete o `tenantId` ativo em um child logger. O `tenantId` é resolvido do ALS estabelecido por `TenantService.run()` (Seção 10.3) — nunca de variáveis estáticas compartilhadas.
```typescript
import type { Job } from 'bullmq'
import logger from '@adonisjs/core/services/logger'
import { TenantService } from '#services/tenant_service'

export default class GenerateReportJob {
  static readonly queueName = 'generate-report'

  static async handle(job: Job) {
    const tenantId = TenantService.getRequiredTenantId()
    const jobLogger = logger.child({ jobId: job.id, queue: this.queueName, tenantId })

    jobLogger.info('Iniciando geração de relatório da usina solar')
    try {
      // lógica de negócios...
      jobLogger.info('Relatório de geração solar concluído com sucesso')
    } catch (error) {
      jobLogger.error({ err: error }, 'Falha ao gerar relatório da usina')
      throw error
    }
  }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* NUNCA defina dados de conexão brutos diretamente nos arquivos de Queue/Worker. Sempre importe `#config/redis`.
* NUNCA atribua um inteiro a `maxRetriesPerRequest` nas configs do Redis usadas pelo BullMQ; DEVE ser `null`.
* NUNCA execute transações pesadas de banco ou consumo direto de APIs externas dentro do `handle`. Delegue a Services.
* NUNCA execute tarefas CPU-bound no event loop principal. Use Sandboxed Workers via processos separados.
* NUNCA encerre o worker abruptamente; sempre use encerramento gracioso via `worker.close()` (`this.app.terminating`).
* NÃO use tentativas infinitas (`attempts: 0`/`999`) sem alerta explícito; sempre use backoff exponencial.
* NÃO silencie erros no `handle` sem relançá-los, a menos que `job.discard()` tenha sido chamado — silenciar sem descartar faz o BullMQ considerar sucesso. Use `job.discard()` em erros de validação/autorização.
* NÃO use `jobId`s automáticos para tarefas que exijam deduplicação estrita; gere string determinística do payload.
* NÃO omita `removeOnComplete`/`removeOnFail`; deixar acumular no Redis causa vazamento de memória.
* NÃO omita a liberação do lock em `finally`, nem libere sem verificar o valor original (use o script Lua) — risco de deadlock/liberação indevida.
* NÃO execute consultas/alterações em transação sem passar `{ client: trx }` ou chamar `model.useTransaction(trx)`.
* **Multi-tenant — Nenhuma ação sem tenant:** nunca grave no banco dentro de um worker sem estabelecer o `TenantService`. Rejeite/falhe o job logo no início se `tenantId` for nulo (sem fallback admin, exceto tarefas globais explicitamente projetadas).
* **Multi-tenant — Nenhum estado compartilhado em nível de classe:** nunca guarde `tenantId` em variáveis estáticas/campos de classe; workers processam jobs concorrentes e isso causa tenant leakage. Sempre via `TenantService.run()`, com limpeza segura em `finally`.
