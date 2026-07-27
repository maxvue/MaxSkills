---
title: Strict Types Declaration
impact: OPTIONAL
impactDescription: Prevents type coercion bugs, enforces type safety — not the convention in the engeapp target project
tags: type-system, strict-types, type-safety, php8
---

# Strict Types Declaration

`declare(strict_types=1)` enforces strict type checking for function arguments and return values. Without it, PHP silently coerces types, hiding bugs. Strict mode catches type errors early, improving code reliability.

**No engeapp (o alvo Laravel 13 / PHP 8.4 desta skill), esta regra NÃO se aplica:** 0 dos 840 arquivos PHP em `app/` usam `declare(strict_types=1)`, e o `pint.json` do projeto não configura a regra `declare_strict_types`. Trate esta regra como opcional — aplicável a código PHP novo isolado ou a outros projetos que já adotem strict types — e não a injete em arquivos existentes do engeapp nem a trate como CRITICAL nesse projeto.

## Bad Example

```php
<?php

// No strict types - silent coercion
function calculateTotal(int $price, int $quantity): int
{
    return $price * $quantity;
}

// These hide problems:
calculateTotal("10", "5");   // Returns 50 - numeric strings coerced to int
calculateTotal(10.99, 2);    // Returns 20 - float truncated to int (deprecated in 8.1)
// calculateTotal("abc", 2); // TypeError in PHP 8.0+ (non-numeric string)
```

## Good Example

```php
<?php

declare(strict_types=1);

// Strict types - TypeError on wrong types
function calculateTotal(int $price, int $quantity): int
{
    return $price * $quantity;
}

calculateTotal(10, 5);       // Returns 50
calculateTotal("10", "5");   // TypeError
calculateTotal(10.99, 2);    // TypeError
```

`declare(strict_types=1)` deve ser a primeira instrução do arquivo, antes até do `namespace`.

## Return Type Enforcement

```php
<?php

declare(strict_types=1);

function getPrice(): float
{
    return 99.99; // Must return float
}

// This would cause TypeError
function broken(): int
{
    return "42"; // TypeError - can't return string as int
}
```

## Why

- **Type Safety**: Catches type bugs at runtime immediately
- **No Surprises**: No silent type coercion
- **Static Analysis**: Works with PHPStan/Psalm for maximum safety
- **Não é o padrão do engeapp**: aplique apenas em código novo isolado ou em projetos que já adotem a convenção — não injete em arquivos existentes do alvo Laravel
