---
name: laravel-multitenancy-data-isolation-best-practices
description: Use when designing, reviewing, or debugging multi-tenant architectures, data isolation, query scopes, and tenant middleware in Laravel. Triggers on requests involving database filters by tenant id (e.g., solar_company_id, designer_solar_company_id), global Eloquent query scopes, and tenant context resolution.
---

# Laravel Multi-tenancy & Data Isolation Best Practices

## Goal
Establish robust, secure, and scalable guidelines for multi-tenant data isolation within Laravel applications. Ensure strict separation of client, project, and document data using global Eloquent query scopes, tenant resolution middleware, context managers, and Artisan/Job integration to prevent cross-tenant data leakage.

## Instructions

### 1. Tenant Context Management (TenantManager)
- Define a thread-safe singleton manager or utilize Laravel 11's `Context` facade to hold the active tenant state during the request/process lifecycle.
- Implement a helper or facade to get/set the active tenant ID (e.g., `UserSolarCompany` ID).
- Example:
  ```php
  namespace App\Services;

  use Illuminate\Support\Facades\Context;

  class TenantManager
  {
      public static function setTenantId(string $tenantId): void
      {
          Context::add('tenant_id', $tenantId);
      }

      public static function getTenantId(): ?string
      {
          return Context::get('tenant_id');
      }

      public static function hasTenant(): bool
      {
          return Context::has('tenant_id');
      }

      public static function forgetTenant(): void
      {
          Context::forget('tenant_id');
      }
  }
  ```

### 2. Tenant Resolution Middleware
- Create a middleware to resolve the active tenant from the authenticated user context (`auth()->user()->solar_company_id`) or custom headers.
- Set the resolved tenant ID in the `TenantManager` at the start of the request lifecycle.
- Example:
  ```php
  namespace App\Http\Middleware;

  use Closure;
  use App\Services\TenantManager;
  use Illuminate\Http\Request;
  use Symfony\Component\HttpFoundation\Response;

  class ResolveTenant
  {
      public function handle(Request $request, Closure $next): Response
      {
          if (auth()->check()) {
              $user = auth()->user();
              if ($user->solar_company_id) {
                  TenantManager::setTenantId($user->solar_company_id);
              }
          }

          return $next($request);
      }
  }
  ```

### 3. Reusable Tenant Traits and Global Scopes
- Create a reusable trait (e.g., `BelongsToTenant`) to be used in models that require tenant isolation.
- Automatically register a `TenantScope` and hook into the model's `creating` event to set the `solar_company_id` automatically.
- Example Trait:
  ```php
  namespace App\Traits;

  use App\Scopes\TenantScope;
  use App\Services\TenantManager;
  use App\Models\User\UserSolarCompany;

  trait BelongsToTenant
  {
      public static function bootBelongsToTenant(): void
      {
          static::creating(function ($model) {
              if (TenantManager::hasTenant() && ! $model->solar_company_id) {
                  $model->solar_company_id = TenantManager::getTenantId();
              }
          });

          static::addGlobalScope(new TenantScope);
      }

      public function tenant()
      {
          return $this->belongsTo(UserSolarCompany::class, 'solar_company_id');
      }
  }
  ```
- Example Global Scope (`TenantScope`):
  ```php
  namespace App\Scopes;

  use App\Services\TenantManager;
  use Illuminate\Database\Eloquent\Builder;
  use Illuminate\Database\Eloquent\Model;
  use Illuminate\Database\Eloquent\Scope;

  class TenantScope implements Scope
  {
      public function apply(Builder $builder, Model $model): void
      {
          if (TenantManager::hasTenant()) {
              $builder->where($model->getTable() . '.solar_company_id', TenantManager::getTenantId());
          }
      }
  }
  ```

### 4. Special Scopes (e.g., `designer_solar_company_id` / Projects)
- If some tables utilize alternative column names (like `designer_solar_company_id` in `Project` models), implement a custom trait (e.g., `BelongsToDesignerTenant`) or dynamically configure the column in the scope.
- Ensure the scope targets the correct column name on the correct database table to prevent SQL ambiguity during joins.

### 5. Tenant Isolation in Jobs and Horizon Queues
- Since background jobs run in a CLI context without sessions or HTTP request middleware, you must pass the tenant context explicitly to queued jobs.
- Inject the active tenant ID in the constructor of the job class and set the tenant context in the job's `handle()` method or via job middleware.
- Example Job:
  ```php
  namespace App\Jobs;

  use App\Services\TenantManager;
  use Illuminate\Bus\Queueable;
  use Illuminate\Contracts\Queue\ShouldQueue;
  use Illuminate\Foundation\Bus\Dispatchable;
  use Illuminate\Queue\InteractsWithQueue;
  use Illuminate\Queue\SerializesModels;

  class SyncProjectTelemetry implements ShouldQueue
  {
      use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

      protected string $tenantId;

      public function __construct(string $tenantId)
      {
          $this->tenantId = $tenantId;
      }

      public function handle(): void
      {
          TenantManager::setTenantId($this->tenantId);

          try {
              // Perform tenant-isolated database operations
          } finally {
              TenantManager::forgetTenant();
          }
      }
  }
  ```

### 6. Validation and Policies
- Utilize Laravel Form Requests and Policies to double-check that users cannot request or update resources belonging to a different tenant.
- Example Policy validation:
  ```php
  public function update(User $user, Project $project): bool
  {
      return $user->solar_company_id === $project->designer_solar_company_id;
  }
  ```

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **No Hardcoded/Manual Tenant Filtering:** Avoid querying with manual `->where('solar_company_id', ...)` filters. Rely on the `BelongsToTenant` trait and its global scope to prevent developer oversight and data leakage.
- **Tenant Context Restoration:** Always clear or restore the tenant context at the end of background jobs, Artisan commands, or test executions to avoid memory leaks or context contamination between consecutive jobs (especially under Octane).
- **Explicit Scope Bypassing:** Restrict bypassing of the tenant scope using `withoutGlobalScope(TenantScope::class)` to system-level operations, administrative dashboards, or explicitly approved cross-tenant console commands. Document all instances of scope bypassing.
- **Database Schema Constraints:** All tenant-specific tables must have indexed `solar_company_id` (or similar) foreign keys defined as `NOT NULL` with appropriate cascade rules in their migrations.
