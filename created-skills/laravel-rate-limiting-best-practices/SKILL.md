---
name: laravel-rate-limiting-best-practices
description: Use when configuring, optimizing, or debugging rate limits for HTTP routes, APIs, login endpoints, or queues in Laravel. Triggers on defining rate limiters in bootstrap/app.php, using RateLimiter facade, applying throttle middleware, customizing 429 response, and testing route throttling.
---

# Laravel Rate Limiting Best Practices

## Goal
Provide clear guidelines and robust standards for implementing, configuring, and testing request limits (rate limiting) in Laravel 13. This ensures the protection of endpoints (such as logins, payments, and AI requests) against brute-force attacks and abuse, optimizing infrastructure costs and maintaining application stability.

## Instructions

1. **Defining Rate Limiters in Laravel 13**:
   - In Laravel v11+, rate limiters are typically defined within `App\Providers\AppServiceProvider.php` (or a dedicated route/security provider) inside the `boot` method using the `RateLimiter::for` method.
   - Use the `Illuminate\Support\Facades\RateLimiter` facade.
   - Always group and name rate limiters semantically (e.g., `api`, `login`, `ai-inference`, `payment-transactions`).

   ```php
   use Illuminate\Cache\RateLimiting\Limit;
   use Illuminate\Http\Request;
   use Illuminate\Support\Facades\RateLimiter;

   RateLimiter::for('api', function (Request $request) {
       return Limit::perMinute(60)->by($request->user()?->id ?: $request->ip());
   });
   ```

2. **Applying the Middleware to Routes**:
   - Apply rate limiters to routes or route groups using the `throttle` middleware, passing the name of the defined limiter.
   - Inside `routes/api.php` or `routes/web.php`:
     ```php
     Route::middleware('throttle:api')->group(function () {
         Route::get('/user', [UserController::class, 'show']);
     });

     Route::middleware('throttle:login')->post('/login', [AuthController::class, 'login']);
     ```

3. **Dynamic Throttling & Identification**:
   - Never use a static limit without user/IP differentiation, otherwise one user could block the entire application.
   - For authenticated routes, scope by the user ID: `$request->user()?->id`.
   - For guest routes (like login/password reset), scope by IP address: `$request->ip()`.
   - For API clients or integrators, scope by API Key or client ID.
   - Consider dynamic limits based on user roles or subscription tiers:
     ```php
     RateLimiter::for('api', function (Request $request) {
         $limit = $request->user()?->isPremium() ? 1000 : 100;
         return Limit::perMinute($limit)->by($request->user()?->id ?: $request->ip());
     });
     ```

4. **Customizing the 429 Too Many Requests Response**:
   - Customize the HTTP 429 response to return clean, standardized JSON instead of default Laravel HTML exception pages for API routes.
   - Set custom response headers and error messages:
     ```php
     RateLimiter::for('ai-inference', function (Request $request) {
         return Limit::perMinute(5)
             ->by($request->user()?->id ?: $request->ip())
             ->response(function (Request $request, array $headers) {
                 return response()->json([
                     'error' => 'Too Many Requests',
                     'message' => 'You have exceeded your AI request quota. Please retry in ' . $headers['Retry-After'] . ' seconds.',
                 ], 429, $headers);
             });
     });
     ```

5. **Rate Limiting in Job Queues**:
   - If jobs interact with external rate-limited APIs (e.g., payment gateways, external AI providers), use the `redis` rate limiter to control queue worker execution:
     ```php
     use Illuminate\Support\Facades\Redis;

     Redis::throttle('payment-gateway')
         ->allow(10)
         ->every(60)
         ->then(function () {
             // Process the payment job...
         }, function () {
             // Release the job back to the queue with a delay
             return $this->release(30);
         });
     ```

6. **Bypassing Rate Limiting in Local/Testing Environments**:
   - To prevent blocking automated tests or local development flows, allow disabling rate limits via `.env` configuration or during test execution.
   - In `AppServiceProvider.php`:
     ```php
     if (app()->runningUnitTests() || config('security.disable_rate_limits')) {
         RateLimiter::for('api', fn () => Limit::none());
     }
     ```

7. **Testing Throttling with Pest**:
   - Use Pest architecture and feature tests to verify that endpoints are correctly throttled.
   - Simulate consecutive requests using loops and assert the status code:
     ```php
     it('throttles login requests after 5 attempts', function () {
         // Perform 5 successful requests or failures
         for ($i = 0; $i < 5; $i++) {
             $response = $this->postJson('/api/login', [
                 'email' => 'user@example.com',
                 'password' => 'wrong-password'
             ]);
             $response->assertStatus(422); // Validation error, but not throttled yet
         }

         // The 6th request must be throttled
         $this->postJson('/api/login', [
             'email' => 'user@example.com',
             'password' => 'wrong-password'
         ])->assertStatus(429);
     });
     ```

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **No Raw Database Locks**: Do NOT write custom DB queries or lock files to count requests. Always use Laravel's native `RateLimiter` facade or `throttle` middleware.
- **Never Block Globally**: Do NOT define rate limiters without a unique identifier (like IP or User ID) using `by()`, as it would throttle the route for all users globally.
- **JSON Response on APIs**: Rate limiters applied to API routes must return JSON responses with standard CORS and retry-after headers, avoiding default HTML error pages.
- **Handle Cache Failures**: Ensure the cache driver is properly configured (e.g., Redis or database) to support rate limits. Rate limiting using the `array` cache driver does not persist across web requests.

## Examples

### Bad Example: Implementing manual count inside a Controller
```php
<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;

class AiController extends Controller
{
    public function generateText(Request $request)
    {
        $key = 'user_ai_limit:' . $request->ip();
        $attempts = Cache::get($key, 0);

        // VIOLATION: Manual rate limiting logic inside controller.
        // Hard to scale, lacks proper HTTP headers, and skips Laravel standards.
        if ($attempts >= 5) {
            return response()->json(['error' => 'Too many requests'], 400);
        }

        Cache::put($key, $attempts + 1, now()->addMinutes(1));

        // Process AI request...
    }
}
```

### Good Example: Defining a Rate Limiter in AppServiceProvider and applying Middleware
```php
// 1. Define in AppServiceProvider.php
namespace App\Providers;

use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        RateLimiter::for('ai-inference', function (Request $request) {
            return Limit::perMinute(5)
                ->by($request->user()?->id ?: $request->ip())
                ->response(function (Request $request, array $headers) {
                    return response()->json([
                        'error' => 'Too Many Requests',
                        'message' => 'AI generation quota exceeded. Try again in ' . $headers['Retry-After'] . ' seconds.',
                    ], 429, $headers);
                });
        });
    }
}

// 2. Apply in routes/api.php
Route::middleware('throttle:ai-inference')->post('/ai/generate', [AiController::class, 'generateText']);
```
