# Laravel Artisan Command Creator

## Goal
Establish consistent guidelines, standards, and practices for constructing, executing, and maintaining Laravel Artisan commands within the Engeapp ecosystem.

## Instructions

### 1. Command Generation & Directory Structure
- Always generate new console commands using the Artisan CLI:
  ```bash
  php artisan make:command {Name}Command
  ```
- Store all console command files inside `app/Console/Commands/`.
- Organize related commands using namespaces split by `:` in the signature (e.g., `app:process-planner-comments-ai`, `trello:register-webhook`).

### 2. Signature & Description Definitions
- Set clear, descriptive signatures and descriptions.
- Prefer using PHP 8 Attributes for command metadata:
  ```php
  use Illuminate\Console\Attributes\Signature;
  use Illuminate\Console\Attributes\Description;

  #[Signature('trello:register-webhook {board? : Trello Board ID}')]
  #[Description('Registra o webhook do EngeApp na API do Trello')]
  class RegisterTrelloWebhook extends Command
  ```
- Clearly document any options and arguments within the signature structure.

### 3. Strict Typing & Dependency Injection
- Enforce strict return types on the `handle()` method. It must return an `int` exit code for execution status:
  - `self::SUCCESS` or `0` for successful runs.
  - `self::FAILURE` or `1` for general failures.
  - `self::INVALID` or `2` for invalid inputs/usage.
- Use method injection within `handle()` to resolve dependencies automatically through the Laravel Service Container (e.g., `public function handle(TrelloService $trelloService): int`).

### 4. Interactive Console I/O (Laravel Prompts)
- For interactive command-line sessions, strictly use the modern functions from the `laravel/prompts` package instead of legacy `$this->ask()`, `$this->confirm()`, or `$this->choice()`.
- Example Prompts usage:
  ```php
  use function Laravel\Prompts\text;
  use function Laravel\Prompts\select;
  use function Laravel\Prompts\confirm;
  use function Laravel\Prompts\spin;

  $boardId = text(
      label: 'Qual o ID do Board no Trello?',
      placeholder: '66e9d8c95de15659b72aac72',
      required: true
  );

  $confirm = confirm('Deseja continuar com o registro?');
  ```
- Wrap long-running operations in `spin()` to give the user a clear and non-blocking visual feedback loader.

### 5. Formatting Console Outputs
- Use standard console output methods for readability:
  - Info: `$this->info('Success message');`
  - Error: `$this->error('Error message');`
  - Warn: `$this->warn('Warning message');`
  - Line: `$this->line('Plain message');`
- Use `$this->table()` to present structured data.
- Use `$this->output->createProgressBar()` for progress bars on iterative/batch actions.

### 6. Logic Isolation & Error Handling
- Keep command classes thin. Command classes should only be responsible for handling Console input, output, and orchestration.
- Delegate all complex business logic, third-party integrations, and extensive database queries to dedicated `Services`, `Actions`, or dispatch them asynchronously via `Jobs`.
- Always wrap execution blocks in `try-catch` segments. Log unexpected critical exceptions with `Log::error()` and display friendly error messages to the terminal using `$this->error()`.

## Constraints
- Do NOT place complex business logic or heavy database transactions directly inside the `handle()` method.
- Do NOT use PHP native output functions such as `echo`, `print_r`, or `var_dump`.
- Do NOT use outdated interactive methods (e.g., `$this->ask()`, `$this->confirm()`, `$this->choice()`). Use `laravel/prompts` instead.
- All codebase comments and PHPDocs MUST be written in Brazilian Portuguese (pt-BR).
