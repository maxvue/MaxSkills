# PROPOSTA DE SKILL: adonisjs-bullmq-multi-tenant-job-isolation-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, configuring, or debugging multi-tenant job execution, tenant queue isolation, concurrency throttling per tenant, or passing tenant context to BullMQ workers in AdonisJS v6. Triggers on setting up jobs with tenant IDs, managing tenant-specific BullMQ rate limits, and wrapping worker run methods with AsyncLocalStorage for database isolation.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp (especificamente o `SocialMediaApp`) é uma aplicação multi-tenant (onde os dados de diferentes empresas/organizadores devem ser isolados). As tarefas em background (como processamento de relatórios, envio de e-mails, interações com APIs de IA e publicação em redes sociais) rodam fora do ciclo de vida de requisição HTTP convencional (sem middleware de tenant ativo). É imperativo isolar os dados durante a execução das tarefas, garantindo que um job pertencente ao Tenant A não consulte ou corrompa os dados do Tenant B, além de permitir o controle de rate-limiting (throttling) de concorrência por tenant para que um tenant não monopolize o worker do Redis.
* **Recursos:** Isolamento de contexto com `AsyncLocalStorage` em workers do BullMQ, injeção e serialização do `tenant_id` no payload do Job no dispatch, middlewares/hooks de worker para carregar o contexto de tenant ativo antes de rodar o job, políticas de rate limiting por tenant nas filas usando BullMQ limiter dinâmico, logs estruturados com tags de tenant.
* **Objetivo:** Estabelecer padrões de projeto robustos e seguros para execução de tarefas assíncronas do BullMQ sob uma arquitetura multi-tenant no AdonisJS v6, impedindo vazamento de dados e equilibrando o uso de recursos de fila entre tenants.
* **Casos de uso:** Processar um job de envio de relatórios do Tenant A garantindo que a base de dados ativa esteja apontando/filtrada para o Tenant A; configurar rate-limiting dinâmico para garantir que um tenant que disparou 1000 jobs de geração de imagens de IA não cause starvation nos outros tenants; registrar logs estruturados que facilitem a depuração de falhas de jobs com identificadores de tenant.
* **Workflows:** [/bug-fix-back-end]
* **Skills próprias utilizadas:**
  - `adonisjs-bullmq-queue-management-best-practices` — Utilizará os padrões de configuração de conexão Redis, instanciação de queues e estrutura base de Workers/Jobs para definir onde e como o contexto de multi-tenancy e rate-limiting por tenant deve ser injetado.
  - `adonisjs-multitenancy-data-isolation-best-practices` — Utilizará os mecanismos de isolamento de dados por tenant (baseados em `TenantService` e `AsyncLocalStorage`) para garantir que os workers executem no escopo isolado correto de banco de dados para cada job.
* **Skills auxiliares:** adonisjs-specialist, adonisjs-best-practices
* **Skills beneficiadas:**
  - `adonisjs-bullmq-job-resilience-retries-best-practices`
  - `adonisjs-editorial-calendar-event-workflow-best-practices`
* **Benefícios:** Garantia absoluta de isolamento de dados de tenants no processamento assíncrono, maior estabilidade das filas com rate limiting dinâmico por tenant, prevenção de vazamento de dados (tenant leakage) e logs ricos para depuração de erros.
