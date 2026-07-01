---
name: laravel-performance-and-profiling-best-practices
description: Use when configuring, optimizing, debugging, or reviewing Laravel debugging/profiling tools like Clockwork, Debugbar, LaraDumps, Telescope, Pulse, Log Viewer, and Pail real-time log tailing.
---

# Laravel Performance and Profiling Best Practices

## Goal
Establish standard guidelines for debugging, profiling, inspecting, and optimizing application performance using various tools within the Engeapp Laravel ecosystem, ensuring security, developer productivity, and preventing data leaks.

## Instructions

### 1. Pulse Performance Monitoring
- **Security & Auth**: Define custom authorization for production using `Pulse::user()`. Restrict to administrators. Do NOT expose `/pulse` publicly without strict middleware.
- **Configuration**: Use `redis` ingest driver in high-traffic environments to offload workers. Configure a shorter storage window if database grows quickly.
- **Recorders & Aggregation**: Create custom recorders for business operations. Identify slow queries (>1000ms) and Redis cache hit/miss rates via the dashboard.

### 2. Clockwork Profiling
- **Environment**: Enable ONLY in local/staging (`CLOCKWORK_ENABLE=true`). Set to `false` in production. Do not use in Pest/PHPUnit tests.
- **Custom Timelines**: Use `clockwork()->startEvent('id', 'desc')` and `clockwork()->endEvent('id')` to measure exact execution times of complex operations. Close in a `finally` block.
- **Telemetry & Logging**: Monitor Database (N+1 issues), Cache, and Memory usage tabs. Use `clock()->info('Msg')` or `clockwork()->log()` for seamless logging. Do not pass massive binary data.
- **Cleanup**: Remove temporary `clock()` markers before creating a PR.

### 3. LaraDumps Debugging
- **Primary Tool**: Use `ds()` instead of `dd()`, `dump()`, or `print_r()`. Label and color output.
- **Features**: Monitor queries (`ds()->queriesOn()`), time (`ds()->time()`), models (`ds()->model()`).
- **Etiquette**: Remove all `ds()` statements before committing. NEVER commit active `ds(...)` helpers. Use `config/laradumps.php` vars to toggle.

### 4. Laravel Debugbar CLI
- Use for inspecting and debugging via CLI without a browser.
- **Commands**: Locate requests (`debugbar:find`), inspect details (`debugbar:get --collector=time`), inspect queries (`debugbar:queries`), and clear storage (`debugbar:clear`).
- **Constraint**: Do NOT dry-run `--result` via Debugbar for mutation queries (`INSERT`, `UPDATE`, `DELETE`) in production.

### 5. Laravel Telescope
- **Watchers**: Customize `config/telescope.php`. Set thresholds (`'slow' => 100`). Disable `hydrations` in `ModelWatcher` locally.
- **Pruning & Security**: Clean data via scheduler (`telescope:prune`). Filter sensitive data (passwords, tokens, CVVs) in `TelescopeServiceProvider`. Restrict production access using Gates. Never commit Telescope dumps.

### 6. Laravel Log Viewer
- **Securing Access**: Define a custom gate (`viewLogViewer`) in `AppServiceProvider`. Require auth in production.
- **Configuration**: Exclude framework frames in stack traces and secure sensitive logs via `exclude_files`. Use `log-viewer:clear-cache` to cleanse indexes.

### 7. Laravel Pail (Real-Time Log Tailing)
- **Launching**: Run `php artisan pail` in the terminal to stream new log entries instantly as they occur.
- **Filtering**:
  - By exception class: `php artisan pail --filter="App\Exceptions\ServiceIntegrationException"`
  - By authenticated user: `php artisan pail --user=42`
  - By message/content: `php artisan pail --message="Failed to send template"`
- **Verbosity**: `-v` (basic trace), `-vv` (context + stack trace), `-vvv` (full stack traces).
- **Structured Logs**: When using custom exceptions with contextual arrays (as in `laravel-exception-handling-logging`), Pail parses and displays the structured context beautifully in the terminal.
- **Etiquette**: Do NOT manually `grep` or `tail` the physical `laravel.log` when Pail can provide a cleaner, filterable stream.

## Constraints
- **No Production Exposure**: Never expose Clockwork, LaraDumps, or Telescope globally in production. Log Viewer and Pulse must be protected by auth gates.
- **No Sensitive Data Leaks**: Never log or dump sensitive user information, credentials, raw authorization tokens, or payment details. Filter such data appropriately.
- **Brazilian Portuguese Comments**: All code comments inside PHP examples must be strictly written in Brazilian Portuguese (pt-BR).
