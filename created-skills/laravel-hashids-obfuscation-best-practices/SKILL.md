---
name: laravel-hashids-obfuscation-best-practices
description: Use when implementing, configuring, or debugging ID obfuscation in Laravel Eloquent models, API routes, or controllers using the vinkla/hashids package. Triggers on route model binding customization, ID masking in API resources, and database ID obfuscation/decoding.
---

# Goal
Establish robust, consistent patterns for database ID obfuscation using the `vinkla/hashids` package in the Laravel backend. This protects sequential database IDs (auto-incrementing primary keys) from public exposure in URLs and API responses, mitigating data harvesting (scraping) and Insecure Direct Object Reference (IDOR) vulnerabilities, while preserving database performance.

# Instructions

## 1. Package Configuration
- Verify configuration values in `config/hashids.php`.
- Define a secure, unique salt for the application. Do NOT hardcode the salt; load it from the `.env` file via `config('hashids.connections.main.salt')`.
- Maintain a minimum length for generated hashes (e.g., `12` or `16` characters) to prevent brute-forcing.

## 2. The `HasHashid` Trait
- Create a reusable trait `App\Traits\HasHashid` for Eloquent models that require ID obfuscation.
- Implement an accessor attribute `hashid` using the `Hashids` facade to encode the model's primary key.
- Override the native `getRouteKeyName` and `getRouteKey` methods to use the custom hashid for implicit Route Model Binding.
- Override the `resolveRouteBinding` method to decode the hashid safely and perform a database lookup. If the hash is invalid or cannot be decoded, throw a `ModelNotFoundException` to automatically return a `404 Not Found` response.

## 3. API Resources & DTOs Integration
- When exporting model attributes via Eloquent API Resources, replace the raw database `id` with the obfuscated `hashid` string.
- If using `laravel-data` for Data Transfer Objects (DTOs), define the identifier properties as `string` and populate them with the model's `hashid`.
- Ensure TypeScript definitions derived from DTOs correctly represent these properties as `string` to match the frontend expectations.

## 4. Input Validation & Form Requests
- To validate incoming hashids, implement a custom validation rule (e.g., `ValidHashid`) or decode the hashid inline within the Form Request before proceeding to controller logic.
- Avoid passing raw hashid strings to internal database queries. Always decode the value to its integer representation before executing queries.

# Examples

### Model Implementation using `HasHashid` Trait
```php
<?php

namespace App\Traits;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\ModelNotFoundException;
use Vinkla\Hashids\Facades\Hashids;

trait HasHashid
{
    /**
     * Get the route key name for the model.
     */
    public function getRouteKeyName(): string
    {
        return 'hashid';
    }

    /**
     * Get the route key value (the encoded hashid).
     */
    public function getRouteKey(): string
    {
        return $this->hashid;
    }

    /**
     * Accessor for the hashid attribute.
     */
    public function getHashidAttribute(): string
    {
        return Hashids::connection($this->getHashidsConnectionName())->encode($this->getKey());
    }

    /**
     * Resolve the implicit route model binding.
     *
     * @param mixed $value
     * @param string|null $field
     * @return Model|null
     *
     * @throws ModelNotFoundException
     */
    public function resolveRouteBinding($value, $field = null): ?Model
    {
        // Decode only when resolving by hashid
        if ($field === 'hashid' || (is_null($field) && $this->getRouteKeyName() === 'hashid')) {
            $decoded = Hashids::connection($this->getHashidsConnectionName())->decode((string) $value);

            if (empty($decoded)) {
                throw (new ModelNotFoundException())->setModel(get_class($this));
            }

            return $this->where($this->getKeyName(), $decoded[0])->firstOrFail();
        }

        return parent::resolveRouteBinding($value, $field);
    }

    /**
     * Get the Hashids connection name associated with this model.
     */
    protected function getHashidsConnectionName(): string
    {
        return 'main';
    }
}
```

### Custom Validation Rule for Request Validation
```php
<?php

namespace App\Rules;

use Closure;
use Illuminate\Contracts\Validation\ValidationRule;
use Vinkla\Hashids\Facades\Hashids;

class ValidHashid implements ValidationRule
{
    /**
     * Create a new rule instance.
     *
     * @param class-string<\Illuminate\Database\Eloquent\Model> $modelClass
     */
    public function __construct(
        protected string $modelClass,
        protected string $connection = 'main'
    ) {}

    /**
     * Run the validation rule.
     */
    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        if (!is_string($value)) {
            $fail(__('The :attribute must be a valid hashid.'));
            return;
        }

        $decoded = Hashids::connection($this->connection)->decode($value);

        if (empty($decoded)) {
            $fail(__('The :attribute is invalid.'));
            return;
        }

        // Check if the record actually exists in the database
        $model = new $this->modelClass;
        $exists = $model->where($model->getKeyName(), $decoded[0])->exists();

        if (!$exists) {
            $fail(__('The selected :attribute does not exist.'));
        }
    }
}
```

# Constraints
- **Do NOT alter database schema column types.** The physical database primary key must remain a fast, auto-incrementing integer (or bigint) for indexing and relationship join performance.
- **Do NOT hardcode salt configuration.** All salts must be resolved from environment variables (`.env`) through the configuration files to maintain security across deployments.
- **Do NOT expose raw database IDs in API responses** for models utilizing this trait. Ensure API Resources and DTOs explicitly map the `id` property to the model's `hashid` attribute.
- **Never perform internal SQL joins using hashids.** Always decode the hashid to the raw integer key before running manual database operations or custom queries.
- **Handle decode failures gracefully.** Invalid or tampered hashes must immediately trigger a `ModelNotFoundException` (resulting in a 404 response) instead of throwing generic PHP array offset exceptions.
