import { DateTime } from 'luxon'
import { BaseModel, beforeCreate, belongsTo, column } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import { ulid } from 'ulid'
import Transaction from '#models/transaction'
import type { AccountableAttribute, AccountableType } from '#enums/accountable'

/**
 * Vínculo polimórfico entre uma transação e sua fonte de fundos
 * (conta ou cartão). O Lucid não possui relação polimórfica nativa, então a
 * resolução de `accountable_type` + `accountable_id` para o model concreto é
 * feita manualmente em `app/services/accountable_resolver.ts`.
 */
export default class TransactionAccountable extends BaseModel {
  static table = 'transaction_accountables'
  static selfAssignPrimaryKey = true

  @beforeCreate()
  static assignUlid(model: TransactionAccountable) {
    if (!model.id) model.id = ulid()
  }

  @column({ isPrimary: true })
  declare id: string

  @column()
  declare transactionId: string

  @column()
  declare accountableType: AccountableType

  @column()
  declare accountableId: string

  @column()
  declare attribute: AccountableAttribute

  @column.dateTime({ autoCreate: true })
  declare createdAt: DateTime

  @column.dateTime({ autoCreate: true, autoUpdate: true })
  declare updatedAt: DateTime

  @belongsTo(() => Transaction, { foreignKey: 'transactionId' })
  declare transaction: BelongsTo<typeof Transaction>
}
