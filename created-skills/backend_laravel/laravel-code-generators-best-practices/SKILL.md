---
name: laravel-code-generators-best-practices
description: >-
  Use when generating or reviewing Laravel backend code (Models, Migrations,
  Controllers, Form Requests, Rules, Observers, Enums, DTOs, Middleware, Events,
  Mailables, Artisan Commands). Enforces strict typing, separation of concerns,
  correct routing, and database conventions for the Engeapp ecosystem. Triggers
  on make:* Artisan generators, schema design, and backend scaffolding reviews.
---

# Laravel Code Generators & Best Practices

## Goal

Establish strict conventions, guidelines, and patterns for creating, modifying, and maintaining the various Laravel backend components in the Engeapp project. This ensures a unified architecture, proper separation of concerns, strong typing, and adherence to modern Laravel (v13+) best practices.

## Instructions

### 1. Models & Migrations

- **Models**:
  - **Reliese Model Generator**: To generate Eloquent models from the database schema, see the specific rules in [Reliese Models Generator Best Practices](references/reliese-models-generator.md). It explains how to separate Base files (generated) from App files (your business logic).
  - Include concise class-level PHPDocs in Brazilian Portuguese (pt-BR) and the `@mixin IdeHelper[ModelName]` annotation.
  - Run `php artisan ide-helper:models -M --nowrite` instead of manually writing auto-generated properties.
  - Explicitly define `$fillable`, `$hidden`, and `$casts`.
  - Always declare return types for Eloquent relationships (e.g., `: BelongsTo`).
  - Use custom casts (e.g., mapping to Spatie Data classes) and register them in `$casts`.
- **Migration Generation (`kitloong/laravel-migrations-generator`)**:
  - Ignore temporary/log tables with `--ignore`. Use `--squash` to consolidate legacy schemas.
  - Run with `--default-index-names --default-fk-names` to enforce defaults.
- **Migration Creation**:
  - Always wrap creation logic in `if (Schema::hasTable('table_name')) { return; }`.
  - Use ULID `char('id', 26)->primary()` for primary keys by default.
  - Separate foreign keys into their own migration files (`..._add_foreign_keys_to_table.php`) wrapped in a try-catch.
  - Provide a valid rollback routine in `down()`.
- **Seeders & Factories**:
  - Place factories in `database/factories/` and seeders in `database/seeders/`.
  - Use the `fake()` helper and define relationships via standard factory bindings.
  - Define explicit factory states with `$this->state()` and `static` return types.
- **Observers**:
  - Generate via `php artisan make:observer {Name}Observer --model={Name}` and register in `AppServiceProvider`.
  - Avoid running heavy logic or external HTTP requests synchronously; dispatch background Jobs (with `afterCommit()`).
  - Avoid infinite loops during `updated`/`saved` by using `$model->saveQuietly()`.
- **Custom Casts**:
  - Implement `Illuminate\Contracts\Database\Eloquent\CastsAttributes`.
  - Ensure graceful handling of null database values in the `get` method. No database queries inside casts.

### 2. Controllers

- **API Controllers**:
  - For detailed patterns on creating and refactoring API Controllers (ensuring thin Controllers, Form Requests, and Resources), consult the reference guide: [API Controller Best Practices](references/api-controller-creator.md).
  - Keep controllers thin. They should only route requests, call services/actions, and return responses.
  - Use Form Requests for validation; never use `$request->validate([...])` inside controllers.
  - Use API Resources (`JsonResource`) or DTOs for responses. Do not return raw models/collections.
- **API Controllers (SPA)**:
  - O front Vue é uma SPA pura servida por rota catch-all; o Laravel **não** renderiza páginas. Os controllers expõem apenas dados em JSON, em `app/Http/Controllers/Api/` (ou na convenção de API do projeto), consumidos no Vue por stores `@maxvue/max-pinia` (MaxPinia).
  - Retorne os dados de página (incluindo dados de sub-page/tabs e itens de menu) como JSON via API Resources/DTOs. **NÃO** renderize páginas no backend nem use wrappers de renderização server-side.
  - "Container pages", "sub-page tabs" e "active menu states" são responsabilidade do front: a navegação e as URLs são resolvidas no Vue Router (com Ziggy via `route()`), e o estado de tab/menu ativo vive na store MaxPinia — o backend só fornece os dados.
  - Ensure data is eager-loaded (to avoid N+1 queries) and handle fallbacks/redirects when data is missing.

### 3. Form Requests & Validation Rules

- **Form Requests**:
  - Generate via `php artisan make:request`.
  - Declare return types explicitly: `public function authorize(): bool` and `public function rules(): array`.
  - Use fluent rule objects in array notation (e.g., `['required', 'email', Rule::unique('users')->ignore($this->route('user'))]`). No pipe-delimited (`|`) strings.
  - Prepare data inside `prepareForValidation()` and transform afterward via `passedValidation()`.
- **Custom Validation Rules**:
  - Generate via `php artisan make:rule RuleName`. Implement `Illuminate\Contracts\Validation\ValidationRule`.
  - Failure handling uses the `$fail` closure with translation keys (e.g., `$fail('validation.custom.key')->translate();`). Do not return booleans.
  - Write dedicated unit and feature tests (e.g., Pest) for the rules.

### 4. Enums & DTOs

- **Enums**:
  - Store in `app/Enums`. Define as backed enums (`: string` or `: int`).
  - Use the Spatie TypeScript Transformer `#[TypeScript]` attribute for frontend integration.
  - Run `php artisan typescript:transform` when modifying Enums or DTOs to sync frontend types.
- **Data Transfer Objects (Spatie Laravel Data)**:
  - To understand how to handle Lazy declarations, DataCollectionOf, DTO validations, and TypeScript typing, consult the full guide: [Data DTO Best Practices](references/data-dto-creator.md).
  - Keep DTOs in `app/Data/` with the `Data` suffix.
  - Use PHP 8 Constructor Promotion.
  - For Eloquent relationships, use `Spatie\LaravelData\Lazy` to avoid N+1 problems. Use `#[DataCollectionOf(RelatedData::class)]` for collections.
  - Do not include database persistence logic inside DTOs.

### 5. Middleware

- **Creation & Registration**:
  - Generate via `php artisan make:middleware`.
  - Inject dependencies via PHP 8 constructor promotion. Keep middleware stateless for Octane compatibility.
  - Register global, group, or alias middleware in `bootstrap/app.php` (Laravel 13 approach) instead of `Kernel.php`.

### 6. Events & Broadcasting

- **Creation & Connections**:
  - Events that use broadcasting must implement `ShouldBroadcast` or `ShouldBroadcastNow`.
  - Implement `broadcastConnections(): array` returning `['reverb']`.
- **Channels & Payloads**:
  - Define `broadcastOn()` returning an array of Channels (prefer `PrivateChannel`).
  - Restrict the payload in `broadcastWith()` instead of sending full models.
  - Authorize private channels in `routes/channels.php` with the `User $user` type and `: bool` returns.
- **Frontend**:
  - Use the `useEcho` composable from `@laravel/echo-vue` in the Vue 3 Composition API to automatically handle listening and cleanup.

### 7. Mailables & Notifications

- **Mailables**:
  - Use the modern syntax: implement `envelope()` and `content()`. Avoid the legacy `build()`.
  - Inject dependencies in the constructor via property promotion. Use the `SerializesModels` trait.
  - For asynchronous email, implement `ShouldQueue` and specify a queue (e.g., `public $queue = 'emails';`).
- **Notifications**:
  - Return channels in `via()`. Use `ShouldQueue`.
  - Define `toDatabase()`, `toMail()`, etc., returning clean serializable arrays or `MailMessage` objects.

### 8. Artisan Commands

- **Creation & Practices**:
  - For console I/O guides (using Laravel Prompts), dependency injection via the container, and output formatting, consult the dedicated reference: [Artisan Command Creator](references/artisan-command-creator.md).
- **Definition & Attributes**:
  - Use PHP 8 attributes for `#[Signature]` and `#[Description]`.
  - Use `:` to group related commands.
- **Logic & Execution**:
  - The `handle()` method must return an `int` exit code (`self::SUCCESS`, `self::FAILURE`, `self::INVALID`).
  - Keep `handle()` focused on I/O. Extract business logic into Jobs, Services, or Actions.
  - Use the console helpers (`$this->info()`, `$this->error()`, `$this->table()`, `createProgressBar()`) for formatted user output.

## Constraints

- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- Do **NOT** use plain PHP functions such as `echo`, `print_r`, `$request->validate()`, inline raw queries, or pipe `|` validations.
- Keep controllers, routes, and observers thin. Avoid running external APIs synchronously without jobs.
- Code comments and PHPDocs **MUST** be written in Brazilian Portuguese (pt-BR) per the global user rules.
