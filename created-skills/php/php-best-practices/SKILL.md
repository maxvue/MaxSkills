---
name: php-best-practices
description: "Use when writing, refactoring, or reviewing PHP 8.5 code in Engeapp. Covers modern PHP patterns, PSR standards, strict typing, constructor property promotion, enums, and SOLID principles."
metadata: {'phpVersion': '8.4 (target atual do engeapp, pinado via composer platform 8.4.99) — notas de 8.5 incluídas apenas como cobertura antecipada para quando o piso subir'}
---
# PHP Best Practices

## Objetivo
Use when writing, refactoring, or reviewing PHP 8.5 code in Engeapp. Covers modern PHP patterns, PSR standards, strict typing, constructor property promotion, enums, and SOLID principles.

Modern PHP 8.x patterns, PSR standards, type system best practices, and SOLID principles. Contains 45 rules for writing clean, maintainable PHP code.

## Instruções

### Step 1: Detect PHP Version

**Always check the project's PHP version before giving any advice.** Features vary significantly across 8.0 - 8.5. Never suggest syntax that doesn't exist in the project's version.

Check `composer.json` for the required PHP version — this is the authoritative floor, including the `config.platform.php` pin when present:
```json
{ "require": { "php": "^8.1" } }   // -> 8.1 rules and below
{ "require": { "php": "^8.3" } }   // -> 8.3 rules and below
{ "require": { "php": ">=8.4" } }  // -> 8.4 rules and below
```

Also check the runtime version, as a secondary sanity check only:
```bash
php -v   # e.g. PHP 8.3.12
```

**Never use the local runtime's `php -v` to authorize syntax above the composer floor.** The composer requirement (and `config.platform.php` if pinned) is the only source of truth for which version the deployed code must run on — a developer's local PHP can be newer than production/CI. If they disagree, the composer floor wins.

### Feature Availability by Version

| Feature | Version | Rule Prefix |
|---------|---------|-------------|
| Union types, match, nullsafe, named args, constructor promotion, attributes | 8.0+ | `type-`, `modern-` |
| Enums, readonly properties, intersection types, first-class callables, never, fibers | 8.1+ | `modern-` |
| Readonly classes, DNF types, true/false/null standalone types | 8.2+ | `modern-` |
| Typed class constants, `#[\Override]`, `json_validate()` | 8.3+ | `modern-` |
| Property hooks, asymmetric visibility, `#[\Deprecated]`, `new` without parens | 8.4+ | `modern-` |
| Pipe operator `|>` | 8.5+ | `modern-` |

**Only suggest features available in the detected version.** If the user asks about upgrading or newer features, mention what becomes available at each version.

### When to Apply

Reference these guidelines when:
- Writing or reviewing PHP code
- Implementing classes and interfaces
- Using PHP 8.x modern features
- Ensuring type safety
- Following PSR standards
- Applying design patterns

### Rule Categories by Priority

| Priority | Category | Impact | Prefix | Rules |
|----------|----------|--------|--------|-------|
| 1 | Type System | CRITICAL | `type-` | 9 |
| 2 | Modern PHP Features | CRITICAL | `modern-` | 16 |
| 3 | PSR Standards | HIGH | `psr-` | 4 |
| 4 | SOLID Principles | HIGH | `solid-` | 5 |
| 5 | Error Handling | HIGH | `error-` | 5 |
| 6 | Performance | MEDIUM | `perf-` | 5 |
| 7 | Security | CRITICAL | `sec-` | 1 |

### Quick Reference

### 1. Type System (CRITICAL) — 9 rules

- `type-strict-mode` - Declare strict types (OPCIONAL no engeapp: 0/840 arquivos em `app/` usam; `pint.json` não exige — aplique só a código novo isolado, não a arquivos existentes do alvo)
- `type-return-types` - Always declare return types
- `type-parameter-types` - Type all parameters
- `type-property-types` - Type class properties
- `type-union-types` - Use union types effectively
- `type-intersection-types` - Use intersection types
- `type-nullable-types` - Handle nullable types properly
- `type-void-never` - Use void/never for appropriate return types
- `type-mixed-avoid` - Avoid mixed type when possible

### 2. Modern PHP Features (CRITICAL) — 16 rules

**8.0+:**
- `modern-constructor-promotion` - Constructor property promotion
- `modern-match-expression` - Match over switch
- `modern-named-arguments` - Named arguments for clarity
- `modern-nullsafe-operator` - Nullsafe operator (?->)
- `modern-attributes` - Attributes for metadata

**8.1+:**
- `modern-enums` - Enums instead of constants
- `modern-enums-methods` - Enums with methods and interfaces
- `modern-readonly-properties` - Readonly for immutable data
- `modern-first-class-callables` - First-class callable syntax
- `modern-arrow-functions` - Arrow functions (7.4+, pairs well with 8.1 features)

**8.2+:**
- `modern-readonly-classes` - Readonly classes

**8.3+:**
- `modern-typed-constants` - Typed class constants (`const string NAME = 'foo'`)
- `modern-override-attribute` - `#[\Override]` to catch parent method typos

**8.4+:**
- `modern-property-hooks` - Property hooks replacing getters/setters
- `modern-asymmetric-visibility` - `public private(set)` for controlled access

**8.5+ (cobertura antecipada — fora do alvo atual):**
- `modern-pipe-operator` - Pipe operator (`|>`) for functional chaining. **No engeapp o piso é `^8.4` / `platform.php: 8.4.99` — este recurso está fora do alvo hoje e não deve ser sugerido nesse projeto**, mesmo que o `php -v` do runtime local reporte 8.5+

### 3. PSR Standards (HIGH) — 4 rules

- `psr-4-autoloading` - Follow PSR-4 autoloading (engeapp: `App\ -> app/`, no `src/` layer)
- `psr-12-coding-style` - Follow PSR-12 coding style
- `psr-naming` - Class/method naming and namespace conventions (with `handle()`/`__invoke()` Laravel exception)
- `psr-file-structure` - One class per file; member ordering is convention, not PSR

### 4. SOLID Principles (HIGH) — 5 rules

- `solid-srp` - Single Responsibility: one reason to change
- `solid-ocp` - Open/Closed: extend, don't modify
- `solid-lsp` - Liskov Substitution: subtypes must be substitutable
- `solid-isp` - Interface Segregation: small, focused interfaces
- `solid-dip` - Dependency Inversion: depend on abstractions

### 5. Error Handling (HIGH) — 5 rules

- `error-custom-exceptions` - Create specific exceptions for different errors
- `error-exception-hierarchy` - Organize exceptions into meaningful hierarchy
- `error-try-catch-specific` - Catch specific exceptions, not generic \Exception
- `error-finally-cleanup` - Use finally for guaranteed resource cleanup
- `error-never-suppress` - Never use @ error suppression operator

### 6. Performance (MEDIUM) — 5 rules

- `perf-avoid-globals` - Avoid global variables, use dependency injection
- `perf-lazy-loading` - Defer expensive operations until needed
- `perf-array-functions` - Use native array functions over manual loops
- `perf-string-functions` - Use native string functions over regex
- `perf-generators` - Use generators for large datasets

### 7. Security (CRITICAL) — 1 rule

- `sec-input-handling` - Input validation, output escaping, password hashing, SQL, and uploads via the Laravel layer (FormRequest, Eloquent bindings, Hash::make, MediaLibrary) — pointer to `laravel-best-practices/rules/security.md` and `laravel-security-hardening-best-practices` for the full engeapp-specific coverage

### Rule Files

Cada regra listada no Quick Reference tem um arquivo próprio em `rules/<slug>.md` com exemplo ruim/bom e explicação. Abra o arquivo correspondente ao aplicar ou auditar um padrão — por exemplo `rules/type-strict-mode.md`, `rules/modern-constructor-promotion.md`, `rules/modern-enums.md`, `rules/solid-srp.md`. `rules/` é a fonte única da verdade; este SKILL.md apenas indexa.

### Output Format

When auditing code, output findings in this format:

```
file:line - [category] Description of issue
```

Example:
```
src/Services/UserService.php:15 - [type] Missing return type declaration
src/Models/Order.php:42 - [modern] Use match expression instead of switch
src/Controllers/ApiController.php:28 - [solid] Class has multiple responsibilities
```

## Restrições
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
