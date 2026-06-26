---
name: adonisjs-migrations-seeders-factories-best-practices
description: Use when creating, updating, or reviewing database migrations, database seeders, or model factories using Lucid ORM in an AdonisJS v6 application. Triggers on migration files, seeder definitions, factory configurations, schema changes, and mock data generation.
---

# Melhores Práticas de Migrações, Seeders e Factories no AdonisJS

## Objetivo
Estabelecer diretrizes estritas para a criação de migrações resilientes, seeders organizados e factories reutilizáveis no ecossistema do AdonisJS v6, garantindo deploys seguros em produção e eficiência em testes automatizados.

## Instruções

### 1. Migrações de Banco de Dados (Database Migrations)

* **Idempotência e Segurança**: Garanta que as operações de esquema nas migrações sejam seguras. Evite renomear ou remover colunas diretamente em bancos de dados de produção sem uma estratégia de migração em múltiplas fases (ex: adicionar nova coluna, sincronizar dados, depreciar a coluna antiga). Sempre defina os métodos `up()` e `down()` para permitir rollbacks limpos.
* **Chaves Primárias e Estrangeiras com ULID**: O padrão da Engeapp utiliza ULIDs de 26 caracteres para IDs. Nas migrações, defina as chaves da seguinte forma:
  - **Chave Primária**: `table.specificType('id', 'CHAR(26)').primary()`
  - **Chave Estrangeira**: `table.specificType('company_id', 'CHAR(26)').nullable().index()` (use `.notNullable()` se for obrigatório).
  - **Restrição (Constraint)**: Sempre defina políticas de atualização e exclusão em cascata:
    ```typescript
    table.foreign('company_id').references('id').inTable('companies').onUpdate('CASCADE').onDelete('CASCADE')
    ```
* **Timestamps e Soft Deletes**:
  - Timestamps: Sempre use `table.timestamps(true, true)` para criar automaticamente as colunas `created_at` e `updated_at` com fuso horário e valores padrão definidos no nível do banco de dados.
  - Soft Deletes: Se o model suportar exclusão lógica (soft delete), use `table.timestamp('deleted_at').nullable()`.
* **Convenções de Nomenclatura**: Os nomes das tabelas devem estar em snake_case (ex: `solar_company`, `calendar_events`).

#### Exemplo de Migração:
```typescript
import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'users'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.specificType('id', 'CHAR(26)').primary()
      table.string('name').notNullable()
      table.specificType('solar_company_id', 'CHAR(26)').nullable().index()
      table.string('email').nullable().unique()
      table.string('password').notNullable()
      table.enum('status', ['active', 'blocked', 'inactive']).defaultTo('active')
      table.timestamps(true, true)
      table.timestamp('deleted_at').nullable()

      table.foreign('solar_company_id').references('id').inTable('solar_company').onUpdate('CASCADE').onDelete('CASCADE')
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}
```

### 2. Seeders de Banco de Dados (Database Seeders)

* **Idempotência**: Os seeders devem ser executáveis múltiplas vezes sem lançar violações de restrição de unicidade ou duplicar registros. Sempre use `firstOrCreate` ou `updateOrCreate` nos models em vez de `create` puro.
* **Aliases de Caminho**: Importe os models usando o alias de caminho `#models/...`.
* **Estrutura e Sequência**:
  - Use o `MainSeeder` como o orquestrador para chamar outros sub-seeders na ordem correta, se necessário.
  - Mantenha os seeders de configuração/sistema (dados estáticos essenciais) separados dos seeders de dados fictícios/demonstração.

#### Exemplo de Seeder:
```typescript
import { BaseSeeder } from '@adonisjs/lucid/seeders'
import SolarCompany from '#models/solar_company'
import User from '#models/user'

export default class MainSeeder extends BaseSeeder {
  async run() {
    const company = await SolarCompany.firstOrCreate(
      { subdomain: 'dev' },
      {
        subdomain: 'dev',
        companyName: 'Empresa Demo',
        tradeName: 'Demo',
        isActive: true
      }
    )

    await User.firstOrCreate(
      { email: 'admin@socialmedia.dev' },
      {
        name: 'Admin',
        email: 'admin@socialmedia.dev',
        password: 'password',
        solarCompanyId: company.id,
        solarCompanyName: company.companyName,
        status: 'active'
      }
    )
  }
}
```

### 3. Factories de Modelos (AdonisJS v6)

* **Sintaxe**: Defina as factories usando `@adonisjs/lucid/factories` e exporte-as.
* **Localização**: Armazene as factories em `database/factories.ts` or em um diretório modular `database/factories/`.
* **Locale do Faker**: Configure o Faker para usar o locale em português do Brasil `pt_BR` ao preencher campos locais (ex: CNPJ, números de telefone, endereços).
* **Relacionamentos**: Use o construtor `.relation()` para gerenciar relacionamentos de modelos durante a geração de dados simulados em testes/seeding.
* **Estados**: Defina estados usando `.state()` para variantes comuns do status do modelo (ex: `blocked`, `inactive`).

#### Exemplo de Factory:
```typescript
import Factory from '@adonisjs/lucid/factories'
import User from '#models/user'
import { CompanyFactory } from './company_factory.js'

export const UserFactory = Factory
  .define(User, ({ faker }) => {
    // Define o locale do Faker para português do Brasil se necessário
    faker.locale = 'pt_BR'
    return {
      name: faker.person.fullName(),
      email: faker.internet.email().toLowerCase(),
      password: 'password123',
      status: 'active' as const
    }
  })
  .state('blocked', (row) => ({ status: 'blocked' }))
  .state('inactive', (row) => ({ status: 'inactive' }))
  .relation('company', () => CompanyFactory)
  .build()
```

## Restrições
* Nunca use chaves primárias inteiras autoincrementais, a menos que seja explicitamente solicitado pela configuração do projeto. Sempre use `CHAR(26)` para ULIDs.
* Nunca use `.create()` ou `.createMany()` de forma direta dentro dos seeders sem garantir que eles não duplicarão dados em execuções subsequentes.
* Nunca execute operações destrutivas de esquema (como remover colunas com dados existentes) em migrações sem um backup ou plano de segurança de migração.
* Sempre defina índices e restrições de chave estrangeira adequadamente em migrações para desempenho e integridade dos dados.
* Não importe models utilizando caminhos relativos como `../../models/user`; sempre use o alias `#models/user`.
