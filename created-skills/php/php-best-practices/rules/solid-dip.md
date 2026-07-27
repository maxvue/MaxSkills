---
title: Dependency Inversion Principle
impact: CRITICAL
impactDescription: Depend on abstractions, improves testability and flexibility
tags: solid, dip, design-principles, abstractions, dependency-injection
---

# Dependency Inversion Principle (DIP)

High-level modules should not depend on low-level modules. Both should depend on abstractions.

## Bad Example

```php
<?php

// High-level module directly depends on low-level implementations
class OrderService
{
    private StripePayment $payment;
    private SmtpMailer $mailer;

    public function __construct()
    {
        // Creating concrete implementations - tight coupling
        $this->payment = new StripePayment('sk_test_...');
        $this->mailer = new SmtpMailer('smtp.gmail.com', 587);
    }

    public function createOrder(array $data): Order
    {
        $order = new Order($data);
        $this->payment->charge($order->getTotal());
        $this->mailer->send($order->getCustomerEmail(), 'Order Confirmation', '...');

        return $order;
    }
}

// Problems:
// - Can't swap the payment/mail provider without changing OrderService
// - Can't test without a real payment gateway and SMTP server
```

## Good Example

```php
<?php

// Define abstractions (interfaces)
interface PaymentGateway
{
    public function charge(Money $amount, PaymentMethod $method): PaymentResult;
}

interface NotificationService
{
    public function notify(User $user, Notification $notification): void;
}

// High-level module depends on abstractions, injected via constructor
class OrderService
{
    public function __construct(
        private PaymentGateway $payment,
        private NotificationService $notifications,
    ) {}

    public function createOrder(CreateOrderCommand $command): Order
    {
        $order = Order::create(customerId: $command->customerId, items: $command->items);

        $paymentResult = $this->payment->charge($order->getTotal(), $command->paymentMethod);

        if (!$paymentResult->isSuccessful()) {
            throw new PaymentFailedException($paymentResult->getError());
        }

        $order->markAsPaid($paymentResult->getTransactionId());
        $this->notifications->notify($order->getCustomer(), new OrderConfirmationNotification($order));

        return $order;
    }
}

// Low-level modules implement the abstractions
class StripePaymentGateway implements PaymentGateway
{
    public function __construct(private StripeClient $stripe) {}

    public function charge(Money $amount, PaymentMethod $method): PaymentResult
    {
        // Stripe implementation
    }
}

// Wire the binding in a Service Provider (Laravel) / DI container
class OrderServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->bind(PaymentGateway::class, StripePaymentGateway::class);
        $this->app->bind(NotificationService::class, EmailNotificationService::class);
    }
}
```

### Testing Benefit

```php
<?php

class OrderServiceTest extends TestCase
{
    public function testCreateOrderChargesPayment(): void
    {
        $payment = $this->createMock(PaymentGateway::class);
        $payment->expects($this->once())
            ->method('charge')
            ->willReturn(PaymentResult::success('txn_123'));

        $service = new OrderService($payment, new NullNotificationService());

        $order = $service->createOrder(new CreateOrderCommand(customerId: 1, items: []));

        $this->assertTrue($order->isPaid());
    }
}
```

## Why

- **Decoupling**: High-level policy doesn't depend on low-level details
- **Testability**: Easy to substitute test doubles / mocks for dependencies
- **Flexibility**: Swap implementations (via the container's `bind()`) without changing business logic
- **Maintainability**: Changes to infrastructure don't affect domain code
