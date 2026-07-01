---
name: laravel-migrations-seeders-factories-best-practices
description: Use when creating, modifying, reviewing, or debugging database migrations, seeders, or model factories in Laravel. Triggers on schema definitions, table creation, foreign keys, database seeders, and factory definitions.
---

# Goal
Ensure database migrations, seeders, and model factories in Laravel comply with Engeapp's architecture standards. This promotes database integrity, fast localized testing, and resilient schema updates.

# Instructions

## 1. Database Migrations
- **Anonymous Classes:** Always write migrations as anonymous classes:
  ```php
  return new class extends Migration { ... };
  ```
- **Existence Checks:** Check if the table already exists before creating it in the `up()` method to prevent execution failures:
  ```php
  public function up(): void
  {
      if (Schema::hasTable('posts')) {
          return;
      }
      Schema::create('posts', function (Blueprint $table) {
          $table->char('id', 26)->primary(); // ULID standard
          // ...
      });
  }
  ```
- **Primary Keys:** Follow the project standard for primary keys (e.g., ULIDs using `char('id', 26)->primary()`).
- **Resilient Foreign Keys:** Add foreign keys in separate migration files named like `add_foreign_keys_to_posts_table.php`. Wrap foreign key statements inside a `try/catch` block to make database setups resilient:
  ```php
  public function up(): void
  {
      try {
          Schema::table('posts', function (Blueprint $table) {
              $table->foreign(['author_id'])
                    ->references(['id'])
                    ->on('users')
                    ->onUpdate('cascade')
                    ->onDelete('cascade');
          });
      } catch (\Exception $e) {
          // ignore
      }
  }
  ```

## 2. Database Seeders
- **Idempotency:** Always write seeders using idempotent methods (e.g., `updateOrCreate` or `firstOrCreate`) to prevent duplicate records when executed repeatedly:
  ```php
  public function run(): void
  {
      User::updateOrCreate(
          ['email' => 'admin@engeapp.com'],
          ['name' => 'Admin User', 'password' => bcrypt('password')]
      );
  }
  ```
- **Reference & Production Data Sync:** When copying static/reference tables (e.g., cities, equipment brands):
  - Disable foreign key checks with the DB-agnostic helper `Schema::withoutForeignKeyConstraints(function () { /* ... */ });` — it works on MariaDB (the project's target SGBD) and keeps seeders portable. The equivalent raw form on MariaDB is `DB::statement('SET FOREIGN_KEY_CHECKS=0')` … `=1`, but prefer the helper so you don't leave checks disabled if the closure throws.
  - Use `truncate()` on target tables before inserting fresh data.
  - Chunk datasets (e.g., `500` items) during bulk insert to prevent memory limit errors:
    ```php
    foreach ($sourceData->chunk(500) as $chunk) {
        DB::table($table)->insert(
            $chunk->map(fn ($row) => (array) $row)->toArray()
        );
    }
    ```

## 3. Model Factories
- **Structure & Namespace:** Match the factories subdirectory with the Model's folder structure (e.g. `database/factories/Finance/PaymentsFactory.php`).
- **Model Mapping & Typing:** Declare the `$model` property explicitly and use PHP type hints:
  ```php
  namespace Database\Factories\Finance;

  use App\Models\Finance\Payments;
  use Illuminate\Database\Eloquent\Factories\Factory;

  class PaymentsFactory extends Factory
  {
      protected $model = Payments::class;

      public function definition(): array
      {
          return [
              'project_id' => Project::factory(),
              'value'      => fake()->randomFloat(2, 100, 5000),
          ];
      }
  }
  ```
- **Data Generation:** Use the global `fake()` helper (e.g., `fake()->sentence()`) instead of `$this->faker` when generating values.
- **Factory States:** Define explicit, type-hinted helper methods for common model states returning `static` and using `$this->state()`:
  ```php
  public function paid(): static
  {
      return $this->state(fn (array $attributes) => [
          'status' => 'paid',
      ]);
  }
  ```

# Constraints
- DO NOT define foreign keys directly in table creation migration files. Put them in separate `add_foreign_keys_to_...` files inside `try/catch` blocks.
- DO NOT run bulk database inserts in seeders without chunking.
- DO NOT hardcode relationship IDs in seeders or factories. Always use factory relationships (e.g. `User::factory()`).
- DO NOT use `$this->faker` in new factories; prefer the global `fake()` helper.
- DO NOT omit void return statements on migration `up`/`down` methods and seeder `run` methods.
