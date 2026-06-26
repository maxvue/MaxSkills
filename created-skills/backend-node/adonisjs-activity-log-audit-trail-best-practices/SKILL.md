---
name: adonisjs-activity-log-audit-trail-best-practices
description: Use when designing, implementing, reviewing, or debugging user activity logs, audit trails, or model change tracking in AdonisJS v6. Triggers on model hooks, custom event listeners for tracking changes, storing before/after states in JSONB, and recording authentication-related actions (login, impersonation).
---

# Boas Práticas para Logs de Atividades e Trilhas de Auditoria no AdonisJS

## Objetivo
Fornecer um padrão seguro, performático e padronizado para projetar e implementar logs de atividades de usuários, rastreamento de alterações em modelos e trilhas de auditoria em aplicações AdonisJS v6, garantindo o isolamento de tenants e uma robusta integridade dos dados.

## Instruções

### 1. Esquema de Banco de Dados para Trilhas de Auditoria
* **JSON Binário (JSONB)**: Use `jsonb` nas migrações para armazenar a diferença (ex: estados anterior/posterior, ou metadados de campos alterados).
* **Tipos de Identificadores**: Sempre use ULID (`CHAR(26)`) para chaves primárias e chaves estrangeiras (ex: `user_id`, `marketing_agency_id`) para se alinhar aos padrões da base de código.
* **Índices**: 
  * Aplique um índice GIN nas colunas JSONB para consultas flexíveis.
  * Crie índices compostos nos identificadores de tenant e carimbo de data/hora (timestamp) (ex: `[marketing_agency_id, created_at]`) para otimizar as consultas de painéis.

```typescript
import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'activity_logs'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.specificType('id', 'CHAR(26)').primary()
      table.specificType('user_id', 'CHAR(26)').nullable().references('id').inTable('users').onDelete('SET NULL')
      table.specificType('marketing_agency_id', 'CHAR(26)').nullable().references('id').inTable('marketing_agencies').onDelete('CASCADE')
      table.string('action').notNullable() // ex: 'POST_CREATED', 'API_KEY_ROTATED'
      table.string('auditable_type').notNullable() // ex: 'User', 'InstagramCredential'
      table.specificType('auditable_id', 'CHAR(26)').notNullable()
      table.jsonb('old_values').nullable()
      table.jsonb('new_values').nullable()
      table.jsonb('metadata').nullable() // Contexto extra (ip, user-agent, impersonator)
      table.timestamp('created_at')
    })

    // Índices
    this.schema.raw(`CREATE INDEX idx_activity_logs_old_gin ON ${this.tableName} USING gin (old_values)`)
    this.schema.raw(`CREATE INDEX idx_activity_logs_new_gin ON ${this.tableName} USING gin (new_values)`)
    this.schema.raw(`CREATE INDEX idx_activity_logs_tenant_date ON ${this.tableName} (marketing_agency_id, created_at DESC)`)
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}
```

### 2. Definição do Modelo Lucid e Atributos Tipados
* **Tipagem**: Defina interfaces TypeScript explícitas para `old_values`, `new_values` e `metadata`. Evite o uso de `any`.
* **Chave Primária Automática**: Defina `static selfAssignPrimaryKey = true` e use um hook `@beforeCreate` para atribuir o ULID.

```typescript
import { DateTime } from 'luxon'
import { BaseModel, beforeCreate, belongsTo, column } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import { ulid } from 'ulid'
import User from '#models/user'

export interface LogMetadata {
  ip: string
  userAgent: string
  impersonatedBy?: string // Rastreia quem impersonou o usuário, se aplicável
}

export default class ActivityLog extends BaseModel {
  static table = 'activity_logs'
  static selfAssignPrimaryKey = true

  @beforeCreate()
  static assignUlid(model: ActivityLog) {
    if (!model.id) model.id = ulid()
  }

  @column({ isPrimary: true })
  declare id: string

  @column()
  declare userId: string | null

  @column()
  declare marketingAgencyId: string | null

  @column()
  declare action: string

  @column()
  declare auditableType: string

  @column()
  declare auditableId: string

  @column()
  declare oldValues: Record<string, any> | null

  @column()
  declare newValues: Record<string, any> | null

  @column()
  declare metadata: LogMetadata | null

  @column.dateTime({ autoCreate: true })
  declare createdAt: DateTime

  @belongsTo(() => User, { foreignKey: 'userId' })
  declare user: BelongsTo<typeof User>
}
```

### 3. Hooks de Model para Rastrear Alterações
* **Extrair Diferenças**: Utilize as propriedades `$original` e `$attributes` do modelo nos hooks Lucid (como `@afterSave` ou `@afterDelete`) para registrar modificações.
* **Determinar Propriedades Alteradas**: Compare as propriedades antes e depois. Filtre campos sensíveis como `password` ou tokens internos.
* **Envio Assíncrono (Async Dispatching)**: Transfira a gravação de logs de auditoria para eventos (`emitter`) ou workers de fila (ex: BullMQ) para evitar bloquear as requisições principais do usuário.

```typescript
// app/listeners/audit_listener.ts
import emitter from '@adonisjs/core/services/emitter'
import ActivityLog from '#models/activity_log'

export default class AuditListener {
  static register() {
    emitter.on('audit:log', async (data) => {
      await ActivityLog.create(data)
    })
  }
}
```

```typescript
// dentro de um modelo auditável: ex: app/models/social_media_credential.ts
import { BaseModel, column, afterSave } from '@adonisjs/lucid/orm'
import emitter from '@adonisjs/core/services/emitter'

export default class SocialMediaCredential extends BaseModel {
  // Atributos do modelo...

  @afterSave()
  static async logSave(model: SocialMediaCredential) {
    const isNew = !model.$original.id
    const oldValues: Record<string, any> = {}
    const newValues: Record<string, any> = {}

    // Excluir chaves sensíveis do log
    const ignoredKeys = ['password', 'token', 'secret', 'updatedAt']

    for (const key of Object.keys(model.$attributes)) {
      if (ignoredKeys.includes(key)) continue

      const originalVal = model.$original[key]
      const currentVal = model.$attributes[key]

      if (originalVal !== currentVal) {
        if (!isNew) {
          oldValues[key] = originalVal
        }
        newValues[key] = currentVal
      }
    }

    if (Object.keys(newValues).length > 0) {
      emitter.emit('audit:log', {
        action: isNew ? 'CREDENTIAL_CREATED' : 'CREDENTIAL_UPDATED',
        auditableType: 'SocialMediaCredential',
        auditableId: model.id,
        oldValues: isNew ? null : oldValues,
        newValues,
      })
    }
  }
}
```

### 4. Isolamento de Tenant e Registro de Impersonação
* **Garantia de Tenancy**: Certifique-se de que o `marketing_agency_id` seja sempre capturado e preenchido para manter o isolamento de dados entre clientes/agências.
* **Impersonação**: Quando um administrador estiver representando (impersonando) um usuário de agência, capture tanto o ID do usuário final (`userId`) quanto o ID do administrador real dentro de `metadata.impersonatedBy` usando os dados da sessão ativa.

## Restrições
* **NÃO use Serialização Manual**: Nunca aplique `prepare: (val) => JSON.stringify(val)` ou `consume: (val) => JSON.parse(val)` em campos JSONB do Lucid, pois isso causa erros de codificação/decodificação duplicados.
* **NÃO inclua Dados Sensíveis nos Logs**: Certifique-se de que credenciais, tokens ou senhas hash sejam explicitamente excluídos de `old_values` e `new_values`.
* **NÃO faça Chamadas Bloqueantes Diretas ao Banco nos Hooks**: Não execute instruções SQL pesadas ou transações de forma síncrona dentro de hooks de ciclo de vida do Lucid ORM. Delegue para `emitter.emit()` ou para um job de fila.
* **NÃO use Interpolação de Strings para Prevenir Injeção de SQL**: Evite a interpolação de strings dentro de construtores de consulta ao buscar ou filtrar valores JSONB. Sempre use bindings de parâmetros (`?`).
