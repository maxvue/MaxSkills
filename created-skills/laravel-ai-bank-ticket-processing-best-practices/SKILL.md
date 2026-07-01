---
name: laravel-ai-bank-ticket-processing-best-practices
description: >-
  Use when creating, modifying, reviewing, or debugging AI-driven bank ticket (boleto) processing workflows in Laravel, orchestrating AgentBankTicketProcessor or AgentAiBilletReader, validating billet data, executing payments via Efí (Gerencianet) SDK, verifying TRT/tax eligibility, or saving payment receipts to projects.
---

# Laravel AI Bank Ticket Processing Best Practices

## Goal

Establish solid guidelines and consistent patterns for the secure processing, validation, payment, and archiving of bank tickets (boletos) - specifically solar project approval fees and TRT (Anotação de Responsabilidade Técnica) fees - using AI agents within the Engeapp Laravel backend.

## Instructions

### 1. Billet Processing Architecture

Billet automation is structured around two specialized AI agents and three corresponding tools:

1.  **`AgentAiBilletReader`**: Responsible for extracting barcode, digit line, holder, value, and due date from PDF files or images (OCR). Implements `Agent, HasStructuredOutput`.
2.  **`AgentBankTicketProcessor`**: Orchestrates the payment workflow. Implements `Agent, HasTools`.
3.  **Tools**:
    *   `CheckBankTicket`: Validates the barcode with the Efí API and confirms if it is a valid TRT or concessionaire fee.
    *   `PayBankTicket`: Executes the payment using the Efí (Gerencianet) SDK.
    *   `SaveBankTicketToProject`: Archives the payment receipt and links the transaction to the corresponding solar project.

### 2. Validation Flow & Eligibility Rules (`CheckBankTicket`)

Before executing any financial transaction, the agent MUST run validation logic to verify eligibility:

1.  **Type Validation**: Only tickets classified as TRT (Anotação de Responsabilidade Técnica) or energy concessionaire approval fees are eligible for automated payment. General commercial tickets (e.g., vendor purchases, utilities not related to concessionaires) MUST be rejected.
2.  **Duplicate Detection**: Query the database to ensure the `line_code` (linha digitável) or `bar_code` (código de barras) has not already been processed or paid.
3.  **Value Boundaries**: Define strict maximum value limits for automated payments (e.g., R$ 5,000.00). Any ticket exceeding this threshold must flag a human intervention request.

### 3. Secure Payment Orchestration (`PayBankTicket`)

When utilizing the Efí (Gerencianet) SDK (`Efi\EfiPay`) to execute payments:

1.  **Strict Sequencing**: The payment tool `PayBankTicket` MUST NOT be invoked unless a prior call to `CheckBankTicket` has explicitly returned a status of `'success'` and confirmed `'is_trt' => true` (or eligible).
2.  **Concurrency / Race Conditions**: Database locks (e.g., `sharedLock` or `lockForUpdate`) must be placed on the ticket record during the payment transaction to prevent duplicate dispatches.
3.  **Idempotency**: Pass a unique payment idempotency key (derived from the `bar_code` or ticket ID) to the payment gateway to ensure that multiple API requests do not trigger multiple payments.
4.  **Error Handling**:
    *   Catch `EfiException` separately to parse API-level validation or balance errors.
    *   Always log payment failures with complete context (excluding sensitive details like raw credentials) to the `emergency` or `finance` channel.

### 4. Receipt Archiving & Project Linking (`SaveBankTicketToProject`)

Once a payment is successfully executed:

1.  **Spatie Media Library Integration**: The payment receipt PDF (fetched from the gateway's receipt URL) must be downloaded and attached to the corresponding `Project` model (`App\Models\Project\Project`) using Spatie's `MediaLibrary`.
2.  **Document Collection**: Save it to a specific collection (e.g., `'homologation_receipts'` or `'trt_receipts'`) with structured custom properties containing the `transaction_id`, `value`, and `payment_date`.
3.  **Project Status Sinking**: Update the project's homologation phase status based on the paid ticket (e.g., marking TRT as "Paid").

### 5. Fallback & Human Intervention

The AI workflow must gracefully hand over control to human operators in the following scenarios:
*   Value or due date mismatches between the extracted data and the API verification result.
*   API returns insufficient funds or authentication errors.
*   The ticket is not eligible for automatic payment (e.g., not a TRT or concessionaire fee).
*   Any system exception thrown during the execution.

In these cases, a database notification or Slack alert must be generated with details of the block and a direct link to the project for manual upload/review.

### 6. Testing Best Practices with Pest

To test billet processing safely without performing real financial transactions:

1.  **Mocking the SDK**: Always use `Http::fake()` or mock the `EfiPay` client response.
2.  **State Verification**: Write tests using Pest to assert:
    *   Only eligible tickets transition to a paid state.
    *   Duplicate payments throw a validation error.
    *   Failed payments trigger human notification events.

```php
it('rejects payments for non-eligible tickets', function () {
    $agent = new AgentBankTicketProcessor();
    // Simulate CheckBankTicket tool returning is_trt = false
    // Assert that PayBankTicket is never called.
});
```

## Constraints

1.  **NEVER** execute `PayBankTicket` without first invoking `CheckBankTicket` on the same ticket's barcode.
2.  **NEVER** hardcode Efí SDK credentials; always retrieve them from `config('services.efi')` or `.env`.
3.  **NEVER** process a payment without a verified `project_id` matching an active project in the database.
4.  **NEVER** log raw credit card details, API keys, or private certificates.
5.  **NEVER** bypass duplicate-checking queries prior to executing a payment.
