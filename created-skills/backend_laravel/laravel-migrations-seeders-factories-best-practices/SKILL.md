---
name: laravel-migrations-seeders-factories-best-practices
description: "Use when creating, reviewing, or debugging database migrations, seeders, or model factories in Laravel. Covers schema definitions, foreign keys, database seeders, and factory states. Covers objectives and core workflows."
---
# Objetivo
Garantir que migrations, seeders e model factories no Laravel estejam em conformidade com os padrões de arquitetura do Engeapp. Isso promove integridade do banco de dados, testes locais rápidos e atualizações de schema resilientes.

# Instruções

## 1. Migrations de Banco de Dados
- **Classes Anônimas:** Sempre escreva migrations como classes anônimas:
  ```php
  return new class extends Migration { ... };
  ```
- **Verificações de Existência:** Verifique se a tabela já existe antes de criá-la no método `up()` para evitar falhas de execução:
  ```php
  public function up(): void
  {
      if (Schema::hasTable('posts')) {
          return;
      }
      Schema::create('posts', function (Blueprint $table) {
          $table->char('id', 26)->primary(); // padrão ULID
          // ...
      });
  }
  ```
- **Chaves Primárias:** Siga o padrão do projeto para chaves primárias (ex.: ULIDs usando `char('id', 26)->primary()`).
- **Chaves Estrangeiras Resilientes:** Adicione chaves estrangeiras em arquivos de migration separados, nomeados como `add_foreign_keys_to_posts_table.php`. Envolva as declarações de chave estrangeira em um bloco `try/catch` para tornar as configurações de banco de dados resilientes:
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

## 2. Seeders de Banco de Dados
- **Idempotência:** Sempre escreva seeders usando métodos idempotentes (ex.: `updateOrCreate` ou `firstOrCreate`) para evitar registros duplicados quando executados repetidamente:
  ```php
  public function run(): void
  {
      User::updateOrCreate(
          ['email' => 'admin@engeapp.com'],
          ['name' => 'Admin User', 'password' => bcrypt('password')]
      );
  }
  ```
- **Sincronização de Dados de Referência e Produção:** Ao copiar tabelas estáticas/de referência (ex.: cidades, marcas de equipamentos), desabilite a verificação de chaves estrangeiras com `DB::statement('SET FOREIGN_KEY_CHECKS=0')` … `=1` (forma real usada em `database/seeders/TestReferenceDataSeeder.php:91`), use `truncate()` nas tabelas de destino antes de inserir os novos dados.
  - Divida os datasets em blocos (ex.: `500` itens) durante a inserção em massa para evitar erros de limite de memória:
    ```php
    foreach ($sourceData->chunk(500) as $chunk) {
        DB::table($table)->insert(
            $chunk->map(fn ($row) => (array) $row)->toArray()
        );
    }
    ```

## 3. Model Factories
- **Estrutura e Namespace:** Faça o subdiretório de factories corresponder à estrutura de pastas do Model (ex.: `database/factories/Finance/PaymentsFactory.php`).
- **Mapeamento e Tipagem do Model:** Declare a propriedade `$model` explicitamente e use type hints do PHP:
  ```php
  namespace Database\Factories\Finance;

  use App\Models\Finance\Payments;
  use App\Models\Project\Project;
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
- **Geração de Dados:** Use o helper global `fake()` (ex.: `fake()->sentence()`) em vez de `$this->faker` ao gerar valores.
- **Factory States:** Defina métodos auxiliares explícitos e com type hint para os estados comuns do model, retornando `static` e usando `$this->state()`:
  ```php
  public function paid(): static
  {
      return $this->state(fn (array $attributes) => [
          'status' => 'paid',
      ]);
  }
  ```

# Restrições
- NÃO fixe (hardcode) IDs de relacionamento em seeders ou factories. Sempre use relacionamentos de factory (ex.: `User::factory()`).
- NÃO omita os retornos `void` nos métodos `up`/`down` das migrations e no método `run` dos seeders.

## Idioma
- Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill esteja escrito.
