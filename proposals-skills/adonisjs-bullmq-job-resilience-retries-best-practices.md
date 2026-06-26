# PROPOSTA DE SKILL: adonisjs-bullmq-job-resilience-retries-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when designing, configuring, implementing, or debugging background jobs resilience, retry strategies, exponential backoff, and failure handling with BullMQ in AdonisJS v6. Triggers on setting up attempts config, error categorization, listening to worker failure events, and configuring retry behaviors.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp (especificamente o `SocialMediaApp`) processa diversas tarefas críticas em background através do BullMQ, como geração de arte, copywriting por IA, postagens automatizadas e processamento de webhooks. Falhas temporárias (como indisponibilidade de APIs de IA ou redes sociais, rate limiting ou timeouts) exigem estratégias robustas de retentativa, tratamento e rastreamento de erros para evitar tarefas travadas ou perdidas silenciosamente.
* **Recursos:** Configuração de retentativas (`attempts`) e atrasos exponenciais (`backoff` com `delay` e tipo `exponential`), classificação e categorização de erros (erros temporários/infraestrutura vs. erros definitivos/negócio), monitoramento e tratamento de falhas em workers (escutar eventos `failed` e logar detalhes do erro/contexto), mitigação de overhead do Redis (uso correto de `removeOnFail` / `removeOnComplete`), tratamento e alertas de jobs que falharam permanentemente.
* **Objetivo:** Fornecer diretrizes e padrões de projeto robustos para implementar resiliência e tratamento de erros avançado em filas do BullMQ no AdonisJS v6, reduzindo falhas em background sem tratamento e melhorando a observabilidade.
* **Casos de uso:** Retentar chamadas falhas às APIs da Gemini, ElevenLabs ou HeyGen devido a timeouts/rate limit; registrar e alertar sobre falhas definitivas na publicação automática de eventos em redes sociais; classificar e processar retentativas no processamento de webhooks de mídias sociais.
* **Workflows:** [/bug-fix-back-end]
* **Skills próprias utilizadas:**
  - `adonisjs-bullmq-queue-management-best-practices` — Estenderá a estrutura base de filas e instanciação de queues para incorporar de forma granulada as opções de resiliência e retentativa em cada Dispatch de Job.
  - `adonisjs-exception-handling-logging-best-practices` — Utilizará as melhores práticas de logs estruturados e monitoramento para registrar exceções lançadas nos Workers durante a execução dos Jobs.
* **Skills auxiliares:** adonisjs-specialist, adonisjs-best-practices
* **Skills beneficiadas:**
  - `adonisjs-bullmq-job-idempotency-deduplication-best-practices`
  - `adonisjs-bullmq-queue-management-best-practices`
  - `adonisjs-editorial-calendar-event-workflow-best-practices`
  - `adonisjs-meta-api-outbound-rate-limiting-best-practices`
* **Benefícios:** Maior confiabilidade no processamento de tarefas assíncronas críticas de IA e integração social, eliminação de falhas silenciosas, observabilidade aprimorada em caso de erros e otimização de recursos Redis.
