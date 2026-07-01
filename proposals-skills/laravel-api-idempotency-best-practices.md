# PROPOSTA DE SKILL: laravel-api-idempotency-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, refactoring, or debugging HTTP idempotency mechanisms, handling duplicate requests, designing safe API mutations (especially payments and integrations), or configuring idempotency keys in request headers and middleware.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp realiza transações de pagamento críticas via APIs externas (Asaas, Efí, Banco Inter), além de disparar mensagerias e processamentos via IA. Garantir que requisições idênticas não gerem duplicidade de cobranças ou processamento redundante em caso de retentativas automáticas por falhas de conexão é crítico para a confiabilidade do sistema.
* **Recursos:**
  - Diretrizes para recebimento e validação do cabeçalho `Idempotency-Key` (ou `X-Idempotency-Key`).
  - Middleware de Idempotência (`IdempotentRequestMiddleware`) que utiliza cache (Redis/Database) para armazenar assinaturas de requisições.
  - Implementação de locks atômicos distribuídos (Cache Lock) para gerenciar requisições concorrentes idênticas.
  - Respostas padronizadas para requisições em andamento (HTTP 409 Conflict) e para requisições concluídas (retorno do payload original com cabeçalho `Original-Response`).
  - Boas práticas para estruturação de testes automatizados (Pest) cobrindo fluxos felizes, concorrência extrema e expiração de cache.
* **Objetivo:** Estabelecer diretrizes consistentes de desenvolvimento para garantir idempotência em rotas de mutação de estado (POST/PUT/PATCH), impedindo duplicações de dados e cobranças indevidas.
* **Casos de uso:** Criação de faturas de pagamento no Asaas/Efí/Banco Inter, agendamento de homologações de projetos solares, disparos de webhooks e execuções de prompts caros em agentes de IA.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - [laravel-code-generators-best-practices](file:///home/johnattas/GitHub/Skills/created-skills-pt-br/laravel-code-generators-best-practices) — Utilizará as diretrizes de criação de middlewares personalizados para estruturar o middleware de idempotência.
  - [laravel-exception-handling-logging](file:///home/johnattas/GitHub/Skills/created-skills-pt-br/laravel-exception-handling-logging) — Utilizará os padrões de tratamento centralizado de exceções para tratar erros de concorrência ou conflitos.
  - [laravel-pest-testing-best-practices](file:///home/johnattas/GitHub/Skills/created-skills-pt-br/laravel-pest-testing-best-practices) — Utilizará as convenções de testes do Pest para escrever testes robustos de concorrência.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - [laravel-asaas-payments-integration](file:///home/johnattas/GitHub/Skills/proposals-skills/laravel-asaas-payments-integration.md) — Assegurará que a criação de cobranças na API do Asaas seja idempotente.
  - [laravel-efi-payments-integration](file:///home/johnattas/GitHub/Skills/proposals-skills/laravel-efi-payments-integration.md) — Garantirá que o envio de faturas na API da Efí seja idempotente.
  - [laravel-inter-payments-integration](file:///home/johnattas/GitHub/Skills/proposals-skills/laravel-inter-payments-integration.md) — Assegurará a idempotência nas transações integradas com o Banco Inter.
* **Benefícios:** Eliminação completa de faturamento duplicado para clientes, redução drástica de processamento redundante e custos com IA, e prevenção de inconsistências no banco de dados causadas por retentativas de clientes HTTP externos ou cliques duplos na interface.
