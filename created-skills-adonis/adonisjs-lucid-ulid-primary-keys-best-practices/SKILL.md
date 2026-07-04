---
name: adonisjs-lucid-ulid-primary-keys-best-practices
description: Use when configuring, reviewing, or implementing ULID as primary keys in AdonisJS Lucid ORM models and database migrations. Triggers on setting up primary key column decorators, generating beforeCreate hooks for ULID generation, creating database migrations with ULID column types, and converting models to use ULIDs.
---

## Objetivo
Fornecer diretrizes e boas práticas para configurar e usar Universally Unique Lexicographically Sortable Identifiers (ULID) como chaves primárias em aplicações AdonisJS v6 usando o Lucid ORM e migrations de banco de dados.

## Instruções
Ao implementar ou revisar configurações de ULID:

### 1. Migrations de Banco de Dados
Defina colunas de chave primária ULID e colunas de chave estrangeira como strings com comprimento de 26 caracteres.

- **Definição da Chave Primária:**
  Use `table.string('id', 26).primary()` para declarar a chave primária.
- **Definição da Chave Estrangeira:**
  Use `table.string('related_id', 26)` para colunas de chave estrangeira.
- **Constraints de Chave Estrangeira:**
  Sempre indexe as chaves estrangeiras e defina os relacionamentos usando `table.foreign('related_id').references('id').inTable('related_table')` com comportamentos `onDelete` apropriados.

*Exemplo de Migration:*
```typescript
import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'posts'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.string('id', 26).primary()
      table.string('user_id', 26).notNullable().index()
      table.string('title').notNullable()
      
      table.timestamp('created_at')
      table.timestamp('updated_at')

      table.foreign('user_id').references('id').inTable('users').onDelete('CASCADE')
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}
```

### 2. Models do Lucid ORM
Configure o model do Lucid para autoatribuir a chave primária e gerar automaticamente o ULID antes da criação.

- **Instale o pacote `ulid`:** Garanta que o pacote npm `ulid` seja importado (`import { ulid } from 'ulid'`).
- **Desabilite o Auto-Increment:** Defina `static selfAssignPrimaryKey = true` na classe do model.
- **Hook Before Create:** Crie um hook `@beforeCreate()` para atribuir um novo ULID à chave primária do model caso ela ainda não esteja definida.
- **Coluna da Chave Primária:** Anote a propriedade `id` com `@column({ isPrimary: true })` como `string`.

*Exemplo de Model:*
```typescript
import { BaseModel, column, beforeCreate } from '@adonisjs/lucid/orm'
import { ulid } from 'ulid'

export default class Post extends BaseModel {
  static selfAssignPrimaryKey = true

  @column({ isPrimary: true })
  declare id: string

  @column()
  declare userId: string

  @column()
  declare title: string

  @beforeCreate()
  static assignUlid(model: Post) {
    if (!model.id) {
      model.id = ulid()
    }
  }
}
```

### 3. Migration: Convertendo Chaves Primárias Inteiras Existentes para ULID
Se você estiver convertendo uma tabela existente com chaves primárias inteiras para ULID:
1. Faça truncate/limpe dados temporários/locais se forem incompatíveis.
2. Remova as constraints de chave estrangeira existentes que referenciam a chave primária.
3. Remova a constraint de valor padrão (ex.: default de sequence) e altere os tipos da coluna para `varchar(26)`.
4. Recrie as constraints de chave estrangeira.
5. Use `this.defer` para garantir que essas queries raw no banco de dados sejam executadas com segurança durante o ciclo de vida da migration.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- Não use funções de auto-geração específicas do banco de dados para ULID (ex.: extensões uuid/ulid do PostgreSQL) diretamente como valores padrão em migrations, a menos que seja necessário; em vez disso, delegue a geração ao hook `@beforeCreate()` do model.
- Nunca misture inteiros auto-incrementados e ULIDs para o mesmo identificador de entidade.
- Garanta que as colunas de chave estrangeira correspondam exatamente ao comprimento de string de 26.
