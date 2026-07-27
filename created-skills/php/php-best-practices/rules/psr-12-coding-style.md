---
title: PSR-12 Coding Style
impact: HIGH
impactDescription: Consistent formatting, improved readability and collaboration
tags: psr, coding-style, formatting, php-fig
---

# PSR-12 Coding Style

Follow PSR-12 extended coding style for consistent, readable code.

## Bad Example

```php
<?php
namespace App\Services;
use App\Models\User;use App\Repositories\UserRepository;

class UserService{
    private $repository;

    public function __construct(UserRepository $repo){
        $this->repository=$repo;
    }

    public function find($id){
        if($id<1){return null;}
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
use InvalidArgumentException;

class UserService
{
    public function __construct(
        private UserRepository $repository,
    ) {}

    public function find(int $id): ?User
    {
        if ($id < 1) {
            return null;
        }

        return $this->repository->find($id);
    }

    public function create(array $data): User
    {
        if (!isset($data['email']) || !isset($data['name'])) {
            throw new InvalidArgumentException('Missing required data');
        }

        return $this->repository->create($data);
    }

    public function update(
        int $id,
        array $data,
        bool $validate = true,
    ): User {
        $user = $this->find($id);

        if ($user === null) {
            throw new UserNotFoundException($id);
        }

        return $this->repository->update($user, $data);
    }
}
```

### Key Formatting Rules

- One blank line after `namespace` and after the `use` block
- Opening brace for classes/methods on its own line
- Space after control structure keywords (`if (`, `foreach (`), operators surrounded by spaces
- Multi-line parameter lists: closing paren, return type, and opening brace on the same line
- Short closures (`fn($n) => ...`) preferred over `function () use (...)` when possible

```php
<?php

try {
    $this->validate($input);
} catch (CustomException $e) {
    $this->logger->error($e->getMessage());
    throw $e;
} finally {
    $this->cleanup();
}
```

## Why

- **Consistency**: All code looks the same regardless of author
- **Readability**: Standardized formatting is easier to read
- **Tooling**: PHP CS Fixer / Laravel Pint enforce it automatically (see `pint.json` in the target project)
- **Industry Standard**: Most PHP projects and frameworks follow PSR-12
