---
title: Interface Segregation Principle
impact: HIGH
impactDescription: Focused interfaces, no forced implementations
tags: solid, isp, design-principles, interfaces
---

# Interface Segregation Principle (ISP)

Clients should not be forced to depend on interfaces they do not use.

## Bad Example

```php
<?php

// Fat interface - forces implementers to define methods they don't need
interface RepositoryInterface
{
    public function find(int $id): ?object;
    public function findAll(): array;
    public function create(array $data): object;
    public function update(int $id, array $data): object;
    public function delete(int $id): void;
    public function paginate(int $page, int $perPage): array;
    public function search(string $query): array;
    public function createMany(array $records): array;
    public function deleteMany(array $ids): void;
}

// Read-only audit log repository is forced to implement write methods it can't support
class AuditLogRepository implements RepositoryInterface
{
    public function create(array $data): object
    {
        throw new LogicException('Audit logs are immutable');
    }

    public function update(int $id, array $data): object
    {
        throw new LogicException('Audit logs are immutable');
    }

    // ...
}
```

## Good Example

```php
<?php

// Segregated interfaces - each has a focused purpose
interface ReadableRepository
{
    public function find(int $id): ?object;
    public function findAll(): array;
}

interface WritableRepository
{
    public function create(array $data): object;
    public function update(int $id, array $data): object;
    public function delete(int $id): void;
}

interface PaginatableRepository
{
    public function paginate(int $page, int $perPage): PaginatedResult;
}

// Full-featured repository composes what it needs
class UserRepository implements ReadableRepository, WritableRepository, PaginatableRepository
{
    // implements all three
}

// Read-only repository only implements what it supports
class AuditLogRepository implements ReadableRepository, PaginatableRepository
{
    // No write methods - audit logs are immutable, and callers can't call
    // methods that don't exist on this type
}

// Service depends only on the capability it actually uses
class UserListService
{
    public function __construct(
        private ReadableRepository&PaginatableRepository $repository,
    ) {}

    public function getPage(int $page): PaginatedResult
    {
        return $this->repository->paginate($page, 20);
    }
}
```

## Why

- **No Dead Code**: Classes don't implement unused/throwing methods
- **Focused Contracts**: Each interface has a clear, specific purpose
- **Flexibility**: Clients depend only on what they need
- **Easier Testing**: Mock only the interfaces actually used
- **Decoupling**: Changes to one interface don't affect unrelated clients
