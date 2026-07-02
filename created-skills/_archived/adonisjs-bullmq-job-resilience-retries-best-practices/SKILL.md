---
name: adonisjs-bullmq-job-resilience-retries-best-practices
description: Use when designing, configuring, implementing, or debugging background jobs resilience, retry strategies, exponential backoff, and failure handling with BullMQ in AdonisJS v6. Triggers on setting up attempts config, error categorization, listening to worker failure events, and configuring retry behaviors.
---

## Objetivo
Estabelecer configurações robustas e padrões de código para jobs em background gerenciados pelo BullMQ no AdonisJS v6, garantindo resiliência, retentativas adequadas, tolerância a falhas e monitoramento claro de erros.

## Instruções

### 1. Configuração de Envio de Jobs (Dispatch)
Ao enviar um job, sempre defina uma política de retentativa com recuo exponencial (exponential backoff) em vez de confiar nas configurações padrões. Defina esta configuração no método `dispatch` do job.

- Use um número razoável de tentativas (`attempts`, tipicamente entre 3 e 5).
- Use `backoff` com `type: 'exponential'` para evitar sobrecarregar serviços downstream durante indisponibilidades.
- Configure políticas de retenção de jobs (`removeOnComplete` e `removeOnFail`) para evitar o inchaço da memória no Redis.

Exemplo de configuração:
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
        backoff: {
          type: 'exponential',
          delay: 2000, // 2s na primeira retentativa, depois 4s, 8s...
        },
        removeOnComplete: { count: 100, age: 24 * 3600 }, // Mantém no máximo 100, expira após 24h
        removeOnFail: { count: 500, age: 7 * 24 * 3600 }, // Mantém no máximo 500 para depuração, expira em 7 dias
      }
    )
  }
}
```

### 2. Categorização de Erros dentro de Handlers
No método `handle` do job, diferencie erros temporários (timeouts de rede, limites de taxa) de erros permanentes (falhas de validação, IDs de recursos inválidos).
- Para **erros temporários**: Deixe o erro propagar para que o BullMQ acione uma nova tentativa de execução.
- Para **erros permanentes**: Capture o erro e chame `await job.discard()`. O `discard()` instrui o BullMQ a NÃO realizar novas tentativas, independentemente de você relançar o erro depois. Em seguida, relance um erro para que a tentativa atual seja marcada como `failed` (e dispare os listeners/alertas) em vez de ser considerada concluída com sucesso.

Exemplo de tratamento:
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
        // Erro permanente: impede novas tentativas (discard) e marca esta tentativa como failed (throw)
        await job.discard()
        throw new Exception('Ocorreu um erro permanente. Descartando tentativas do job.', {
          status: 400,
          code: 'E_JOB_FATAL_ERROR',
        })
      }
      
      // Erro temporário: relança para acionar a retentativa com backoff do BullMQ
      throw error;
    }
  }
}
```

### 3. Registro de Listeners de Eventos do Worker
Trate erros globais de workers e rastreie falhas no nível da aplicação. Os workers devem registrar ouvintes para os eventos `failed` e `error` para relatar métricas ou emitir alertas (como no Sentry).
- Não permita que uma única falha de job derrube o processo do worker.
- Registre os listeners de eventos dentro do comando Ace do AdonisJS que inicializa os workers.

Instancie o `Worker` e registre os listeners dentro do método `run()` do comando Ace (o `app` já estará inicializado nesse ponto do ciclo de vida). Use `this.app.terminating` para encerrar o worker graciosamente e mantenha o comando vivo enquanto o worker processa.

Exemplo de estrutura em `commands/worker.ts`:
```typescript
import { BaseCommand } from '@adonisjs/core/ace'
import type { CommandOptions } from '@adonisjs/core/types/ace'
import { Worker } from 'bullmq'
import redisConfig from '#config/redis'
import FetchNewsJob from '#jobs/fetch_news_job'
import logger from '@adonisjs/core/services/logger'

export default class WorkerCommand extends BaseCommand {
  static commandName = 'worker'
  static description = 'Inicia os workers do BullMQ'

  // Mantém o processo vivo e carrega o container da aplicação
  static options: CommandOptions = {
    startApp: true,
    staysAlive: true,
  }

  async run() {
    const worker = new Worker(
      FetchNewsJob.queueName,
      async (job) => FetchNewsJob.handle(job),
      { connection: redisConfig.connection }
    )

    // Loga falhas específicas de jobs
    worker.on('failed', (job, err) => {
      logger.error(
        { err, jobId: job?.id, queueName: FetchNewsJob.queueName },
        `Job falhou após ${job?.attemptsMade} tentativas: ${err.message}`
      )
    })

    // Loga erros globais de conexão/worker
    worker.on('error', (err) => {
      logger.error({ err }, `Erro global do worker: ${err.message}`)
    })

    // Encerramento gracioso ao parar a aplicação
    this.app.terminating(async () => {
      await worker.close()
    })
  }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- NÃO use tentativas infinitas (`attempts: 0` ou valores muito altos como `999`) sem um mecanismo de alerta explícito.
- NÃO coloque valores fixos (hardcoded) para parâmetros de conexão do Redis dentro de filas ou workers. Sempre importe e use as propriedades de conexão de `#config/redis`.
- NÃO silencie erros no `handle` sem relançá-los para o BullMQ, a menos que `job.discard()` tenha sido chamado explicitamente. Silenciar erros sem descartar fará com que o BullMQ assuma que o job foi concluído com sucesso.
- Sempre use `job.discard()` em erros de validação ou de autorização para evitar retentativas redundantes.
