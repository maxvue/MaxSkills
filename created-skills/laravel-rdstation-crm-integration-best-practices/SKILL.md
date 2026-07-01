---
name: laravel-rdstation-crm-integration-best-practices
description: Use when creating, reviewing, or debugging integrations with the RD Station CRM API, handling OAuth2 authentication flow (access/refresh tokens), sending solar project lead data, or managing webhook responses (won deals) within the Engeapp Laravel backend. Triggers on CRM sync jobs, OAuth token storage, and webhook controllers.
---

# Laravel RD Station CRM Integration Best Practices

## Goal
Establish solid guidelines, patterns, and architectural standards for creating, maintaining, and debugging a resilient, secure, and performant integration between the Engeapp Laravel backend and the RD Station CRM API (including webhooks).

## Instructions

### 1. Integration Class Design (`BaseApi` Extension)
- Extend the `App\Http\Integrations\BaseApi` class for calling external APIs.
- Create a dedicated namespace: `App\Http\Integrations\RdStation`.
- Structure the integration folder with:
  - `RdStationCrmApi.php` (The main integration class extending `BaseApi`).
  - `Attributes.json` (Required fields mapping).
  - `EndPoints.json` (Endpoints mapping, HTTP methods, and rules).
- Dynamically resolve the active base URL inside `defineComputedBaseUrl()` for sandbox/production environments.

### 2. Resilient OAuth2 Authentication Flow
- Maintain a database table (e.g., `rd_station_oauth_tokens`) to store OAuth2 tokens dynamically: `access_token`, `refresh_token`, and `expires_at`.
- Override the `getAccessToken()` method in your `RdStationCrmApi` class to:
  1. Retrieve active token data from the database.
  2. If the token is expired or close to expiration (e.g., within 5 minutes), fetch a new token using the `refresh_token` flow.
  3. Update and persist the new token credentials back to the database securely.
  4. Cache the active `access_token` using Laravel's cache layer with a proper TTL.

### 3. Asynchronous Sync via Horizon & Queues
- Never execute CRM API calls synchronously during HTTP requests. Always dispatch jobs to the queue.
- Implement the `ShouldQueue` interface on all sync jobs (e.g., `SyncLeadToRdStationJob`).
- Handle Rate Limiting (HTTP 429) gracefully:
  - Catch `RequestException` or HTTP response failures.
  - Implement exponential backoff retry logic:
    ```php
    public int $tries = 5;

    public function backoff(): array
    {
        return [10, 30, 90, 270, 810];
    }
    ```
- Run synchronization operations inside safe database transactions when updating lead/project status locally.

### 4. Idempotent Webhook Processing
- Route incoming webhook requests (e.g., opportunity won) to a dedicated `RdStationWebhookController`.
- Validate the incoming payload using a custom Form Request (`RdStationWebhookRequest`).
- Ensure transactional safety and idempotency using database transactions and unique constraints:
  - Check if the project/deal has already been processed or created locally (using the RD Station CRM opportunity ID) before creating new database records.
  - Wrap lead conversion, client creation, and project/homologation initiation within:
    ```php
    DB::transaction(function () use ($data) {
        // ... Check if exists ...
        // ... Create Client ...
        // ... Create Project & Homologation ...
    });
    ```

### 5. Mocking and Testing (Pest PHP)
- Write unit and feature tests using Pest PHP.
- Do not make real API requests during testing. Mock the RD Station CRM API responses using `Http::fake()`:
  ```php
  Http::fake([
      'api.rd.services/*' => Http::response(['status' => 'success'], 200),
  ]);
  ```
- Use factories to set up model states (e.g., `Lead` or `Project`) before testing synchronization jobs.

## Constraints
- **NO Static Hardcoding:** Never hardcode credentials, URLs, or client keys. Always retrieve them from `config()` files, which reference `.env` variables.
- **NO Synchronous API Calls:** Do not make API calls directly from controllers or models; delegate all integration network calls to queue workers.
- **NO Blind Retries:** Never retry requests infinitely without exponential backoff, otherwise rate limit headers will be exhausted and IP blocking may occur.
