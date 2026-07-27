---
title: Open/Closed Principle
impact: HIGH
impactDescription: Extend without modifying, reduces regression risk
tags: solid, ocp, design-principles, extension
---

# Open/Closed Principle (OCP)

Classes should be open for extension but closed for modification.

## Bad Example

```php
<?php

// Must modify this class every time a new payment method is added
class PaymentProcessor
{
    public function process(string $type, float $amount): PaymentResult
    {
        if ($type === 'credit_card') {
            $fee = $amount * 0.029;
            return new PaymentResult($amount + $fee, 'credit_card');
        }

        if ($type === 'paypal') {
            $fee = $amount * 0.035;
            return new PaymentResult($amount + $fee, 'paypal');
        }

        // Adding a new type means editing this method again
        if ($type === 'pix') {
            $fee = 0;
            return new PaymentResult($amount + $fee, 'pix');
        }

        throw new InvalidArgumentException("Unknown payment type: {$type}");
    }
}
```

## Good Example

```php
<?php

// Define contract for payment methods
interface PaymentMethod
{
    public function process(Money $amount): PaymentResult;
    public function getName(): string;
}

// Each payment method is a separate class - closed for modification
class CreditCardPayment implements PaymentMethod
{
    private const FEE_PERCENTAGE = 0.029;

    public function __construct(private PaymentGateway $gateway) {}

    public function process(Money $amount): PaymentResult
    {
        return $this->gateway->charge($amount->multiply(1 + self::FEE_PERCENTAGE));
    }

    public function getName(): string
    {
        return 'credit_card';
    }
}

// New payment method - extend without modifying existing code
class PixPayment implements PaymentMethod
{
    public function __construct(private PixGateway $gateway) {}

    public function process(Money $amount): PaymentResult
    {
        return $this->gateway->charge($amount);
    }

    public function getName(): string
    {
        return 'pix';
    }
}

// Payment processor is closed for modification
class PaymentProcessor
{
    /** @var array<string, PaymentMethod> */
    private array $methods = [];

    public function registerMethod(PaymentMethod $method): void
    {
        $this->methods[$method->getName()] = $method;
    }

    public function process(string $methodName, Money $amount): PaymentResult
    {
        if (!isset($this->methods[$methodName])) {
            throw new UnsupportedPaymentMethodException($methodName);
        }

        return $this->methods[$methodName]->process($amount);
    }
}
```

## Why

- **No Regression Risk**: Existing code isn't modified when adding features
- **Easy Extension**: New functionality via new classes, not changes
- **Better Testing**: Existing tests remain valid
- **Framework Integration**: Works well with DI containers (bind new implementations without touching consumers)
