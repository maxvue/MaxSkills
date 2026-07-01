---
name: laravel-pest-testing-best-practices
description: Use when writing, debugging, or reviewing Unit, Feature, or Architecture tests using Pest PHP. Triggers on test creation, assertions, mocking dependencies, factory usage, database testing setup, asserting code standards, checking architectural boundaries, enforcing naming conventions, preventing architectural violations, or mocking HTTP client calls (Http::fake, Http::sequence, Http::assertSent) for external API integration tests.
---

# Laravel Pest Testing & Architecture Best Practices

## Goal
Define standard guidelines, patterns, and conventions for writing Unit, Feature, and Architecture tests with Pest PHP in the Engeapp ecosystem, ensuring transaction safety, proper factory usage, clean assertions, and strict architectural boundaries.

## Instructions
1. **Test Syntax**:
   - Use the `test('description', function () { ... })` syntax instead of `it('description')` or PHPUnit-style class methods.
   - Keep descriptions clear, concise, and in Brazilian Portuguese (e.g., `'Client gendler_name retorna Masculino para M'`), matching the Engeapp convention.
   - Use the Pest v3 functional `arch()` helper to define architecture test suites, e.g., `arch('controllers')->expect(...)`.

2. **Assertions (Expectations)**:
   - Use Pest's fluent API (`expect()`) for all assertions.
   - Common expectation examples:
     - `expect($value)->toBe($expected)`
     - `expect($value)->toBeTrue()` / `expect($value)->toBeFalse()`
     - `expect($value)->toBeInstanceOf(ClassName::class)`
     - `expect($collection)->toHaveCount($count)`
     - `expect($value)->not->toBe($other)`

3. **Database & Isolation**:
   - **Feature Tests**: All tests inside the `tests/Feature` directory automatically use the `DatabaseTransactions` trait (as configured in `tests/Pest.php`). Do NOT manually add `use DatabaseTransactions` or `use RefreshDatabase` in individual files.
   - **Unit Tests**: Keep unit tests pure. Do not query the database or depend on database state in `tests/Unit`.

4. **Factories & Model Creation**:
   - Use Laravel Model Factories to instantiate models.
   - Use `Model::factory()->make()` for instantiating models in memory when database persistence is not required (e.g., testing accessors/mutators or logic that doesn't read/write to the DB). This speeds up test execution.
   - Use `Model::factory()->create()` only when the database must be queried, relationships need to be persisted, or model lifecycle hooks (`booted` / `created` / etc.) need to run.

5. **HTTP Requests (Controller Feature Tests)**:
   - Use Pest/Laravel test request helpers: `$this->get($uri)`, `$this->post($uri, $data)`, `$this->actingAs($user)`.
   - Always assert the HTTP response status (e.g., `$response->assertOk()`, `$response->assertStatus(200)`, `$response->assertRedirect()`).

6. **Mocking & Fakes**:
   - Mock external API calls, email sending, jobs, or heavy notifications.
   - Use standard Laravel Fakes for facades: `Queue::fake()`, `Event::fake()`, `Http::fake()`.

7. **Architecture Testing (Pest v3)**:
   - Save architecture tests in the `tests/Architecture` directory or in dedicated test files named like `tests/Feature/ArchitectureTest.php` if appropriate.
   - **Enforcing Class Inheritance**:
     ```php
     arch('controllers')
         ->expect('App\Http\Controllers')
         ->toExtend('App\Http\Controllers\Controller');
     ```
   - **Enforcing Naming Conventions**:
     ```php
     arch('services')
         ->expect('App\Services')
         ->toHaveSuffix('Service');
     ```
   - **Layer Isolation & Coupling Constraints**:
     ```php
     arch('domain')
         ->expect('App\Domain')
         ->not->toUse('App\Http');
     ```
   - **Strict Dependency & Code Quality Rules**:
     ```php
     arch('globals')
         ->expect('App')
         ->not->toUse(['dd', 'dump', 'ray', 'var_dump']);
     ```
   - **Resolving External Dependencies / False Positives**:
     Exclude third-party classes, models, or vendor code that can cause false positives when testing architecture boundaries using `ignoring()`:
     ```php
     arch('domain')
         ->expect('App\Domain')
         ->not->toUse('App\Infrastructure')
         ->ignoring('App\Infrastructure\Traits\SharedTrait');
     ```

8. **HTTP Client Mocking**:
   - Always call `Http::preventStrayRequests()` in `beforeEach()` to ensure no real network requests escape. It throws immediately on unmocked calls.
   - Use `Http::fake(['domain.com/*' => Http::response([...], 200)])` for specific URL patterns. Avoid wildcard `*` — it masks unintended requests.
   - Use `Http::sequence()` for code that makes multiple requests to the same endpoint (retry logic, paginated APIs):
     ```php
     Http::fake(['api.service.com/send' => Http::sequence()->push('Error', 500)->push(['id' => 'abc'], 200)]);
     ```
   - Use `Http::failedConnection()` to verify application resilience during outages.
   - Always assert with `Http::assertSent()`, `Http::assertNotSent()`, or `Http::assertNothingSent()` — verify URL, method, payload, headers, and query params.
   - For Engeapp `BaseApi`-based integrations: mock the target URLs defined in `EndPoints.json`.
   - Do NOT use PHPUnit/Mockery mocks to intercept `Http` class methods. Only use native `Http::fake()`.
   - Do NOT use real credentials, sandbox tokens, or API keys in mocks — use fake placeholders (e.g., `'fake-token'`).

## Constraints
- Do NOT use PHPUnit-style test classes or method declarations (e.g., `public function test_something()`). Use Pest's functional syntax and `arch()` helper.
- Do NOT mix `DatabaseTransactions` with `RefreshDatabase` inside test files. Let the global `tests/Pest.php` handle the transactional state for the `Feature` suite.
- Do NOT query the database inside `tests/Unit`. Use mock objects or `make()` factories instead.
- Do NOT use standard PHPUnit assertions (like `$this->assertEquals()`) unless absolutely necessary. Prefer Pest's `expect()` API.
- Do NOT use English for test descriptions, as the project standard uses Portuguese for description texts (e.g., `test('retorna erro se o cpf for invalido', function() { ... })`).
- Do NOT query the database or mock facades within architecture tests. Keep them purely focused on static analysis and class relationships.
- Do NOT define architecture tests with empty boundaries or overlapping scopes that could slow down the test runner.
- Do NOT allow raw SQL or low-level query builders in Controllers; enforce they go through Services or DTOs by checking dependency violations.
