---
name: laravel-exception-handling-logging
description: Use when defining, refactoring, or debugging exception handlers, custom Exceptions, logging structures, and monolog configurations in Laravel. Triggers on custom exception creation, try-catch blocks for API integrations, logging errors or warnings, and error reporting configurations.
---

# Exception Handling & Logging in Laravel

## Goal
Establish standardized patterns for exception handling and structured logging in the Laravel ecosystem of Engeapp. This ensures external APIs and internal jobs handle errors gracefully without silent failures or log pollution.

## Instructions

### 1. Creating Custom Exceptions
*   **Artisan Command**: Generate exceptions using `php artisan make:exception {ExceptionName} --no-interaction`.
*   **Contextual Data**: Add a `context()` method to the exception class to automatically capture relevant state when the exception is reported:
    ```php
    public function context(): array
    {
        return [
            'lead_id' => $this->leadId,
            'api_endpoint' => $this->endpoint,
        ];
    }
    ```
*   **Rendering for APIs**: If the exception is expected to be returned via an API response, implement a `render($request)` method:
    ```php
    public function render($request): \Illuminate\Http\JsonResponse
    {
        return response()->json([
            'success' => false,
            'error' => 'INTEGRATION_ERROR',
            'message' => $this->getMessage(),
        ], 422);
    }
    ```
*   **Custom Reporting**: Only implement `report()` if you need custom logic (e.g., sending to Slack, Discord, or specific analytics). Otherwise, let Laravel's global exception handler capture and log it.

### 2. Structured Logging Practices
*   **Integration Channels**: Configure and use specific channels in `config/logging.php` for third-party integrations (e.g., `whatsapp`, `gemini`, `autentique`). Avoid logging integration details to the default channel.
*   **Log Context**: Always pass parameters as context arrays rather than concatenating them into strings. This keeps log analysis tools clean:
    ```php
    // Good
    Log::channel('whatsapp')->error('Failed to send promotional template message', [
        'lead_id' => $lead->id,
        'phone' => $lead->phone,
        'error' => $exception->getMessage()
    ]);

    // Bad
    Log::channel('whatsapp')->error("Failed to send template to lead " . $lead->id . " - Error: " . $exception->getMessage());
    ```
*   **Avoid Sensitive Data**: Do not log authentication tokens, raw credit card details, passwords, or customer credentials.

### 3. Graceful Try-Catch Handling in Services
*   **Defensive Integration**: Always wrap external API calls (e.g., HTTP clients, SDKs) in a try-catch block.
*   **Avoid Silent Failures**: When catching an error, do not leave the catch block empty. Log the details and throw a descriptive custom exception.
    ```php
    try {
        $response = Http::timeout(5)->post($url, $payload);
    } catch (\Throwable $e) {
        Log::channel('service_name')->error('API Connection failed', [
            'url' => $url,
            'exception' => $e->getMessage(),
        ]);
        throw new ServiceIntegrationException('Unable to reach Service API', 0, $e);
    }
    ```

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
*   **NEVER** use empty catch blocks (`catch (\Throwable $e) {}`) that hide errors without logging or reporting.
*   **DO NOT** log sensitive user data (passwords, auth tokens, full card numbers).
*   **DO NOT** use default log channels (`single`, `daily`) for specific third-party integration logs; always use/create a dedicated channel.
*   **DO NOT** write inline comments explaining basic catch blocks; let standard exception and method names express the logic.
