---
title: Liskov Substitution Principle
impact: HIGH
impactDescription: Subtypes are substitutable, maintains polymorphism
tags: solid, lsp, design-principles, substitutability
---

# Liskov Substitution Principle (LSP)

Subtypes must be substitutable for their base types without altering correctness.

## Bad Example

```php
<?php

class Rectangle
{
    protected int $width;
    protected int $height;

    public function setWidth(int $width): void
    {
        $this->width = $width;
    }

    public function setHeight(int $height): void
    {
        $this->height = $height;
    }

    public function getArea(): int
    {
        return $this->width * $this->height;
    }
}

// Violates LSP - Square changes Rectangle behavior
class Square extends Rectangle
{
    public function setWidth(int $width): void
    {
        // Breaks the contract - also sets height
        $this->width = $width;
        $this->height = $width;
    }
}

function resizeRectangle(Rectangle $rect): int
{
    $rect->setWidth(5);
    $rect->setHeight(10);
    return $rect->getArea(); // Expects 50
}

echo resizeRectangle(new Rectangle()); // 50 - correct
echo resizeRectangle(new Square());    // 100 - unexpected! LSP violated
```

## Good Example

```php
<?php

// Use interface for common behavior instead of forcing inheritance
interface Shape
{
    public function getArea(): int;
}

readonly class Rectangle implements Shape
{
    public function __construct(
        private int $width,
        private int $height,
    ) {}

    public function getArea(): int
    {
        return $this->width * $this->height;
    }
}

readonly class Square implements Shape
{
    public function __construct(private int $side) {}

    public function getArea(): int
    {
        return $this->side * $this->side;
    }
}

// Both work correctly with the Shape interface
function calculateTotalArea(array $shapes): int
{
    return array_sum(array_map(fn (Shape $shape) => $shape->getArea(), $shapes));
}

echo calculateTotalArea([new Rectangle(5, 10), new Square(5)]); // 75 - correct
```

### Contract Preservation

Substitutable implementations must honor the same exceptions and return semantics documented on the interface:

```php
<?php

interface PaymentGateway
{
    /**
     * @throws InsufficientFundsException When balance is insufficient
     * @throws PaymentDeclinedException When payment is declined
     */
    public function charge(Money $amount, PaymentMethod $method): PaymentResult;
}

// Both implementations must throw the same exceptions for the same conditions
class StripeGateway implements PaymentGateway { /* ... */ }
class PayPalGateway implements PaymentGateway { /* ... */ }
```

## Why

- **Substitutability**: Subclasses work in place of parent classes
- **Reliability**: Code using base types works with any subtype
- **Testing**: Base type tests apply to all subtypes
- **Design Quality**: Violations (overridden methods that narrow behavior or throw) indicate wrong inheritance hierarchy — prefer interfaces + composition
