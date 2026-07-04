import Transaction from '#models/transaction'
import AccountableResolver from '#services/accountable_resolver'

export default class TransactionService {
  private resolver = new AccountableResolver()

  async index(userId: string, profileIds: string[]): Promise<Record<string, unknown>[]> {
    // 1. Fetch transactions, preloading their pivot table of polymorphic relationships (accountables)
    const rows = await Transaction.query()
      .whereIn('profile_id', profileIds)
      .whereNull('deleted_at')
      .preload('accountables')
      .orderBy('date', 'desc')

    // 2. Extract all polymorphic links
    const allLinks = rows.flatMap((r) => r.accountables)

    // 3. Batch load polymorphic entities (avoiding N+1 queries)
    const resolvedMap = await this.resolver.loadForMany(allLinks)

    // 4. Map entities and inject them post-serialization (Lucid's serialize drops ad-hoc properties)
    return rows.map((row) => {
      const obj = row.serialize()
      
      obj.accountables = row.accountables.map((link) => {
        const resolved = resolvedMap.get(
          this.resolver.key(link.accountableType, link.accountableId)
        )
        // Only serialize the concrete entity if resolved
        const visible = resolved ? resolved.serialize() : null
        
        return { 
          ...link.serialize(), 
          resolved: visible 
        }
      })
      
      return obj
    })
  }
}
