---
title: File Structure
impact: MEDIUM
impactDescription: Predictable file organization, improves readability
tags: psr, file-structure, organization, php-fig
---

# File Structure

Organize PHP files with proper ordering of elements and logical grouping.

**Nota:** apenas "um class/interface/trait/enum por arquivo" e a organização básica (`<?php`, `declare`, `namespace`, `use`, classe) fazem parte do PSR-12. A ordenação de membros da classe (constantes → propriedades → construtor → métodos por visibilidade) e o agrupamento de `use` em blocos comentados abaixo são convenção opcional deste projeto, não exigência PSR.

## Bad Example

```php
<?php
class UserService {
use LoggableTrait;
private $repo;
const MAX = 100;
public function find($id) {}
private $logger;
public const MIN = 1;
public function __construct($repo, $logger) {
$this->repo = $repo;
$this->logger = $logger;
}
}
namespace App\Services;
use App\Repositories\UserRepository;
```

## Good Example

```php
<?php

namespace App\Services;

use App\Contracts\UserServiceInterface;
use App\Events\UserCreated;
use App\Exceptions\UserNotFoundException;
use App\Models\User;
use App\Repositories\UserRepository;
use DateTimeImmutable;
use InvalidArgumentException;
use Psr\Log\LoggerInterface;

/**
 * Handles user-related business operations.
 */
final class UserService implements UserServiceInterface
{
    use LoggableTrait;

    public const DEFAULT_PAGE_SIZE = 20;

    public readonly string $version;
    private UserRepository $repository;
    private LoggerInterface $logger;

    public function __construct(
        UserRepository $repository,
        LoggerInterface $logger,
    ) {
        $this->repository = $repository;
        $this->logger = $logger;
        $this->version = '1.0.0';
    }

    public function find(int $id): ?User
    {
        return $this->repository->find($id);
    }

    public function create(array $data): User
    {
        $this->validateCreateData($data);

        $user = $this->repository->create($data);

        $this->logger->info('User created', ['id' => $user->getId()]);

        return $user;
    }

    private function validateCreateData(array $data): void
    {
        if (empty($data['email'])) {
            throw new InvalidArgumentException('Email is required');
        }
    }
}
```

### Standard File Structure Order (PSR-12)

```
1. Opening PHP tag (<?php)
2. File-level docblock (optional - license, copyright)
3. namespace declaration
4. Blank line
5. use statements (grouped and sorted)
6. Blank line
7. Class/Interface/Trait/Enum docblock
8. Class/Interface/Trait/Enum declaration
```

Dentro da classe, a ordenação de membros (constantes → propriedades → construtor → métodos) é uma convenção comum e recomendada, mas não é exigida pelo PSR-12.

### Use Statement Organization

O Pint do projeto-alvo (`ordered_imports`, `single_line_after_imports`) produz um único bloco alfabético contíguo de `use`, sem separação por comentários (`// PHP native classes`, `// External packages` etc.) — é o padrão real dos arquivos do engeapp (ex.: `app/Services/TrelloService.php`):

```php
<?php

namespace App\Services;

use App\Models\File\File;
use App\Repositories\UserRepository;
use DateTimeImmutable;
use Illuminate\Support\Str;
use Psr\Log\LoggerInterface;
```

## Why

- **Predictability**: Developers know where to find things
- **Readability**: Logical ordering improves code comprehension
- **Tooling**: `ordered_imports`/`single_line_after_imports` (Pint) enforce import order automatically
- **One Class Per File**: This is the actual PSR-12 requirement — the member-ordering convention above is a project preference, not PSR compliance

