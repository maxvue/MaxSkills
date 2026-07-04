---
name: laravel-pulse-custom-recorders-and-cards
description: Use when designing, building, or modifying Laravel Pulse custom recorders, custom telemetry dashboards, or custom Pulse cards. Triggers on extending Pulse Recorder, creating custom Pulse blade components, customizing storage endpoints, and configuring Pulse recorders in pulse.php.
---

# Laravel Pulse Custom Recorders and Cards

## Goal
Establish guidelines, patterns, and implementation examples for extending Laravel Pulse with custom telemetry recorders and visual dashboard cards within the Engeapp ecosystem.

## Instructions
1. **Custom Recorders Creation:**
   - Create a custom recorder class extending `Laravel\Pulse\Recorders\Recorder`.
   - Implement the `record` or class-specific method to intercept events (e.g. using Laravel event listeners or middleware).
   - Use the `Laravel\Pulse\Pulse` facade's methods such as `Pulse::record()` or `Pulse::set()` to store metrics.
   - For example, to record AI agent costs, record a type (e.g., `ai_cost`), key (e.g., user ID or agent model name), value (cost or tokens used), and optional timestamp.
   - Use appropriate database column types and keys.
   - Ensure the recorder is registered under the `recorders` array in `config/pulse.php`.

2. **Custom Cards (Dashboard Components):**
   - Create a Livewire component representing the Pulse card.
   - Use the `Laravel\Pulse\Livewire\Card` base class.
   - Inject the Pulse data into the view using the `Pulse` service. Use `Pulse::aggregate()` or other telemetry query methods.
   - Create a corresponding Blade view using Pulse's native layout helpers and Tailwind classes (e.g., `<x-pulse::card>`, `<x-pulse::card-header>`, etc.).
   - Make sure custom cards follow the visual style of native Pulse cards (dark/light themes, typography, spacing).
   - Register the custom Livewire component inside a service provider or directly render it in the dashboard view.

3. **Performance and Storage Management:**
   - Define data retention policies in `config/pulse.php` (e.g., `trim` configurations).
   - Set up scheduled cleanups using `pulse:clear` or `pulse:work` if necessary.
   - Add proper database indexes on custom tables if custom storage drivers are used.
   - Ensure high-frequency recordings are sampled appropriately using the `sample_rate` configuration option.

4. **Security and Authorization:**
   - Configure a custom authorization Gate in `AuthServiceProvider` (or `AppServiceProvider`) using `Pulse::auth()`.
   - Restrict access to the `/pulse` route in production to authorized administrators.

## Examples
See the following examples in the `examples/` directory:
- [custom-recorder.php](file:///home/johnattas/GitHub/Skills/created-skills/laravel-pulse-custom-recorders-and-cards/examples/custom-recorder.php): Boilerplate code for creating a custom Pulse recorder (monitoring external API latency and AI costs).
- [pulse-card.blade.php](file:///home/johnattas/GitHub/Skills/created-skills/laravel-pulse-custom-recorders-and-cards/examples/pulse-card.blade.php): Blade template using Livewire to render a custom Pulse dashboard card.

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- DO NOT query the Pulse database tables directly from the application code; always use the `Pulse` facade query APIs.
- DO NOT perform heavy database writes or blocking synchronous external calls inside custom recorders. Use async queuing or lightweight in-memory storage (e.g., Redis ingest driver) if high performance is required.
- DO NOT expose the Pulse dashboard publicly; always secure it behind a Gate.
- DO NOT duplicate native Pulse recorders (e.g., do not rewrite slow queries or server health metrics).
