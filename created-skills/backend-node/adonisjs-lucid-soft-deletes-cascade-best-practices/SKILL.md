---
name: adonisjs-lucid-soft-deletes-cascade-best-practices
description: Use when implementing, configuring, reviewing, or debugging soft deletes, cascading soft deletes, or restoring soft-deleted records and their relationships using Lucid ORM in AdonisJS v6. Triggers on models defining soft delete attributes, hooks, query scopes, and cascading delete logic.
---

## Objetivo
Padronizar e orientar a implementação de exclusões lógicas (soft deletes), exclusões lógicas em cascata e restauração de registros e suas relações associadas utilizando o Lucid ORM no AdonisJS v6.

## Instruções

## 1. Definição da Migration de Banco de Dados
Ao criar ou modificar esquemas de banco de dados que exijam soft delete, defina a coluna timestamp anulável `deleted_at`.

```typescript
import { BaseSchema } from '@adonisjs/lucid/schema'

export default class extends BaseSchema {
  protected tableName = 'calendar_events'

  async up() {
    this.schema.createTable(this.tableName, (table) => {
      table.string('id').primary()
      // Outras colunas...
      
      table.timestamp('deleted_at', { useTz: true }).nullable()
      table.timestamp('created_at').notNullable()
      table.timestamp('updated_at').nullable()
    })
  }

  async down() {
    this.schema.dropTable(this.tableName)
  }
}
```

## 2. Mixin de Soft Delete Reutilizável em TypeScript
Implemente um Mixin TypeScript reutilizável usando o helper `compose` do AdonisJS. Isso centraliza os escopos de consulta de exclusão lógica, hooks de ciclo de vida e métodos utilitários.

Crie o arquivo `app/mixins/with_soft_deletes.ts`:

```typescript
import { DateTime } from 'luxon'
import { BaseModel, beforeFind, beforeFetch, column } from '@adonisjs/lucid/orm'
import { ModelQueryBuilderContract, scope } from '@adonisjs/lucid/types/model'
import { NormalizeConstructor } from '@adonisjs/core/types/helpers'

export function withSoftDeletes<T extends NormalizeConstructor<typeof BaseModel>>(superclass: T) {
  class SoftDeletableModel extends superclass {
    @column.dateTime({ serializeAs: null })
    declare deletedAt: DateTime | null

    /**
     * Hook para excluir automaticamente linhas deletadas logicamente das consultas de seleção
     */
    @beforeFind()
    static ignoreDeletedFind(query: ModelQueryBuilderContract<any>) {
      const context = query.client.userContext || {}
      if (context.withTrashed) {
        return
      }
      if (context.onlyTrashed) {
        query.whereNotNull('deleted_at')
        return
      }
      query.whereNull('deleted_at')
    }

    @beforeFetch()
    static ignoreDeletedFetch(query: ModelQueryBuilderContract<any>) {
      const context = query.client.userContext || {}
      if (context.withTrashed) {
        return
      }
      if (context.onlyTrashed) {
        query.whereNotNull('deleted_at')
        return
      }
      query.whereNull('deleted_at')
    }

    /**
     * Escopo de consulta para incluir registros deletados logicamente
     */
    static withTrashed = scope((query) => {
      query.client.userContext = query.client.userContext || {}
      query.client.userContext.withTrashed = true
    })

    /**
     * Escopo de consulta para buscar APENAS registros deletados logicamente
     */
    static onlyTrashed = scope((query) => {
      query.client.userContext = query.client.userContext || {}
      query.client.userContext.onlyTrashed = true
    })

    /**
     * Marca o registro como deletado logicamente
     */
    async softDelete() {
      this.deletedAt = DateTime.now()
      await this.save()
    }

    /**
     * Restaura um registro deletado logicamente
     */
    async restore() {
      this.deletedAt = null
      await this.save()
    }
  }

  return SoftDeletableModel
}
```

## 3. Aplicando o Mixin aos Models Lucid
Componha a classe do model usando o mixin `withSoftDeletes`.

```typescript
import { compose } from '@adonisjs/core/helpers'
import { BaseModel, belongsTo, hasMany } from '@adonisjs/lucid/orm'
import type { BelongsTo, HasMany } from '@adonisjs/lucid/types/relations'
import { withSoftDeletes } from '#mixins/with_soft_deletes'
import CalendarEventArtwork from '#models/calendar/calendar_event_artwork'

export default class CalendarEvent extends compose(BaseModel, withSoftDeletes) {
  // ... Colunas ...

  @hasMany(() => CalendarEventArtwork)
  declare artworks: HasMany<typeof CalendarEventArtwork>
}
```

## 4. Implementando Soft Delete em Cascata
Quando um registro pai (ex: `CalendarEvent`) for deletado logicamente, propague o status para os seus relacionamentos filhos dentro de uma transação de banco de dados.

Evite deletar linhas filhas uma a uma dentro de estruturas de repetição (loops). Em vez disso, use atualizações em lote transacionais ou escopos de consulta.

```typescript
import db from '@adonisjs/lucid/services/db'

export default class CalendarEvent extends compose(BaseModel, withSoftDeletes) {
  // ...

  /**
   * Execução segura de exclusão lógica em cascata dentro de uma transação
   */
  async cascadeSoftDelete() {
    await db.transaction(async (trx) => {
      // Usar o contexto da transação para as operações no banco
      this.useTransaction(trx)
      
      // Realizar soft delete no pai
      await this.softDelete()

      // Propagar soft delete para as artes (artworks) relacionadas
      await this.related('artworks')
        .query()
        .useTransaction(trx)
        .update({ deleted_at: this.deletedAt })
    })
  }

  /**
   * Restauração em cascata segura dentro de uma transação
   */
  async cascadeRestore() {
    await db.transaction(async (trx) => {
      this.useTransaction(trx)
      
      // Restaurar o pai
      await this.restore()

      // Restaurar as relações filhas que foram deletadas na mesma data/hora
      await this.related('artworks')
        .query()
        .useTransaction(trx)
        .apply((scopes) => scopes.withTrashed())
        .whereNotNull('deleted_at')
        .update({ deleted_at: null })
    })
  }
}
```

## Restrições
- **Uso de Transações Obrigatório**: Nunca propague alterações de soft delete entre múltiplas tabelas/models sem envolver a execução em uma transação de banco de dados (`db.transaction()`).
- **Não Sobrescrever o Método Delete Nativo**: Não sobrescreva o método `delete()` base do modelo diretamente com comportamento de soft delete, a menos que isso seja explicitamente documentado e esperado pela arquitetura da aplicação, pois outros componentes ou scripts CLI podem depender da exclusão física real. Prefira métodos explícitos como `softDelete()`, `cascadeSoftDelete()` e `restore()`.
- **Query Scopes Vinculados ao Contexto**: Ao realizar consultas contendo joins, certifique-se de selecionar explicitamente as colunas desejadas ou qualificar as colunas `deleted_at` (ex: `nome_tabela.deleted_at IS NULL`) para evitar erros de ambiguidade de nome de coluna no SQL.
- **Não Utilizar Pacotes do AdonisJS v5**: Evite instalar pacotes NPM obsoletos projetados para soft deletes no AdonisJS v5. Utilize a abordagem nativa de Mixin TypeScript descrita acima para o AdonisJS v6.
