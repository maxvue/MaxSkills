---
name: laravel-brazilian-payments-integration
description: Use when configuring, debugging, or creating payment integrations with Brazilian gateways (Asaas, Efí, Banco Inter, Mercado Pago). Triggers on creating customers, generating invoices (Pix, Boleto, Credit Card, Bolix), checking payment status, and handling webhooks from these providers.
---

# Laravel Brazilian Payments Integration

## Goal
Standardize and secure the integration of Brazilian payment gateways (Asaas, Efí/Gerencianet, Banco Inter, Mercado Pago) within the Engeapp backend ecosystem. This skill ensures strict adherence to the `BaseApi` connector patterns, typed data pipelines using Spatie Laravel Data (DTOs), robust Enum-backed statuses, secure webhook signature/token validation, and dedicated logging practices.

## Instructions

### 1. BaseApi Integration Architecture & SDK Initialization
All interactions with APIs must be routed through a dedicated integration namespace extending `BaseApi` (e.g., `app/Http/Integrations/{Gateway}/`), except when specific SDKs are mandated (like Efí).
- **Files**:
  - `Connector.php`: The PHP integration connector.
  - `Attributes.json`: Definition of validation rules for payloads.
  - `EndPoints.json`: Declaration of endpoint hierarchies.
- **Asaas**: Sandbox `https://sandbox.asaas.com/api/v3`, Production `https://api.asaas.com/api/v3`. Use header `access_token`. For Asaas specific integration details, see [references/asaas.md](references/asaas.md).
- **Efí**: Instantiate the Efi SDK (`EfiPay`) using config parameters via `config('bank.efi_options')`. Certificate path dynamically resolved via `resolveLocalDiskPath()`.
- **Banco Inter**: Sandbox `https://cdg.sandbox.bancointer.com.br`, Production `https://api.bancointer.com.br`. Load mTLS certificates (`.crt` and `.key`) from `storage/app/certificates/`. Retrieve OAuth2 token via `/oauth/v2/token` and cache securely.
- **Mercado Pago**: Implement `MercadoPagoService` for business logic, isolating the connector. Resolve credentials via `config('services.mercadopago.access_token')`.

### 2. Payload and Data Mapping using DTOs
Ensure all payloads sent to or received from payment gateways are mapped via Spatie Laravel Data transfer objects.
- Store DTOs in specific namespaces, e.g., `app/Data/Asaas/`, `app/Data/Inter/`.
- Use Constructor Property Promotion for all properties and ensure strict type hints.

### 3. Enum Mapping
Map payment methods and transaction statuses using Backed Enums decorated with `#[TypeScript]` for frontend type synchronization.
- e.g., `AsaasBillingType` (`BOLETO`, `CREDIT_CARD`, `PIX`, `UNDEFINED`), `AsaasPaymentStatus`.

### 4. Webhook Security and Asynchronous Processing
Webhooks must be received via dedicated routes pointing to specific controllers.
- **Asaas**: `POST /api/webhooks/asaas`. Validate `asaas-access-token` header matches `config('services.asaas.webhook_token')`.
- **Efí**: `POST /api/bank/efi/webhook/{secure_code}`. Verify token against `webhook_code_bolix` or `webhook_code_link` in `Payments` model.
- **Banco Inter**: `POST /api/bank/inter/webhook/{secure_token}`. Validate token matches `config('bank.inter_webhook_token')`.
- **Mercado Pago**: Validate `x-signature` header or security query params using Mercado Pago Webhook Signing Secret.

**Processing Rule for All Gateways:**
- **Do not process webhook payloads synchronously.**
- Store the raw payload inside the `bank_webhooks` table with status `pending`, then dispatch a background job (e.g., `ProcessInterWebhookJob`, `ProcessEfiWebhookJob`, `ProcessMercadoPagoWebhookJob`).
- Return a prompt HTTP response (e.g., `200 OK`) immediately to prevent timeouts and duplicate notifications.
- Implement idempotency by checking database status before processing.

### 5. Exception Handling & Dedicated Logging
- Wrap all external calls in try-catch blocks. Catch specific exceptions (e.g., `EfiException`) and generic network exceptions.
- Throw custom exceptions for handling transactional or API validation failures.
- Log activity using dedicated log channels defined in `config/logging.php` (e.g., `asaas`, `efi`, `inter`, `mercadopago`).
- Avoid silent failures. Ensure failover/fallback sync commands exist (e.g., `SyncEfiPaymentsStatusCommand` CLI).

---

## Constraints
- **Do NOT** perform raw HTTP requests to APIs outside the `BaseApi` integration structure or approved SDKs.
- **Do NOT** process webhook events synchronously. Always queue them to prevent timeouts.
- **Do NOT** bypass signature or token verification on webhooks.
- **Do NOT** hardcode credentials, client IDs, secrets, or certificate paths.
- **Do NOT** log sensitive credit card parameters (CVV, full card numbers) or raw authentication keys.
- **Do NOT** allow duplicate processing of the same payment event. Implement transactional locks or unique keys.
- **Do NOT** use English inline comments or PHPDoc blocks in PHP code. All PHP comments and documentation must strictly be in Brazilian Portuguese (pt-BR).
