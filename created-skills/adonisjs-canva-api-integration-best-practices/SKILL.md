---
name: adonisjs-canva-api-integration-best-practices
description: Use when implementing, configuring, reviewing, or debugging integrations with the Canva API in an AdonisJS application, managing Canva OAuth 2.0 flows, uploading media assets to Canva, exporting or publishing designs created on Canva directly to the social media calendar, or handling Canva webhook notifications for design updates.
---

## Goal
Establish robust, secure, and resilient development standards for integrating the Canva API into AdonisJS v6 applications. This covers multi-tenant OAuth 2.0 credential management, media assets synchronization, secure webhook endpoints, and rate-limiting handling.

## Instructions

### 1. Canva OAuth 2.0 Flow Integration (AdonisJS Ally)
When implementing OAuth 2.0 with Canva, extend AdonisJS Ally by creating a custom Canva driver or implementing a custom flow if not built-in.
- **Config & Env:** Define variables (`CANVA_CLIENT_ID`, `CANVA_CLIENT_SECRET`, `CANVA_CALLBACK_URL`) in `start/env.ts` using `Env.schema.string()`.
- **Token Storage:** Save credentials within `SocialMediaCredential` model. Include fields `access_token`, `refresh_token`, and `token_expires_at` (using Luxon `DateTime`).
- **Token Refreshing:** Implement a token refresh helper within the service. Before any API request, check if the token expires in less than 5 minutes, and trigger refresh if needed:
  ```typescript
  if (credential.tokenExpiresAt && credential.tokenExpiresAt.diffNow('minutes').minutes < 5) {
    await this.refreshCanvaToken(credential)
  }
  ```

### 2. Canva Media Upload API
To export backend-generated assets to Canva:
- **HTTP client:** AdonisJS v6 não possui cliente HTTP de primeira-parte. Use a API `fetch` nativa do Node 18+ (global, sem dependência extra). Se preferir uma biblioteca, instale `got` ou `axios`. Sempre cheque `response.ok` e trate erros antes de consumir o corpo (`await response.json()`).
- **Chunks & Size:** For large files, stream them directly to avoid memory exhaustion.
- **Endpoint:** `POST https://api.canva.com/v1/asset-uploads`
- **Request Format:** Use `multipart/form-data` with fields `file`, `mime_type`, and `asset_name`.
- **Async Handling:** The Canva Upload API is asynchronous. Check the upload status by polling the endpoint provided in the response metadata (`GET https://api.canva.com/v1/asset-uploads/{uploadId}`) until status is `completed` or `failed`.

### 3. List and Import Canva Designs
For pulling finalized designs back into the editorial calendar:
- **List designs:** `GET https://api.canva.com/v1/designs` filtering by client/user scopes.
- **Exporting design:** Call `POST https://api.canva.com/v1/exports` to generate high-resolution PNG or PDF outputs.
- **Download to Drive:** Stream the output from the generated Canva export URL and save it using the AdonisJS `drive` service. Com `fetch` nativo, converta o corpo da resposta (web `ReadableStream`) para um stream Node antes de gravar:
  ```typescript
  import drive from '@adonisjs/drive/services/main'
  import { Readable } from 'node:stream'

  const response = await fetch(exportUrl)
  if (!response.ok || !response.body) {
    throw new Error(`Failed to download Canva export: ${response.status}`)
  }
  const nodeStream = Readable.fromWeb(response.body)
  await drive.use().putStream(destinationPath, nodeStream)
  ```

### 4. Canva Webhooks Processing
- **Verification:** Canva webhooks require validation using HMAC-SHA256 signature verification. Verify the `X-Canva-Signature` header against the payload and the webhook secret key:
  ```typescript
  import crypto from 'node:crypto'
  
  const hmac = crypto.createHmac('sha256', webhookSecret)
  hmac.update(rawRequestBody)
  const computedSignature = hmac.digest('hex')
  if (computedSignature !== providedSignature) {
    throw new Error('Invalid webhook signature')
  }
  ```
- **Job Offloading:** Never process design updates directly inside the HTTP webhook controller response. Immediately push the payload to a BullMQ queue and return a `200 OK` response to Canva within the 3-second timeout window.

### 5. Rate Limiting and Resilience
- **Rate Limit (HTTP 429):** Canva API enforces rate limits. Intercept responses and check for `429` status. Implement exponential backoff retry logic.
- **Circuit Breaker:** If a connection fails consecutively or returns `401 Unauthorized` (indicating revoked permission), disable the credential (`is_active = false`) and log the event with details.

## Constraints
- **Do NOT** store OAuth client secrets or webhook keys in source code. Always use `env.get()`.
- **Do NOT** perform Canva API HTTP calls synchronously within DB transactions, as this blocks pool connections.
- **Do NOT** allow raw unauthenticated webhooks; HMAC verification is mandatory.
- **Do NOT** use in-memory buffers (`fs.readFileSync`) for large media assets. Always use readable/writable streams.
