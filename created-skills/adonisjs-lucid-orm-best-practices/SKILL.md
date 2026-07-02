---
name: adonisjs-lucid-orm-best-practices
description: Use when creating, modifying, reviewing, or debugging Lucid ORM models, migrations, relationships, queries, or database configurations in an AdonisJS application. Triggers on class definitions extending BaseModel, decorators like @column, @belongsTo, @hasMany, @manyToMany, database queries using model Query Builder, and transactions.
---

# Melhores Práticas para o AdonisJS Lucid ORM

## Objetivo
Fornecer diretrizes estritas e padrões para definições de modelos, relacionamentos, carregamento adiantado (eager loading/preload), ganchos de banco de dados (hooks) e segurança transacional usando o Lucid ORM em aplicações AdonisJS v6.

## Instruções

### 1. Definições de Modelos e Chaves Primárias
* **Classe Base**: Todos os modelos devem estender `BaseModel` de `@adonisjs/lucid/orm`.
* **Nome da Tabela**: Sempre defina o nome da tabela do banco de dados explicitamente via `static table = 'nome_da_tabela'`.
* **Atribuição Automática de Chave Primária**: Para chaves primárias baseadas em ULID, defina `static selfAssignPrimaryKey = true`. Use um gancho `@beforeCreate()` para atribuir um novo ULID antes de inserir o registro.
* **Sintaxe TypeScript Declare**: Sempre use o modificador `declare` do TypeScript para campos em vez de inicializadores de propriedade para evitar problemas em tempo de execução com campos de classe ESNext.
* **Timestamps**: Anote os timestamps usando `@column.dateTime({ autoCreate: true })` e `@column.dateTime({ autoCreate: true, autoUpdate: true })` com o tipo `DateTime` do `luxon`.

```typescript
import { DateTime } from 'luxon'
import { BaseModel, beforeCreate, column } from '@adonisjs/lucid/orm'
import { ulid } from 'ulid'

export default class User extends BaseModel {
  static table = 'users'
  static selfAssignPrimaryKey = true

  @beforeCreate()
  static assignUlid(model: User) {
    if (!model.id) model.id = ulid()
  }

  @column({ isPrimary: true })
  declare id: string

  @column.dateTime({ autoCreate: true })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true })
  declare updatedAt: DateTime
}
```

### 2. Serialização de Colunas e Campos JSON
* **Serialização JSON**: Ao trabalhar com colunas JSON ou não estruturadas no banco de dados (ex: configurações, parâmetros), use `@column` com as funções `prepare` e `consume` para lidar de forma segura com a serialização.
* **Ocultação de Campos**: Use `@column({ serializeAs: null })` para evitar que campos sensíveis (como senhas) sejam expostos em respostas JSON padrão.

```typescript
  @column({
    prepare: (value) => value ? JSON.stringify(value) : null,
    consume: (value) => {
      if (!value) return null
      return typeof value === 'string' ? JSON.parse(value) : value
    }
  })
  declare metadata: Record<string, any> | null

  @column({ serializeAs: null })
  declare password: string
```

### 3. Definição de Relacionamentos
* **Importações**: Importe decoradores como `@belongsTo`, `@hasMany`, `@manyToMany` de `@adonisjs/lucid/orm`. Importe as definições de tipo de relacionamento (`BelongsTo`, `HasMany`, `ManyToMany`) apenas como importações de tipo TypeScript de `@adonisjs/lucid/types/relations`.
* **Chaves Estrangeiras**: Sempre especifique explicitamente a propriedade `foreignKey` nas opções do decorador de relacionamento.
* **Aliases de Importação**: Importe modelos associados no topo do arquivo usando aliases de caminho (ex: `#models/...`).

```typescript
import { BaseModel, belongsTo, hasMany, column } from '@adonisjs/lucid/orm'
import type { BelongsTo, HasMany } from '@adonisjs/lucid/types/relations'
import SolarCompany from '#models/solar_company'
import CalendarEventArtwork from '#models/calendar/calendar_event_artwork'

export default class User extends BaseModel {
  @column()
  declare solarCompanyId: string | null

  @belongsTo(() => SolarCompany, { foreignKey: 'solarCompanyId' })
  declare solarCompany: BelongsTo<typeof SolarCompany>

  @hasMany(() => CalendarEventArtwork, { foreignKey: 'userId' })
  declare artworks: HasMany<typeof CalendarEventArtwork>
}
```

### 4. Carregamento Adiantado (Eager Loading) e Consultas Eficientes
* **Eager Loading**: Sempre use `.preload()` para buscar relações em vez de carregamento tardio (lazy loading) para evitar problemas de consultas N+1.
* **Relações Aninhadas**: Carregue relacionamentos aninhados usando um callback do builder:
  ```typescript
  const users = await User.query()
    .preload('solarCompany', (query) => {
      query.preload('address')
    })
  ```
* **Performance**: Evite executar consultas ao banco de dados dentro de loops. Busque os recursos necessários previamente ou consulte usando opções em lote (bulk).

### 5. Gerenciamento de Transações
* **Transações**: Use transações de banco de dados (`db.transaction`) para múltiplas consultas que dependem umas das outras.
* **Passagem de Contexto**: Garanta que todas as consultas de modelo dentro de uma transação utilizem a instância da transação (`trx`) via `useTransaction(trx)` ou pelo argumento de opções.

```typescript
import db from '@adonisjs/lucid/services/db'

const trx = await db.transaction()

try {
  const user = new User()
  user.name = 'John Doe'
  // Usa o cliente de transação
  await user.useTransaction(trx).save()

  await Profile.create({ userId: user.id, bio: 'Hello' }, { client: trx })

  await trx.commit()
} catch (error) {
  await trx.rollback()
  throw error
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Inicializadores de Propriedade**: Nunca use inicializadores padrão de propriedades de classe (ex: `id = ''`) em modelos. Sempre use `declare`.
* **SQL Raw**: Evite consultas SQL brutas (raw SQL) a menos que otimizações complexas sejam necessárias. Prefira o Lucid Query Builder.
* **Prevenção de N+1**: Nunca execute consultas separadas ao banco de dados dentro de loops `forEach` ou `map`. Carregue todos os dados através de relacionamentos adiantados (preload).
* **Transações**: Nunca execute mutações sequenciais sem envolver a confirmação (commit) e reversão (rollback) da transação em um bloco `try/catch`.
