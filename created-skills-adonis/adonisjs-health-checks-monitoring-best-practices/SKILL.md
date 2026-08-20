---
name: adonisjs-health-checks-monitoring-best-practices
description: Use when designing, configuring, implementing, or debugging health checks, system monitoring services, or readiness/liveness checks in AdonisJS v6. Triggers on configuring database health checkers, Redis/BullMQ connection validation, external API availability checks (WhatsApp Cloud, gateways de pagamento EFI/Inter), setting up custom health reporters, or exposing security-hardened health check endpoints.
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Estabelecer diretrizes claras e padrões de código estruturados para implementar endpoints de verificação de integridade (health checks), monitoramento de integridade do sistema e validações de dependências (PostgreSQL, Redis, BullMQ, APIs externas) em aplicações AdonisJS v6, garantindo a detecção precoce de falhas de infraestrutura e prevenindo a degradação silenciosa de workers.

## Instruções

> **Nota sobre o pacote oficial**: O AdonisJS v6 oferece o módulo oficial de health checks. Atenção às origens dos checks — eles NÃO vêm todos de `@adonisjs/core/health`:
> - De `@adonisjs/core/health`: `HealthChecks`, `BaseCheck`, `Result`, `MemoryHeapCheck`, `MemoryRSSCheck`, `DiskSpaceCheck`.
> - De `@adonisjs/lucid/database`: `DbCheck`, `DbConnectionCountCheck` (banco de dados).
> - De `@adonisjs/redis`: `RedisCheck`, `RedisMemoryUsageCheck` — **esse pacote não está instalado no EngeAppNode**; instale `@adonisjs/redis` antes de usá-los (ou use a checagem manual de Redis mais abaixo).
>
> Estenda com checagens customizadas apenas com a classe base `BaseCheck` (não existe um export `Check`), para integrações externas que o pacote não cobre (WhatsApp Cloud, EFI, Inter). Os exemplos manuais abaixo servem como referência conceitual e para casos não cobertos pelo pacote.

## 1. Expondo um Endpoint Seguro `/health`
No AdonisJS v6, exponha uma rota dedicada para verificações de status de integridade. Este endpoint deve ser protegido contra varreduras não autorizadas para evitar ataques de Negação de Serviço (DoS) e evitar o vazamento de status do sistema para terceiros.

Exponha a rota em `start/routes.ts`:
```typescript
import router from '@adonisjs/core/services/router'
const HealthCheckController = () => import('#controllers/health_check_controller')

// Expor endpoint de health check público ou protegido por token
router.get('/health', [HealthCheckController, 'handle']).as('health.check')
```

Implemente o Controller in `app/controllers/health_check_controller.ts`:
```typescript
import { HttpContext } from '@adonisjs/core/http'
import env from '#start/env'
import HealthCheckService from '#services/health_check_service'

export default class HealthCheckController {
  async handle({ request, response, logger }: HttpContext) {
    const expectedToken = env.get('HEALTH_CHECK_TOKEN')
    const incomingToken = request.header('x-health-token') || request.input('token')

    if (expectedToken && incomingToken !== expectedToken) {
      logger.warn({ ip: request.ip() }, 'Tentativa de health check não autorizada bloqueada')
      return response.unauthorized({
        status: 'error',
        message: 'Unauthorized health probe'
      })
    }

    const report = await HealthCheckService.generateReport()
    
    if (report.status === 'CRITICAL') {
      return response.status(503).send(report)
    }

    return response.ok(report)
  }
}
```

## 2. Validação de Conexão PostgreSQL (Lucid)
Para verificar a saúde do banco de dados principal, use o serviço de banco de dados Lucid para executar uma consulta de teste leve. A verificação do status do pool de conexões e o cálculo da latência garantem que a consulta seja executada rapidamente sem travar.

Implemente a verificação do banco de dados em `app/services/health_check_service.ts`:
```typescript
import db from '@adonisjs/lucid/services/db'

export async function checkDatabase() {
  const start = process.hrtime()
  try {
    // Executa uma consulta mínima para verificar a conexão
    await db.connection().rawQuery('SELECT 1')
    const diff = process.hrtime(start)
    const latencyMs = Number((diff[0] * 1e3 + diff[1] * 1e-6).toFixed(2))

    return {
      status: 'OK',
      latencyMs,
    }
  } catch (error) {
    return {
      status: 'CRITICAL',
      error: error.message || 'Falha na conexão com o banco de dados',
    }
  }
}
```

## 3. Validação de Conexão Redis e BullMQ
Para workers de tarefas em segundo plano (BullMQ) e cache, garanta que o serviço Redis responda prontamente. Instancie um cliente temporário ou use as configurações de conexão para verificar a latência por meio de um comando `PING`.

```typescript
import Redis from 'ioredis'
import redisConfig from '#config/redis'

export async function checkRedis() {
  const start = process.hrtime()
  // Usar as configurações de conexão do arquivo de configuração
  const client = new Redis(redisConfig.connection)

  try {
    await client.ping()
    const diff = process.hrtime(start)
    const latencyMs = Number((diff[0] * 1e3 + diff[1] * 1e-6).toFixed(2))
    
    // client.quit() faz flush dos comandos pendentes antes de fechar (await-avel);
    // disconnect() encerra o socket imediatamente, sem flush.
    await client.quit()
    
    return {
      status: 'OK',
      latencyMs,
    }
  } catch (error) {
    try {
      await client.quit()
    } catch {}
    
    return {
      status: 'CRITICAL',
      error: error.message || 'Falha na conexão com o Redis',
    }
  }
}
```

## 4. Disponibilidade de APIs Externas (WhatsApp Cloud / Gateways de Pagamento)
Verifique a conectividade com integrações externas usadas pelo EngeApp (por exemplo, API do WhatsApp Cloud, gateways de pagamento como EFI/Inter). Use o `fetch` nativo do Node (sem introduzir `axios`), com `AbortSignal.timeout` para impor timeouts agressivos (máximo de 2 segundos) e evitar que a lentidão externa bloqueie a verificação de saúde interna.

```typescript
export async function checkExternalApi(name: string, url: string) {
  const start = process.hrtime()
  try {
    // Requisição HEAD/GET leve ao endpoint base, com timeout via AbortSignal
    await fetch(url, { method: 'HEAD', signal: AbortSignal.timeout(2000) })
    const diff = process.hrtime(start)
    const latencyMs = Number((diff[0] * 1e3 + diff[1] * 1e-6).toFixed(2))

    return {
      status: 'OK',
      latencyMs,
    }
  } catch (error) {
    // Tratar problemas de APIs de terceiros como WARNING em vez de CRITICAL
    // para evitar o disparo de reinicializações de contêiner falsas-positivas
    return {
      status: 'WARNING',
      error: `${name} inacessível: ${error.message}`,
    }
  }
}

// Ex.: checkExternalApi('WhatsApp Cloud', 'https://graph.facebook.com/')
//      checkExternalApi('EFI', 'https://api.efipay.com.br/')
```

## 5. Orquestração de Relatório Padronizado
Combine todas as verificações em um payload JSON consolidado. A resposta deve listar o status de cada serviço individual e especificar um status global (`OK`, `WARNING` ou `CRITICAL`).

```typescript
// app/services/health_check_service.ts
import logger from '@adonisjs/core/services/logger'

export default class HealthCheckService {
  static async generateReport() {
    const [dbResult, redisResult, whatsappResult] = await Promise.all([
      checkDatabase(),
      checkRedis(),
      checkExternalApi('WhatsApp Cloud', 'https://graph.facebook.com/'),
    ])

    const services = {
      database: dbResult,
      redis: redisResult,
      whatsapp: whatsappResult,
    }

    // Determinar status global
    let status = 'OK'
    if (dbResult.status === 'CRITICAL' || redisResult.status === 'CRITICAL') {
      status = 'CRITICAL'
    } else if (whatsappResult.status === 'WARNING') {
      status = 'WARNING'
    }

    const report = {
      status,
      timestamp: new Date().toISOString(),
      services,
    }

    if (status === 'CRITICAL') {
      logger.error({ report }, 'O status de integridade do sistema é CRITICAL')
    } else if (status === 'WARNING') {
      logger.warn({ report }, 'O status de integridade do sistema está degradado (WARNING)')
    }

    return report;
  }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Sem Vazamentos em Produção**: Nunca retorne credenciais de banco de dados, informações de esquema de tabela, tokens de API ou stack traces detalhados no payload JSON do `/health`.
- **Limite de Timeout Curto**: Cada verificação de integridade direcionada a serviços externos ou bancos de dados deve ter um timeout explícito (máximo de 2000-3000ms) para evitar que as requisições fiquem aguardando indefinidamente.
- **Sem Cache Estático**: Sempre execute as checagens de forma dinâmica para requisições ativas. Não sirva um status "OK" em cache indefinidamente.
- **Status Tolerante para Terceiros**: APIs de terceiros degradadas (WhatsApp Cloud, EFI, Inter) devem acionar um status `WARNING` em vez de `CRITICAL` para que ferramentas de orquestração de contêineres (Docker, Kubernetes) não executem reinicializações desnecessárias de contêineres.
- **Gerenciamento Limpo de Conexões**: Sempre feche e desconecte conexões temporárias (por exemplo, clientes `ioredis`) dentro de blocos `finally` ou blocos equivalentes para evitar vazamento de memória e exaustão de conexões.
