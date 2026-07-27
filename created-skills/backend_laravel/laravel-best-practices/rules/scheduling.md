# Task Scheduling Best Practices

## Use `withoutOverlapping()` on Variable-Duration Tasks

Without it, a long-running task spawns a second instance on the next tick, causing double-processing or resource exhaustion.

## Use `onOneServer()` on Multi-Server Deployments

Without it, every server runs the same task simultaneously. Requires a shared cache driver (Redis, database, Memcached).

## Use `runInBackground()` for Concurrent Long Tasks

By default, tasks at the same tick run sequentially. A slow first task delays all subsequent ones. `runInBackground()` runs them as separate processes.

## Use `environments()` to Restrict Tasks

Prevent accidental execution of production-only tasks (billing, reporting) on staging.

```php
Schedule::command('billing:charge')->monthly()->environments(['production']);
```

## Use `takeUntilTimeout()` for Time-Bounded Cursor Processing

`takeUntilTimeout()` é um método de `LazyCollection`, não do agendador — não existe encadeado em `Schedule::command(...)`. Use-o DENTRO do corpo do comando, sobre a coleção lazy que ele processa, para que um comando agendado a cada 15 minutos com um cursor sem limite pare antes de sobrepor a próxima execução:

```php
// Dentro do handle() do Artisan Command, não em routes/console.php
Order::query()->lazy()->takeUntilTimeout(now()->addMinutes(14))->each(function ($order) {
    // processa $order
});
```

## Use Schedule Groups for Shared Configuration

Avoid repeating `->onOneServer()->timezone('America/New_York')` across many tasks.

```php
Schedule::daily()
    ->onOneServer()
    ->timezone('America/New_York')
    ->group(function () {
        Schedule::command('emails:send --force');
        Schedule::command('emails:prune');
    });
```
