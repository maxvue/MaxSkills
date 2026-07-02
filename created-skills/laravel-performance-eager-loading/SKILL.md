---
name: laravel:performance-eager-loading
description: Prevent N+1 queries by eager loading; enable lazy-loading protection in non-production; choose selective fields
---

# Eager Loading and N+1 Prevention

## Load Relations Explicitly

```php
Post::with(['author', 'comments'])->paginate();
```

- Use `load()`/`loadMissing()` after fetching models when needed
- Select only required columns for both base query and relations

## Guard Against Lazy Loading in Dev/Test

Add to a service provider (non-production):

```php
Model::preventLazyLoading(! app()->isProduction());
```

## Verify

- Use a query logger or debugbar to confirm relation queries are minimized
- Add tests that assert counts or avoid unexpected query spikes


## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
