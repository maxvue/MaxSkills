---
title: First-Class Callable Syntax
impact: MEDIUM
impactDescription: Concise callable references with IDE support
tags: modern-features, first-class-callables, closures, php81
---

# First-Class Callable Syntax

Use first-class callable syntax to create closures from callables (PHP 8.1+).

## Bad Example

```php
<?php

class StringProcessor
{
    public function toUpperCase(string $str): string
    {
        return strtoupper($str);
    }
}

// Old way - verbose Closure::fromCallable
$processor = new StringProcessor();
$upper = Closure::fromCallable([$processor, 'toUpperCase']);

// String-based callable - no IDE support, error-prone
$callback = [$processor, 'toUpperCase'];
array_map($callback, $strings); // Works but fragile

$trimmer = Closure::fromCallable('trim');
```

## Good Example

```php
<?php

class StringProcessor
{
    public function toUpperCase(string $str): string
    {
        return strtoupper($str);
    }
}

// Instance methods - concise and type-safe
$processor = new StringProcessor();
$upper = $processor->toUpperCase(...);

$strings = ['hello', 'world'];
$uppercased = array_map($upper, $strings); // ['HELLO', 'WORLD']

// Static methods
class DateFormatter
{
    public static function format(DateTimeInterface $date): string
    {
        return $date->format('Y-m-d');
    }
}

$formatDate = DateFormatter::format(...);
$formatted = array_map($formatDate, $dates);

// Built-in functions
$trim = trim(...);
$cleaned = array_map($trim, $dirtyStrings);

// Practical use: subscribing methods as event listeners
class UserController
{
    public function __construct(private EventDispatcher $dispatcher)
    {
        $this->dispatcher->subscribe('user.created', $this->onUserCreated(...));
    }

    private function onUserCreated(User $user): void
    {
        // Handle event
    }
}
```

## Why

- **Concise Syntax**: `$obj->method(...)` instead of `Closure::fromCallable()`
- **IDE Support**: Full autocompletion, refactoring, and navigation
- **Type Safety**: Closures maintain the callable's type signature
- **Refactoring Safe**: Renaming methods updates references automatically
- **Consistency**: Same syntax for instance, static, and global functions
