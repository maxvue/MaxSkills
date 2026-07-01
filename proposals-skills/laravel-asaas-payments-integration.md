# PROPOSTA DE SKILL: laravel-asaas-payments-integration

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when configuring, debugging, or creating payment integrations with the Asaas API. Triggers on creating customers, generating invoices (Pix, Boleto, Credit Card), checking payment status, and handling webhooks from Asaas.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp necessita de uma integração nativa e robusta com a API do Asaas para gerenciar cobranças recorrentes (assinaturas), emissão de boletos, recebimento via Pix e pagamentos com cartão de crédito, seguindo a arquitetura BaseApi.
* **Recursos:** Padrões de conexão herdeiros de BaseApi (Connector, Attributes.json, EndPoints.json), estruturação de payloads usando DTOs (laravel-data), manipulação segura do webhook do Asaas, tratamento de erros de transação e logs de auditoria.
* **Objetivo:** Fornecer diretrizes e padrões de projeto claros para integrar o gateway Asaas de maneira consistente, segura e resiliente no backend Engeapp.
* **Casos de uso:** Geração de cobranças Pix imediatas, criação de carnês/assinaturas de clientes no Asaas, e recepção automática de pagamentos confirmados via webhook.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-base-api-integration-patterns` — Fornecerá o design pattern obrigatório para construir o conector (Connector, Attributes.json, EndPoints.json) herdando de `BaseApi`.
  - `laravel-code-generators-best-practices` — Utilizada para estruturar os dados enviados para a API do Asaas e recebidos por ela, incluindo payloads do webhook.
  - `laravel-code-generators-best-practices` — Fornecerá os padrões para mapear status das cobranças do Asaas (RECEIVED, CONFIRMED, OVERDUE, etc.).
  - `laravel-exception-handling-logging` — Utilizada para tratar de falhas de comunicação HTTP e registrar logs de depuração do fluxo de pagamento.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Rapidez e padronização no desenvolvimento de fluxos financeiros com o Asaas, mitigação de fraudes/erros de conciliação e garantia de tratamento correto de webhooks.
