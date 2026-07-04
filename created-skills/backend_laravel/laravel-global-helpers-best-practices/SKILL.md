---
name: laravel-global-helpers-best-practices
description: Use when creating, modifying, refactoring, or testing global helper functions (Helpers) or utility classes in the Laravel backend. Triggers on helper autoload, global function declarations, and custom utility utilities.
---

# Laravel Global Helpers and Utility Classes Best Practices

## Goal
Establish clean, modular, stateless, and fully-tested patterns for creating, maintaining, and refactoring global helper functions and static utility classes in the Laravel backend of the Engeapp ecosystem.

## Instructions

### 1. Architectural Choice: Static Utility Class vs. Global Helper Function
To maintain a clean global namespace and ensure excellent IDE autocompletion, prioritize:
- **Static Utility Classes** under a namespace (e.g., `App\Helpers\StringHelper::capitalize()`) for complex logic, domain-specific utilities, or collections of related methods.
- **Global Helper Functions** (e.g., `capitalize()`) only when the utility is highly generic, frequently used across multiple contexts (Views, Controllers, Service classes), and directly improves readability.

### 2. Naming Conventions and Directory Structure
- **Static Utility Classes**:
  - File path: `app/Helpers/ClassUtilityName.php` (singular, PascalCase, ending in `Helper` or `Utility`, e.g., `App\Helpers\MathUtility.php`).
  - Class name: `ClassUtilityName` matching the filename.
  - Method names: camelCase (e.g., `public static function formatBrl()`).
- **Global Helper Function Files**:
  - File path: `app/Helpers/DomainHelpers.php` (plural, PascalCase, ending in `Helpers.php`, e.g., `app/Helpers/StringHelpers.php`).
  - Function names: snake_case (e.g., `format_cnpj()`).
  - Note: Inconsistencies like `numbersHelper.php` (mixed casing) are strictly prohibited for new files.

### 3. Protection Against Collisions
All global function declarations **MUST** be wrapped in a `function_exists` check to prevent fatal errors due to name collisions or multiple file loadings:
```php
if (! function_exists('format_cnpj')) {
    /**
     * Formats a raw string into a standard CNPJ format (99.999.999/9999-99).
     *
     * @param string|null $cnpj
     * @return string
     */
    function format_cnpj(?string $cnpj): string
    {
        // Implementation
    }
}
```

### 4. Stateless Design & Laravel Octane Compatibility
Because Laravel Octane (FrankenPHP) boots the application once and keeps it in memory across requests, all helper code must be 100% stateless:
- **NO** static properties that store state inside utility classes.
- **NO** static variables inside helper functions that preserve values between invocations.
- Do not inject stateful service instances or requests into the constructor or keep reference in static variables.
- Pass required state explicitly via function arguments, or use Laravel's `Context` facade if request-bound contextual metadata is required.

### 5. Registering Global Helpers via Composer
To register new files containing global functions, add them to the `autoload.files` array in `composer.json`:
```json
"autoload": {
    "files": [
        "app/Helpers/MyNewHelpers.php"
    ]
}
```
After modifying `composer.json`, run `composer dump-autoload` to update the autoloader.

### 6. Testing Helpers with Pest
Every helper function and static utility method must be fully covered by unit tests:
- Create unit tests in `tests/Unit/Helpers/` (e.g., `tests/Unit/Helpers/StringHelpersTest.php`).
- Group test assertions using Pest `test()` or `it()` blocks.
- Verify both valid input formats, boundary cases, null values, and incorrect formats (robustness).
Example:
```php
test('format_cnpj formats raw numbers correctly', function () {
    expect(format_cnpj('12345678000199'))->toBe('12.345.678/0001-99');
});
```

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **NEVER** define a global helper function without wrapping it in a `if (! function_exists(...))` block.
- **NEVER** use static state variables or static class properties to preserve state across requests.
- **NEVER** use generic names that might collide with Laravel's built-in helper functions (e.g., `array_get`, `collect`, `request`). Always check the Laravel Helpers documentation before creation.
- **NEVER** create raw helper files without strict PHP 8 parameter typing and explicit return types.
