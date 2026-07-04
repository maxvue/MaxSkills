---
name: laravel-activity-log-best-practices
description: Use when configuring, implementing, or debugging user activity logs, audit trails, or model change logs using spatie/laravel-activitylog. Triggers on tracking model events, storing custom log metadata, retrieving activity history for frontend views, and cleaning up old logs.
---

# Laravel Activity Log Best Practices

## Goal
Establish guidelines, conventions, and standards for user activity tracking, Eloquent model change auditing, and custom activity logging using the `spatie/laravel-activitylog` package in the Engeapp Laravel ecosystem. Ensure compliance with LGPD requirements, prevent N+1 query issues during log retrieval, and handle user impersonation events correctly.

## Instructions

1. **Eloquent Model Auto-Logging**:
   - Import the `LogsActivity` trait and the `LogOptions` class.
   - Implement the `getActivitylogOptions()` method to return a configured `LogOptions` object.
   - Always chain `logOnly(['field1', 'field2'])` to specify fields explicitly instead of using wildcard logging, preventing performance hits and unwanted logging of sensitive fields.
   - Use `logOnlyDirty()` to record only the changes made.
   - Customize the log name using `useLogName('model-name')` to ease filtering.
   - Set `dontSubmitEmptyLogs()` to avoid empty activity database inserts.
   - Example:
     ```php
     use Spatie\Activitylog\Traits\LogsActivity;
     use Spatie\Activitylog\LogOptions;

     class Client extends Model
     {
         use LogsActivity;

         public function getActivitylogOptions(): LogOptions
         {
             return LogOptions::defaults()
                 ->logOnly(['name', 'document', 'status'])
                 ->logOnlyDirty()
                 ->dontSubmitEmptyLogs()
                 ->useLogName('clients');
         }
     }
     ```

2. **Handling User Impersonation**:
   - Integrate with the `lab404/laravel-impersonate` package (see `laravel-user-impersonation-best-practices`).
   - If an admin is impersonating a user, capture the real impersonator's ID using `app('impersonate')->getImpersonatorId()` and save it in custom properties.
   - Example helper to record custom properties during model boot or manually:
     ```php
     activity()
         ->tap(function (Activity $activity) {
             if (app('impersonate')->isImpersonating()) {
                 $activity->setExtraProperty('impersonator_id', app('impersonate')->getImpersonatorId());
                 $activity->setExtraProperty('is_impersonated', true);
             }
         });
     ```

3. **Custom Activity Logging**:
   - For non-model lifecycle events (e.g., user login, export, API access), log manually using the `activity()` helper.
   - Chain methods explicitly: `performedOn()`, `causedBy()`, `withProperties()`, `log()`.
   - Example:
     ```php
     activity()
         ->causedBy(auth()->user())
         ->withProperties(['ip' => request()->ip(), 'browser' => request()->userAgent()])
         ->log('User logged in successfully.');
     ```

4. **Optimized Activity Retrieval**:
   - Always eager-load the `causer` and `subject` relationships when rendering activity logs to prevent N+1 query issues.
   - Use paginated queries for large log datasets.
   - Example:
     ```php
     $logs = Activity::with(['causer', 'subject'])
         ->where('log_name', 'clients')
         ->latest()
         ->paginate(15);
     ```

5. **Log Database Maintenance & Cleanup**:
   - Configure log retention policy in `config/activitylog.php` using `delete_records_older_than_days`.
   - Register the cleanup command `activitylog:clean` to run daily in the scheduler (`routes/console.php` in Laravel 13).
   - Example:
     ```php
     use Illuminate\Support\Facades\Schedule;

     Schedule::command('activitylog:clean')->daily()->at('03:00');
     ```

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- Do NOT use wildcard `logAll()` on models. Specify fields explicitly using `logOnly()`.
- Do NOT log sensitive information (e.g., passwords, credit card info, auth tokens) in model attributes or custom properties.
- Do NOT query activity logs without eager-loading `causer` and `subject` relations.
- Do NOT omit impersonation metadata when recording actions performed during impersonation sessions.
