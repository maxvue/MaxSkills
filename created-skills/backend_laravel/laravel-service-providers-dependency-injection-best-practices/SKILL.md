---
name: laravel-service-providers-dependency-injection-best-practices
description: Use when creating, modifying, or registering Laravel Service Providers, binding services (bind, singleton, scoped) to the Service Container, resolving dependencies via dependency injection, or ensuring memory safety and Octane compatibility in singleton bindings.
---

# Goal

Provide clear, robust guidelines and implementation patterns for registering services via Service Providers and resolving them using dependency injection in Laravel, specifically ensuring compatibility with high-performance stateless environments like Laravel Octane.

# Instructions

### 1. Service Provider Creation and Registration
- Use Artisan to generate new Service Providers:
  ```bash
  php artisan make:provider PaymentServiceProvider --no-interaction
  ```
- Ensure the new provider is registered in the `bootstrap/providers.php` file (the standard provider registration file for Laravel 11+).

### 2. Choosing the Correct Binding Lifetime
Choose the appropriate container registration method based on the lifecycle of the object:
- **`bind`**: Use when a new, distinct instance of the service is required every time it is resolved.
- **`singleton`**: Use when a single shared instance should be reused across the entire application lifecycle. 
  - *Caution*: In Laravel Octane, a singleton persists across multiple user requests.
- **`scoped`**: Use when a single instance is required per request/cycle, but should be discarded and rebuilt on the next request. This is the safest default for services that carry request-specific data.

### 3. Laravel Octane Memory Safety & Stateless Bindings
To prevent memory leaks and state pollution across requests in Octane:
- **Never** inject the `Application` container, the `Request`, the `Session`, or the `Config` repository directly into a singleton's constructor.
- **Always** resolve request-specific instances lazily using a closure inside the singleton binding, or bind the service as `scoped`:
  ```php
  // Bad: Resolves the request once at application boot and keeps it forever
  $this->app->singleton(MyService::class, function ($app) {
      return new MyService($app['request']);
  });

  // Good: Resolves the current request dynamically when the service is consumed
  $this->app->singleton(MyService::class, function () {
      return new MyService(fn () => request());
  });

  // Good: Registered as scoped, so a new instance is created for each new request
  $this->app->scoped(MyService::class, function ($app) {
      return new MyService($app['request']);
  });
  ```
- Do not store state or append data to static properties on services registered as singletons.

### 4. Dependency Injection & PHP 8 Constructor Promotion
- Always use **Constructor Property Promotion** for clean, readable dependency injection:
  ```php
  public function __construct(
      protected PaymentGateway $gateway,
      protected LoggerInterface $logger,
  ) {}
  ```
- Ensure all parameters have explicit type declarations and return types.
- Avoid leaving empty, zero-parameter constructors.

### 5. Writing Container Resolution Tests
Verify that your bindings resolve correctly from the Service Container using Pest:
```php
use App\Services\PaymentGateway;
use App\Contracts\PaymentGatewayContract;

test('it resolves payment gateway contract to payment gateway service', function () {
    $service = app(PaymentGatewayContract::class);
    
    expect($service)->toBeInstanceOf(PaymentGateway::class);
});
```

# Examples

### Example: A Safe PaymentServiceProvider
```php
<?php

namespace App\Providers;

use App\Contracts\PaymentGatewayContract;
use App\Services\AutentiquePaymentGateway;
use Illuminate\Support\ServiceProvider;
use Illuminate\Contracts\Foundation\Application;

class PaymentServiceProvider extends ServiceProvider
{
    /**
     * Register services.
     */
    public function register(): void
    {
        // Use scoped to ensure that each request gets its own instance,
        // preventing cross-request token exposure.
        $this->app->scoped(PaymentGatewayContract::class, function (Application $app) {
            return new AutentiquePaymentGateway(
                token: (string) config('services.autentique.token'),
                // Lazy resolution wrapper for request info if needed
                requestIp: fn () => request()->ip()
            );
        });
    }
}
```

### Example: Consuming the Registered Service
```php
<?php

namespace App\Http\Controllers;

use App\Contracts\PaymentGatewayContract;
use Illuminate\Http\JsonResponse;

class PaymentController extends Controller
{
    // PHP 8 Constructor Property Promotion
    public function __construct(
        protected PaymentGatewayContract $paymentGateway
    ) {}

    public function process(): JsonResponse
    {
        $result = $this->paymentGateway->charge(100.00);

        return response()->json([
            'success' => $result->isSuccess(),
            'transaction_id' => $result->getTransactionId(),
        ]);
    }
}
```

# Constraints

- Do **NOT** use `singleton` for any service that processes or holds request-specific data unless dependencies are resolved using closures.
- Do **NOT** mutate static properties on classes inside the container.
- Do **NOT** manually instantiate services using `new` inside Controllers or Models if they should be managed and injected by the container.
- Do **NOT** bypass constructor injection in favor of the `app()` helper inside service classes (prefer proper constructor DI).

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
