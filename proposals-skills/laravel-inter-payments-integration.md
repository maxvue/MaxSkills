# PROPOSTA DE SKILL: laravel-inter-payments-integration

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
* **Wake Word (YAML Description):** Use when implementing, modifying, or debugging payment and billing integrations with Banco Inter API (using inter-co/pj-sdk-php) in Laravel. It applies to generating hybrid invoices (Boleto + Pix, also known as Bolix), querying payment status, managing API credentials, handling OAuth2 authentication, and processing webhooks.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp precisa faturar e cobrar clientes utilizando cobranças híbridas (Boleto + Pix/Bolix) do Banco Inter. Atualmente, a classe `InterPaymentExecute` no diretório `app/Services/Bank/` é apenas um placeholder. É necessária uma padronização para a integração segura, gerenciamento do ciclo de vida dos tokens OAuth2 do Banco Inter, tratamento de certificados digitais SSL (exigidos pelo Inter) e resiliência em falhas de comunicação com a API.
* **Recursos:**
  - Gerenciamento seguro de credenciais e certificados SSL do Banco Inter via Storage/config.
  - Autenticação e cache do token de acesso OAuth2.
  - Geração de cobranças híbridas (Bolix - Boleto com código de barras e QR Code Pix).
  - Consulta ativa de status de pagamento de boletos/Bolix.
  - Processamento seguro e idempotente de webhooks do Banco Inter para notificações de pagamento.
  - Tratamento resiliente de erros HTTP específicos da API do Banco Inter.
* **Objetivo:** Fornecer diretrizes consistentes e seguras para a integração de serviços de cobrança e pagamento utilizando a API do Banco Inter no Engeapp.
* **Casos de uso:** Geração automática de boletos/Bolix após fechamento de contratos de projetos fotovoltaicos, atualização automática de faturas para status "pago" via webhook ou consulta ativa programada, conciliação bancária de pagamentos recebidos via Banco Inter.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-base-api-integration-patterns` — Utilizará as convenções de chamada de APIs externas estruturadas baseadas na classe `BaseApi` para padronizar a comunicação com os endpoints do Banco Inter.
  - `laravel-jobs-queues-horizon-best-practices` — Utilizada para orquestrar as consultas de status e reprocessamento de webhooks do Banco Inter por meio de jobs assíncronos.
  - `laravel-exception-handling-logging` — Utilizada para padronizar o tratamento de falhas na comunicação com a API do Inter e registrar logs de transações bancárias.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Automação segura do faturamento e conciliação bancária, conformidade com os requisitos de segurança e TLS do Banco Inter, e prevenção de inconsistências nos status de pagamento dos clientes.
