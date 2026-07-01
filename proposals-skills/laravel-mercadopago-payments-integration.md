# PROPOSTA DE SKILL: laravel-mercadopago-payments-integration

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when integrating, configuring, testing, or debugging Mercado Pago gateway payments, handling Mercado Pago webhooks, processing refunds, or managing subscriptions and transactions in Laravel.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp processa transações de assinatura e compras pontuais de serviços ou homologações de projetos. Centralizar os padrões de integração com a API do Mercado Pago evita erros de concorrência e inconsistências no processamento de status de transações.
* **Recursos:** Integração segura via SDK oficial do Mercado Pago ou HTTP client nativo do Laravel, tratamento resiliente de webhooks (IPNs) com assinaturas de segurança, logs estruturados de requisições e estratégias de idempotência para evitar transações duplicadas.
* **Objetivo:** Fornecer diretrizes sólidas e padrões consistentes para implementar e manter o fluxo de integração de pagamentos e webhooks do Mercado Pago no backend Laravel do Engeapp.
* **Casos de uso:** Recebimento de pagamentos via Pix (Mercado Pago), processamento de assinaturas via cartão de crédito e tratamento assíncrono de notificações de pagamento.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-base-api-integration-patterns` — Utilizará os padrões estruturais de integração de APIs externas para estruturar os clients, payloads e tratamento de erros com a API do Mercado Pago.
  - `laravel-pest-testing-best-practices` — Orientará a escrita de testes de feature e unitários para as integrações de pagamento e simulação de webhooks com mocks do HTTP Client.
  - `laravel-jobs-queues-horizon-best-practices` — Utilizará as boas práticas de filas para o processamento em background de webhooks de pagamento.
  - `laravel-services-best-practices` — Centralizará as chamadas da API do Mercado Pago em classes de serviços específicas isolando as regras de negócio.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Garantia de conciliação de pagamentos em tempo real, prevenção contra processamentos duplicados, desacoplamento do código e aumento da testabilidade do fluxo financeiro.
