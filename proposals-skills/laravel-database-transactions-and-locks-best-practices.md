# PROPOSTA DE SKILL: laravel-database-transactions-and-locks-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, reviewing, or debugging database transactions, Eloquent transactional operations, database locks (shared locks, pessimistic locks, lockForUpdate, sharedLock), or handling concurrency and race conditions in Laravel. Triggers on DB::transaction, DB::beginTransaction, DB::commit, DB::rollBack, sharedLock(), lockForUpdate(), retry() helper, and transaction-related exception handling.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp executa rotinas concorrentes cruciais, como processamento de webhook de mensagens do WhatsApp (`WebhookWhatsappJob`), manipulação de chat e ativação de protocolos de suporte de forma paralela (`SupportContact::getActiveSupport`), além de exclusões massivas de projetos e cartões (`ProjectDeletionService`). Nesses cenários, a ausência de controle transacional adequado ou locks pessimistas pode causar race conditions (condições de corrida), dados inconsistentes, concorrência indevida e falhas silenciosas de banco de dados.
* **Recursos:** Padrões para transações implícitas (`DB::transaction`) e explícitas/manuais (`DB::beginTransaction`, `DB::commit`, `DB::rollBack`), aplicação de pessimistic locking (`lockForUpdate` para escrita e `sharedLock` para leitura), mitigação de deadlocks com o helper `retry()`, tratamento de exceções transacionais e sincronização de eventos de fila (`afterCommit`) para evitar inconsistência de leitura concorrente em listeners.
* **Objetivo:** Fornecer diretrizes e padrões de projeto robustos para implementar transações seguras de banco de dados, gerenciar concorrência através de locks e implementar mecanismos resilientes de tratamento de falhas em aplicações Laravel.
* **Casos de uso:**
  - Recuperação, unificação e criação concorrente de protocolo de suporte ativo evitando duplicados (`SupportContact::getActiveSupport`).
  - Processamento em lote ou individual de webhooks recebidos paralelamente (`WebhookWhatsappJob`).
  - Lógicas de deleção em cascata transacionadas para evitar órfãos (`ProjectDeletionService`).
* **Workflows:** [/bug-fix-back-end]
* **Skills próprias utilizadas:**
  - `laravel-events-listeners-best-practices` — Utilizará as boas práticas de dispatch de eventos para integrá-los corretamente com o ciclo de vida transacional (garantindo que os listeners não executem antes do commit da transação via `afterCommit` ou dispatch tardio).
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-events-listeners-best-practices` — Será beneficiada ao documentar a prevenção de erros comuns de corrida de fila com transações não commitadas.
* **Benefícios:** Garantia de integridade referencial e transacional dos dados, mitigação de race conditions em rotinas altamente concorrentes (como chats e webhooks), eliminação de deadlocks persistentes por falta de tentativas automáticas, e consistência entre o banco de dados e as filas de processamento assíncrono.
