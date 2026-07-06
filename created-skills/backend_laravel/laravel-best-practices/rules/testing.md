# Testing Best Practices

O engeapp usa **Pest exclusivamente** (`pestphp/pest ^3.7`): escreva testes com `test()`/`it()` em closures, não com classes/métodos PHPUnit. As asserções `$this->...` continuam válidas porque a closure é vinculada ao TestCase, mas o esqueleto do teste é sempre funcional. Os `Feature/` estendem `Tests\TestCase` + `DatabaseTransactions` via `tests/Pest.php`.

## Use `LazilyRefreshDatabase` Over `RefreshDatabase`

`RefreshDatabase` migrates once per process and wraps each test in a rolled-back transaction. `LazilyRefreshDatabase` skips even that first migration if the schema is already up to date. (O engeapp já aplica `DatabaseTransactions` globalmente em `tests/Pest.php` para os testes de `Feature`; confira essa configuração antes de trocar de trait.)

## Use Model Assertions Over Raw Database Assertions

Mais expressivo, type-safe e falha com mensagens mais claras.

```php
// Evite
it('cria o usuário', function () {
    $user = User::factory()->create();
    $this->assertDatabaseHas('users', ['id' => $user->id]);
});

// Prefira
it('cria o usuário', function () {
    $user = User::factory()->create();
    $this->assertModelExists($user);
});
```

## Use Factory States and Sequences

Named states make tests self-documenting. Sequences eliminate repetitive setup.

```php
// Evite
$user = User::factory()->create(['email_verified_at' => null]);

// Prefira
$user = User::factory()->unverified()->create();
```

## Use `Exceptions::fake()` to Assert Exception Reporting

Instead of `withoutExceptionHandling()`, use `Exceptions::fake()` to assert the correct exception was reported while the request completes normally.

## Call `Event::fake()` After Factory Setup

Model factories rely on model events (e.g., `creating` to generate UUIDs). Calling `Event::fake()` before factory calls silences those events, producing broken models.

```php
// Evite — o fake silencia os eventos que a factory precisa
it('faz X', function () {
    Event::fake();
    $user = User::factory()->create();
});

// Prefira — faça o fake depois do setup da factory
it('faz X', function () {
    $user = User::factory()->create();
    Event::fake();
});
```

## Use `recycle()` to Share Relationship Instances Across Factories

Without `recycle()`, nested factories create separate instances of the same conceptual entity.

```php
Ticket::factory()
    ->recycle(Airline::factory()->create())
    ->create();
```
