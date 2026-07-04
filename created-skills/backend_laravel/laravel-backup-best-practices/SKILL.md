---
name: laravel-backup-best-practices
description: Use when configuring, executing, testing, or debugging backups in Laravel, setting up spatie/laravel-backup, managing backup destinations, defining backup schedules, or handling backup failure alerts.
---

# Laravel Backup Best Practices

## Goal
Establish solid, secure, and automated guidelines for backing up databases and application files within the Laravel ecosystem (specifically for Engeapp), ensuring business continuity and disaster recovery capabilities.

## Instructions

### 1. Installation & Initial Configuration
1. **Install Spatie Laravel Backup:**
   If the package is not installed, install it using Composer:
   ```bash
   composer require spatie/laravel-backup
   ```
2. **Publish Configuration:**
   Publish the package configuration file:
   ```bash
   php artisan vendor:publish --provider="Spatie\Backup\BackupServiceProvider"
   ```
   This generates `config/backup.php`.

### 2. Backup Configuration (`config/backup.php`)
1. **Source Configuration (`backup.source`):**
   - **Database:** Ensure all relevant database connections are selected (typically `mysql` or `pgsql`).
   - **Files:** Limit backups to essential files, such as dynamic user uploads (e.g., `storage/app/public`). Exclude `node_modules/`, `vendor/`, `storage/framework/`, and cache directories to reduce file size.
2. **Destination Configuration (`backup.destination`):**
   - Configure disks for backup storage. Avoid storing backups only on the same server (`local` disk).
   - Use external destinations such as AWS S3 (`s3`) or WebDAV (`webdav`).
   - Retrieve all disk credentials strictly from environment variables (`.env`).
3. **Retention Policies (`backup.cleanup`):**
   - Define a clean-up strategy to automatically remove old backups and prevent storage exhaustion.
   - Recommended policy: Keep daily backups for 7 days, weekly backups for 4 weeks, monthly backups for 4 months, and yearly backups for 2 years.

### 3. Backup Scheduling
1. **Artisan Commands:**
   - Run clean-up: `php artisan backup:clean`
   - Run backup: `php artisan backup:run` (or `--only-db` to backup only the database).
2. **Console Scheduler:**
   - Register the commands in `routes/console.php` (Laravel 11+) or `app/Console/Kernel.php`:
     ```php
     use Illuminate\Support\Facades\Schedule;

     // Clean old backups daily at 1:00 AM
     Schedule::command('backup:clean')->daily()->at('01:00');

     // Run database and file backup daily at 2:00 AM
     Schedule::command('backup:run')->daily()->at('02:00');
     ```
   - Alternatively, configure these tasks via **Laravel Totem** dashboard.

### 4. Logging & Notifications
1. **Structured Exception Logging:**
   - Integrate Spatie Backup notifications with notification channels (Mail, Slack, Discord, or Telegram) by configuring `backup.notifications` inside `config/backup.php`.
   - Ensure Laravel's logging configuration (`config/logging.php`) records backup status and failures using structured context (e.g., including storage disk and backup size).
2. **Monitoring Health:**
   - Run `php artisan backup:monitor` periodically or schedule it to ensure backup files are fresh and destinations are accessible.

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **Security:** Do not write or commit credentials, AWS keys, or WebDAV passwords directly into `config/backup.php` or `config/filesystems.php`. Use `.env` and `env()` helpers instead.
- **Privacy:** Never include sensitive runtime environment files (like `.env`) or private keys (`oauth-private.key`) in the backup zip. Exclude them explicitly in `config/backup.php`.
- **Location:** Do not store backups in the `public/` directory or any web-accessible path.
- **Resource Management:** Avoid running full file backups during peak system usage hours. Prefer late-night schedules for full backups.
