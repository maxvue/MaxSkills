---
name: laravel-redis-integration-best-practices
description: Use when configuring, optimizing, or debugging Redis database connections, queues, sessions, cache stores, pub/sub channels, or distributed locks in Laravel. Triggers on Redis facade usage, phpredis/predis config, cache tags, connection exceptions, and Horizon queue backend configurations.
---

# Laravel Redis Integration Best Practices

## Goal
Establish solid guidelines and consistent patterns for configuring, optimizing, securing, and developing resilient Redis-based routines in the Engeapp Laravel backend.

## Instructions

### 1. Redis Client & Configuration
* **Default Client:** Always use `phpredis` as the default client (as it is implemented in C and offers much higher performance than `predis`).
* **Persistent Connections:** Ensure `REDIS_PERSISTENT` is enabled in production environments to avoid the overhead of establishing a new connection on every request.
* **Timeout and Read Timeout:** Set reasonable values for `timeout` and `read_timeout` (e.g., 1.5s to 2.0s) to prevent a slow Redis instance from blocking web workers.

Example configuration in `config/database.php`:
```php
'redis' => [
    'client' => env('REDIS_CLIENT', 'phpredis'),

    'options' => [
        'cluster' => env('REDIS_CLUSTER', 'redis'),
        'prefix' => env('REDIS_PREFIX', Str::slug(env('APP_NAME', 'laravel'), '_') . '_database_'),
        'persistent' => env('REDIS_PERSISTENT', true),
        'timeout' => 1.5,
        'read_timeout' => 1.5,
    ],
    // ... connections configuration ...
],
```

### 2. Semantic Key Naming Convention
To prevent key collisions and ensure visibility, use a structured colon-separated naming convention:
* **Pattern:** `app_name:domain:resource:identifier`
* **Example:** `engeapp:payments:charge:123456`
* **Rule:** Never use hardcoded strings for Redis keys. Define constants or helper methods on the service/model class handling the resource.

```php
class PaymentService
{
    private const REDIS_PREFIX = 'engeapp:payments:charge:';

    public function getCacheKey(int $chargeId): string
    {
        return self::REDIS_PREFIX . $chargeId;
    }
}
```

### 3. Distributed Locks for Concurrency Control
Always use distributed locks for critical business logic (e.g., payment processing, inventory updates, concurrent ticket creation) to prevent race conditions.
* Use `Cache::lock($name, $seconds)` which uses the Redis lock driver.
* Utilize `block($seconds, callable)` to wait for the lock if it's currently held.
* Wrap logic in a `try/finally` block or pass a closure to `block()` to ensure the lock is always released.

```php
use Illuminate\Support\Facades\Cache;

$lock = Cache::lock('payment_lock_user_' . $userId, 10);

try {
    // Block for up to 5 seconds waiting for the lock
    $lock->block(5, function () use ($paymentData) {
        // Critical transaction/payment logic here
    });
} catch (\Illuminate\Contracts\Cache\LockTimeoutException $e) {
    // Handle the lock acquisition failure gracefully
    throw new PaymentProcessingException('Process already in execution. Please try again in a few seconds.', 429);
}
```

### 4. Redis Pipelines for Batch Operations
When reading or writing multiple keys, use `Redis::pipeline()` to send commands in a single batch, reducing round-trip time (RTT).

```php
use Illuminate\Support\Facades\Redis;

$results = Redis::pipeline(function ($pipe) use ($geckodriverPorts) {
    foreach ($geckodriverPorts as $port => $timestamp) {
        $pipe->hset('geckodriver_ports', $port, $timestamp);
    }
});
```

### 5. Resilient Connection Failbacks and Exception Handling
Redis connection drops should not bring down the entire application (unless it's a hard dependency like session or rate-limiting).
* Catch `RedisException` or general cache drivers exceptions.
* Implement a fallback database query or default values if the Redis server goes offline.

```php
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Redis;
use RedisException;

public function getActivePorts(): array
{
    try {
        return Redis::hgetall('geckodriver_ports') ?: [];
    } catch (RedisException $e) {
        Log::error('Redis connection failure in CleanupGeckodriverPorts', [
            'exception' => $e->getMessage()
        ]);
        
        // Fallback option (e.g. read from fallback persistent source or return empty)
        return [];
    }
}
```

### 6. Cache Tags and Invalidation
When caching structured database query results, use Cache Tags so they can be selectively invalidated.
* **Important:** Redis does not natively support tags; Laravel implements this by creating additional tracking keys, which can be memory-heavy. Avoid tags if caching millions of keys.
* Flush tags selectively instead of clearing the entire cache.

```php
use Illuminate\Support\Facades\Cache;

// Storing with tags
Cache::tags(['solar-data', 'nasa-power'])->put($cacheKey, $data, now()->addDays(7));

// Invalidating by tag
Cache::tags(['solar-data'])->flush();
```

### 7. Horizon and Queue Tuning
* Make sure `horizon.php` connection configuration matches the persistent default connection.
* Avoid dispatching huge payloads in jobs. Instead, store the Model ID in the job payload and fetch the fresh data from the database/cache inside the job.
* Configure redis queue connection with a high enough `retry_after` (larger than your longest-running job).

## Constraints
* **DO NOT** run slow Redis commands (like `KEYS *`, `FLUSHALL`, `FLUSHDB`) in production. Use `SCAN` or clean cache using Laravel's native cache clear commands.
* **DO NOT** use Redis cache tags without verifying the driver. The database and file cache drivers do not support tags.
* **DO NOT** write raw Redis queries without catching connection exceptions. Always assume Redis can go offline.
* **DO NOT** serialize complete Eloquent models directly to Redis; use `json_encode` of necessary data or standard model serialization via jobs.
