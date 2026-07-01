---
name: laravel-task-scheduling-best-practices
description: Use when creating, configuring, auditing, or debugging Laravel task schedules (Schedule) in routes/console.php, managing cron jobs, preventing overlapping processes, configuring background executions, handling task outputs, logging scheduler errors, optimizing recurrent backend tasks, and configuring/maintaining Studio Totem for task management.
---

# Laravel Task Scheduling — Best Practices

## Goal
Establish solid guidelines and consistent patterns for scheduling, monitoring, concurrency control, and log management of background tasks in Laravel 13 (using the `Schedule` facade in `routes/console.php`) and Studio Totem.

## Instructions

### 1. Task Registration & Location
- Always register all scheduled tasks inside `routes/console.php` using the `Illuminate\Support\Facades\Schedule` facade.
- Do not define complex business logic or database queries inside the scheduler closures in `routes/console.php`.
- **Preferred Pattern:** Encapsulate the execution logic inside a dedicated Artisan Command (created via `php artisan make:command`) or a Queue Job, and then schedule it using:
  ```php
  use Illuminate\Support\Facades\Schedule;

  Schedule::command('system:cleanup-temp-files')->daily();
  Schedule::job(new CleanAbandonedCartsJob)->hourly();
  ```

### 2. Concurrency and Overlapping Prevention
- For commands that process substantial amounts of data or interface with external APIs, always prevent execution overlap to avoid server resource exhaustion and race conditions:
  ```php
  Schedule::command('sync:external-crm')
      ->hourly()
      ->withoutOverlapping(60); // Define a lock expiration time in minutes
  ```
- **Totem:** For sensitive operations via Totem UI, enable the **"Don't Overlap"** setting to apply native `.withoutOverlapping()` logic.
- Use `runInBackground()` when you have multiple scheduled commands executing at the same time and you want them to execute asynchronously rather than sequentially:
  ```php
  Schedule::command('reports:compile')->daily()->runInBackground();
  ```
- If the application runs in a multi-server load-balanced environment, ensure the command only executes on a single server by utilizing `onOneServer()` (requires a database or redis cache driver as the default cache store).

### 3. Log Management and Output Control
- **Output Redirection:** Never let the task outputs vanish. Always append standard outputs and error streams to dedicated log files or channel them to custom handlers.
- **Error Hooks:** Utilize failure and success callback hooks to log anomalies or trigger alerts.
- **Totem Database Log Cleanup (Retention Policy):** Totem logs every execution status and output in the `totem_task_results` table. Schedule the built-in Totem cleanup command to prevent database bloat:
  ```bash
  php artisan totem:cleanup --days=7
  ```

### 4. Execution Conditions & Environments
- Strictly enforce environment boundaries to prevent destructive tasks or mock updates from executing in production:
  ```php
  Schedule::command('test:reset-sandbox')
      ->daily()
      ->environments(['local', 'staging']);
  ```
- Use dynamic conditional constraints (`when()` or `skip()`) to determine execution dynamically.
- **Totem Environment Configurations:** Respect configurations inside `config/totem.php`. Use `.env` variables to toggle parameters across environments (`TOTEM_WEB_MIDDLEWARE`, `TOTEM_WEB_ROUTE_PREFIX`, `TOTEM_TABLE_PREFIX`, `TOTEM_DATABASE_CONNECTION`).

### 5. Totem Dashboard Security and Authentication
- The Laravel Totem dashboard is served at the route prefix specified by `TOTEM_WEB_ROUTE_PREFIX` (default is `/tasks`).
- Access must be strictly restricted. Implement route authorization in `AppServiceProvider.php` using `Totem::auth()` and the `viewTotem` gate:
  ```php
  use Studio\Totem\Totem;
  use Illuminate\Support\Facades\Gate;

  Gate::define('viewTotem', fn ($user) => $user->is_developer || in_array($user->email, $allowedEmails));

  Totem::auth(function () {
      $user = auth()->user();
      return $user && ($user->is_developer || in_array($user->email, $allowedEmails));
  });
  ```

### 6. Standard Artisan Command Design & External API Calls
- Any command registered in Totem or Laravel should define explicit, descriptive signatures.
- Return standard exit codes (`self::SUCCESS` or `0` for success; `self::FAILURE` or `1` for failures).
- **Avoiding Blocking:** Commands must not block execution indefinitely. If a command performs HTTP requests to external APIs, define explicit timeouts:
  ```php
  use Illuminate\Support\Facades\Http;
  Http::timeout(10)->get('https://api.external.service/data');
  ```
- For extremely heavy operations, decouple the command from the scheduler by dispatching a queued Job in background.

## Constraints
- **NEVER** write heavy processing, HTTP requests, or raw database queries directly inside `routes/console.php` closures. Always delegate to an Artisan command or a queue Job.
- **NEVER** omit `withoutOverlapping()` for cleanups or synchronization tasks that might take longer than their execution interval.
- **NEVER** run commands without specifying environment boundaries if they modify test data or mock external API integrations.
- **NEVER** use plain PHP `echo` or standard outputs within scheduler command closures; always utilize structured logging via `Log::channel()`.
- **NEVER** expose the `/tasks` (or configured prefix) dashboard route to the public. Secure it behind authentication gates.
- **NEVER** schedule a high-frequency command without configuring a corresponding log cleanup policy (`totem:cleanup`).
- **DO NOT** execute blocking third-party API calls inside scheduled commands without an explicit HTTP timeout.

## Examples

### Scheduling in routes/console.php
```php
<?php

use Illuminate\Support\Facades\Schedule;
use Illuminate\Support\Facades\Log;
use App\Jobs\CleanupInactiveUsersJob;

// 1. Artisan command scheduled with overlap protection and output logging
Schedule::command('geckodriver:cleanup-ports')
    ->everyFiveMinutes()
    ->withoutOverlapping(10)
    ->runInBackground()
    ->appendOutputTo(storage_path('logs/geckodriver-cleanup.log'))
    ->onFailure(function () {
        Log::channel('scheduler')->error('Geckodriver ports cleanup task failed.');
    });

// 2. Queue Job scheduled to run on a single server, restricted to production
Schedule::job(new CleanupInactiveUsersJob)
    ->dailyAt('02:00')
    ->onOneServer()
    ->environments(['production']);
```
