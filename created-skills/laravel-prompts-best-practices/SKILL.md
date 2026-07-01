---
name: laravel-prompts-best-practices
description: Use when creating, modifying, or styling interactive console/CLI inputs using Laravel Prompts. Triggers on text prompts, password fields, select/confirm prompts, spinner loading screens, multi-select questions, and validation in CLI commands.
---

# Laravel Prompts Best Practices

## Goal
Establish solid guidelines and consistent patterns for utilizing the Laravel Prompts library in interactive Artisan commands, improving the developer and operator terminal experience.

## Instructions
1. **Importing Functions**:
   - Always import specific prompt functions using the `use function` syntax rather than calling them statically or via fully qualified names.
     ```php
     use function Laravel\Prompts\text;
     use function Laravel\Prompts\select;
     use function Laravel\Prompts\confirm;
     use function Laravel\Prompts\spin;
     use function Laravel\Prompts\progress;
     ```

2. **Prompt Types & Usage**:
   - **Text**: For simple text inputs. Provide a clear `label`, optional `placeholder`, and `hint`.
   - **Password**: For sensitive data inputs. Prevents characters from being displayed.
   - **Confirm**: For boolean decisions. Always provide a logical `default` value (true/false).
   - **Select**: For choosing a single option from a predefined list.
   - **Multiselect**: For choosing multiple options.
   - **Suggest**: Auto-completes input from an array of values as the user types.
   - **Search**: For search-as-you-type options, ideal for database lookups.
   - **Spin**: Show a loading spinner during long-running tasks.
   - **Progress**: Show a progress bar when iterating over collections.

3. **Input Validation**:
   - Use the `validate` argument with a closure to validate inputs. Return a string describing the error if invalid, or `null` if valid.
     ```php
     $email = text(
         label: 'What is your email address?',
         validate: fn (string $value) => match (true) {
             ! filter_var($value, FILTER_VALIDATE_EMAIL) => 'The email address is invalid.',
             default => null
         }
     );
     ```

4. **Non-Interactive Fallbacks**:
   - Ensure CLI commands support non-interactive execution (e.g., CI/CD, scheduled tasks).
   - Fall back to checking command arguments or options when the input is not interactive.
     ```php
     $name = $this->argument('name') ?? text('What is your name?');
     ```

5. **Visual Output Elements**:
   - Use built-in alert functions `info()`, `warning()`, `error()`, and `note()` for styled output instead of raw echo or `$this->info()`.

## Constraints
- **Do not** use legacy Symfony Console inputs like `$this->ask()` or `$this->confirm()` unless Laravel Prompts is incompatible with the environment.
- **Do not** block the terminal with long-running synchronous tasks without using `spin()` or `progress()` to give feedback.
- **Do not** write custom ASCII loaders or spinners. Use the native `spin()` function.
- **Do not** omit validation for critical inputs (e.g., database IDs, emails, file paths).
