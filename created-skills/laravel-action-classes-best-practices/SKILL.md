---
name: laravel-action-classes-best-practices
description: Use when designing, writing, reviewing, or debugging Action classes (Single Responsibility classes) in a Laravel application. Triggers on files under app/Actions, custom action classes execution, dependency injection within actions, and transactions management inside single-action workflows.
---

# Goal
Ensure that business logic is isolated into clean, testable, and reusable Single Responsibility Action classes within the Laravel application, separating complex workflows from controllers, models, and jobs.

# Instructions
1. **File Location & Naming:**
   - Store all action classes inside the `app/Actions` directory (create it if it does not exist).
   - Use PascalCase for the class name and suffix it with `Action` (e.g., `CreateInvoiceAction.php`, `ProcessPaymentAction.php`).
   - Place them in subdirectories if organized by subdomain (e.g., `app/Actions/Billing/CreateInvoiceAction.php`).

2. **Single Responsibility & Entry Point:**
   - Each action must represent a single business transaction or task.
   - Expose exactly one public method named `execute()`.
   - Other methods within the class must be `private` or `protected` helpers.

3. **Dependency Injection:**
   - Inject static dependencies (services, repository classes, API clients, other actions) via the constructor `__construct()`.
   - Pass dynamic data (models, scalar values, DTOs) as parameters to the `execute()` method.

4. **Input Handling (No HTTP Requests):**
   - Never pass an HTTP Request object (`Illuminate\Http\Request`) to an action.
   - Extract data in controllers/requests and pass scalar types, Eloquent Models, or Data Transfer Objects (DTOs, like Spatie Data classes) to `execute()`.

5. **Database Transactions:**
   - If the action performs multiple write operations (inserts, updates, deletes), wrap the logic in a database transaction using `DB::transaction()` to ensure atomicity.
   - Rely on `laravel-database-eloquent-best-practices` for database interactions.

6. **Error Handling & Exceptions:**
   - Throw domain-specific exceptions (e.g., `PaymentFailedException`) when business rules are violated.
   - Let the caller (Controller, Job, Command) handle how the exception is reported or displayed to the user.

7. **Relation to Services:**
   - Refer to `laravel-services-best-practices` for architectural boundaries. Use *Services* for coordinating multiple domains or when multiple methods are cohesive. Use *Actions* for discrete, single-action business workflows.

# Constraints
- Do NOT define multiple public entry points or methods in an Action class.
- Do NOT access session, cookie, or request headers directly inside an Action.
- Do NOT generate HTML responses or return `JsonResponse` objects from an Action. Return raw data, Models, or DTOs.
- Do NOT suppress errors with empty `catch` blocks. All exceptions must either be handled, logged, or rethrown.

# Examples
### Action Class Definition
```php
<?php

namespace App\Actions\Billing;

use App\Models\User;
use App\Models\Invoice;
use App\Services\PaymentGatewayService;
use App\Data\InvoiceData;
use Illuminate\Support\Facades\DB;
use App\Exceptions\BillingException;

class CreateInvoiceAction
{
    // Inject the payment gateway service dependency
    public function __construct(
        protected PaymentGatewayService $gateway
    ) {}

    /**
     * Executes the invoice creation workflow.
     *
     * @param User $user
     * @param InvoiceData $data
     * @return Invoice
     * @throws BillingException
     */
    public function execute(User $user, InvoiceData $data): Invoice
    {
        return DB::transaction(function () use ($user, $data) {
            // 1. Charge the user via external gateway
            $charge = $this->gateway->charge($user, $data->amount);

            if (!$charge->successful()) {
                throw new BillingException("Payment failed: " . $charge->errorMessage());
            }

            // 2. Create the invoice record
            $invoice = $user->invoices()->create([
                'amount' => $data->amount,
                'due_at' => $data->dueAt,
                'status' => 'paid',
                'transaction_id' => $charge->transactionId(),
            ]);

            return $invoice;
        });
    }
}
```

### Calling the Action in a Controller
```php
<?php

namespace App\Http\Controllers;

use App\Http\Requests\InvoiceStoreRequest;
use App\Actions\Billing\CreateInvoiceAction;
use Illuminate\Http\JsonResponse;

class InvoiceController extends Controller
{
    public function store(
        InvoiceStoreRequest $request,
        CreateInvoiceAction $createInvoiceAction
    ): JsonResponse {
        $user = $request->user();
        
        // Extract DTO from request
        $invoiceData = $request->toDto();

        // Run the action
        $invoice = $createInvoiceAction->execute($user, $invoiceData);

        return response()->json([
            'message' => 'Invoice created successfully.',
            'data' => $invoice,
        ], 201);
    }
}
```
