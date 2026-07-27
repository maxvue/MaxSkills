---
title: Type-Safe Enums
impact: CRITICAL
impactDescription: Provides type safety for constants, prevents invalid values
tags: modern-features, enums, type-safety, php81
---

# Type-Safe Enums

Enums (PHP 8.1+) provide type-safe constants with methods. They prevent invalid values, enable IDE autocompletion, and encapsulate related behavior. Always prefer enums over class constants for finite sets of values.

## Bad Example

```php
<?php

// Class constants - no type safety
class OrderStatus
{
    public const PENDING = 'pending';
    public const PROCESSING = 'processing';
    public const CANCELLED = 'cancelled';
}

// Anyone can pass invalid value
function updateStatus(string $status): void
{
    // 'invalid_status' would be accepted
}

updateStatus('typo'); // No error!
```

## Good Example

```php
<?php

// String-backed enum - for database/API values
enum OrderStatus: string
{
    case Pending = 'pending';
    case Processing = 'processing';
    case Shipped = 'shipped';
    case Delivered = 'delivered';
    case Cancelled = 'cancelled';

    public function label(): string
    {
        return match ($this) {
            self::Pending => 'Awaiting Processing',
            self::Processing => 'Being Prepared',
            self::Shipped => 'On the Way',
            self::Delivered => 'Delivered',
            self::Cancelled => 'Cancelled',
        };
    }

    public function canTransitionTo(self $newStatus): bool
    {
        return match ($this) {
            self::Pending => in_array($newStatus, [self::Processing, self::Cancelled], true),
            self::Processing => in_array($newStatus, [self::Shipped, self::Cancelled], true),
            self::Shipped => $newStatus === self::Delivered,
            self::Delivered, self::Cancelled => false,
        };
    }
}

// Usage
$status = OrderStatus::Pending;
$status->value;   // 'pending'
$status->name;    // 'Pending'
$status->label(); // 'Awaiting Processing'

// From database/API value
$status = OrderStatus::from('pending');    // OrderStatus::Pending
$status = OrderStatus::tryFrom('invalid'); // null (no exception)

// Type safety in function signatures - invalid values rejected
function updateOrderStatus(Order $order, OrderStatus $newStatus): void
{
    if (!$order->status->canTransitionTo($newStatus)) {
        throw new InvalidStatusTransitionException($order->status, $newStatus);
    }

    $order->status = $newStatus;
}
```

### In Eloquent/Database

```php
<?php

// Model with enum casting
class Order extends Model
{
    protected $casts = [
        'status' => OrderStatus::class,
    ];
}

// Query with enum
Order::where('status', OrderStatus::Pending)->get();

// Validation rule
'status' => ['required', new Enum(OrderStatus::class)],
```

## Why

- **Type Safety**: Invalid values caught immediately (TypeError)
- **IDE Support**: Autocompletion and refactoring support
- **Encapsulation**: Related behavior lives with the data (methods)
- **Match Expressions**: Natural pairing with exhaustive match
- **Database Integration**: Backed enums map to DB values; `from()`/`tryFrom()` convert raw values safely
