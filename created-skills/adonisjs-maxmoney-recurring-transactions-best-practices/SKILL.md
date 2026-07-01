---
name: adonisjs-maxmoney-recurring-transactions-best-practices
description: Use when designing, implementing, configuring, validating, or debugging recurring financial transactions, expense/revenue recurrence rules, parent-child transaction propagation, or BullMQ background processing jobs for transaction generation in AdonisJS v6 for MaxMoney (Dinheirou) application.
---

## Objetivo
Estabelecer padrões de código, manipulação de transações de banco de dados e padrões de processamento em segundo plano para transações financeiras recorrentes (despesas, receitas) no MaxMoney (Dinheirou) desenvolvido com AdonisJS v6.

## Instruções

### 1. Estrutura do Banco de Dados e Modelos
Ao lidar com transações recorrentes, certifique-se de que os modelos (`Expense`, `Revenue`) possuam os seguintes atributos:
- `recurrenceType`: Enum do tipo string representando a frequência (`'none' | 'daily' | 'weekly' | 'monthly' | 'yearly'`).
- `recurrenceGroupId`: String (ULID) agrupando todas as instâncias pertencentes à mesma regra de recorrência.
- Chave Primária: `id` como ULID atribuído no hook `@beforeCreate`.

Garanta que o schema do banco de dados possua um índice na coluna `recurrence_group_id` para filtragem eficiente durante edições ou geração em cascata.

### 2. Schema de Validação do VineJS
Certifique-se de que as requisições de entrada validem as regras de recorrência utilizando o VineJS. Exemplo de schema para armazenamento:
```typescript
import vine from '@vinejs/vine'

export const storeTransactionValidator = vine.compile(
  vine.object({
    profile_id: vine.string(),
    subcategory_id: vine.string(),
    account_id: vine.string().optional(),
    card_id: vine.string().optional(),
    description: vine.string().maxLength(255),
    amount: vine.number().min(0),
    date: vine.date(),
    notes: vine.string().optional(),
    is_paid: vine.boolean().optional(),
    recurrence_type: vine.enum(['none', 'daily', 'weekly', 'monthly', 'yearly'] as const).optional(),
    recurrence_end_date: vine.date().optional(),
  })
)
```

### 3. Atualizações em Cascata & Transações de Banco de Dados
Ao atualizar ou excluir transações recorrentes, o sistema deve suportar três estratégias (escopos de propagação):
1. **Única (`'single'`)**: Modificar ou excluir apenas o registro selecionado. Limpar o `recurrenceGroupId` se ele for desvinculado da série.
2. **Futuras (`'future'`)**: Modificar ou excluir o registro selecionado e todas as instâncias subsequentes no grupo de recorrência (`date >= target_date`).
3. **Todas (`'all'`)**: Modificar ou excluir todos os registros associados ao `recurrenceGroupId`.

Para evitar inconsistências, **sempre encapsule as atualizações/exclusões em cascata em uma transação SQL**:
```typescript
import db from '@adonisjs/lucid/services/db'
import Expense from '#models/expense'

async function updateFutureTransactions(
  targetExpense: Expense, 
  data: Record<string, any>, 
  profileId: string
) {
  return await db.transaction(async (trx) => {
    // Bloqueia os registros para atualização para evitar modificações concorrentes
    const futureExpenses = await Expense.query()
      .useTransaction(trx)
      .where('recurrenceGroupId', targetExpense.recurrenceGroupId!)
      .where('profileId', profileId)
      .where('date', '>=', targetExpense.date.toSQLDate()!)
      .whereNull('deletedAt')
      .forUpdate()

    for (const exp of futureExpenses) {
      exp.useTransaction(trx)
      exp.merge({
        subcategoryId: data.subcategory_id ?? exp.subcategoryId,
        accountId: data.account_id ?? exp.accountId,
        cardId: data.card_id ?? exp.cardId,
        description: data.description ?? exp.description,
        amount: data.amount ?? exp.amount,
        notes: data.notes ?? exp.notes,
      })
      await exp.save()
    }
  })
}
```

### 4. Geração via Job em Segundo Plano (BullMQ)
Para a criação automatizada de novas instâncias (ex: quando uma recorrência não possui limite ou precisa gerar instâncias para o próximo mês), envie jobs em segundo plano via BullMQ:
- Implemente um worker/job `GenerateRecurringTransactionsJob`.
- Execute periodicamente (ex: job cron diário) para escanear recorrências que necessitam de novas entradas para o período seguinte.
- Verifique e respeite qualquer limite de `recurrence_end_date` ou número máximo de ocorrências.
- Garanta a idempotência utilizando chaves de bloqueio ou verificando se uma transação com o mesmo `recurrenceGroupId` and `date` alvo já existe antes de inserir.

## Restrições
- **NÃO realize operações em cascata sem transações**: Nunca execute atualizações/exclusões de múltiplas linhas em loops sem encapsular a lógica em `db.transaction(async (trx) => { ... })`.
- **NÃO realize matemática de datas no lado do cliente para geração**: Não permita que o frontend calcule datas para gerar ocorrências. Sempre gerencie a progressão de datas de recorrência no backend usando Luxon.
- **NÃO use console.log para depuração**: Use `@adonisjs/core/services/logger` para rastreamento e reporte de falhas de fila ou reversão (rollback) de transações.
- **Sempre Valide Permissões**: Confirme o acesso do usuário ao perfil (`assertAccess`) e à conta (`assertAccountAccess`) antes de modificar qualquer transação na série.
