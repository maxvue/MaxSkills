import UserAccount from '#models/user_account'
import UserCard from '#models/user_card'
import TransactionAccountable from '#models/transaction_accountable'
import { type AccountableType } from '#enums/accountable'

/**
 * Instância concreta resolvida a partir de um vínculo polimórfico.
 */
export type Accountable = UserAccount | UserCard

/**
 * Resolve vínculos polimórficos (`accountable_type` + `accountable_id`) para os
 * models concretos. O Lucid não tem `morphTo` nativo, então fazemos isso
 * manualmente — inclusive o preload em lote, agrupando por tipo para evitar N+1.
 */
export default class AccountableResolver {
  /**
   * Resolve um único vínculo para sua instância (UserAccount | UserCard).
   * Retorna `null` se o registro referenciado não existir mais.
   */
  async resolve(type: AccountableType, id: string): Promise<Accountable | null> {
    switch (type) {
      case 'account':
        return await UserAccount.find(id)
      case 'card':
        return await UserCard.find(id)
      default:
        throw new Error(`Tipo de accountable não suportado: "${type}"`)
    }
  }

  /**
   * Carrega em lote os accountables de vários vínculos, evitando N+1.
   * Retorna um mapa `accountable_type:accountable_id` → instância.
   */
  async loadForMany(rows: TransactionAccountable[]): Promise<Map<string, Accountable>> {
    const idsByType = new Map<AccountableType, Set<string>>()

    for (const row of rows) {
      const set = idsByType.get(row.accountableType) ?? new Set<string>()
      set.add(row.accountableId)
      idsByType.set(row.accountableType, set)
    }

    const result = new Map<string, Accountable>()

    for (const [type, ids] of idsByType) {
      const idList = [...ids]
      let instances: Accountable[] = []

      switch (type) {
        case 'account':
          instances = await UserAccount.query().whereIn('id', idList)
          break
        case 'card':
          instances = await UserCard.query().whereIn('id', idList)
          break
        default:
          throw new Error(`Tipo de accountable não suportado: "${type}"`)
      }

      for (const instance of instances) {
        result.set(this.key(type, instance.id), instance)
      }
    }

    return result
  }

  /**
   * Chave estável para o mapa retornado por `loadForMany`.
   */
  key(type: AccountableType, id: string): string {
    return `${type}:${id}`
  }
}
