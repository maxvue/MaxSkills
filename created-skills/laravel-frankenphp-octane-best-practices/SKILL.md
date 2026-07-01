---
name: laravel-frankenphp-octane-best-practices
description: Use when configuring, deploying, or debugging Laravel Octane on FrankenPHP (or Swoole/RoadRunner), and when writing, refactoring, or reviewing PHP code for Octane statelessness. Triggers on Octane config files, FrankenPHP worker scripts, Caddyfile adjustments, deployment scripts restarting FrankenPHP, and on singletons, static properties, container bindings, memory leaks, or shared-state leakage between requests.
---

# Laravel FrankenPHP Octane Best Practices

## Goal
Provide guidelines, configurations, and strategies to successfully run, deploy, and debug Laravel Octane powered by FrankenPHP, ensuring high performance, zero-downtime deployments, and preventing memory leaks or state pollution in persistent memory environments.

## Instructions

1. **State Isolation & Memory Leak Prevention**:
   - Ensure service providers register application services that maintain request-specific state (like current user, session, dynamic config) using `$this->app->scoped()` instead of `$this->app->singleton()`. A `scoped` binding acts as a singleton for the duration of a single request but is destroyed and recreated on subsequent requests.
   - If utilizing custom services that persist state across requests, implement custom resetters or register class resetters under `octane.listeners` or `octane.warm` inside `config/octane.php`.
   - Manually clear any static arrays or collections at the end of a request cycle by listening to Octane's `RequestTerminated` event or defining a custom resetter class. Never declare static properties that accumulate data across request cycles (e.g., `public static array $cache = [];`) without resetting them.
   - **Resolver closures in singletons**: If a service truly must be a singleton but needs request-specific data, never inject the application container (`$app`), the HTTP `Request`, the config repository (`$config`), or the session manager (`$session`) directly into its constructor. Inject a resolver closure (e.g. `fn () => $app['request']`) or resolve dynamically inside methods via helpers (`request()`, `config()`, `auth()`) or facades.
   - **Third-party package state**: Verify packages that maintain internal state are reset between requests. If a package is not Octane-aware, add its reset logic to the `octane.listeners` array under the `RequestReceived` event.
   - **Concurrency / `Octane::concurrently`**: When running tasks via the `Concurrency` facade (`Concurrency::run(...)` / `Concurrency::defer(...)`) or `Octane::concurrently()`, remember they execute in isolated worker processes. Ensure database connections and transactional integrity are properly maintained within each concurrent task.

2. **FrankenPHP Worker Configuration**:
   - In production, ensure FrankenPHP is configured to run in worker mode using the `--worker` flag. For example:
     `php artisan octane:start --server=frankenphp --workers=4 --max-requests=10000`
   - Use the `--max-requests` option to automatically restart workers after they process a set number of requests to mitigate slow memory leaks from third-party libraries.
   - Adjust PHP configurations inside `php.ini` or FrankenPHP's environment variables (e.g., `FRANKENPHP_CONFIG`) to match worker concurrency requirements.

3. **Caddyfile Configuration for FrankenPHP**:
   - When deploying FrankenPHP behind Caddy or using FrankenPHP's built-in Caddy server, configure the Caddyfile to direct traffic to Octane's worker script correctly.
   - Ensure static assets (CSS, JS, images) are served directly by Caddy/FrankenPHP without hitting the PHP worker process.
   - Example Caddyfile routing:
     ```caddyfile
     example.com {
         root * /home/forge/example.com/public
         file_server
         
         # Route all requests to FrankenPHP worker
         frankenphp {
             num_workers 4
         }
     }
     ```

4. **Zero-Downtime Deployment & Reloads**:
   - When performing a deploy, do not simply kill the server. Instead, reload the workers gracefully.
   - Use the Artisan reload command in your deployment script:
     ```bash
     php artisan octane:reload
     ```
   - Ensure your deployment workflow (e.g., deployer, bash scripts) calls `octane:reload` after caching config, routing, and views.
   - If running FrankenPHP as a systemd service, configure systemd to support graceful reloads (e.g., sending `SIGHUP` or `SIGUSR1` to reload configurations/workers).

## Constraints
- **No direct request storage**: Do NOT store the current `Request` object in singletons or class properties that persist across requests.
- **No unmanaged state**: Never use PHP superglobals (`$_GET`, `$_POST`, `$_SERVER`, `$_SESSION`) or `global` variables directly; always use Laravel's request lifecycle objects.
- **No unmanaged static properties**: Do NOT append to static arrays/collections during a request without resetting them at the end of the request.
- **No hard restarts during user traffic**: Do NOT run `octane:stop` followed by `octane:start` in production deployment scripts unless necessary, as it causes downtime. Always prefer `octane:reload`.

## Examples

### Example: Registering a Stateful Service Correctly
```php
// In AppServiceProvider.php
// BAD: Registering request-dependent service as a singleton
$this->app->singleton(TenantManager::class, function ($app) {
    return new TenantManager($app['request']->getHost());
});

// GOOD: Registering request-dependent service as scoped
$this->app->scoped(TenantManager::class, function ($app) {
    return new TenantManager($app['request']->getHost());
});
```

### Bad Example: A Singleton storing request-specific state in its constructor
```php
<?php

namespace App\Services;

use Illuminate\Http\Request;

class PaymentService
{
    protected Request $request;

    // VIOLATION: Injecting Request directly into a Singleton constructor.
    // This Request will persist across subsequent requests/users!
    public function __construct(Request $request)
    {
        $this->request = $request;
    }

    public function processPayment()
    {
        $ip = $this->request->ip();
        // Payment processing logic...
    }
}
```

### Good Example: Singleton refactored with a resolver closure
```php
<?php

namespace App\Services;

use Closure;
use Illuminate\Http\Request;

class PaymentService
{
    // OPTION A: Inject a request resolver Closure
    public function __construct(
        protected Closure $requestResolver
    ) {}

    public function processPayment()
    {
        /** @var Request $request */
        $request = ($this->requestResolver)();
        $ip = $request->ip();
        // Payment processing logic...
    }
}

// Service Provider binding:
$this->app->singleton(PaymentService::class, function ($app) {
    return new PaymentService(fn () => $app['request']);
});
```

### Good Example: Singleton resolving state dynamically (stateless)
```php
<?php

namespace App\Services;

class PaymentService
{
    // OPTION B: No dependencies in constructor. Resolve helpers dynamically.
    public function __construct() {}

    public function processPayment()
    {
        // Resolve request dynamically per method call
        $ip = request()->ip();
        // Payment processing logic...
    }
}
```

### Example: Graceful Reload in Deployer Script
```php
// In deploy.php (Deployer)
task('deploy:octane_reload', function () {
    run('{{bin/php}} {{release_path}}/artisan octane:reload');
})->desc('Reload Laravel Octane workers gracefully');

after('deploy:publish', 'deploy:octane_reload');
```
