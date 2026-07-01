---
name: laravel-cache-best-practices
description: Use when implementing, configuring, or debugging caching mechanisms in Laravel. Triggers on Cache facade usage, Cache::remember, Cache::forget, Cache::put, cache configuration, TTL definitions, and cache-aside patterns.
---

# Laravel Cache Best Practices

## Goal
Establish solid guidelines, consistent key naming conventions, and structured patterns for caching data, API responses, and database queries within the Laravel ecosystem of Engeapp. This ensures optimal application performance, data consistency, and stateless compatibility under Laravel Octane.

## Instructions

### 1. Cache Key Naming Conventions
Always use structured, predictable, and scoped cache keys. Avoid using plain strings or dynamically generated IDs without context.
- **External APIs:** Use the format `api:{provider}:{endpoint_or_resource}:{unique_identifier}`
  - Example: `api:correios:zipcode:01001000`
  - Example: `api:cnpj:company:12345678000199`
- **Eloquent Models:** Use the format `model:{table_name}:{id}:{attribute_or_relation}`
  - Example: `model:inverters:45:nominal_power`
  - Example: `model:support_contacts:12:channel_users`
- **Application Contexts:** Use the format `app:{context}:{identifier}`
  - Example: `app:support_template:welcome_message`

### 2. Time-To-Live (TTL) Specifications
Always define a precise, appropriate TTL. Avoid caching data forever (`rememberForever`) unless it is truly static and immutable.
- Use explicit carbon helpers or seconds integers to represent duration.
- Recommended TTLs:
  - External Address APIs (CEP, CNPJ): 3 to 6 months (`now()->addMonths(6)`).
  - External Token APIs (e.g., Correios, CRM): Up to token expiration (`now()->addHours(24)`).
  - Eloquent relations/attributes: 10 minutes to 3 days, depending on frequency of updates.

### 3. Cache-Aside Pattern
Prefer using `Cache::remember` over manual `Cache::has` and `Cache::put` blocks to prevent race conditions and ensure clean code.

```php
// Padrão recomendado para buscar dados com fallback e cacheamento automático
$inverterPower = Cache::remember(
    "model:inverters:{$this->id}:nominal_power",
    now()->addMinutes(120),
    fn () => $this->nominal_power / 1000
);
```

### 4. Cache Invalidation via Observers
To avoid data stale states, always invalidate model caches using Eloquent Observers. Avoid putting cache invalidation logic inside Controllers or Models.
- Create an Observer using `php artisan make:observer {ModelName}Observer --model={ModelName}`.
- Trigger `Cache::forget` on `saved`, `deleted`, and `restored` events.

```php
namespace App\Observers;

use App\Models\Inverter;
use Illuminate\Support\Facades\Cache;

class InverterObserver
{
    /**
     * Limpa o cache quando o inversor é salvo ou atualizado.
     */
    public function saved(Inverter $inverter): void
    {
        Cache::forget("model:inverters:{$inverter->id}:nominal_power");
    }

    /**
     * Limpa o cache quando o inversor é deletado.
     */
    public function deleted(Inverter $inverter): void
    {
        Cache::forget("model:inverters:{$inverter->id}:nominal_power");
    }
}
```

### 5. Race Conditions and Concurrency
For high-concurrency tasks or heavy recalculations, use atomic locks (`Cache::lock`) to prevent Cache Stampede (multiple processes querying the same database data simultaneously when cache expires).

```php
use Illuminate\Support\Facades\Cache;

// Adquire uma trava atômica por até 10 segundos para processar dados de API pesados
$lock = Cache::lock('api:processing:heavy_report', 10);

if ($lock->get()) {
    // Processamento seguro sem concorrência concorrente
    
    $lock->release();
}
```

### 6. Octane Compatibility (Stateless)
- Avoid using the `array` cache driver in production environments, as it is in-memory and will not sync across multiple Octane workers.
- Do not store state directly in class static properties because they persist between requests in the Octane worker. Always use the `Cache` facade or Laravel's `Context` facade for request-scoped metadata tracking.

---

## Constraints
- **NO Plain Keys:** Never use cache keys without structured prefixes (e.g., do not use just `$this->id`, use `"model:inverters:{$this->id}"` instead).
- **NO Inline Cache Invalidation:** Do not inline cache invalidation code inside controllers; delegate it to Observers.
- **NO Stateful Singletons:** Never store cached values in singleton instance properties unless you explicitly implement a cleanup mechanism or bind them using resolver closures.
- **Brazilian Portuguese Comments:** All code comments inside PHP examples must be strictly written in Brazilian Portuguese (pt-BR).
