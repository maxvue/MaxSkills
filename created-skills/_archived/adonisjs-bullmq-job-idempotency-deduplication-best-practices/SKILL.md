---
name: adonisjs-bullmq-job-idempotency-deduplication-best-practices
description: Use when implementing, reviewing, or debugging BullMQ background jobs, queue worker configurations, or webhook processors that require idempotency, duplicate request prevention, or Redis lock mechanisms in AdonisJS. Triggers on custom job declarations, job data processing, setting jobIds for deduplication, and transaction-wrapped database operations.
---

# Boas Práticas de Idempotência e Deduplicação de Jobs no AdonisJS com BullMQ

## Objetivo
Estabelecer diretrizes e padrões sólidos de desenvolvimento para garantir idempotência, prevenir o processamento duplicado de tarefas e webhooks assíncronos, e proteger operações concorrentes de banco de dados usando BullMQ e locks distribuídos do Redis no AdonisJS v6.

## Instruções

### 1. Deduplicação de Jobs via `jobId` no BullMQ
Ao disparar jobs para uma fila onde o processamento duplicado deve ser evitado (ex: eventos de webhook de pagamento, callbacks de gateways ou webhooks de telemetria de inversores/equipamentos), sempre defina um `jobId` determinístico e exclusivo nas opções do job.

* **Geração de Chave Determinística:** Combine um prefixo do domínio com um identificador único do payload (ex: `webhook:payment:evt_12345`).
* **Comportamento de Deduplicação do BullMQ:** Se um job com um `jobId` específico já estiver em estado de espera (`waiting`), atrasado (`delayed`) ou ativo (`active`), o BullMQ rejeitará ou ignorará qualquer nova tentativa de adicionar um job com o mesmo `jobId`, evitando enfileiramento duplicado.
* **Evitar Vazamento de Memória:** Sempre especifique as restrições `removeOnComplete` e `removeOnFail` para garantir que o banco de dados Redis seja limpo após a execução do job.

#### Exemplo:
```typescript
import { webhooksQueue } from '#services/queue_service'

export default class WebhookJob {
  static readonly queueName = 'webhooks'

  static async dispatch(webhookId: string, externalEventId: string) {
    // Gera um jobId único e determinístico baseado no ID do evento externo
    const jobId = `webhook:inverter:${externalEventId}`

    await webhooksQueue.add(
      'process',
      { webhookId },
      {
        jobId,
        // Limpa automaticamente o histórico de jobs no Redis para evitar vazamento de memória
        removeOnComplete: { age: 3600 }, // Mantém jobs concluídos por 1 hora
        removeOnFail: { age: 86400 },    // Mantém jobs que falharam por 24 horas (para depuração)
        attempts: 3,                     // Tenta reexecutar até 3 vezes em caso de falha
        backoff: {
          type: 'exponential',
          delay: 5000,                   // Aguarda 5s antes da primeira tentativa, subindo exponencialmente
        },
      }
    )
  }
}
```

---

### 2. Locks Distribuídos com Redis (ioredis)
Se um job já estiver no estado ativo (`active`, em processamento) e outra requisição idêntica chegar, o `jobId` do BullMQ não impedirá que o segundo job seja executado se o primeiro já tiver sido removido, ou se eles executarem simultaneamente em workers diferentes. Nesses casos, é necessário criar um lock distribuído no início do handler.

Como este projeto não utiliza o pacote oficial `@adonisjs/redis` nativamente no AdonisJS v6, instancie o cliente `Redis` do pacote `ioredis` diretamente usando as configurações de conexão compartilhadas.

#### Implementação do Helper de Lock:
Crie um utilitário ou use padrões inline para adquirir e liberar locks de forma atômica:

```typescript
import { Redis } from 'ioredis'
import redisConfig from '#config/redis'

const redis = new Redis(redisConfig.connection)

/**
 * Adquire um lock distribuído.
 * NX: Define a chave apenas se ela ainda não existir.
 * PX: Define o tempo de expiração em milissegundos.
 */
export async function acquireLock(key: string, value: string, ttlMs: number): Promise<boolean> {
  const result = await redis.set(key, value, 'PX', ttlMs, 'NX')
  return result === 'OK'
}

/**
 * Libera o lock de forma atômica usando um script Lua para garantir
 * que apenas o cliente que adquiriu o lock possa liberá-lo.
 */
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

#### Uso do Lock no Handler do Job:
```typescript
import type { Job } from 'bullmq'
import logger from '@adonisjs/core/services/logger'
import { acquireLock, releaseLock } from '#helpers/lock_helper' // ou caminho customizado

export default class WebhookJob {
  static async handle(job: Job<{ webhookId: string }>) {
    const { webhookId } = job.data
    const lockKey = `lock:webhook:${webhookId}`
    // Cria um token único de proprietário para o lock usando ID do job e timestamp
    const lockValue = `job:${job.id}:${Date.now()}`
    
    // Tenta adquirir o lock por 30 segundos
    const acquired = await acquireLock(lockKey, lockValue, 30000)
    if (!acquired) {
      logger.warn({ webhookId }, 'Webhook já está sendo processado por outro worker. Pulando execução.')
      return
    }

    try {
      // Executa as operações de banco de dados envolvidas em transação
    } finally {
      // Sempre libera o lock no bloco finally
      await releaseLock(lockKey, lockValue)
    }
  }
}
```

---

### 3. Transações Lucid ORM
Toda inserção, alteração ou exclusão de banco de dados executada em um job de segundo plano ou processador de webhook deve ser envolvida em uma transação ACID do Lucid ORM. Isso evita gravações parciais se uma etapa falhar ou se o job for reexecutado.

* Envolva as consultas e atualizações de banco de dados em `db.transaction()`.
* Passe o objeto de transação `{ client: trx }` para todas as consultas, inserções e opções de criação de modelos.
* Use `model.useTransaction(trx)` ao salvar instâncias de modelos já existentes.

#### Exemplo:
```typescript
import { DateTime } from 'luxon'
import db from '@adonisjs/lucid/services/db'
import Webhook from '#models/webhook'
import InverterReading from '#models/inverter_reading'

// Dentro da lógica do handler do Job:
await db.transaction(async (trx) => {
  // Consulta executada dentro do contexto da transação.
  // Use o query builder com { client: trx } para amarrar a leitura à transação de forma explícita.
  const webhook = await Webhook.query({ client: trx }).where('id', webhookId).first()
  if (!webhook || webhook.processedAt) {
    return // Já processado ou não encontrado
  }

  // Executa atualizações passando a instância da transação
  await InverterReading.updateOrCreate(
    { externalReadingId: reading.externalReadingId },
    { ...reading },
    { client: trx }
  )

  // Vincula a transação à instância do modelo antes de salvar
  webhook.useTransaction(trx)
  webhook.processedAt = DateTime.now()
  await webhook.save()
})
```

---

## Restrições
* **NÃO** use `jobId`s gerados automaticamente para tarefas que exijam deduplicação estrita. Sempre gere uma string determinística baseada no payload.
* **NÃO** omita as opções `removeOnComplete` e `removeOnFail` ao adicionar jobs à fila. Deixá-los acumular no Redis causa vazamentos de memória.
* **NÃO** omita a liberação do lock do Redis em um bloco `finally`. Deixar de liberá-lo causa deadlocks.
* **NÃO** libere um lock de Redis sem verificar se o valor do lock coincide com o valor original gerado pelo contexto de execução atual. Use o script Lua fornecido para garantir a atomicidade.
* **NÃO** execute consultas ou alterações de banco de dados dentro de um job sem envolvê-las em uma transação Lucid ORM caso envolvam múltiplas tabelas ou atualizações dependentes.
* **NÃO** execute operações de banco de dados dentro de um bloco de transação sem passar explicitamente `{ client: trx }` ou chamar `model.useTransaction(trx)`. Fazer isso ignora a fronteira transacional.
