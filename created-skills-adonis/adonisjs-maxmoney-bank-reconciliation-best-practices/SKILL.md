---
name: adonisjs-maxmoney-bank-reconciliation-best-practices
description: Use when designing, implementing, configuring, reviewing, or debugging bank reconciliation features, OFX statement parsers, transaction matching rules, and automatic ledger reconciliation in AdonisJS v6. Triggers on files modifying transaction matching logic, OFX imports, reconciliation controllers, and database schema updates for bank statements in MaxMoney.
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Fornecer diretrizes de design de arquitetura, modelagem de banco de dados e lógica de negócios de backend para a construção de conciliação bancária segura e confiável no AdonisJS v6 para a plataforma financeira MaxMoney.

## Instruções

Ao implementar ou modificar recursos de conciliação bancária, siga as seguintes melhores práticas:

## 1. Modelagem e Esquema do Banco de Dados (Lucid ORM)
Desenhe o esquema do banco de dados para separar claramente os dados brutos do extrato bancário das transações locais do livro-razão (ledger). Use as seguintes estruturas de modelos:

*   **BankStatementImport:** Rastreia os arquivos enviados ou sessões de sincronização via API.
    *   Campos: `id` (ULID), `accountId` (ULID, pertence a `UserAccount`), `fileName` (string), `fileHash` (string, checksum único para evitar importações duplicadas), `importedAt` (DateTime).
*   **BankStatementTransaction:** Transações brutas extraídas do extrato do banco.
    *   Campos: `id` (ULID), `importId` (ULID, pertence a `BankStatementImport`), `fitid` (string, ID de Transação da Instituição Financeira - único por conta bancária), `amount` (número/decimal, positivo para créditos, negativo para débitos), `date` (Date, sem horário), `description` (texto bruto do banco), `status` (enum: `'pending'`, `'reconciled'`, `'ignored'`, `'discrepant'`).
*   **BankReconciliation:** O registro de conciliação que vincula os itens do banco aos registros locais.
    *   Campos: `id` (ULID), `bankTransactionId` (ULID, pertence a `BankStatementTransaction`), `reconciledType` (enum: `'expense'`, `'revenue'`, `'transfer'`), `reconciledId` (string, link polimórfico para o registro específico), `reconciledBy` (ULID, pertence a `User`), `method` (enum: `'auto'`, `'manual'`).

Exemplo de definições de Modelos usando aliases de subcaminhos (ex: `#models/...`):
```typescript
// app/models/bank_statement_transaction.ts
import { DateTime } from 'luxon'
import { BaseModel, beforeCreate, belongsTo, column } from '@adonisjs/lucid/orm'
import type { BelongsTo } from '@adonisjs/lucid/types/relations'
import { ulid } from 'ulid'
import BankStatementImport from '#models/bank_statement_import'

export default class BankStatementTransaction extends BaseModel {
  static table = 'bank_statement_transactions'
  static selfAssignPrimaryKey = true

  @beforeCreate()
  static assignUlid(model: BankStatementTransaction) {
    if (!model.id) model.id = ulid()
  }

  @column({ isPrimary: true })
  declare id: string

  @column()
  declare importId: string

  @column()
  declare fitid: string

  @column()
  declare amount: number

  @column.date()
  declare date: DateTime

  @column()
  declare description: string

  @column()
  declare status: 'pending' | 'reconciled' | 'ignored' | 'discrepant'

  @belongsTo(() => BankStatementImport, { foreignKey: 'importId' })
  declare import: BelongsTo<typeof BankStatementImport>
}
```

## 2. Pipeline de Importação Idempotente (Processamento de OFX)
*   **Verificação de Arquivo Duplicado:** Calcule o hash SHA-256 do arquivo enviado antes de processá-lo. Verifique na tabela `BankStatementImport`; rejeite com uma mensagem de erro clara se o hash já existir.
*   **Desduplicação de Transações (`fitid`):** Use o `fitid` fornecido pelo banco (encontrado em tags `<FITID>` no OFX/OFC) combinado com o `accountId` como uma verificação de unicidade composta. Ignore ou pule linhas que já foram importadas para evitar contagem duplicada.

## 3. Algoritmo de Regras de Correspondência (Matching Engine)
Implemente uma lógica de correspondência em camadas para lidar com transações automaticamente quando o nível de confiança for alto:

1.  **Correspondência Exata (Fase 1):**
    *   Busque um registro local não pago (`Expense` / `Revenue` onde `isPaid` ou equivalente seja `false`) vinculado à mesma conta (`UserAccount` / `Profile`).
    *   Critérios: `amount` (valor) coincide exatamente, e o `date` local está dentro de uma janela de $\pm$3 dias a partir da data (`date`) da transação bancária.
    *   Se encontrar apenas uma correspondência, vincule-a automaticamente como `'reconciled'` com o método `'auto'`.
2.  **Correspondência Aproximada/Fuzzy (Fase 2):**
    *   Se nenhuma correspondência exata for encontrada, expanda a janela de data para $\pm$7 dias.
    *   Use algoritmos de distância de strings (ex: Jaro-Winkler ou Levenshtein) para medir a similaridade de texto entre a descrição bruta do banco e a descrição do registro local.
    *   Se for obtido um score de similaridade alto ($>85\%$), sugira o vínculo ao usuário, ou realize a conciliação automática se o usuário tiver configurado regras de conciliação automática.

## 4. Tratamento Atômico de Transações
As atualizações de conciliação devem ser completamente atômicas. Envolva a lógica em uma transação do banco de dados Lucid:
```typescript
import db from '@adonisjs/lucid/services/db'

await db.transaction(async (trx) => {
  // 1. Marca a transação local como paga
  expense.useTransaction(trx)
  expense.isPaid = true
  await expense.save()

  // 2. Marca o item do extrato bancário como conciliado
  bankTx.useTransaction(trx)
  bankTx.status = 'reconciled'
  await bankTx.save()

  // 3. Cria o vínculo de conciliação
  const link = new BankReconciliation()
  link.useTransaction(trx)
  link.bankTransactionId = bankTx.id
  link.reconciledType = 'expense'
  link.reconciledId = expense.id
  link.method = 'auto'
  await link.save()
})
```

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
*   **Proibido Vínculos Múltiplos:** Uma única transação `BankStatementTransaction` não deve ser vinculada a várias transações locais, a menos que seja implementado um recurso específico de desmembramento de transações (split transaction) modelado explicitamente com relações de pai e filho.
*   **Proibido Deleção Física (Hard Delete):** Nunca remova linhas da tabela `BankStatementTransaction`. Se uma conciliação for desfeita, exclua o registro de `BankReconciliation` e altere o status da transação bancária de volta para `'pending'`.
*   **Desacoplamento de Importação e Matching:** Não execute o engine de correspondência (matching engine) dentro da mesma requisição HTTP que processa o arquivo OFX. Coloque a tarefa em fila usando BullMQ ou um processo em segundo plano para garantir respostas rápidas e resiliência com novas tentativas.
*   **Proibido Ponto Flutuante para Valores Monetários:** Garanta que os valores financeiros sejam tratados com precisão. Como números no Javascript são de ponto flutuante, represente a moeda em centavos (inteiros) no banco de dados e faça a conversão quando necessário, ou use colunas decimais precisas para evitar erros de arredondamento.
*   **Consumo no Front via MaxPinia:** Os endpoints de conciliação que servem dados de página ao front (ex.: listagem de transações pendentes, sugestões de match, status de importação) devem ser expostos como caminhos string `/api/...` e consumidos por uma store `@maxvue/max-pinia` no front, nunca por `axios.get`/`fetch` manual. Ações do usuário (confirmar/desfazer vínculo, editar regras de conciliação) devem fluir pelo auto-save da store (`apiPostRoute` resolvendo `/api/...`), não por submits manuais — sem `route()`/Ziggy.
