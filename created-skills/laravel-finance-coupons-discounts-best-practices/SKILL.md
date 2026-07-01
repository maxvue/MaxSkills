---
name: laravel-finance-coupons-discounts-best-practices
description: Use when creating, modifying, applying, or validating discount coupons (cupons de desconto), referral usage rules, or financial discounts (descontos financeiros) in Laravel. Triggers on coupon validation logic, payment discount adjustments, coupon-project associations, and discount expiration checks.
---

# Laravel Finance Coupons & Discounts Best Practices

## Goal
Establish solid guidelines and consistent patterns for creating, validating, applying, and auditing discount coupons and financial discounts in the Engeapp Laravel backend, preventing race conditions, rounding errors, and illegitimate redemptions.

## Instructions

### 1. Coupon Validation Logic
Always use the static method `FinanceDiscountCoupons::getCouponByCode($code, $project_id)` to resolve and validate a coupon code. When implementing or reviewing validation logic, ensure that:
- **Active Status:** The coupon must be active (`active = true`).
- **Expiration:** Check if the current time is after the expiration date (`expiration`).
- **Global Usage Limit:** The total usage count (`count_use` via `uses()->count()`) must not exceed the coupon's total allowed amount (`amount`).
- **Company/Integrator Limit:** Check if the solar company's usage count exceeds the maximum limit allowed per integrator (`limit_use`).
- **Audience Restrictions:** If `reference_use` is defined, verify that it matches either the solar company ID or the client ID.

### 2. Secure Application & Concurrency (Race Conditions)
When a coupon is applied during checkout, race conditions can allow a coupon to be used beyond its limits if multiple requests happen simultaneously.
- **Database Transactions:** Always wrap the payment creation, coupon validation, and coupon usage registration inside a database transaction:
  ```php
  use Illuminate\Support\Facades\DB;

  DB::transaction(function () use ($code, $projectId, $paymentData) {
      // 1. Fetch coupon with lock for update to prevent concurrent changes
      $coupon = FinanceDiscountCoupons::where('code', $code)
          ->lockForUpdate()
          ->first();

      // 2. Perform validations...
      
      // 3. Create payment and register coupon use
  });
  ```
- **Pessimistic Locking:** Use `.lockForUpdate()` when querying the coupon to block concurrent checkouts from reading obsolete usage counts.

### 3. Precision Discount Calculations (BRL)
To prevent centesimal rounding differences when applying discount values (fixed or percentages):
- **Float Avoidance:** Do not use plain float calculations for financial operations.
- **Type Checking:** Distinguish clearly between percentual discounts (`type_discount === 'percent'`) and fixed value discounts (`type_discount === 'value'`).
- **Calculation Precision:** Format calculation results with 2 decimal places using BCMath functions or safe rounding helper methods before storing them in the payment fields:
  ```php
  if ($coupon->type_discount === 'percent') {
      $discountValue = round(($totalAmount * $coupon->value) / 100, 2);
      $totalAmount -= $discountValue;
  } elseif ($coupon->type_discount === 'value') {
      $totalAmount -= $coupon->value;
  }
  ```

### 4. Auditing and Usage Registration
Every time a coupon is successfully applied, record the history in the `finance_discounts_coupon_use` table:
- Map relations explicitly: `payment_id`, `coupon_id`, `project_id`, `client_id`, `solar_company_id`, and `coupon_code`.
- Do not rely solely on automated event hydration if it can be done cleanly during creation.

---

## Constraints
- **NO Database Writes in Read Events:** NEVER invoke `$model->save()` or database write operations inside Eloquent model events that trigger on read (such as `retrieved` or `booted` read hooks). Doing so creates recursive queries, massive performance issues, and write locks on simple select queries.
- **Attribute Assignments:** NEVER mismatch relationship assignments (e.g. assigning client IDs or company IDs to `project_id` by mistake). Verify assignments carefully:
  ```php
  // BAD: Overwriting project_id instead of setting client_id
  $model->project_id = $model->payment->project->client_id;

  // GOOD: Assigning to the correct properties
  $model->client_id = $model->payment->project->client_id;
  $model->solar_company_id = $model->payment->project->client->solar_company_id;
  ```
- **Float comparison:** Never perform direct equal comparisons on floats when validating remaining balances.
