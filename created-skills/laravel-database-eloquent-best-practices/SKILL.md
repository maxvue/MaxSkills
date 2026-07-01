---
name: laravel-database-eloquent-best-practices
description: Use when writing, refactoring, or reviewing Laravel Eloquent queries, database migrations, indexing strategy, handling relationships, scopes, database transactions, concurrency optimization, or configuring model pruning and data retention policies.
---

# Laravel Eloquent & Database Best Practices

## Goal
Establish robust guidelines and structured patterns for optimizing Eloquent queries, preventing N+1 queries, using scopes, handling transactions and concurrency, and executing high-performance database operations within the Engeapp ecosystem.

## Instructions

### 1. Query Optimization & Eager Loading
- **Prevent N+1 Queries**: Always load required relationships using `with()`, `load()`, or `loadMissing()`. 
- **Selective Columns**: Specify only needed columns to keep memory usage low, including the primary key and foreign key (e.g., `Project::with('client:id,name,email')->get()`).
- **Pagination & Batch Loading**: Do NOT use `all()` or `get()` on tables with large volumes. Use `paginate()`, `cursorPaginate()`, `chunkById()`, `lazy()`, or `cursor()`.
- **Subqueries & Aggregations**: Use `addSelect()` for subqueries. Use `withCount()` or `withExists()` instead of loading full collections to check existence or count.
- **Strict Loading**: Ensure `Model::preventLazyLoading(! app()->isProduction())` is configured.
- **Jobs**: Remember models passed to Jobs lose loaded relationships. Call `$this->model->loadMissing(...)` inside `handle()`.
- **Strategic Indexing**: Define indexes on columns frequently used in `where`, `orderBy`, `join`, or foreign key constraints in migrations.

### 2. Eloquent Scopes & Dynamic Filtering
- **Local Scopes**: Prefix methods with `scope` (e.g., `scopeUnread`), type-hint `$query` as `Illuminate\Database\Eloquent\Builder`, and explicitly declare return type `: Builder`. Or use Laravel 11 `#[Scope]` attributes.
- **Documenting**: Write clear PHPDoc blocks above scopes in **Brazilian Portuguese (pt-BR)**.
- **Dynamic Scopes**: Accept parameters after the `$query` argument to customize constraints.
- **Global Scopes**: Define in `booted()` using `static::addGlobalScope` or extract to dedicated classes.
- **Filtering Pattern**: Replace long `if`/`switch` blocks in controllers with dynamic model filter scopes using the `when()` helper.
- **Constraints**: Do NOT perform termination methods (`get()`, `first()`, `paginate()`) inside scope methods. Do NOT omit type-hints.

### 3. Database Transactions & Concurrency Locks
- **Automatic Transactions**: Use `DB::transaction()` as default. It handles `commit`/`rollback` and allows specifying retry attempts.
- **Manual Transactions**: Use `DB::beginTransaction()`, `DB::commit()`, and `DB::rollBack()` only for complex flows. Always wrap in `try-catch`.
- **Pessimistic Locking**: Use `lockForUpdate()` (Exclusive) to prevent rows from being modified or selected with shared lock. Use `sharedLock()` to prevent modifications but allow reading. Always use within transactions.
- **Deadlock Retries**: Specify a retry count as the second argument in `DB::transaction(..., 3)`.
- **Post-Commit Actions**: Never dispatch queue jobs, trigger events, or call external APIs inside a transaction block before it commits. Use `afterCommit` property or method on Jobs.

### 4. Concurrency Execution
- **Parallel Processing**: Use `Concurrency::run` to execute an array of closures in parallel. Use `Concurrency::defer` for fire-and-forget tasks.
- **Drivers**: Explicitly specify the driver (`process`, `fork`, `sync`) via `Concurrency::driver()`.
- **Timeouts**: Always enforce strict timeouts on concurrent tasks (`timeout: 10`).
- **Exception Handling**: Wrap blocks in `try-catch` catching `Illuminate\Concurrency\Exceptions\ExecutionException`.
- **State Management**: Do not mutate class properties or singletons inside closures. Closures serialize variables; keep imported scopes small (pass scalar IDs, not Eloquent models).
- **Constraints**: NEVER modify static variables or app config state inside closures. NEVER execute database transactions wrapping a `Concurrency::run` call.

### 5. Model Pruning & Data Retention
- **Choosing the Right Trait**:
  - Use `Prunable` when the model has associated resources requiring cleanup via model events or observers (e.g., deleting files from Spatie MediaLibrary, dispatching cleanup jobs on `deleting`/`deleted`).
  - Use `MassPrunable` when deleting large volumes of data where performance is critical and no model events, observers, or cascade cleanups are needed.
- **Defining the `prunable` Method**: Always declare return type (`: Builder`). Return a query builder defining obsolete record criteria.
  ```php
  public function prunable(): Builder
  {
      return static::where('created_at', '<=', now()->subMonths(3));
  }
  ```
- **Pruning Hook** (only with `Prunable`): Optionally define a `pruning(): void` method, called before EACH model is pruned, for side effects/cleanup (e.g., `Storage::disk('s3')->delete($this->file_path)`). The `MassPrunable` trait also uses `prunable()` but does NOT invoke the per-model `pruning()` hook.
- **Scheduling in `routes/console.php`**: Run `Schedule::command('model:prune')->daily()`. For tables with extreme volume, schedule at off-peak hours: `->dailyAt('03:00')`.
- **Database Optimization**: Index columns used in `prunable()` (typically `created_at`) to prevent full-table scans. Use `--chunk` for huge tables to avoid memory exhaustion or long locks.

## Constraints
- Do NOT run queries inside loops.
- Do NOT write class-level comments or scope descriptions in English. Always use pt-BR.
- All code comments inside PHP examples must be strictly written in Brazilian Portuguese (pt-BR).
- Do NOT use `Prunable` on models deleting thousands of records daily without event requirements — use `MassPrunable` instead.
- Do NOT schedule intensive pruning commands during peak business hours.
