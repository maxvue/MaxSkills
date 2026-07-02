---
name: laravel-telescope-debugging-best-practices
description: Use when configuring, optimizing, or using Laravel Telescope in development or local environments to debug database queries, request payloads, jobs, exceptions, commands, or cache hits and misses. Triggers on telescope configuration, filtering entries, environment setup, and telemetry performance analysis.
---

# Goal
Provide consistent guidelines and best practices for configuring, optimizing, and using Laravel Telescope inside the Engeapp ecosystem. This ensures efficient local telemetry and debugging without degrading database performance or leaking sensitive data.

# Instructions

## 1. Local Environment and Installation
* **Environment Restriction:** Telescope is primarily designed for development. Restrict its loading to the local environment inside the `register` method of `TelescopeServiceProvider`:
  ```php
  if ($this->app->environment('local')) {
      $this->app->register(\Laravel\Telescope\TelescopeServiceProvider::class);
      $this->app->register(TelescopeServiceProvider::class);
  }
  ```
* **Master Switch Control:** Toggle Telescope programmatically using the `TELESCOPE_ENABLED` environment variable in `.env`.

## 2. Watcher Configurations (`config/telescope.php`)
* **Query Watcher (`QueryWatcher`):**
  - Set the `'slow'` threshold to `100` milliseconds to identify performance bottlenecks.
  - Enable `'ignore_packages' => true` to ignore framework and package queries, focusing solely on application database operations.
* **Model Watcher (`ModelWatcher`):**
  - Keep `'hydrations'` enabled (`true`) only when debugging memory leaks or specific Eloquent behavior, as it introduces substantial overhead during large database operations.
* **Request Watcher (`RequestWatcher`):**
  - Adjust `'size_limit'` (default `64` KB) to prevent excessively large payload responses from bloating the database.

## 3. Data Pruning and Storage Optimization
* **Database Size Management:** Telescope tables (`telescope_entries`, `telescope_entries_tags`, etc.) can grow rapidly.
* **Pruning Schedule:** Always schedule the prune command in `routes/console.php` (Laravel 11+) or `app/Console/Kernel.php`:
  ```php
  use Illuminate\Support\Facades\Schedule;

  Schedule::command('telescope:prune --hours=24')->daily();
  ```
* **Performance Offloading:** If query overhead becomes a bottleneck during local development, change the `TELESCOPE_DRIVER` to a lighter backend or selectively disable high-frequency watchers (like cache or query logs).

## 4. Security and Data Privacy
* **Sensitive Details Sanitization:** Ensure no private keys, passwords, or personal identifiable information (PII) are stored in telemetry logs.
* **Sanitization Configuration:** In `TelescopeServiceProvider.php`, use `hideSensitiveRequestDetails` to strip tokens and credentials:
  ```php
  Telescope::hideRequestParameters(['_token', 'password', 'password_confirmation', 'client_secret', 'private_key']);
  Telescope::hideRequestHeaders(['cookie', 'x-csrf-token', 'x-xsrf-token', 'authorization']);
  ```
* **Access Gate Restriction:** Restrict dashboard access in non-local environments by defining the `viewTelescope` gate in `TelescopeServiceProvider::gate()` using strictly verified email addresses or specific roles.

# Constraints
* Do not enable Telescope in production without active authorization gates and sensitive data filtering.
* Never log raw credentials, mTLS certificates, or database passwords in the Telescope request parameters or headers.
* Do not leave the `DumpWatcher` enabled on persistent shared staging environments.
* Never run migrations or test suites without ensuring Telescope is configured to run silently or disabled (`TELESCOPE_ENABLED=false`).

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
