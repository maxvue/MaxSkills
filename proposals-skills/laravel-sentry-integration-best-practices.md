# PROPOSTA DE SKILL: laravel-sentry-integration-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when integrating, configuring, or debugging Sentry in a Laravel application. Triggers on Sentry SDK installation, configuring Sentry config files, adding custom breadcrumbs, capturing exceptions with Sentry::captureException, and setting up performance APM/tracing.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp opera com múltiplos microsserviços, agentes de IA e jobs em segundo plano. Sem uma integração centralizada e refinada do Sentry, exceções em produção e problemas de latência (APM) são difíceis de correlacionar, impedindo a rápida resolução de incidentes.
* **Recursos:**
  - Instalação e configuração do pacote oficial `sentry/sentry-laravel`.
  - Configuração do handler de logs no arquivo `config/sentry.php` e `.env` (ex: controle de `traces_sample_rate` e `profiles_sample_rate`).
  - Enriquecimento de exceções com contexto do usuário autenticado (User Context), tags personalizadas e metadados.
  - Implementação de breadcrumbs para rastrear o fluxo antes de uma falha (como consultas SQL anteriores, requisições HTTP).
  - Captura manual de exceções e envio de mensagens customizadas via Facade `Sentry`.
  - Configuração e boas práticas para evitar o envio de dados sensíveis (PII, como senhas e cartões de crédito) para o Sentry.
* **Objetivo:** Fornecer diretrizes sólidas e padrões consistentes para o monitoramento de erros em tempo real e análise de performance (APM) utilizando o Sentry no backend Laravel do Engeapp.
* **Casos de uso:**
  - Captura automática de exceções não tratadas em requisições web, APIs e comandos Artisan.
  - Rastreamento detalhado de falhas em Jobs e filas do Horizon com contexto do payload do Job.
  - Otimização de queries SQL lentas através de transações e spans de APM do Sentry.
  - Filtro e higienização de payloads de requisições contendo dados sensíveis de clientes antes de serem enviados ao Sentry.
* **Workflows:**
  - `bug-fix-back-end` — Auxiliará na identificação de bugs a partir dos rastros detalhados gerados no Sentry.
  - `deploy` — Ajudará a monitorar a estabilidade da aplicação em tempo real imediatamente após um novo release.
* **Skills próprias utilizadas:**
  - `laravel-exception-handling-logging` — Utilizará os padrões de tratamento de exceção globais para acoplar a captura do Sentry de forma limpa.
  - `laravel-jobs-queues-horizon-best-practices` — Integrará o Sentry no monitoramento de Jobs com tratamento de retry/falhas.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-base-api-integration-patterns` — Se beneficiará do rastreamento de requisições externas como transações (Spans) de HTTP client no Sentry.
* **Benefícios:** Detecção proativa de bugs antes que afetem múltiplos usuários, diagnóstico rápido de gargalos de performance no banco de dados e APIs, e enriquecimento de relatórios de falhas com contexto exato de execução.
