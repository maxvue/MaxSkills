---
name: laravel-services-best-practices
description: Use when creating, refactoring, or reviewing Laravel Service classes, applying Single Responsibility Principle, dependency injection, and standardized error handling. Triggers on Service class creation, business logic encapsulation, and external API integrations.
---

# Laravel Services Best Practices

## Goal
Establish clean, testable, and consistent guidelines for creating and maintaining Service classes in Laravel, ensuring controllers remain thin, business logic is centralized, and dependency injection is properly utilized.

## Instructions

1. **Architecture & File Location**:
   - Save all service classes in `app/Services/` (e.g., `app/Services/TrelloService.php`).
   - Use the `App\Services` namespace.
   - Name files using the `Service` suffix (e.g., `PaymentService.php`).

2. **Single Responsibility Principle (SRP)**:
   - Each Service class should focus on a single domain or closely related set of business actions.
   - For highly complex operations, use specialized services (e.g., `ProjectDeletionService.php`).

3. **Dependency Injection**:
   - Inject required dependencies (repositories, other services, API clients) via the constructor.
   - Use PHP 8 constructor property promotion to declare and assign dependencies.
   - Never resolve dependencies manually using `app()` or `resolve()` helper functions inside methods if they can be injected.

4. **Method Signatures & Data Transfer Objects (DTOs)**:
   - Avoid passing raw, unvalidated arrays or request objects directly into Service methods.
   - Use typed Data Transfer Objects (DTOs) for incoming parameters (integrate with `laravel-code-generators-best-practices`).
   - Define explicit return types (DTO, Model, Collection, array, etc.) for all public methods.

5. **Error Handling & Logging**:
   - Standardize business logic failures by throwing custom, domain-specific Exceptions rather than returning false or error strings.
   - Catch infrastructure-level exceptions (e.g., HTTP requests, database deadlocks) and wrap/rethrow them as domain exceptions where appropriate.
   - Log failures using the `Log` facade with descriptive messages and context arrays, avoiding generic statements.

## Constraints
- **No Controller/HTTP coupling**: Do not reference HTTP request variables (`request()`), sessions, or redirect helpers inside Service classes.
- **No View presentation logic**: Services must not render HTML, return JSON responses, or construct UI components.
- **No static state accumulation**: Avoid declaring public static properties that persist across requests to maintain compatibility with Octane.

## Examples

### Example: Standard Laravel Service implementation
```php
<?php

namespace App\Services;

use App\Data\OrderData;
use App\Models\Order;
use App\Services\Payment\GatewayService;
use App\Exceptions\PaymentFailedException;
use Illuminate\Support\Facades\Log;
use Throwable;

class OrderProcessingService
{
    // PHP 8 Constructor Property Promotion
    public function __construct(
        protected GatewayService $gateway
    ) {}

    /**
     * Process and finalize a customer order.
     *
     * @param Order $order
     * @param OrderData $data
     * @return Order
     * @throws PaymentFailedException
     */
    public function process(Order $order, OrderData $data): Order
    {
        try {
            // Business logic encapsulation
            $paymentResult = $this->gateway->charge($order, $data->paymentDetails);

            if (!$paymentResult->successful()) {
                throw new PaymentFailedException("Payment rejected: " . $paymentResult->getErrorMessage());
            }

            $order->update([
                'status' => 'paid',
                'transaction_id' => $paymentResult->getTransactionId(),
            ]);

            return $order;
        } catch (Throwable $e) {
            Log::error('Order processing failed', [
                'order_id' => $order->id,
                'error' => $e->getMessage(),
            ]);

            if ($e instanceof PaymentFailedException) {
                throw $e;
            }

            throw new PaymentFailedException('An unexpected error occurred during payment processing.', 0, $e);
        }
    }
}
```
