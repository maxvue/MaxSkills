# Laravel Asaas Payments Integration

## Goal
Establish clear, secure, and resilient standards for integrating the Asaas payment gateway into the Engeapp backend. This integration must follow the native `BaseApi` pattern, utilize DTOs for payload typing, implement webhook security, and log transactional operations for auditability.

## Instructions

### 1. File and Directory Structure
Each integration must be isolated in its own directory. For Asaas, create the directory `app/Http/Integrations/Asaas/` containing:
- `Asaas.php` — The main connector class extending `BaseApi`.
- `Attributes.json` — API attribute configuration and validation constraints.
- `EndPoints.json` — Hierarchical endpoint routing mapping Asaas resources (Customers, Payments, Subscriptions).

### 2. Implementing the Connector Class (Asaas.php)
Because Asaas uses the `access_token` header instead of standard `Bearer` authentication, the connector must override the parent `request()` method to inject Guzzle headers correctly.

```php
<?php

namespace App\Http\Integrations\Asaas;

use App\Http\Integrations\BaseApi;
use Illuminate\Http\Client\Response;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Http;

class Asaas extends BaseApi
{
    protected array $bases_url = [
        'production' => 'https://api.asaas.com/v3',
        'development' => 'https://sandbox.asaas.com/v3',
    ];

    protected function getAccessToken() : ?string
    {
        return config('services.asaas.token');
    }

    /**
     * Override BaseApi request to support Asaas-specific access_token header
     */
    protected function request(string $method) : Response
    {
        $token = $this->getAccessToken();

        if ($this->clear_cache) {
            $this->setCacheKey();
            Cache::forget($this->cache_key);
        }

        if ($this->with_cache) {
            $this->setCacheKey();
            $data = Cache::get($this->cache_key);
            if ($data) {
                return $this->getToCache($data);
            }
        }

        $http = Http::contentType('application/json')
            ->timeout(120)
            ->withHeaders([
                'access_token' => $token,
            ]);

        if ($this->certificate_path) {
            $http->withOptions(['cert' => $this->certificate_path]);
        }

        $method = mb_strtolower($method);

        if (!in_array($method, ['get', 'post', 'put', 'patch', 'delete'])) {
            $method = 'get';
        }

        $data_send = $this->data_array;
        foreach ($this->data_array_path as $path_remove) {
            unset($data_send[$path_remove]);
        }

        $response = $http->{$method}($this->url, $data_send);

        if ($this->with_cache) {
            $data_cache = [
                'body'    => $response->body(),
                'status'  => $response->status(),
                'headers' => $response->headers(),
            ];
            Cache::put($this->cache_key, $data_cache, $this->cache_seconds);
        }

        return $response;
    }
}
```

### 3. Setting Up Schema Files
Create the JSON configurations inside `app/Http/Integrations/Asaas/`:

#### Attributes.json Example
```json
{
    "name": {
        "type": "string",
        "description": "Customer name",
        "required": true
    },
    "cpfCnpj": {
        "type": "string",
        "description": "Customer CPF or CNPJ",
        "required": true
    },
    "billingType": {
        "type": "enum",
        "enum": ["BOLETO", "CREDIT_CARD", "PIX", "UNDEFINED"],
        "description": "Type of payment",
        "required": true
    },
    "value": {
        "type": "number",
        "description": "Invoice total amount",
        "required": true
    },
    "dueDate": {
        "type": "string",
        "description": "Payment due date (YYYY-MM-DD)",
        "required": true
    },
    "customer": {
        "type": "string",
        "description": "Asaas customer ID",
        "required": true
    }
}
```

#### EndPoints.json Example
```json
{
    "customers": {
        "create": {
            "end_point": "/customers",
            "method": "POST",
            "description": "Register a new customer in Asaas",
            "attributes": {
                "body": ["name", "cpfCnpj"]
            }
        }
    },
    "payments": {
        "create": {
            "end_point": "/payments",
            "method": "POST",
            "description": "Generate a new charge/invoice",
            "attributes": {
                "body": ["customer", "billingType", "value", "dueDate"]
            }
        },
        "get": {
            "end_point": "/payments/{id}",
            "method": "GET",
            "description": "Retrieve specific invoice details",
            "attributes": {
                "path": ["id"]
            }
        }
    }
}
```

### 4. Handling Webhooks Securely
Webhooks are essential for capturing real-time updates (e.g. payments received, overdue alerts).
- **Authentication**: Check the request header `asaas-access-token` and match it with `config('services.asaas.webhook_token')`. If they do not match, abort the request with 401 Unauthorized.
- **DTOs**: Map Asaas webhook payloads using Spatie Data classes to ensure structural consistency.
- **Asynchronous Execution**: Webhook controllers should quickly save/queue payloads and respond to Asaas with HTTP 200 OK. Heavy database updates or user notifications should be dispatched to background Jobs.

```php
// Example: Webhook Controller verification
public function handle(Request $request)
{
    $token = $request->header('asaas-access-token');
    
    if ($token !== config('services.asaas.webhook_token')) {
        abort(401, 'Unauthorized Webhook Token');
    }
    
    // Dispatch webhook payload to a Job for background processing
    ProcessAsaasWebhookJob::dispatch($request->all());
    
    return response()->json(['status' => 'success'], 200);
}
```

## Constraints
- **Do NOT** bypass the webhook token authentication check. Webhooks are public facing endpoints and are highly vulnerable to malicious payloads.
- **Do NOT** execute long-running operations synchronously in the webhook handler (e.g., rendering PDF reports or querying multiple external services). Dispatch queue jobs to avoid webhook timeouts.
- **Do NOT** store credit card info locally. Send PCI-compliant payment requests directly to Asaas and store only the masked card information or transaction tokens returned by Asaas.
- **Do NOT** write hardcoded credentials in code; use environmental variables via `config/services.php`.
