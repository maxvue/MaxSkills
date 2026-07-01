# PROPOSTA DE SKILL: laravel-context-metadata-tracking-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, refactoring, or debugging Laravel Context (Illuminate\Support\Facades\Context) to track request metadata, share state between HTTP requests and queued Jobs, configure context logging, or sanitize context keys in a stateless environment. Triggers on Context::add(), Context::get(), Context::pull(), log context configuration, and sharing request metadata.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp executa múltiplos fluxos assíncronos (Jobs, webhooks, processamento de IA) iniciados a partir de requisições do usuário. Sem um mecanismo centralizado de metadados como a Facade Context, correlacionar logs de uma mesma requisição que passa por filas em background é extremamente difícil, prejudicando a depuração.
* **Recursos:** Rastreamento unificado de metadados, injeção automática de dados do usuário autenticado no contexto do log, propagação automática do contexto para Jobs da fila (Horizon), e limpeza adequada em ambientes Octane.
* **Objetivo:** Estabelecer diretrizes e padrões para o uso estruturado da Facade Context no Laravel, garantindo rastreabilidade fim a fim.
* **Casos de uso:** Rastreamento de requisições de IA associando o ID do usuário aos Logs de background, depuração de erros em webhooks vinculando a requisição HTTP original ao Job na fila, auditoria simplificada com logs estruturados enriquecidos.
* **Workflows:** [bug-fix-back-end, deploy]
* **Skills próprias utilizadas:**
  - `laravel-exception-handling-logging` — Utilizará as definições de canais de logs e logs estruturados para injetar o contexto global automaticamente em logs de erro.
  - `laravel-jobs-queues-horizon-best-practices` — Alinhará a propagação do contexto de requisição com a execução de Jobs em fila supervisionados pelo Horizon.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Rastreabilidade completa de transações, menor esforço de depuração em produção, integração perfeita de metadados entre requisições HTTP e processamento em fila.
