# PROPOSTA DE SKILL: laravel-efi-payments-integration

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, updating, or debugging financial integrations with the Efi API (formerly Gerencianet), managing PIX/Bolix payments, handling Efi webhooks, or syncing payment statuses. Triggers on EfiPay SDK usage, payment controller modifications, and payment sync jobs.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp realiza transações financeiras e necessita de uma padronização rígida para chamadas da API Efí, segurança em webhooks (validação de payloads/certificados) e tratamento resiliente de erros HTTP de timeout e conexões instáveis.
* **Recursos:** Configurações do SDK EfiPay, tratamento de exceções com EfiException, tratamento resiliente de timeouts (como erros cURL 28), segurança em webhooks de pagamento, processamento assíncrono via Jobs e filas dos webhooks recebidos.
* **Objetivo:** Fornecer diretrizes consistentes e seguras para a integração de serviços de cobrança e pagamento utilizando a API da Efí no Engeapp.
* **Casos de uso:** Criação de cobranças PIX/Bolix, Webhook de notificação de pagamento, comando console de sincronização periódica de status de pagamentos pendentes.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-base-api-integration-patterns` — Fornecerá os padrões básicos de comunicação de API interna do Engeapp.
  - `laravel-exception-handling-logging` — Utilizada para estruturar o logging e tratamento de falhas e cURL timeouts da API de pagamentos.
  - `laravel-jobs-queues-horizon-best-practices` — Fornecerá as diretrizes de processamento assíncrono em background (ShouldQueue) para Webhooks e concorrência na atualização do status do pagamento.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Maior resiliência e estabilidade em transações financeiras, logs claros de erros de comunicação com a Efí, prevenção de falhas silenciosas na atualização de status de pagamentos.
