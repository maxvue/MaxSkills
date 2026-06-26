---
name: adonisjs-bullmq-queue-management-best-practices
description: Use when configuring, creating, auditing, or debugging background jobs, queues, or workers using BullMQ in an AdonisJS ecosystem. Triggers on Redis connections for queues, sandboxed workers, job retry and failure logic, and rate limiting backend tasks.
---

# Boas Práticas de Gerenciamento de Filas com BullMQ no AdonisJS

## Objetivo
Fornecer regras rígidas, padrões de configuração e modelos de código para a implementação de um sistema de filas resiliente com BullMQ em aplicações backend AdonisJS v6, otimizando conexões Redis, tratando retentativas/falhas de jobs e isolando tarefas pesadas.

## Instruções

### 1. Configuração da Conexão Redis (`config/redis.ts`)
* Estabeleça conexões dedicadas e estáveis com o Redis utilizando `maxRetriesPerRequest: null` dentro das opções de `connection` para evitar falhas em loops de conexão do BullMQ.
* Exemplo de configuração de conexão:
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
* Reaproveite a conexão padrão do Redis configurada em `config/redis.ts` em vez de gerar novas instâncias de conexão por fila.
* Exporte instâncias nomeadas de Queue:
  ```typescript
  import { Queue } from 'bullmq'
  import redisConfig from '#config/redis'

  const { connection } = redisConfig

  export const themeExtractionQueue = new Queue('theme-extraction', { connection })
  export const fetchNewsQueue = new Queue('fetch-news', { connection })
  export const strategyManagerQueue = new Queue('strategy-manager', { connection })
  ```

### 3. Estrutura de Definição de Jobs (`app/jobs/`)
* Defina cada job de background em sua própria classe sob `app/jobs/`.
* Mantenha as propriedades estáticas: `queueName` como uma string estrita de leitura (`readonly`).
* Implemente `static async dispatch(...)` para enfileirar novos jobs utilizando a instância da fila correspondente. Inclua opções como tentativas, backoff e gerenciamento de memória.
* Implemente `static async handle(job: Job<T>)` contendo a execução lógica do job, delegando tarefas complexas para Services da camada de negócio.
* Exponha uma interface de tipo TypeScript explícita para `JobData`.
* Exemplo de estrutura de Job:
  ```typescript
  import type { Job } from 'bullmq'
  import { fetchNewsQueue } from '#services/queue_service'
  import { NewsFetchService } from '#services/news_fetch_service'

  export interface FetchNewsJobData {
    solarCompanyId: string
  }

  export default class FetchNewsJob {
    static readonly queueName = 'fetch-news'

    static async dispatch(solarCompanyId: string) {
      await fetchNewsQueue.add('fetch', { solarCompanyId }, {
        attempts: 3,
        backoff: {
          type: 'exponential',
          delay: 5000,
        },
        removeOnComplete: { count: 100 },
        removeOnFail: { count: 500 },
      })
    }

    static async handle(job: Job<FetchNewsJobData>) {
      const service = new NewsFetchService()
      await service.fetchForCompany(job.data.solarCompanyId)
    }
  }
  ```

### 4. Comando Ace para os Workers do BullMQ (`commands/worker.ts`)
* Instancie todos os workers dentro de um Comando Ace (ex: `worker:run`) usando a opção `{ startApp: true }` para carregar todo o contexto do AdonisJS.
* Garanta Graceful Shutdown: Escute os sinais do sistema `SIGTERM` e `SIGINT` e aguarde `worker.close()` para todos os workers ativos antes de encerrar o processo.
* Implemente Workers Isolados (Sandboxed Workers) para tarefas pesadas de CPU (como copywriting de IA, processamento de imagem) referenciando arquivos de processadores externos para não bloquear o loop de eventos principal do Node.js.
* Exemplo de estrutura de comando:
  ```typescript
  import { BaseCommand } from '@adonisjs/core/ace'
  import { Worker } from 'bullmq'
  import redisConfig from '#config/redis'
  import FetchNewsJob from '#jobs/fetch_news_job'

  export default class WorkerRun extends BaseCommand {
    static commandName = 'worker:run'
    static description = 'Start BullMQ workers'
    static options = { startApp: true }

    async run() {
      const { connection } = redisConfig

      const workers = [
        new Worker(FetchNewsJob.queueName, (job) => FetchNewsJob.handle(job), {
          connection,
        }),
      ]

      this.logger.info(`Workers started: ${workers.map((w) => w.name).join(', ')}`)

      await new Promise<void>((resolve) => {
        const shutdown = async () => {
          this.logger.info('Shutting down workers…')
          await Promise.all(workers.map((w) => w.close()))
          resolve()
        }
        process.once('SIGTERM', shutdown)
        process.once('SIGINT', shutdown)
      })
    }
  }
  ```

### 5. Ciclo de Vida do Job, Retentativas e Rate Limiting
* Sempre defina estratégias de retentativas com backoff exponencial no método `Queue.add` utilizando as propriedades (`attempts`, `backoff`).
* Use as opções `removeOnComplete` e `removeOnFail` para liberar memória do Redis e evitar perda de desempenho.
* Utilize a capacidade de rate-limiting do BullMQ no worker ou na fila para dependências de APIs de terceiros.

## Restrições
* NUNCA defina dados de conexão brutos diretamente nos arquivos de Queue ou Worker. Sempre importe a configuração central do Redis de `#config/redis`.
* NUNCA atribua um número inteiro para `maxRetriesPerRequest` nas configurações do Redis utilizadas no BullMQ; o valor DEVE ser `null`.
* NUNCA execute transações de banco de dados pesadas ou consumo direto de APIs externas dentro do método `handle` do Job. Delegue esta lógica para Services.
* NUNCA execute tarefas intensivas de CPU diretamente no loop principal de eventos. Utilize Workers Isolados (Sandboxed Workers) via processos separados para tarefas pesadas.
* NUNCA encerre o processo do Worker abruptamente no encerramento do sistema. Implemente sempre um encerramento gracioso via `worker.close()`.
