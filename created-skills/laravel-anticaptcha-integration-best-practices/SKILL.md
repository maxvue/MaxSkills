---
name: laravel-anticaptcha-integration-best-practices
description: Use when implementing, configuring, or debugging CAPTCHA resolution services (Anti-Captcha) in the Laravel backend, including ImageToText tasks, handling API keys, handling errors, timeouts, and logging.
---

# Laravel Anti-Captcha Integration Best Practices

## Goal
Provide clear, structured guidelines and code patterns for integrating, solving, and monitoring CAPTCHA resolution services (specifically Anti-Captcha) within the Laravel backend of the Engeapp ecosystem, ensuring resilience, secure configuration, robust error handling, and dedicated logging.

## Instructions

### 1. Configuration & Key Management
- Always use environment variables to store the Anti-Captcha API key.
- The configuration must be read via `config('app.anticaptcha')` which points to `env('ANTICAPTCHA_KEY')` in `config/app.php`.
- Do NOT hardcode the API key in classes, controllers, or services.
- Always check if the API key is configured before initiating a captcha request. If empty, fail gracefully or throw a configuration exception.

### 2. Utilizing App Classes
Engeapp has wrapper classes for Anti-Captcha under `App\Classes\Anticaptcha`:
- **`App\Classes\Anticaptcha\Anticaptcha`**: Use the static helper `image(string $path, array $options = [])` for quick ImageToText tasks. It handles instantiation, task creation, and polling automatically.
- **`App\Classes\Anticaptcha\ImageToText`**: Direct instantiation for more customized visual CAPTCHAs.
  - Set the image file using `$api->setFile($filePath)`.
  - Set optional flags (e.g., `$api->phrase = true`, `$api->numeric = 1` for numbers only, `$api->case = true` for case sensitive).
  - Invoke `$api->createTask()` to submit.
  - Invoke `$api->waitForResult()` to poll for the solution.
  - Retrieve the solved text with `$api->getTaskSolution()`.

### 3. Error Handling and Resilience
- Captcha resolution depends on external APIs and is prone to network failure, timeouts, or insufficient balance.
- Check return values:
  - If `createTask()` returns `false` or `null`, a task creation error occurred. Inspect `$api->errorMessage` or `$api->errorCode`.
  - If `waitForResult()` returns `false`, the task processing timed out or failed.
- Implement retries with backoff if network connection drops, but cap the total execution time (default API timeout is 30s per request, polling takes up to 300s by default).
- For automated scrapers/services, catch `Illuminate\Http\Client\ConnectionException` and `Illuminate\Http\Client\RequestException` appropriately.

### 4. Transaction Logging
- All captcha transactions must be logged in the dedicated `anticaptcha` channel (`Log::channel('anticaptcha')`).
- Log warnings or errors with context: include the source file, error description, task ID, and relevant metadata (excluding secret keys).
- Logs are routed to `storage/logs/anticaptcha.log`. Make sure to monitor it when debugging captcha-related automation failures.

## Examples

### Example 1: Resolving a CAPTCHA Image using the Static Wrapper
```php
use App\Classes\Anticaptcha\Anticaptcha;
use Illuminate\Support\Facades\Log;

$imagePath = storage_path('app/captchas/temp_captcha.png');

if (!file_exists($imagePath)) {
    Log::channel('anticaptcha')->error("Captcha image file not found at: {$imagePath}");
    return null;
}

// Solve using the static helper with custom options (numbers only, case sensitive)
$solution = Anticaptcha::image($imagePath, [
    'numeric' => 1,
    'case' => true,
]);

if ($solution === null) {
    Log::channel('anticaptcha')->warning("Failed to resolve captcha for image: {$imagePath}");
} else {
    Log::channel('anticaptcha')->info("Captcha resolved successfully: {$solution}");
}
```

### Example 2: Detailed Workflow using ImageToText Class Directly
```php
use App\Classes\Anticaptcha\ImageToText;
use Illuminate\Support\Facades\Log;

$api = new ImageToText();
$imagePath = storage_path('app/captchas/temp_captcha.png');

if (!$api->setFile($imagePath)) {
    Log::channel('anticaptcha')->error("Failed to load captcha file: " . $api->errorMessage);
    return null;
}

// Configure options
$api->phrase = false;
$api->numeric = 1; // 1 = only numbers
$api->minLength = 4;
$api->maxLength = 6;

// Create task
$taskCreated = $api->createTask();
if ($taskCreated === null || $taskCreated === false) {
    Log::channel('anticaptcha')->error("Captcha task creation failed. Message: {$api->errorMessage}");
    return null;
}

Log::channel('anticaptcha')->info("Captcha task created. Task ID: {$api->taskId}");

// Poll for result (max 120 seconds)
$solved = $api->waitForResult(120);

if (!$solved) {
    Log::channel('anticaptcha')->error("Captcha resolution failed. Error Code: {$api->errorCode}, Error: {$api->errorMessage}");
    return null;
}

$solution = $api->getTaskSolution();
Log::channel('anticaptcha')->info("Captcha solved successfully. Task ID: {$api->taskId}, Result: {$solution}");
```

## Constraints
- **Do NOT** commit the API key (`ANTICAPTCHA_KEY`) to Git. Keep it in the `.env` file.
- **Do NOT** use default logging channels for captcha logs; always write to `Log::channel('anticaptcha')`.
- **Do NOT** hardcode long sleep periods or infinite polling loops. Use `$api->waitForResult($maxSeconds)` with a sane timeout to prevent hanging Laravel worker processes or Octane threads.
