---
name: adonisjs-database-transactions-concurrency-best-practices
description: Use when writing, modifying, reviewing, or debugging database transactions, handling concurrency control, managing database locks (SELECT FOR UPDATE), resolving deadlocks, or orchestrating multi-table atomic writes with Lucid ORM in AdonisJS v6. Triggers on database.transaction, db.transaction, model.useTransaction, transaction rollback, and row locking queries.
---

# Boas Práticas para Transações de Banco de Dados e Concorrência no AdonisJS v6

## Objetivo
Estabelecer padrões rígidos, confiáveis e seguros para gerenciar transações de banco de dados, estratégias de bloqueio (locking) e controle de concorrência usando Lucid ORM no AdonisJS v6, evitando registros órfãos, gravações sujas (dirty writes), deadlocks e vazamento de conexões (connection leaks).

## Instruções

### 1. Transações Gerenciadas (Recomendado)
Prefira utilizar o bloco de transação autogerenciado `db.transaction(async (trx) => { ... })` em vez de iniciar e confirmar transações manualmente. Ele gerencia automaticamente o commit/rollback e é menos propenso a erros.

```typescript
import db from '@adonisjs/lucid/services/db'
import User from '#models/user'

await db.transaction(async (trx) => {
  const user = new User()
  user.fill({ username: 'john_doe', email: 'john@example.com' })
  
  // Vincula a instância do model à transação
  user.useTransaction(trx)
  await user.save()

  // Para operações em models relacionados
  await user.related('profile').create({ bio: 'Developer' }, { client: trx })
})
```

### 2. Transações Manuais
Quando for necessário o controle manual do ciclo de vida da transação, sempre envolva as operações em um bloco `try/catch` para garantir que o rollback seja executado em caso de falha.

```typescript
import db from '@adonisjs/lucid/services/db'
import User from '#models/user'

const trx = await db.transaction()

try {
  const user = new User()
  user.fill({ username: 'john_doe', email: 'john@example.com' })
  user.useTransaction(trx)
  await user.save()

  await trx.commit()
} catch (error) {
  await trx.rollback()
  throw error
}
```

### 3. Vinculação de Consultas e Models
- **Models criados ou atualizados**: Você DEVE chamar `modelInstance.useTransaction(trx)` antes de invocar `.save()`.
- **Query Builder**: Passe a instância da transação no parâmetro de opções `query({ client: trx })`.

```typescript
// Consulta realizada dentro de uma transação
const activeUser = await User.query({ client: trx })
  .where('email', 'john@example.com')
  .first()
```

### 4. Bloqueio Pessimista (SELECT FOR UPDATE)
Para prevenir condições de corrida (por exemplo, múltiplos webhooks atualizando a mesma linha simultaneamente), bloqueie as linhas usando `.forUpdate()`.

```typescript
await db.transaction(async (trx) => {
  // Consulta com bloqueio de escrita (lock para escrita)
  const wallet = await Wallet.query({ client: trx })
    .where('userId', user.id)
    .forUpdate()
    .firstOrFail()

  wallet.balance += amount
  wallet.useTransaction(trx)
  await wallet.save()
})
```

### 5. Prevenção de Deadlocks e Retentativas
- Mantenha as transações curtas e focadas em operações atômicas. Não inclua chamadas de rede lentas (ex: APIs de gateway de pagamento, envio de e-mails, uploads de arquivos) dentro dos blocos de transação. Faça as requisições de rede primeiro e depois persista no banco de dados.
- Bloqueie os registros consistentemente na mesma ordem em diferentes transações para prevenir esperas circulares.

## Restrições
- **NÃO use queries brutas para transações**: Nunca use comandos SQL manuais (`BEGIN`, `COMMIT`, `ROLLBACK`) para gerenciar transações, a menos que a API do Lucid esteja completamente indisponível para um caso específico.
- **NÃO deixe conexões órfãs**: Toda transação manual aberta (`db.transaction()`) DEVE obrigatoriamente ter uma execução correspondente de `trx.commit()` ou `trx.rollback()`.
- **Vinculação obrigatória**: Não execute consultas ou salve models dentro de um callback/bloco de transação sem passar `trx` ou sem usar `useTransaction(trx)`. Ignorar essa regra fará com que a operação ignore o contexto da transação, provocando leituras sujas ou bloqueios indesejados.
