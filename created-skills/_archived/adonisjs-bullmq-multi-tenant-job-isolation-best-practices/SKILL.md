---
name: adonisjs-bullmq-multi-tenant-job-isolation-best-practices
description: Use when implementing, configuring, or debugging multi-tenant job execution, tenant queue isolation, concurrency throttling per tenant, or passing tenant context to BullMQ workers in AdonisJS v6. Triggers on setting up jobs with tenant IDs, managing tenant-specific BullMQ rate limits, and wrapping worker run methods with AsyncLocalStorage for database isolation.
---

# Boas Práticas de Isolamento de Jobs Multi-Tenant com BullMQ no AdonisJS

## Objetivo
Estabelecer padrões de design robustos, seguros e de alto desempenho para a execução de tarefas assíncronas em segundo plano utilizando BullMQ sob uma arquitetura multi-tenant no AdonisJS v6. Isso previne o vazamento de dados (tenant leakage), garante o isolamento correto do banco de dados por job e implementa limitação de concorrência para evitar a inanição de recursos.

## Instruções

### 1. Tipagem de Dados de Job Multi-Tenant (`JobPayload`)
Todo job executado em segundo plano em um contexto multi-tenant deve exigir explicitamente um identificador de tenant (`tenantId`) em sua interface de payload. Isso garante que o contexto seja propagado desde a requisição de despacho original até a execução final do worker assíncrono.

Defina a estrutura do payload em `app/jobs/`:
```typescript
export interface BaseTenantJobData {
  tenantId: string // Resolve para integradorId ou clientId dependendo do escopo de isolamento
}

export interface MyTenantJobData extends BaseTenantJobData {
  usinaId: string
  action: 'generate' | 'publish'
}
```

### 2. Captura de Contexto durante o Despacho
Ao despachar um job a partir de controllers, middlewares ou services durante uma requisição HTTP ativa, recupere o ID do tenant ativo do `TenantService` (que utiliza `AsyncLocalStorage`) e serialize-o no payload do job.

```typescript
import { TenantService } from '#services/tenant_service'
import GenerateReportJob from '#jobs/generate_report_job'

export default class UsinaReportController {
  async handle({ request, response }: HttpContext) {
    const usinaId = request.input('usinaId')
    
    // Recupera o ID do tenant ativo no contexto da requisição HTTP
    const tenantId = TenantService.getRequiredTenantId()
    
    // Passa o tenantId como parte do payload do job
    await GenerateReportJob.dispatch({
      tenantId,
      usinaId,
      action: 'generate',
    })

    return response.ok({ message: 'Relatório de geração solar agendado' })
  }
}
```

### 3. Restauração do Contexto do Worker (Envelopamento de Execução)
Como os workers do BullMQ rodam fora do ciclo de vida da requisição/resposta HTTP, o contexto do tenant é naturalmente perdido. O processador do worker deve interceptar o payload do job de entrada, recuperar o `tenantId` e envolver o manipulador real do job dentro de `TenantService.run()` utilizando o `AsyncLocalStorage` do Node.

Em `commands/worker.ts` (ou na configuração do seu worker):
```typescript
import { Worker, Job } from 'bullmq'
import { TenantService } from '#services/tenant_service'
import redisConfig from '#config/redis'
import GenerateReportJob from '#jobs/generate_report_job'

export default class WorkerRun extends BaseCommand {
  static commandName = 'worker:run'
  static options = { startApp: true }

  async run() {
    const { connection } = redisConfig

    const reportWorker = new Worker(
      GenerateReportJob.queueName,
      async (job: Job) => {
        const { tenantId } = job.data

        if (!tenantId) {
          throw new Error(`Job ${job.id} falhou: tenantId está ausente no payload`)
        }

        // Restaura o contexto do tenant para todas as consultas e escopos do banco de dados a jusante
        return await TenantService.run(tenantId, async () => {
          return await GenerateReportJob.handle(job)
        })
      },
      { connection }
    )
  }
}
```

### 4. Isolamento e Limitação de Concorrência de Tenant (Throttling)
Para evitar que um único tenant monopolize os workers da fila (por exemplo, um tenant disparando 10.000 tarefas e bloqueando todos os outros), aplique o isolamento de concorrência.

#### Opção A: Rate-Limiting Global e Filas Dedicadas por Tenant
ATENÇÃO: o BullMQ open-source NÃO suporta rate-limiting por grupo (`limiter.groupKey`). Essa funcionalidade existe apenas no BullMQ **Pro** (`Worker` de `@taskforcesh/bullmq-pro`, pago). Em open-source, o `limiter` aplica um teto **global** à fila inteira, não por tenant:
```typescript
const worker = new Worker(
  'high-throughput-queue',
  async (job) => { /* lógica do processador */ },
  {
    connection,
    // Teto GLOBAL da fila (não por tenant): no máx. 100 jobs por segundo no total
    limiter: {
      max: 100,
      duration: 1000,
    },
    concurrency: 10,
  }
)
```
Para isolamento real por tenant com open-source, use uma das estratégias:
- **Filas dedicadas por tenant** (`generate-report:${tenantId}`) com um worker/limiter próprio por fila; ou
- O **controle de concorrência na camada de aplicação com Redis** descrito na Opção B.
Se rate-limiting nativo por grupo for um requisito rígido, adote BullMQ Pro com `BullMQPro` + `group: { id: tenantId }` no payload.

#### Opção B: Controle de Concorrência na Camada de Aplicação com Redis
Se precisar limitar as execuções ativas simultâneas por tenant no nível do aplicativo, verifique as cotas de uso do tenant ou crie travas (locks) de concorrência dentro de um Service ou diretamente na execução do job antes de executar chamadas pesadas de IA ou APIs externas.

### 5. Logs Estruturados Multi-Tenant
Para permitir a depuração limpa de jobs multi-tenant, injete o `tenantId` ativo no contexto do Logger do AdonisJS. Sempre utilize loggers filhos (`child loggers`) dentro de suas tarefas em background.

```typescript
import type { Job } from 'bullmq'
import logger from '@adonisjs/core/services/logger'
import { TenantService } from '#services/tenant_service'

export default class GenerateReportJob {
  static readonly queueName = 'generate-report'

  // O tenantId NÃO é lido de estado global: ele é resolvido do ALS estabelecido
  // por TenantService.run() no worker (ver Seção 3). O handle depende desse
  // contexto implícito — nunca de variáveis estáticas compartilhadas.
  static async handle(job: Job) {
    const tenantId = TenantService.getRequiredTenantId()
    
    // Cria um logger escopado com a tag do tenant
    const jobLogger = logger.child({
      jobId: job.id,
      queue: this.queueName,
      tenantId,
    })

    jobLogger.info('Iniciando geração de relatório da usina solar')

    try {
      // Executa a lógica de negócios...
      jobLogger.info('Relatório de geração solar concluído com sucesso')
    } catch (error) {
      jobLogger.error({ err: error }, 'Falha ao gerar relatório da usina')
      throw error
    }
  }
}
```

## Restrições
* **Nenhuma Ação de Worker sem Tenant**: Nunca realize inserções, atualizações ou exclusões no banco de dados dentro de uma tarefa de worker sem antes estabelecer o contexto do `TenantService`.
* **Nenhum Estado Compartilhado em Nível de Classe**: Nunca armazene o `tenantId` do job atual em variáveis estáticas ou campos de classe compartilhados. Os workers processam múltiplos jobs de forma concorrente, e variáveis estáticas causarão vazamento de dados entre tenants (tenant leakage). Sempre execute as tarefas dentro de `TenantService.run()`.
* **Limpeza Segura de Contexto em Falhas**: Se o processo do worker falhar ou lançar uma exceção, garanta que o contexto seja limpo. O `TenantService.run()` gerencia a pilha de contextos automaticamente, mas quaisquer conexões ou configurações manuais personalizadas devem ser tratadas em um bloco `finally`.
* **Validação Explícita do Payload**: Rejeite e falhe qualquer job logo no início do Worker caso o `tenantId` esteja indefinido ou nulo no payload. Não utilize tenants padrão/admin de fallback a menos que tenha sido explicitamente projetado para tarefas globais administrativas.
