---
name: adonisjs-multitenancy-data-isolation-best-practices
description: Use when designing, reviewing, or debugging multi-tenant architectures, data isolation, query scopes, and tenant middleware in AdonisJS. Triggers on requests involving database filters by tenant id (e.g., solarCompanyId, idSolarCompany), global Lucid query scopes, and tenant context resolution.
---

# Melhores Práticas de Multi-Tenancy e Isolamento de Dados no AdonisJS

## Objetivo
Fornecer diretrizes estritas e padrões para implementação de arquiteturas multi-tenant, isolamento de dados, escopos globais de consulta (Lucid) e resolução de contexto de requisição/job em aplicações AdonisJS v6.

## Instruções

### 1. Resolução do Contexto do Tenant (AsyncLocalStorage)
Para evitar vazamento de dados de tenants e garantir a segurança de tipos, gerencie o contexto ativo do tenant usando o `AsyncLocalStorage` do Node.js.
Crie um serviço dedicado `TenantService` para armazenar e recuperar o ID do tenant ativo com segurança.

```typescript
import { AsyncLocalStorage } from 'node:async_hooks'

export class TenantService {
  private static storage = new AsyncLocalStorage<string>()

  /**
   * Executa uma função de callback dentro do contexto de um tenant específico
   */
  static run<T>(tenantId: string, callback: () => T): T {
    return this.storage.run(tenantId, callback)
  }

  /**
   * Obtém o ID do tenant ativo no contexto de execução atual
   */
  static getTenantId(): string | null {
    return this.storage.getStore() ?? null
  }

  /**
   * Obtém o ID do tenant ativo ou lança um erro se não estiver definido
   */
  static getRequiredTenantId(): string {
    const tenantId = this.getTenantId()
    if (!tenantId) {
      throw new Error('O contexto do tenant não foi inicializado no fluxo de execução atual')
    }
    return tenantId
  }
}
```

### 2. Middleware de Detecção de Tenant
Implemente um middleware para resolver o tenant a partir da requisição (ex: subdomínios, cabeçalhos customizados como `X-Tenant-Id` ou associação com o usuário autenticado) e vincule a execução ao contexto do tenant.

```typescript
import type { HttpContext } from '@adonisjs/core/http'
import { TenantService } from '#services/tenant_service'

export default class TenantMiddleware {
  async handle(ctx: HttpContext, next: () => Promise<void>) {
    // 1. Resolve o ID do tenant (ex: do usuário autenticado ou cabeçalho da requisição)
    const tenantId = ctx.auth.user?.solarCompanyId || ctx.request.header('X-Tenant-Id')

    if (!tenantId) {
      return ctx.response.unauthorized({ error: 'Não foi possível resolver o contexto do tenant' })
    }

    // 2. Envolve a execução da requisição subsequente dentro do contexto do tenant
    await TenantService.run(tenantId, async () => {
      await next()
    })
  }
}
```

### 3. Escopos Globais de Consulta do Lucid (Global Query Scopes)
Use escopos globais de consulta do Lucid para aplicar automaticamente filtros de tenant em todas as consultas. Isso garante isolamento estrito de dados por padrão.

Crie uma classe reutilizável `TenantScope`:
```typescript
import { ModelQueryBuilderContract } from '@adonisjs/lucid/types/model'
import { TenantService } from '#services/tenant_service'

export class TenantScope {
  /**
   * Mapeamento do nome da coluna dependendo das convenções de nomenclatura do modelo
   */
  constructor(private tenantKey: 'solarCompanyId' | 'idSolarCompany' = 'solarCompanyId') {}

  apply(builder: ModelQueryBuilderContract<any>) {
    const tenantId = TenantService.getTenantId()
    
    // Apenas aplica o escopo se um ID de tenant estiver definido no contexto
    if (tenantId) {
      builder.where(this.tenantKey, tenantId)
    }
  }
}
```

Adicione o escopo global aos seus modelos:
```typescript
import { BaseModel, beforeCreate, column } from '@adonisjs/lucid/orm'
import { TenantScope } from '#scopes/tenant_scope'

export default class SocialMediaAgent extends BaseModel {
  static table = 'calendar_social_media_agent'

  @column()
  declare idSolarCompany: string // Chave estrangeira no banco de dados

  // Aplica o escopo global apontando para a chave estrangeira correta
  static boot() {
    super.boot()
    this.addGlobalScope('tenant', new TenantScope('idSolarCompany').apply)
  }
}
```

### 4. Consistência de Tenant em Mutações
Garanta a integridade dos dados durante a criação e atualização usando ganchos (hooks) do Lucid (`beforeCreate`, `beforeSave`). Isso evita que um usuário crie registros acidentalmente ou maliciosamente sob um tenant diferente.

```typescript
import { BaseModel, beforeCreate, column } from '@adonisjs/lucid/orm'
import { TenantService } from '#services/tenant_service'

export default class SocialMediaCharacter extends BaseModel {
  static table = 'social_media_characters'

  @column()
  declare solarCompanyId: string

  @beforeCreate()
  static setTenant(model: SocialMediaCharacter) {
    const tenantId = TenantService.getRequiredTenantId()
    
    // Garante ou sobrescreve o ID do tenant com o contexto atual
    model.solarCompanyId = tenantId
  }
}
```

### 5. Jobs em Segundo Plano Multi-Tenant (BullMQ)
Ao disparar jobs em segundo plano, sempre passe o contexto do tenant ativo no payload do job. Reestabeleça o contexto do tenant dentro da execução do worker usando `TenantService.run`.

**Disparando o Job:**
```typescript
import { Queue } from 'bullmq'
import { TenantService } from '#services/tenant_service'

const queue = new Queue('social-media-agent')
await queue.add('generate-script', {
  eventId: 'event_123',
  tenantId: TenantService.getRequiredTenantId() // Passa o contexto do tenant
})
```

**Execução do Worker:**
```typescript
import { Worker, Job } from 'bullmq'
import { TenantService } from '#services/tenant_service'

new Worker('social-media-agent', async (job: Job) => {
  const { eventId, tenantId } = job.data

  // Executa o job dentro do contexto do tenant
  await TenantService.run(tenantId, async () => {
    // A lógica de processamento do job possui acesso isolado ao banco de dados automaticamente
    const event = await CalendarEvent.findOrFail(eventId)
    await event.generateScript()
  })
})
```

## Restrições
* **Sem Consultas Manuais de Tenant**: Evite adicionar manualmente filtros `.where('solarCompanyId', ...)` em ações padrão de controllers. Confie nos escopos globais de consulta para evitar vazamentos de dados.
* **Armazenamento de Contexto Estático**: Nunca armazene o ID do tenant ativo em variáveis estáticas de classe ou propriedades globais, pois elas persistem entre requisições HTTP concorrentes nos ambientes Octane e Node.js. Sempre use `AsyncLocalStorage`.
* **Mapeamento de Chave Estrangeira**: Verifique duas vezes o nome da chave estrangeira do tenant em cada modelo (ex: `solarCompanyId` ou `idSolarCompany`). Aplicar o nome da chave incorreto quebrará as consultas ao banco de dados.
* **Proteção de Mutação**: Nunca insira ou atualize registros sem verificar se a propriedade `tenantId` está alinhada com o contexto ativo do tenant.
* **Desativação de Escopos**: Apenas ignore os escopos globais (`ignoreScopes(['tenant'])`) em contextos administrativos/console ou após realizar uma validação explícita de autenticação e autorização.
