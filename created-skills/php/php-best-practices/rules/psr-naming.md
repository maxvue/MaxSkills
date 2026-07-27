---
title: Naming and Namespace Conventions
impact: HIGH
impactDescription: Clear communication through consistent naming and namespace organization
tags: psr, naming, namespaces, conventions
---

# Naming and Namespace Conventions

- **Classes/Interfaces/Traits/Enums**: `StudlyCaps` (PascalCase), descriptive nouns — `UserService`, `OrderRepository`, `UserNotFoundException`. Avoid generic names (`Manager`, `Helper`, `Data`) and verbs as class names (`GetUser`).
- **Methods**: `camelCase`, verb-led and descriptive — `findByEmail()`, `isActive()`, `createOrder()`. Boolean methods read as a question (`is`/`has`/`can`/`should` prefix).
- **Namespace**: mirrors the PSR-4 directory structure (see `psr-4-autoloading.md`); import (`use`) related classes at the top instead of fully-qualified names inline.

**Exceção Laravel real do engeapp:** `handle()` e `__invoke()` NÃO são "nomes vagos" a evitar — são o contrato exigido pelo framework para Jobs (`ShouldQueue::handle()`) e Commands (`Command::handle()`). O engeapp tem 112 ocorrências de `public function handle(` em `app/Jobs` e `app/Console`. Não sinalize esses métodos como violação de nomenclatura.

## Bad Example

```php
<?php

// Wrong: snake_case class, generic name
class user_manager
{
    // Wrong: underscores, no verb, abbreviation
    public function get_usr_by_id(int $id) {}

    // Wrong: vague name (but NOT handle()/__invoke() in Jobs/Commands — see note above)
    public function process(): void {}
}

// No namespace - global scope pollution
class Order {}

// Fully qualified names everywhere instead of `use`
class UserService
{
    public function find(int $id): \App\Domain\User\User
    {
        return $this->repository->find($id);
    }
}
```

## Good Example

```php
<?php

namespace App\Services;

use App\Models\User;
use App\Repositories\UserRepository;

class UserService
{
    public function __construct(
        private UserRepository $repository,
    ) {}

    public function findByEmail(string $email): ?User
    {
        return $this->repository->findByEmail($email);
    }

    public function isActive(User $user): bool
    {
        return $user->status === 'active';
    }
}

// Job — handle() is the required Laravel contract, not a vague name
namespace App\Jobs;

class ProcessPaymentJob implements \Illuminate\Contracts\Queue\ShouldQueue
{
    public function handle(): void
    {
        // ...
    }
}
```

## Why

- **Clarity**: PascalCase/camelCase distinguish classes from methods/variables at a glance
- **Discoverability**: Suffixes (`Service`, `Repository`, `Exception`) and verb prefixes indicate purpose
- **Autoloading**: Namespace mirroring the directory is what PSR-4 actually requires (see `psr-4-autoloading.md`)
- **Framework Contracts First**: naming conventions yield to framework-required method names like `handle()`/`__invoke()`
