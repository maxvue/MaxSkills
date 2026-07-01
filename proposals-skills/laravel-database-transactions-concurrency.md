# PROPOSTA DE SKILL: laravel-database-transactions-concurrency

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing database transactions, handling database locks (sharedLock, lockForUpdate), managing deadlock retries, or configuring transaction-safe events and queue jobs. Triggers on DB::transaction, DB::beginTransaction, lockForUpdate, sharedLock, and transactional operations.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp lida com operações concorrentes pesadas, integrações assíncronas e agentes de IA que podem atualizar dados simultaneamente. A falta de padrões claros para transações e travas de concorrência pode levar a inconsistências de dados (race conditions) ou travamentos (deadlocks).
* **Recursos:** Padrões de transações automáticas e manuais, uso de locks pessimistas (lockForUpdate) e otimistas, tratamento e retry de deadlocks, e dispatch pós-commit (afterCommit) para eventos e jobs.
* **Objetivo:** Fornecer diretrizes sólidas para garantir a integridade dos dados durante transações complexas e gerenciar concorrência de forma robusta no banco de dados.
* **Casos de uso:** Processamento de saldo, agendamentos simultâneos de reuniões/tarefas, garantia de criação exclusiva de registros sob concorrência e execuções de background jobs integrados a chamadas externas.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as definições de models e escopos para aplicar as travas de concorrência (locks) corretas nos queries construídos.
  - `laravel-jobs-queues-horizon-best-practices` — Integrará o envio seguro de jobs somente após a conclusão (commit) de transações para evitar que o job tente ler dados ainda não persistidos.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** laravel-services-best-practices
* **Benefícios:** Prevenção de race conditions e corrupção de dados, tratamento resiliente de deadlocks no banco de dados e consistência nas operações assíncronas do ecossistema.
