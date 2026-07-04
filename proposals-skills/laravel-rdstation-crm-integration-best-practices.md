# PROPOSTA DE SKILL: laravel-rdstation-crm-integration-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, reviewing, or debugging integrations with the RD Station CRM API, handling OAuth2 authentication flow (access/refresh tokens), sending solar project lead data, or managing webhook responses (won deals) within the Engeapp Laravel backend. Triggers on CRM sync jobs, OAuth token storage, and webhook controllers.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp realiza a gestão de vendas e projetos de engenharia solar, necessitando de uma integração robusta e confiável com o RD Station CRM para sincronizar leads e oportunidades sem perdas ou duplicidades e automatizar a abertura de homologações de projetos assim que uma venda for ganha no CRM.
* **Recursos:**
  - Fluxo de autenticação OAuth2 dinâmica, incluindo a renovação e persistência seguras de access e refresh tokens no banco de dados.
  - Sincronização automatizada de Leads e Oportunidades com base nas atualizações de orçamentos e dimensionamentos no Engeapp.
  - Processamento assíncrono via Horizon/Queues com retries exponenciais e tratamento de rate limiting da API do RD Station.
  - Endpoint de Webhook dedicado para receber atualizações do RD Station CRM (oportunidades marcadas como ganhas) e iniciar o projeto/homologação de forma transacional e idempotente.
  - Estruturação de mocks HTTP com Pest PHP para testar de forma confiável todos os fluxos de comunicação com a API do RD Station.
* **Objetivo:** Fornecer diretrizes e padrões de arquitetura para a integração dinâmica, resiliente e segura da API e webhooks do RD Station CRM no backend Laravel do Engeapp.
* **Casos de uso:** Sincronizar dados de dimensionamento fotovoltaico de um lead do Engeapp para o RD Station CRM, atualizar valores de propostas comerciais no CRM, e processar webhooks de vendas ganhas para criar automaticamente projetos e fluxos de homologação.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - [laravel-base-api-integration-patterns](file:///home/johnattas/GitHub/Skills/created-skills/backend_laravel/laravel-base-api-integration-patterns) — Utilizará os padrões estruturais de APIs integradas da classe `BaseApi` para chamadas HTTP externas.
  - [laravel-jobs-queues-horizon-best-practices](file:///home/johnattas/GitHub/Skills/created-skills/backend_laravel/laravel-jobs-queues-horizon-best-practices) — Utilizará as boas práticas de Jobs e Horizon para o processamento assíncrono e retentativas das chamadas à API de sincronização.
  - [laravel-exception-handling-logging](file:///home/johnattas/GitHub/Skills/created-skills/backend_laravel/laravel-exception-handling-logging) — Utilizará os padrões de tratamento de erros para monitorar falhas de comunicação ou autenticação OAuth.
  - [laravel-pest-testing-best-practices](file:///home/johnattas/GitHub/Skills/created-skills/backend_laravel/laravel-pest-testing-best-practices) — Utilizará os padrões de escrita de testes para mockar a API do RD Station CRM com Pest PHP.
* **Skills auxiliares:** laravel-specialist
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Automação total do fluxo comercial-técnico (leads e contratos), eliminação de inserção manual de dados de potência solar e concessionária no CRM, visibilidade em tempo real do pipeline e robustez no processamento de transações e webhooks.
