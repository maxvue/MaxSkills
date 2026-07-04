---
name: laravel-context-metadata-tracking-best-practices
description: Use when implementing, refactoring, or debugging Laravel Context (Illuminate\Support\Facades\Context) to track request metadata, share state between HTTP requests and queued Jobs, configure context logging, or sanitize context keys in a stateless environment. Triggers on Context::add(), Context::get(), Context::pull(), log context configuration, and sharing request metadata.
---

## Goal
Establish solid guidelines, patterns, and best practices for implementing, debugging, and managing request/job context metadata using Laravel's native Context Facade (`Illuminate\Support\Facades\Context`) within the Engeapp ecosystem.

## Instructions

### 1. Request Context Initialization via Middleware
Always capture request-specific metadata in a global or route-specific middleware.
- **Trace ID:** Look for an incoming `X-Trace-Id` or `X-Request-Id` header. If missing, generate a new UUID.
- **Auth Info:** Store the authenticated user's ID and role, but ensure it is sanitized and doesn't leak sensitive data.
- **IP & User Agent:** Store metadata that helps correlate logs.

Example Middleware:
```php
namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Context;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;

class CaptureRequestMetadata
{
    public function handle(Request $request, Closure $next): Response
    {
        Context::add([
            'trace_id' => $request->header('X-Trace-Id') ?? (string) Str::uuid(),
            'user_id' => $request->user()?->id,
            'ip_address' => $request->ip(),
        ]);

        $response = $next($request);

        // Optional: Include trace_id in response headers
        $response->headers->set('X-Trace-Id', Context::get('trace_id'));

        return $response;
    }
}
```

### 2. Sharing Context with Queued Jobs
Laravel automatically propagates `Context` data to queued jobs.
- Rely on native Context propagation for queue jobs.
- Avoid manually passing trace IDs as job parameters if they are already stored in the Context.
- When writing queue listeners, use `Context::get('trace_id')` to trace asynchronous processing.

### 3. Log Integration & Configuration
Configure Laravel's log formatter to output context metadata automatically.
- Define a custom Monolog formatter or use Laravel's default logging configuration to append context.
- Keep keys flat and descriptive to facilitate log querying in tools like Elasticsearch, AWS CloudWatch, or local log viewers.

### 4. Memory Management & Laravel Octane Compatibility
Since Engeapp runs on Laravel Octane, state persistence between requests must be carefully handled.
- Laravel automatically flushes the `Context` facade state after each request when running Octane.
- However, if you store state in custom static properties or singletons, you must manually reset them using Octane event listeners (`tick` or request terminators) or avoid them entirely in favor of `Context`.

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **NO Sensitive Data:** Never store passwords, API keys, full credit card numbers, or personally identifiable information (PII) directly in the Context.
- **NO Large Objects:** Do not store heavy Eloquent model instances or massive arrays in the Context. Store IDs (e.g., `user_id`, `project_id`) instead.
- **Avoid Overwriting:** Ensure third-party libraries or internal packages do not overwrite system keys like `trace_id` by using structured prefixing (e.g., `engeapp:trace_id`) if namespace collision is possible.
- **Keep it Stateless:** Do not use Context as a replacement for HTTP Session or Cache. It only lasts for the lifecycle of a single request/process execution.
