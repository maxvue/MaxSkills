---
title: PSR-4 Autoloading
impact: CRITICAL
impactDescription: Standard autoloading, predictable class location
tags: psr, autoloading, organization, php-fig
---

# PSR-4 Autoloading

Follow PSR-4 autoloading standard for class file organization.

## Bad Example

```php
<?php

// File: includes/classes/user_model.php
// Wrong: File name doesn't match class name
// Wrong: Using underscores instead of directories

class User_Model
{
    // ...
}

// File: lib/MyApp/Services/userService.php
// Wrong: File name case doesn't match class name

namespace MyApp\Services;

class UserService
{
    // ...
}

// Manual includes - fragile and error-prone
require_once 'includes/classes/user_model.php';
require_once 'includes/classes/order_model.php';
require_once 'lib/helpers.php';
```

## Good Example

Em projetos Laravel (como o engeapp), o mapeamento PSR-4 padrão é `App\ -> app/`, sem camada `src/Domain/Application/Infrastructure` — Laravel não usa Doctrine nem essa separação por padrão:

```php
<?php

// File: app/Services/UserService.php
// Namespace matches directory structure (App\ -> app/)

namespace App\Services;

use App\Models\User;
use App\Repositories\UserRepository;

class UserService
{
    public function __construct(
        private UserRepository $repository,
    ) {}

    public function find(int $id): ?User
    {
        return $this->repository->find($id);
    }
}

// File: app/Repositories/UserRepository.php
namespace App\Repositories;

use App\Models\User;

class UserRepository
{
    public function find(int $id): ?User
    {
        return User::find($id);
    }
}
```

Fora do Laravel, um projeto pode optar por `src/` com camadas Domain/Application/Infrastructure — mas isso é uma escolha de arquitetura, não uma exigência do PSR-4:

```php
<?php

// File: src/Domain/User/User.php
// Namespace matches directory structure

namespace App\Domain\User;

class User
{
    public function __construct(
        private UserId $id,
        private Email $email,
    ) {}
}
```

### Composer Configuration

Laravel (engeapp):

```json
{
    "autoload": {
        "psr-4": {
            "App\\": "app/",
            "Database\\Factories\\": "database/factories/",
            "Database\\Seeders\\": "database/seeders/"
        }
    }
}
```

Projeto não-Laravel com camada `src/`:

```json
{
    "autoload": {
        "psr-4": {
            "App\\": "src/",
            "Tests\\": "tests/"
        }
    }
}
```

## Why

- **Automatic Loading**: No manual require/include statements needed
- **Predictable Structure**: Class location is deterministic from namespace
- **IDE Support**: Enables full autocompletion and navigation
- **Composer Integration**: Standard Composer autoloader works out of the box
- **Interoperability**: Works with any PSR-4 compliant framework
- **Maintainability**: Clear organization makes codebases easier to navigate
