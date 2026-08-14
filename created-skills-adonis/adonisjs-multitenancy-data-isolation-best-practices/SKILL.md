---
name: adonisjs-multitenancy-data-isolation-best-practices
description: Use when designing, reviewing, or debugging multi-tenant architectures, data isolation, query scopes, and tenant middleware in AdonisJS. Triggers on requests involving database filters by tenant id (e.g., solarCompanyId, idSolarCompany), Lucid query hooks and named scopes, and tenant context resolution.
---

# Melhores Práticas de Multi-Tenancy e Isolamento de Dados no AdonisJS

## Objetivo
Fornecer diretrizes estritas e padrões para implementação de arquiteturas multi-tenant, isolamento de dados, filtro automático via query hooks/named scopes (Lucid) e resolução de contexto de requisição/job em aplicações AdonisJS v6.

## Instruções

### 1. Resolução do Contexto do Tenant (AsyncLocalStorage)
Para evitar vazamento de dados de tenants e garantir a segurança de tipos, gerencie o contexto ativo do tenant usando o `AsyncLocalStorage` do Node.js.
Crie um serviço dedicado `TenantService` para armazenar e recuperar o ID do tenant ativo com segurança.

```typescript
import { AsyncLocalStorage } from 'node:async_hooks'

export class TenantService {
  private static storage = new AsyncLocalStorage<string | symbol>()
  private static readonly CROSS_TENANT = Symbol('cross_tenant')

  /**
   * Executa uma função de callback dentro do contexto de um tenant específico
   */
  static run<T>(tenantId: string, callback: () => T): T {
    return this.storage.run(tenantId, callback)
  }

  /**
   * Executa uma operação administrativa cross-tenant deliberada (bypass de isolamento)
   */
  static runCrossTenant<T>(callback: () => T): T {
    return this.storage.run(this.CROSS_TENANT, callback)
  }

  /**
   * Verifica se o contexto atual é uma operação cross-tenant autorizada
   */
  static isCrossTenant(): boolean {
    return this.storage.getStore() === this.CROSS_TENANT
  }

  /**
   * Obtém o ID do tenant ativo no contexto de execução atual
   */
  static getTenantId(): string | null {
    const store = this.storage.getStore()
    return typeof store === 'string' ? store : null
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
Implemente um middleware para resolver o tenant a partir da autenticação (associação com o usuário autenticado ou subdomínio validado no banco) e vincule a execução ao contexto do tenant. **Nunca** confie em cabeçalhos controlados pelo cliente como `X-Tenant-Id`.

```typescript
import type { HttpContext } from '@adonisjs/core/http'
import { TenantService } from '#services/tenant_service'

export default class TenantMiddleware {
  async handle(ctx: HttpContext, next: () => Promise<void>) {
    // 1. Exige autenticação prévia (guard web/sessão). Use authenticate() que lança 401
    //    caso o usuário não esteja logado.
    const user = await ctx.auth.authenticate()

    // 2. Resolve o ID do tenant a partir do vínculo do usuário autenticado no servidor
    const tenantId = user.solarCompanyId

    if (!tenantId) {
      return ctx.response.forbidden({ error: 'Usuário não possui tenant associado' })
    }

    // 3. Envolve a execução da requisição subsequente dentro do contexto do tenant
    await TenantService.run(tenantId, async () => {
      await next()
    })
  }
}
```

> **Variante com múltiplos tenants ou subdomínio (ajuste ao seu schema):** Se um usuário puder acessar múltiplos tenants ou o sistema usar subdomínios, o subdomínio/seletor serve apenas para identificar o tenant pretendido, mas **sempre** deve ser validado contra o banco e contra os vínculos do usuário autenticado:
> ```typescript
> import type { HttpContext } from '@adonisjs/core/http'
> import { TenantService } from '#services/tenant_service'
> import SolarCompany from '#models/solar_company'
>
> export default class SubdomainTenantMiddleware {
>   async handle(ctx: HttpContext, next: () => Promise<void>) {
>     const user = await ctx.auth.authenticate()
>     const slug = (ctx.request.hostname() ?? '').split('.')[0]
>
>     const company = await SolarCompany.findBy('slug', slug)
>     if (!company) {
>       return ctx.response.notFound({ error: 'Tenant inexistente' })
>     }
>
>     const isMember = await user.related('solarCompanies').query().where('id', company.id).first()
>     if (!isMember) {
>       return ctx.response.forbidden({ error: 'Usuário sem acesso a este tenant' })
>     }
>
>     await TenantService.run(company.id, async () => {
>       await next()
>     })
>   }
> }
> ```

### 3. Filtro Automático de Tenant via Query Hooks do Lucid
> **Importante:** o Lucid v6 NÃO possui `addGlobalScope`/`static boot()` (isso é Eloquent/Laravel). No Adonis use **query hooks** (`@beforeFind`, `@beforeFetch`, `@beforePaginate`) para aplicar o filtro de tenant automaticamente, ou **named scopes** via `scope()` para aplicação explícita.

Crie um helper reutilizável que aplica o filtro no query builder, lendo o `tenantKey` dinamicamente para suportar convenções diferentes (`solarCompanyId` vs `idSolarCompany`).

> **Falhe fechado, nunca aberto:** O helper de filtro nunca pode "pular" o `where` por ausência de contexto — um contexto vazio é indistinguível de um contexto perdido. Use `getRequiredTenantId()` (que lança) e reserve o bypass para a chamada explícita `TenantService.runCrossTenant()`.

```typescript
import type { ModelQueryBuilderContract } from '@adonisjs/lucid/types/model'
import type { LucidModel } from '@adonisjs/lucid/types/model'
import { TenantService } from '#services/tenant_service'

export function applyTenantFilter(
  query: ModelQueryBuilderContract<LucidModel>,
  tenantKey: 'solarCompanyId' | 'idSolarCompany' = 'solarCompanyId'
) {
  // Bypass APENAS quando declarado explicitamente via TenantService.runCrossTenant()
  if (TenantService.isCrossTenant()) {
    return
  }

  // Falha FECHADO: sem contexto de tenant, a consulta NÃO roda em vez de rodar sem filtro.
  // Contexto perdido (job sem payload de tenant, comando Ace, callback fora do escopo do
  // AsyncLocalStorage) vira erro imediato, nunca vazamento silencioso entre tenants.
  const tenantId = TenantService.getRequiredTenantId()
  query.where(tenantKey, tenantId)
}
```

Aplique automaticamente em cada modelo usando os decorators de query hook do Lucid. Os hooks recebem o próprio query builder, então o filtro vale para `find*`, `fetch`/`all`, `paginate` e demais consultas de leitura:
```typescript
import { BaseModel, beforeFind, beforeFetch, beforePaginate, column } from '@adonisjs/lucid/orm'
import type { ModelQueryBuilderContract } from '@adonisjs/lucid/types/model'
import { applyTenantFilter } from '#scopes/tenant_scope'

export default class CalendarEvent extends BaseModel {
  static table = 'calendar_events'

  @column()
  declare idSolarCompany: string // Chave estrangeira no banco de dados

  // Aplica o filtro de tenant apontando para a chave estrangeira correta
  @beforeFind()
  @beforeFetch()
  static applyTenant(query: ModelQueryBuilderContract<typeof CalendarEvent>) {
    applyTenantFilter(query, 'idSolarCompany')
  }

  @beforePaginate()
  static applyTenantOnPaginate([countQuery, query]: [
    ModelQueryBuilderContract<typeof CalendarEvent>,
    ModelQueryBuilderContract<typeof CalendarEvent>,
  ]) {
    applyTenantFilter(countQuery, 'idSolarCompany')
    applyTenantFilter(query, 'idSolarCompany')
  }
}
```

> Para aplicação **explícita** (em vez de automática), prefira um named scope:
> ```typescript
> import { BaseModel, column, scope } from '@adonisjs/lucid/orm'
>
> export default class CalendarEvent extends BaseModel {
>   static forTenant = scope((query) => applyTenantFilter(query, 'idSolarCompany'))
> }
> // Uso: await CalendarEvent.query().withScopes((s) => s.forTenant())
> ```

### 4. Consistência de Tenant em Mutações
Garanta a integridade dos dados durante a criação e atualização usando ganchos (hooks) do Lucid (`beforeCreate`, `beforeSave`). Isso evita que um usuário crie registros acidentalmente ou maliciosamente sob um tenant diferente.

```typescript
import { BaseModel, beforeCreate, column } from '@adonisjs/lucid/orm'
import { TenantService } from '#services/tenant_service'

export default class SolarProject extends BaseModel {
  static table = 'solar_projects'

  @column()
  declare solarCompanyId: string

  @beforeCreate()
  static setTenant(model: SolarProject) {
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

const queue = new Queue('solar-proposals')
await queue.add('generate-proposal', {
  projectId: 'project_123',
  tenantId: TenantService.getRequiredTenantId() // Passa o contexto do tenant
})
```

**Execução do Worker:**
```typescript
import { Worker, Job } from 'bullmq'
import { TenantService } from '#services/tenant_service'

new Worker('solar-proposals', async (job: Job) => {
  const { projectId, tenantId } = job.data

  // Executa o job dentro do contexto do tenant
  await TenantService.run(tenantId, async () => {
    // A lógica de processamento do job possui acesso isolado ao banco de dados automaticamente
    const project = await SolarProject.findOrFail(projectId)
    await project.generateProposal()
  })
})
```

> Se `job.data.tenantId` vier ausente, o job deve falhar explicitamente (`TenantService.run` exige uma string) — com o filtro fechado, um job sem tenant erra em vez de processar dados de todos os tenants.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Origem do Tenant Sempre Confiável**: O ID do tenant ativo nunca pode vir de dado controlado pelo cliente — cabeçalhos (`X-Tenant-Id`), query string, cookies ou corpo da requisição. Derive-o do vínculo do usuário autenticado; se usar subdomínio, resolva-o contra o cadastro de tenants e valide a associação do usuário antes de abrir o contexto. Use `ctx.auth.authenticate()` (que lança 401), nunca `ctx.auth.check()` (que só retorna boolean e deixa passar requisições anônimas).
* **Sem Consultas Manuais de Tenant**: Evite adicionar manualmente filtros `.where('solarCompanyId', ...)` em ações padrão de controllers. Confie nos query hooks (`@beforeFind`/`@beforeFetch`/`@beforePaginate`) para evitar vazamentos de dados.
* **Armazenamento de Contexto Estático**: Nunca armazene o ID do tenant ativo em variáveis estáticas de classe ou propriedades globais, pois elas persistem entre requisições HTTP concorrentes nos ambientes Octane e Node.js. Sempre use `AsyncLocalStorage`.
* **Mapeamento de Chave Estrangeira**: Verifique duas vezes o nome da chave estrangeira do tenant em cada modelo (ex: `solarCompanyId` ou `idSolarCompany`). Aplicar o nome da chave incorreto quebrará as consultas ao banco de dados.
* **Proteção de Mutação**: Nunca insira ou atualize registros sem verificar se a propriedade `tenantId` está alinhada com o contexto ativo do tenant.
* **Desativação do Filtro Automático**: Para consultas cross-tenant (contextos administrativos/console), não há `ignoreScopes` no Lucid. Envolva a operação **explicitamente** em `TenantService.runCrossTenant(() => ...)`, sempre após validação explícita de autenticação e autorização. Nunca desative o filtro simplesmente deixando de inicializar o contexto: contexto ausente deve ser erro, não permissão total.
