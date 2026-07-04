---
name: laravel-sentry-integration-best-practices
description: Use when integrating, configuring, or debugging Sentry in a Laravel application. Triggers on Sentry SDK installation, configuring Sentry config files, adding custom breadcrumbs, capturing exceptions with Sentry::captureException, and setting up performance APM/tracing.
---

# Goal
Provide solid guidelines and consistent standards for real-time error tracking and Application Performance Monitoring (APM) using Sentry in the Laravel backend of the application.

# Instructions

### 1. Installation & Initialization
Install the official Sentry Laravel SDK:
```bash
composer require sentry/sentry-laravel
```

Publish the configuration file:
```bash
php artisan sentry:publish --dsn=YOUR_SENTRY_DSN
```
This command adds the `SENTRY_LARAVEL_DSN` variable to your `.env` file and creates the `config/sentry.php` file.

### 2. Laravel 11+ Exception Integration
Integrate Sentry handler into the exception handler setup located in `bootstrap/app.php`:
```php
use Sentry\Laravel\Integration;

return Application::configure(basePath: dirname(__DIR__))
    // ...
    ->withExceptions(function (Exceptions $exceptions) {
        Integration::handles($exceptions);
    })->create();
```

### 3. Log Channel Integration
Configure Sentry as a log channel in `config/logging.php` to capture logs:
```php
'channels' => [
    'stack' => [
        'driver' => 'stack',
        'channels' => explode(',', env('LOG_STACK', 'single,sentry')),
        'ignore_exceptions' => false,
    ],

    'sentry' => [
        'driver' => 'sentry',
        'level' => env('LOG_LEVEL', 'error'), // Send only errors and above to Sentry automatically
        'bubble' => true,
    ],
],
```

### 4. Environment-Specific Configuration (`.env`)
Configure Sentry behavior depending on the environment:
```env
SENTRY_LARAVEL_DSN="https://key@sentry.io/project"
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```
- In high-traffic **production** environments, keep `SENTRY_TRACES_SAMPLE_RATE` low (e.g., `0.05` to `0.1`) to avoid rate limiting and excessive quotas.
- In **staging/development**, it can be set to `1.0` (100%) for debugging purposes.

### 5. Context Enrichment
Enrich exceptions with the authenticated user context, tenant information, or environment tags.

#### A. Global User Context (Middleware / Service Provider)
Configure context tracking inside `App\Providers\AppServiceProvider` or a custom `SentryServiceProvider`:
```php
use Sentry\State\Scope;
use function Sentry\configureScope;

public function boot(): void
{
    if (app()->bound('sentry')) {
        configureScope(function (Scope $scope): void {
            if (auth()->check()) {
                $scope->setUser([
                    'id' => auth()->id(),
                    'email' => auth()->user()?->email,
                    'username' => auth()->user()?->name,
                ]);
            }
            
            $scope->setTag('environment', app()->environment());
            $scope->setTag('php_version', phpversion());
        });
    }
}
```

#### B. Dynamic Tags & Extra Metadata
Add tags to group and filter issues, and extra data for deeper diagnosis:
```php
use Sentry\State\Scope;
use function Sentry\configureScope;

configureScope(function (Scope $scope) use ($tenantId, $apiVersion): void {
    $scope->setTag('tenant_id', $tenantId);
    $scope->setTag('api_version', $apiVersion);
    $scope->setExtra('payload_details', ['step' => 'execution', 'retries' => 3]);
});
```

### 6. Custom Breadcrumbs
Record breadcrumbs to trace the events that occurred immediately before the exception:
```php
use Sentry\Breadcrumb;
use function Sentry\addBreadcrumb;

addBreadcrumb(new Breadcrumb(
    level: Breadcrumb::LEVEL_INFO,
    type: Breadcrumb::TYPE_DEFAULT,
    category: 'payment',
    message: 'Processing invoice payment',
    metadata: [
        'invoice_id' => $invoice->id,
        'gateway' => 'asaas',
    ]
));
```

### 7. Manual Exception Capture
Use the `Sentry` Facade to capture non-fatal exceptions in `try/catch` blocks:
```php
use Sentry\Laravel\Facade as Sentry;

try {
    $this->paymentService->charge($invoice);
} catch (PaymentException $e) {
    Sentry::captureException($e);
    // Continue application flow
}
```

### 8. Horizon & Queue Monitoring
Sentry automatically monitors Laravel queues. Ensure the following:
- Keep `sentry/sentry-laravel` active in queue workers (Octane/Horizon).
- Customize queue job transaction names so they appear clearly in the Performance tab.
- In queue jobs, attach the job payload ID or user context during execution.

### 9. Sanitization & Sensitive Data (PII Prevention)
Prevent sensitive customer data (passwords, bank card details, auth tokens, etc.) from leaking to Sentry.

#### A. Configure Default Sanitization
Set `send_default_pii` to `false` in `config/sentry.php`:
```php
'send_default_pii' => false,
```

#### B. Advanced Request Filter (`before_send` hook)
Sanitize payloads or query parameters inside `config/sentry.php`:
```php
'before_send' => function (\Sentry\Event $event): ?\Sentry\Event {
    $request = $event->getRequest();
    
    if (isset($request['data'])) {
        $sensitiveFields = ['password', 'password_confirmation', 'credit_card', 'token', 'cvv'];
        foreach ($sensitiveFields as $field) {
            if (isset($request['data'][$field])) {
                $request['data'][$field] = '[FILTERED]';
            }
        }
        $event->setRequest($request);
    }
    
    return $event;
},
```

# Constraints
- Do NOT send PII (Personally Identifiable Information) under any circumstances. Ensure credentials, credit card details, and auth tokens are filtered out via `before_send` or by setting `send_default_pii => false`.
- Do NOT set `traces_sample_rate` to `1.0` in high-traffic production environments. Keep it between `0.01` and `0.20` to prevent rate limiting, high billing, and performance overhead.
- Do NOT capture common, expected HTTP exceptions such as `ValidationException`, `AuthenticationException`, or `ModelNotFoundException` that are part of standard flow. Configure them in the `dont_report` list of the Exception Handler or under Sentry's `ignore_exceptions` configuration.
- Do NOT block execution for exception reports. Always verify Sentry calls do not cause critical service degradation if Sentry servers are offline.

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
