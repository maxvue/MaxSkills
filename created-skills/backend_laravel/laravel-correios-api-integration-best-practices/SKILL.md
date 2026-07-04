---
name: laravel-correios-api-integration-best-practices
description: Use when creating, refactoring, reviewing, or debugging integrations with the official Correios API. Triggers on authentication token management, caching strategies for postal codes (CEP), parcel tracking, shipping rate calculations, and handling Correios network timeouts or authentication failures.
---

# Laravel Correios API Integration Best Practices

## Goal
Establish solid, consistent guidelines for integrating, consuming, and debugging the official Correios API in the Laravel backend of the Engeapp ecosystem. This ensures resilient dynamic authentication token renewal, safe caching of postal codes (CEPs), robust exception handling, and compatibility with stateless execution environments like Laravel Octane.

## Instructions

### 1. Dynamic Token Management & Octane Compatibility
*   **Do Not Persist Tokens in Instance State**: Avoid storing the active token inside service properties without validation checks. In stateless environments (Laravel Octane), services registered as singletons persist across requests. Storing a token directly in a property can cause authentication failures if the token expires in the API while remaining in the memory state.
*   **Cache-Backed Resolution**: Always resolve the token dynamically from the cache. Ensure the cache TTL aligns with the Correios token validity (usually 24 hours).
*   **Auto-Renewal Flow**: When the token is missing or expired, fetch a new one, store it in the cache, and return it. If the token request fails, throw a custom exception and clear any partial cache values.

### 2. Caching Strategies for Postal Codes (CEP)
*   **Avoid Redundant Requests**: Store address details fetched by CEP in the cache for 24 hours (`now()->addHours(24)`) or more, depending on business requirements.
*   **Cache Decoded Data Only**: Store the raw array representation of the address in the cache. 
*   **Prevent Runtime Method Errors**: Never invoke the `json()` method directly on data retrieved from the cache. Once cached, the value is returned as a plain array. Ensure you verify the structure before extracting values.

### 3. Graceful Exception Handling and Logging
*   **HTTP Client Timeout & Retries**: Always enforce a timeout (e.g., 5 seconds) and consider using retries for temporary network blips:
    ```php
    Http::timeout(5)->retry(3, 100)
    ```
*   **Structured Logging**: Log all connection and API failures to a dedicated log channel (e.g., `Log::channel('correios')`) using a context array. Never concatenate sensitive or dynamic values in the log message string.
*   **Custom Exceptions**: Avoid silent failures or returning generic empty values. Throw a domain-specific exception (e.g., `CorreiosIntegrationException`) when the API is unreachable, credentials are invalid, or responses are malformed.

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
*   **NEVER** silence HTTP exceptions or connection failures by returning `null` without logging the error with full context.
*   **DO NOT** invoke HTTP response methods (like `json()`) on arrays read from the cache.
*   **DO NOT** store the authentication token in static class properties or instance properties without a mechanism to refresh it when it expires in the cache.
*   **DO NOT** couple Correios integration services directly to HTTP request variables (`request()`) or view generation logic.

## Examples

### Resilient CorreiosService Implementation

```php
<?php

namespace App\Services;

use App\Exceptions\CorreiosIntegrationException;
use Illuminate\Http\Client\Response;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Throwable;

class CorreiosService
{
    protected string $baseUrl;
    protected string $user;
    protected string $code;

    public function __construct()
    {
        $this->baseUrl = config('api.correios.base_url');
        $this->user = config('api.correios.user');
        $this->code = config('api.correios.code');
    }

    /**
     * Resolves the authentication token dynamically, leveraging cache.
     *
     * @return string
     * @throws CorreiosIntegrationException
     */
    public function getToken(): string
    {
        $token = Cache::get('correios_api_token');

        if (!$token) {
            $token = $this->fetchNewToken();
            // Cache the token for 24 hours
            Cache::put('correios_api_token', $token, now()->addHours(24));
        }

        return $token;
    }

    /**
     * Fetches a new authentication token from Correios API.
     *
     * @return string
     * @throws CorreiosIntegrationException
     */
    protected function fetchNewToken(): string
    {
        $url = $this->baseUrl . '/token/v1/autentica';

        try {
            $response = Http::timeout(5)
                ->withBasicAuth($this->user, $this->code)
                ->post($url);

            if ($response->failed()) {
                Log::channel('correios')->error('Correios authentication failed', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                ]);

                throw new CorreiosIntegrationException('Failed to authenticate with Correios API.');
            }

            $token = $response->json('token');

            if (!$token) {
                throw new CorreiosIntegrationException('Correios authentication response did not contain a token.');
            }

            return $token;
        } catch (Throwable $e) {
            if ($e instanceof CorreiosIntegrationException) {
                throw $e;
            }

            Log::channel('correios')->error('Unexpected error during Correios authentication', [
                'exception' => $e->getMessage(),
            ]);

            throw new CorreiosIntegrationException('Unexpected authentication error.', 0, $e);
        }
    }

    /**
     * Consults address details by CEP.
     *
     * @param string $cep
     * @return array
     * @throws CorreiosIntegrationException
     */
    public function getCep(string $cep): array
    {
        // Supposing helpers 'cepIsNotValid' and 'cepOnlyNumber' are available
        if (cepIsNotValid($cep)) {
            return [];
        }

        $cep = cepOnlyNumber($cep);
        $cacheKey = 'correios_api_ceps_' . $cep;

        return Cache::remember($cacheKey, now()->addHours(24), function () use ($cep) {
            $url = $this->baseUrl . '/cep/v1/enderecos/' . $cep;

            try {
                $token = $this->getToken();
                $response = Http::timeout(5)
                    ->withToken($token)
                    ->get($url);

                if ($response->status() === 404) {
                    return [];
                }

                if ($response->failed()) {
                    Log::channel('correios')->error('Correios CEP query failed', [
                        'cep' => $cep,
                        'status' => $response->status(),
                        'body' => $response->body(),
                    ]);

                    throw new CorreiosIntegrationException("Failed to query CEP {$cep} from Correios.");
                }

                return $response->json() ?? [];
            } catch (Throwable $e) {
                if ($e instanceof CorreiosIntegrationException) {
                    throw $e;
                }

                Log::channel('correios')->error('Unexpected error during Correios CEP query', [
                    'cep' => $cep,
                    'exception' => $e->getMessage(),
                ]);

                throw new CorreiosIntegrationException("Unexpected error querying CEP {$cep}.", 0, $e);
            }
        });
    }
}
```
