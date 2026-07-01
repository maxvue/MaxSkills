---
name: laravel-security-hardening-best-practices
description: Use when designing, reviewing, or debugging Laravel application security, securing Eloquent models (encryption, mass assignment), writing secure controllers, hardening file uploads, configuring security headers, or mitigating OWASP Top 10 vulnerabilities (SQLi, XSS, CSRF, IDOR).
---

# Laravel Security Hardening Best Practices

## Goal
Establish robust security guidelines and hardening practices for backend development in the Laravel ecosystem of Engeapp. This prevents data leaks, mitigates OWASP Top 10 vulnerabilities, secures integrations, and ensures safe file handling.

## Instructions

### 1. Eloquent Model Security
- **Encryption of Sensitive Fields**: Use Laravel's built-in `'encrypted'` cast or custom encrypted casting for PII (Personally Identifiable Information) and third-party API keys/tokens. Always hide these columns using `$hidden` in the model.
- **Mass Assignment Protection**: Do not use `protected $guarded = [];`. Explicitly declare safe attributes in the `$fillable` array.
- **Strict Loading & Prevention of Lazy Loading**: Enforce strict model safety rules in `AppServiceProvider`.

### 2. Preventing SQL Injection (SQLi)
- **Parameterized Queries**: Always use Eloquent or query builder parameter bindings. Never concatenate user input directly into query strings (e.g., in `whereRaw`, `selectRaw`, `orderByRaw`, `DB::statement`).
- **Safe Raw Expressions**: If raw SQL is unavoidable, use methods that actually bind parameters: `DB::select('select * from users where id = ?', [$id])` for a raw SELECT, or array bindings on a query builder condition: `->whereRaw('id = ?', [$id])`. Note that `DB::raw()` is only an unescaped SQL fragment — it does **not** accept bindings and does **not** parameterize, so user input must NEVER be passed into it directly.

### 3. Mitigating IDOR (Insecure Direct Object References)
- **Scoped Route Model Binding**: Use scoped route model bindings where a child resource belongs to a parent. E.g., `Route::get('/projects/{project}/documents/{document}', ...)` will automatically ensure the document belongs to the project.
- **Strict Authorization via Policies & Gates**: Validate permissions on every resource access request. Always use `$this->authorize('view', $model)` or `Gate::authorize()` inside controller actions.
- **UUIDs/ULIDs for Public Identifiers**: Avoid exposing auto-incrementing integer IDs in URLs. Prefer ULIDs/UUIDs (like `HasUlids` trait) for model primary/route keys.

### 4. Input Sanitization & XSS Prevention
- **Blade Escaping**: Rely on Blade's double-curly braces `{{ $variable }}` which automatically escapes output using `htmlspecialchars`. Use `{!! $variable !!}` ONLY with verified, sanitized rich text and never with direct user input.
- **Form Requests**: Filter and sanitize input within dedicated Form Requests. Define strict validation rules (e.g., `email`, `url`, `integer`, `string`, `max`).

### 5. Secure File Uploads
- **Validation**: Enforce mime-type, extension, and file size checks. E.g., `required|file|mimes:pdf,jpg,png|max:10240`.
- **Storage**: Never store user-uploaded files in the public directory under their original name. Use `$request->file('doc')->store('homologations')` to automatically generate a secure unique filename.
- **Non-executable Paths**: Ensure uploaded files are stored in non-executable disks (e.g., S3/MinIO) or that the server configuration prevents executing scripts in the upload folder.

### 6. CSRF, CORS & Security Headers
- **CSRF Token Validation**: Ensure CSRF protection is active for all state-changing requests (POST, PUT, PATCH, DELETE). Only exempt webhooks (like external integration call-backs) under strict URL matching.
- **Secure Sessions**: Set `'secure' => true` and `'http_only' => true` in `config/session.php`.
- **CORS Config**: Limit origins, headers, and methods in `config/cors.php` to only those explicitly required.

### 7. Secure Exception Handling & Logging
- **Production Safety**: Ensure `app.debug` is `false` in production.
- **Sanitized Logs**: Mask credentials and secrets in logs. Do not log passwords, tokens, or personal identifiers in plain text. Use structured logging patterns.

## Constraints
- NEVER use unvalidated input in database queries or file system paths.
- NEVER leave `app.debug` enabled in production environments.
- NEVER bypass policies or authorize checks for convenience during database operations or API development.
- NEVER use raw string concatenation in SQL raw methods (`DB::raw()`, `whereRaw()`, etc.).
