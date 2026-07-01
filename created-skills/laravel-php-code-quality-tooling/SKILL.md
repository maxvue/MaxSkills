---
name: laravel-php-code-quality-tooling
description: Use when formatting, statically analyzing, or automatically refactoring PHP code in the Engeapp backend. Triggers on running Laravel Pint before commits, resolving Larastan/PHPStan type errors, configuring phpstan.neon, running Rector dry-runs, upgrading code to PHP 8.4+ or Laravel 13 conventions, or setting up IDE autocomplete with Barryvdh IDE Helper.
---

# Laravel PHP Code Quality Tooling

## Goal
Establish solid guidelines and safe execution patterns for the Engeapp backend PHP code quality pipeline: formatting with Laravel Pint, static analysis with Larastan/PHPStan, automated refactoring with Rector, and IDE autocomplete setup with Barryvdh IDE Helper. These tools form the standard pre-commit and upgrade toolchain.

## Instructions

### 1. Laravel Pint — Code Formatting
- **Execution**: Always run before finalizing changes:
  ```bash
  vendor/bin/pint --dirty --format agent
  ```
- **`--dirty` flag**: Only formats files with uncommitted Git changes. Protects historical commits and avoids mass diffs on unrelated files. Always use it.
- **Pipeline order**: Run Pint **after** Rector (to clean up formatting irregularities from automated refactoring) and **before** Larastan (to ensure style fixes don't introduce syntax issues).
- **Style preset**: Follow rules in `pint.json`. Do NOT override unless instructed by the user.
- **Constraints**: Never run Pint without `--dirty` on the entire codebase. Never commit modified PHP files without running Pint first.

### 2. Larastan/PHPStan — Static Analysis
- **Configuration (`phpstan.neon`)**:
  ```neon
  parameters:
      level: 1
      paths:
          - app/
      tmpDir: bootstrap/cache/phpstan
      scanFiles:
          - _ide_helper_models.php
      excludePaths:
          - vendor/*
      ignoreErrors:
          - '#has no type specified in iterable type#'
  ```
- **Execution**: `vendor/bin/phpstan analyse`
- **IDE Helper integration**: Do NOT inject PHPDoc annotations directly into model classes. Always generate them to a separate file:
  ```bash
  php artisan ide-helper:models -M --nowrite
  ```
  Add `@mixin IdeHelperUser` in the model's PHPDoc block so IDEs and Larastan can link to the generated helper.
- **Relationship generics**: Explicitly type relationship return types:
  ```php
  /** @return HasMany<PlannerCard, $this> */
  public function cards(): HasMany { ... }
  ```
- **Common fixes**:
  - Undefined property/method on models → ensure `@mixin IdeHelper[Model]` is present and `_ide_helper_models.php` is up to date.
  - Type mismatch from `$request->input()` → cast explicitly: `/** @var string $email */ $email = $request->input('email');`
- **Constraints**: Never downgrade below level `1`. Never add inline `@phpstan-ignore` without first attempting to fix the type structure. If suppression is necessary, add it to `ignoreErrors` in `phpstan.neon` with an exact regex.

### 3. Rector — Automated Refactoring
- **Configuration (`rector.php`)**:
  ```php
  return static function (RectorConfig $rectorConfig): void {
      $rectorConfig->paths([__DIR__ . '/app', __DIR__ . '/routes', __DIR__ . '/database', __DIR__ . '/tests']);
      $rectorConfig->ruleWithConfiguration(RemoveFuncCallRector::class, ['ds']);
      $rectorConfig->sets([SetList::DEAD_CODE, SetList::CODE_QUALITY, SetList::TYPE_DECLARATION]);
      $rectorConfig->skip([
          __DIR__ . '/_ide_helper.php',
          __DIR__ . '/_ide_helper_models.php',
          Rector\TypeDeclaration\Rector\Property\TypedPropertyFromAssignsRector::class,
      ]);
  };
  ```
- **Execution — always dry-run first**:
  ```bash
  vendor/bin/rector process --dry-run   # read-only check
  vendor/bin/rector process             # apply changes
  vendor/bin/rector process --clear-cache
  vendor/bin/rector process app/Http/Controllers/UserController.php --dry-run
  ```
- **Eloquent safety**: Do NOT let Rector add typed properties to models for relations or dynamic attributes. Preserve `@property` and `@mixin` annotations.
- **Spatie Data DTOs**: Keep constructor property promotion intact — do not allow Rector to decompose constructors that map to TypeScript models.
- **Octane safety**: Avoid Rector refactorings that introduce `static` properties or static caches inside services or controllers (causes request-to-request memory leaks).
- **Always run Pint after Rector** to maintain style consistency.

### 4. Barryvdh IDE Helper — Autocomplete Setup
- **Generate autocomplete metadata** (run after any significant model/facade changes):
  ```bash
  php artisan ide-helper:generate       # Facade helpers
  php artisan ide-helper:models -M --nowrite  # Model PHPDocs to separate file
  php artisan ide-helper:meta           # PhpStorm container bindings
  ```
- **Unified composer script**: `composer run format` executes Pint, all ide-helper commands, and TypeScript type transformations in one step.
- **Git**: Ensure `_ide_helper.php`, `_ide_helper_models.php`, and `.phpstorm.meta.php` are in `.gitignore` unless there is a project-specific reason to share them.
- **Constraints**: NEVER run `php artisan ide-helper:models` without `-M --nowrite`. NEVER commit models populated with autogenerated PHPDoc comments. Always pass `--no-interaction` in automated environments.

## Constraints
- Run tools in this order: **Rector → Pint → Larastan**.
- Do NOT apply Rector to `bootstrap/cache/`, `storage/`, `vendor/`, or `node_modules/`.
- Do NOT let Rector alter DTO constructor properties that map to frontend TypeScript models.
- Do NOT commit any PHP files without running Pint first.
- All code comments inside PHP examples must be strictly written in Brazilian Portuguese (pt-BR).
