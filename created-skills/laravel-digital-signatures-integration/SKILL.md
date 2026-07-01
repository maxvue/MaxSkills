---
name: laravel-digital-signatures-integration
description: Use when designing, implementing, or modifying electronic and digital signature integrations (such as Autentique or Clicksign) within the Laravel codebase. It covers document upload/creation, signer configuration, secure webhook handling, and background job processing for signed documents.
---

# Laravel Digital Signatures Integration

## Goal
Establish secure, robust, and consistent development patterns for integrating electronic and digital signatures via third-party APIs (like Autentique and Clicksign) within the Laravel backend of the Engeapp ecosystem.

## Instructions

### 1. Configuration Setup
Always store API credentials in `.env` and load them via `config/services.php`. Never access `env()` directly outside of configuration files.
Never hardcode API tokens or webhook secrets in service classes or controllers.

### 2. Service Architecture
Create dedicated Service classes (e.g., `ClicksignService`, `SignatureService`) to encapsulate all API operations.
- Inject configurations or API clients using constructor property promotion where applicable.
- For Clicksign, use Laravel's `Http` facade to make API requests. Do not use raw curl or external third-party SDKs.
- For Autentique, use the provided GraphQL/Document client appropriately.
- Log failures using a dedicated logging channel (e.g., `autentique`, `clicksign`), specifying clear context.

### 3. Asynchronous Webhook Processing
**Never process webhooks synchronously** to prevent HTTP timeouts. Always validate the webhook, extract the required payload identifiers, and dispatch a queued job (e.g., `ProcessClicksignWebhookJob`, `ReloadPowerAttorneyStatusJob`) to handle the business logic, status synchronization, or file downloading.

## Autentique-Specific Instructions

### Document Creation & Signer Configuration
When dispatching a document for signatures, use the Autentique Documents client. Define signers clearly, including the delivery method (e.g., WhatsApp).

```php
use App\Models\Project\ProjectPowerOfAttorneyDocument;
use vinicinbgs\Autentique\Documents;

class SignatureService
{
    public function __construct(private readonly Documents $documents) {}

    public function sendToAutentique(ProjectPowerOfAttorneyDocument $documentModel, string $filePath, ?string $phone = null): void
    {
        $attributes = [
            'document' => ['name' => 'PROCURAÇÃO - ' . $documentModel->project->client->name],
            'signers'  => [
                ['email' => 'contato@enge.tec.br', 'action' => 'SIGN'],
                [
                    'phone' => '+' . ($documentModel->send_to ?? $documentModel->project->client->international_phone_number), 
                    'delivery_method' => 'DELIVERY_METHOD_WHATSAPP', 
                    'action' => 'SIGN'
                ],
            ],
            'file' => $filePath,
        ];

        $response = $this->documents->create($attributes);
        $documentId = data_get($response, 'data.createDocument.id');

        if ($documentId) {
            $documentModel->uuid_doc = (string) $documentId;
            $documentModel->save();
        }
    }
}
```

### Secure Webhook Validation (Autentique)
Always validate incoming webhook requests against the configured webhook secret. The secret must be compared using constant-time string comparison (`hash_equals`) to prevent timing attacks.

```php
private function isValidToken(Request $request, string $secret): bool
{
    $token = $request->bearerToken();
    if (!$token) {
        return false;
    }
    return hash_equals($secret, $token);
}
```

### Build Linear Signature History
When retrieving document details, map the array of signatures to a linear history trace to expose progress in real-time to the frontend.

## Clicksign-Specific Instructions

### Clicksign Service Methods
Upload documents, create signers, and add signers to documents using the HTTP facade.

```php
// Example: Add signer to document
public function addSignerToDocument(string $documentKey, string $signerKey, string $signAs = 'sign'): array
{
    $response = Http::withToken($this->token)
        ->post("{$this->baseUrl}/api/v1/lists", [
            'list' => [
                'document_key' => $documentKey,
                'signer_key' => $signerKey,
                'sign_as' => $signAs,
            ],
        ]);

    if ($response->failed()) {
        Log::channel('clicksign')->error('Failed to associate signer with document', [
            'document_key' => $documentKey,
            'signer_key' => $signerKey,
            'status' => $response->status(),
            'body' => $response->json(),
        ]);
        $response->throw();
    }

    return $response->json();
}
```

### Webhook Handling and Signature Validation (Clicksign)
- Clicksign sends webhooks using `POST`.
- The webhook payload authenticity is validated using the `X-Hook-Signature` header (HMAC SHA256 signature of the request body).

```php
public function handle(Request $request): Response
{
    $signature = $request->header('X-Hook-Signature');
    $secret = config('services.clicksign.webhook_secret');
    $payload = $request->getContent();

    if (empty($signature) || empty($secret)) {
        return response('Unauthorized', 401);
    }

    $computedSignature = hash_hmac('sha256', $payload, $secret);

    if (!hash_equals($computedSignature, $signature)) {
        return response('Unauthorized', 401);
    }

    $data = $request->json()->all();
    ProcessClicksignWebhookJob::dispatch($data);

    return response('Webhook processed successfully', 200);
}
```

### Resilient Signed Document Download (General/Clicksign)
Upon receiving a signed status notification, fetch the signed PDF securely and save it using Laravel's `Storage` abstraction. Implement a Queue Job with automatic retries for resilient downloads.

## Constraints
- **No Synchronous Webhook Processing:** Always delegate webhook payload processing, document downloading, and status checks to background queue jobs.
- **Strict Webhook Validation:** Never bypass `X-Hook-Signature` (Clicksign) or Token verification (Autentique). Always use `hash_equals()` for constant-time comparison to prevent timing attacks.
- **Config-Driven Secrets:** Do not hardcode URLs, tokens, or webhook secrets in the code.
- **Use Laravel HTTP Client (For REST APIs):** Do not use raw PHP `curl_*` commands. Always use Laravel's `Http` facade when communicating via REST.
- **Dedicated Logging:** All events, errors, and validation failures must be logged into their respective log channels.
