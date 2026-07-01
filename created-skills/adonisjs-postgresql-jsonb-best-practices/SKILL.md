---
name: adonisjs-postgresql-jsonb-best-practices
description: Use when configuring, querying, updating, or indexing PostgreSQL JSON/JSONB columns, using Lucid ORM JSON capabilities, writing raw PostgreSQL JSONB queries (whereRaw, jsonb_to_record, contains @>, exists ??), mapping JSON data in Lucid models, or optimizing database performance for JSON fields in AdonisJS.
---

# Boas Práticas de AdonisJS & PostgreSQL JSONB

## Objetivo
Estabelecer convenções limpas, seguras quanto a tipos e altamente performáticas para mapeamento, consulta, atualização e indexação de colunas PostgreSQL JSON/JSONB em aplicações AdonisJS v6 usando o Lucid ORM.

## Instruções

### 1. Migrações de Banco de Dados
Sempre defina colunas JSONB usando `table.jsonb()` nos arquivos de migração, em vez de `table.json()`. O JSONB armazena os dados em um formato binário decomposto, permitindo buscas mais rápidas e suporte a indexação.

```typescript
import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'users'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.string('id').primary()
      table.jsonb('metadata').nullable() // Use jsonb para armazenamento de JSON binário
      table.timestamp('created_at')
      table.timestamp('updated_at')
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}
```

### 2. Mapeamento de Model Lucid & Tipagem Estrita
O Lucid ORM gerencia nativamente a serialização e desserialização de JSON. Evite chamadas manuais para `JSON.stringify()` ou `JSON.parse()` em preparadores/consumidores, pois isso aciona bugs de dupla serialização.
Em vez disso, use o decorador `@column()` padrão e mapeie a propriedade para uma interface ou tipo TypeScript específico, evitando o uso de `any`.

```typescript
import { BaseModel, column } from '@adonisjs/lucid/orm'

// 1. Defina uma interface TypeScript estrita para a estrutura JSON
export interface UserMetadata {
  theme: 'light' | 'dark'
  notificationsEnabled: boolean
  preferences: {
    marketingEmails: boolean
    weeklyDigest: boolean
  }
}

export default class User extends BaseModel {
  @column({ isPrimary: true })
  declare id: string

  // 2. Decore com a coluna padrão e defina a tipagem de forma estrita
  @column()
  declare metadata: UserMetadata | null
}
```

### 3. Indexação de Banco de Dados
Para consultas de alta performance, indexe as colunas JSONB nas migrações utilizando índices GIN (Generalized Inverted Index) ou B-Tree.
- **Índice GIN (Objeto JSONB Completo)**: Ideal para buscar chaves ou verificar a existência de valores contidos em qualquer lugar dentro do JSON.
- **Índice B-Tree (Caminho Específico)**: Ideal para consultas que visam uma propriedade escalar específica dentro do JSON.

```typescript
import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'users'

  async up() {
    this.schema.alterTable(this.tableName, (table) => {
      // 1. Índice GIN para verificação de continuação/presença (ex: tags ou chaves de metadados)
      this.schema.raw(`CREATE INDEX idx_users_metadata_gin ON ${this.tableName} USING gin (metadata)`)

      // 2. Índice B-Tree para caminhos JSON específicos (a conversão do tipo deve coincidir com a consulta)
      this.schema.raw(`CREATE INDEX idx_users_metadata_theme ON ${this.tableName} (((metadata->>'theme')::text))`)
    })
  }

  async down() {
    this.schema.alterTable(this.tableName, (table) => {
      this.schema.raw('DROP INDEX idx_users_metadata_gin')
      this.schema.raw('DROP INDEX idx_users_metadata_theme')
    })
  }
}
```

### 4. Consultando Colunas JSONB
Utilize os métodos auxiliares JSON do Lucid/Knex ou consultas brutas (raw) com segurança. O Lucid v6 **não** expõe um `whereJson` genérico para igualdade de objeto; use os helpers JSON reais do query builder:
- **`whereJsonObject`**: Filtra linhas cuja coluna JSON é igual ao objeto informado.
- **`whereJsonSuperset`**: Verifica se o JSON da coluna contém (é superset de) o objeto/par chave-valor informado (operador `@>`).
- **`whereJsonSubset`**: Verifica se o JSON da coluna é subset do objeto informado (operador `<@`).
- **`whereJsonPath`**: Compara um valor extraído por JSONPath (operador `@@` / `jsonb_path_query`).
- **`whereRaw`**: Use para operadores PostgreSQL avançados, garantindo que todas as entradas sejam parametrizadas.

```typescript
// Corresponder a um par chave-valor contido no objeto (operador @>)
const darkThemeUsers = await User.query().whereJsonSuperset('metadata', { theme: 'dark' })

// Verificar superset em um caminho específico do JSON
const emailSubscribers = await User.query()
  .whereJsonSuperset('metadata', { preferences: { marketingEmails: true } })

// Comparar valor extraído por JSONPath
const proUsers = await User.query().whereJsonPath('metadata', '$.theme', '=', 'dark')

// Operador de continuação raw avançado (@>)
const tagMatches = await User.query().whereRaw("metadata->'tags' @> ?", [JSON.stringify(['newsletter'])])
```

### 5. Atualizações Parciais
Para atualizar apenas campos específicos de uma coluna JSONB sem reescrever todo o documento, use atualizações `whereRaw` ou `raw` utilizando `jsonb_set` ou o operador de concatenação `||`.

```typescript
import db from '@adonisjs/lucid/services/db'

// Opção A: Atualizar utilizando jsonb_set
await User.query()
  .where('id', userId)
  .update({
    metadata: db.raw("jsonb_set(coalesce(metadata, '{}'::jsonb), '{theme}', ?::jsonb)", [JSON.stringify('dark')])
  })

// Opção B: Mesclar objetos usando o operador de concatenação ||
await User.query()
  .where('id', userId)
  .update({
    metadata: db.raw("coalesce(metadata, '{}'::jsonb) || ?::jsonb", [JSON.stringify({ theme: 'dark' })])
  })
```

## Restrições
- **NÃO Usar Preparadores/Consumidores Manuais**: Não adicione funções `prepare` ou `consume` aos decoradores `@column()` de colunas JSON que chamam `JSON.stringify` ou `JSON.parse`. Isso causa erros de dupla serialização, pois o driver de banco lida com a serialização nativamente.
- **NÃO Usar Tipagem `any`**: Nunca tipifique uma coluna JSON como `any` nos Models do Lucid. Sempre defina um `type` ou `interface` TypeScript para garantir segurança de tipo estática.
- **NÃO Usar Operadores PostgreSQL sem Escape**: No Knex (motor de consulta do Lucid), o ponto de interrogação `?` é tratado como um placeholder posicional. Se você utilizar operadores JSONB do PostgreSQL como `?`, `?|` ou `?&`, você **DEVE** escapá-los como `\\?` (ex: `metadata \\? ?`), ou utilizar funções do PostgreSQL como `jsonb_exists(metadata, ?)` para evitar exceções de sintaxe de binding.
- **Limitações do Índice GIN**: Não use índices GIN para comparações de intervalo (ex: `<` ou `>`). Use índices B-Tree específicos nas propriedades extraídas.
- **Prevenção de Injeção de SQL**: Nunca interpole variáveis diretamente em strings dentro de `whereRaw` ou `db.raw`. Sempre passe as variáveis através do array de bindings.

```typescript
// ❌ PERIGOSO - Risco de Injeção de SQL
User.query().whereRaw(`metadata->>'theme' = '${theme}'`)

//  SEGURO - Usando Bindings
User.query().whereRaw("metadata->>'theme' = ?", [theme])
```

## Examples

### Exemplo Completo: Logs de Custo de IA com Metadados Tipados

**Tipos TypeScript e Interface (`app/types/ai_cost.ts`):**
```typescript
export interface AiExecutionMetadata {
  promptTemplate: string
  totalTokens: number
  modelConfig: {
    temperature: number
    maxTokens: number
  }
}
```

**Model Lucid (`app/models/agent_ai_cost.ts`):**
```typescript
import { BaseModel, beforeCreate, column } from '@adonisjs/lucid/orm'
import { ulid } from 'ulid'
import { AiExecutionMetadata } from '#types/ai_cost'

export default class AgentAiCost extends BaseModel {
  static table = 'agents_ai_cost'

  @beforeCreate()
  static assignUlid(model: AgentAiCost) {
    if (!model.id) model.id = ulid()
  }

  @column({ isPrimary: true })
  declare id: string

  @column()
  declare agent: string

  // Coluna de metadados JSONB com tipagem estrita
  @column()
  declare typeData: AiExecutionMetadata | null
}
```

**Consultando a existência de chaves utilizando a alternativa `jsonb_exists`:**
```typescript
// Encontrar logs de execução que contêm 'promptTemplate' dentro do metadado JSON
const logs = await AgentAiCost.query()
  .whereRaw("jsonb_exists(type_data, ?)", ['promptTemplate'])
```
