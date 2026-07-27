---
title: Security — Input, Output, Passwords, SQL, Uploads
impact: CRITICAL
impactDescription: Root causes of injection, XSS, credential compromise, and file-upload RCE
tags: security, validation, xss, sql-injection, passwords, file-uploads, laravel
---

# Security — Input, Output, Passwords, SQL, Uploads

No engeapp (Laravel 13 / PHP 8.4), estas cinco preocupações de segurança são resolvidas pela camada do framework, não por PHP cru (`$_POST`, `new PDO`, `move_uploaded_file`, `password_hash()` diretos). Use a cobertura completa e já correta em:

- `created-skills/backend_laravel/laravel-best-practices/rules/security.md` — Mass Assignment, autorização, SQL injection, CSRF, upload de arquivos
- `created-skills/backend_laravel/laravel-security-hardening-best-practices/` — hardening geral

Esta regra existe apenas como resumo de princípios e para o caso raro de código PHP fora do framework Laravel.

## Princípios (mapeados para a camada real do engeapp)

- **Validação de entrada**: FormRequest + `$request->validated()`, nunca `$request->all()` direto em `create()`/`update()`.
- **Escape de saída**: Blade escapa por padrão com `{{ }}` (nunca `{!! !!}` com conteúdo do usuário); no front Vue, evite `v-html` com dados não confiáveis.
- **SQL**: Eloquent/Query Builder já usam bindings parametrizados (`User::where('name', $value)`); nunca interpole input em `DB::select("...{$x}...")`.
- **Senhas**: `Hash::make()`/`Hash::check()` (bcrypt via config, nunca MD5/SHA1) — ver `app/Http/Controllers/Settings/PasswordController.php`, `Auth/RegisterUserController.php` no engeapp.
- **Upload de arquivos**: validação de tipo/tamanho via regras do FormRequest (`file`, `mimes`, `max`) e armazenamento via Spatie MediaLibrary/VueFinder — não `move_uploaded_file()` cru.
- **CSRF**: o engeapp é SPA (Vue Router, sem Sanctum); a proteção depende do cookie `XSRF-TOKEN` reenviado pelo axios em requisições estateful. Nota: há uma exceção real no projeto — `EfiWebhookController.php` lê `$_POST['notification']` como fallback de payload de webhook externo (não é input de usuário autenticado via form; é webhook de gateway de pagamento), então nem todo uso de superglobal no projeto é um erro a ser corrigido.

## Bad Example (fora do padrão do engeapp)

```php
// SQL injection
$result = mysqli_query($conn, "SELECT * FROM users WHERE id = " . $_GET['id']);

// Senha fraca
$hash = md5($password);

// Upload sem validação
move_uploaded_file($_FILES['file']['tmp_name'], '/var/www/uploads/' . $_FILES['file']['name']);
```

## Good Example (engeapp / Laravel)

```php
// Validação + SQL seguro via Eloquent
$user = User::where('id', $request->validated('id'))->firstOrFail();

// Senha
$user->update(['password' => Hash::make($request->validated('password'))]);

// Upload via FormRequest + MediaLibrary
// (regras: 'file' => 'required|file|mimes:pdf,jpg,png|max:10240')
$model->addMediaFromRequest('file')->toMediaCollection('documents');
```

## Why

- **Consistência**: reutiliza a mesma proteção que o framework já aplica em todo o projeto, em vez de reinventar em PHP cru
- **Sem duplicação**: a cobertura detalhada vive em `laravel-best-practices/rules/security.md` e `laravel-security-hardening-best-practices`
