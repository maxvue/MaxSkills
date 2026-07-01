---
name: laravel-api-integration-patterns
description: Use when creating, debugging, extending external HTTP API integrations, or implementing HTTP idempotency mechanisms. Triggers on setting up new API connectors, Attributes.json or EndPoints.json, configuring OAuth2 caching, and designing safe API mutations (especially payments and integrations).
---

# Laravel API Integration Patterns

## Goal
Standardize the creation, modification, and debugging of external HTTP API integrations built on top of the Engeapp native `BaseApi` class, alongside establishing clean, reliable guidelines for implementing API request idempotency using Redis/Cache distributed locks and response caching.

## Instructions

### 1. Understand the Architecture
All external API integrations in Engeapp must inherit from `BaseApi`. Each integration must reside in its own folder (e.g., `app/Http/Integrations/MyService/`) containing:
- `Connector.php` (The PHP class extending `BaseApi`)
- `Attributes.json` (Attribute validation definition)
- `EndPoints.json` (Nested endpoint structure and execution config)

### 2. Creating the Attributes (Attributes.json)
- Define all query, path, and body properties that will be sent to the API.
- For each attribute, specify its `type`, a `description` explaining its purpose, and whether it is `required` (boolean).

### 3. Defining the Endpoints (EndPoints.json)
- Map your API endpoints in a hierarchical JSON object.
- Every executable endpoint must define: `end_point`, `method`, `description`, and `attributes` (an object grouping parameters into `query`, `path`, or `body`). Placeholders in `end_point` MUST be listed under `path`.

### 4. Implementing the Connector Class (Connector.php)
- Create a class extending `BaseApi` under the namespace `App\Http\Integrations\YourIntegrationName`.
- Define the `$base_url` property or a `$bases_url` array.
- Implement `getAccessToken()` to return the bearer token or OAuth2 structure.
- Utilize magic call chains like `$connector->group()->endpoint($payload)` to call endpoints specified in `EndPoints.json`.

### 5. Authentication, Caching, and Token Caching
- For OAuth2 flows, set the `$OAuth2` property array or implement custom token logic inside `getAccessToken()`. Token will be automatically cached using Laravel's Cache facade.
- `BaseApi` provides fluent methods to configure request caching: `$api->withCache(seconds)`, `$api->withoutCache()`, `$api->clearCache()`.

### 6. API Idempotency Implementation
Implement an `IdempotentRequestMiddleware` for safe API mutations:
1. **Retrieve the Idempotency Key:** Extract from `Idempotency-Key` or `X-Idempotency-Key` headers.
2. **Atomic Distributed Lock:** Acquire a cache lock using `idempotency:lock:{key}` with a short TTL. Return `409 Conflict` if unable to acquire.
3. **Cache Lookup:** Check if `idempotency:response:{key}` exists. If found, release lock and return cached response with `Original-Response: true` header.
4. **Request Execution:** Allow the request to proceed.
5. **Response Cache Serialization:** Cache the status code, content, and headers of successful (HTTP 2xx) responses for a durable period.
6. **Lock Release:** Release the distributed lock in a `finally` block.

### 7. Response Serialization Guidelines
Store a simplified payload in the cache instead of the entire `Response` object: `status`, `content`, and filtered `headers` (excluding cookies).

### 8. Testing Idempotency (Pest)
Feature tests must cover:
1. **Success Path:** Send a request with a key, assert successful processing, and send it again to verify the cached response is returned.
2. **Concurrent Request Conflict:** Mock the lock to simulate a concurrent request and assert a `409 Conflict`.
3. **Expired Cache:** Verify that requests are processed fresh when the TTL expires.

## Constraints
- **Do NOT** define API request methods manually using `Http::get` or `Http::post` within the connector class unless implementing high-level aggregation.
- **Do NOT** skip defining `path` attributes in `EndPoints.json` if the URL contains curly braces.
- **Do NOT** write inline SQL or instantiate models in connectors.
- **Never** cache error responses (HTTP 4xx or 5xx).
- **Never** cache the raw PHP Response object directly to avoid serialization issues.
- **Do not** store idempotency keys in cache forever. Always set a TTL (recommended 24 hours).
- **Do not** bypass locking; lock acquisition must precede cache lookup to prevent race conditions.
