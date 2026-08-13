---
name: laravel-task-scheduling-best-practices
description: "Use when creating, configuring, or debugging Laravel task schedules in routes/console.php, cron jobs, overlapping prevention, background tasks, scheduler logging, and Studio Totem integration. Covers objectives and core workflows."
---
# Agendamento de Tarefas no Laravel — Boas Práticas

## Objetivo
Estabelecer diretrizes sólidas e padrões consistentes para agendamento, monitoramento, controle de concorrência e gerenciamento de logs de tarefas em background no Laravel 13 (usando a facade `Schedule` em `routes/console.php`) e no Studio Totem.

## Instruções

### 1. Registro e Localização das Tarefas
- Sempre registre todas as tarefas agendadas dentro de `routes/console.php` usando a facade `Illuminate\Support\Facades\Schedule`.
- Não defina lógica de negócio complexa ou consultas ao banco de dados dentro das closures do scheduler em `routes/console.php`.
- **Padrão Preferido:** Encapsule a lógica de execução dentro de um Artisan Command dedicado (criado via `php artisan make:command`) ou um Queue Job, e então agende-o usando:
  ```php
  use Illuminate\Support\Facades\Schedule;

  Schedule::command('system:cleanup-temp-files')->daily();
  Schedule::job(new CleanAbandonedCartsJob)->hourly();
  ```

### 2. Concorrência e Prevenção de Sobreposição
- Para comandos que processam quantidades substanciais de dados ou interagem com APIs externas, sempre previna a sobreposição de execução para evitar esgotamento de recursos do servidor e race conditions:
  ```php
  Schedule::command('sync:external-crm')
      ->hourly()
      ->withoutOverlapping(60); // Define um tempo de expiração do lock em minutos
  ```
- **Totem:** Para operações sensíveis via UI do Totem, habilite a configuração **"Don't Overlap"** para aplicar a lógica nativa de `.withoutOverlapping()`.
- Use `runInBackground()` quando você tiver múltiplos comandos agendados executando ao mesmo tempo e quiser que eles executem de forma assíncrona em vez de sequencial:
  ```php
  Schedule::command('reports:compile')->daily()->runInBackground();
  ```
- Se a aplicação rodar em um ambiente multi-servidor com balanceamento de carga, garanta que o comando execute apenas em um único servidor utilizando `onOneServer()` (requer um driver de cache de banco de dados ou redis como o cache store padrão).

### 3. Gerenciamento de Logs e Controle de Saída
- **Redirecionamento de Saída:** Nunca deixe as saídas das tarefas desaparecerem. Sempre anexe as saídas padrão e os streams de erro a arquivos de log dedicados ou direcione-os para handlers customizados.
- **Hooks de Erro:** Utilize os hooks de callback de falha e sucesso para registrar anomalias ou disparar alertas.
- **Limpeza dos Logs no Banco do Totem (Política de Retenção):** O Totem registra cada status de execução e saída na tabela `task_results` (o nome pode ganhar prefixo se `TOTEM_TABLE_PREFIX` estiver definido; no engeapp está vazio, então é `task_results`).
- **Prefira o auto-cleanup nativo por tarefa.** Cada tarefa do Totem tem os campos `auto_cleanup_num` e `auto_cleanup_type` (colunas na tabela `tasks`, editáveis pela própria UI do Totem no formulário da tarefa). O método `Task::autoCleanup()` roda automaticamente após cada execução: com `auto_cleanup_num > 0` ele poda a `task_results` daquela tarefa, ou mantendo apenas os N resultados mais recentes (`auto_cleanup_type = 'results'`), ou apagando resultados mais antigos que N dias (qualquer outro `auto_cleanup_type`). **Atenção ao off-by-one:** o corte usa `Carbon::now()->subDays($auto_cleanup_num - 1)`, ou seja, com `auto_cleanup_num = N` o Totem mantém os resultados dos últimos N-1 dias completos, não N — configure a retenção considerando essa diferença. Configure essa retenção por tarefa na UI em vez de agendar deleções manuais — isso mantém a poda vinculada à tarefa e limitada ao seu próprio histórico.
- **Poda manual só como fallback.** O Totem **não** expõe comando artisan de limpeza (registra apenas `schedule:list` e `totem:assets`). Portanto, use uma deleção agendada apenas para schedules que NÃO passam pelo Totem (registrados direto em `routes/console.php`), ou para uma varredura global de segurança:
  ```php
  // routes/console.php — fallback para o que não é gerenciado pelo Totem
  use Illuminate\Support\Facades\DB;

  Schedule::call(fn () => DB::table('task_results')
      ->where('created_at', '<', now()->subDays(7))->delete())->daily();
  ```

### 4. Condições de Execução e Ambientes
- Imponha estritamente os limites de ambiente para evitar que tarefas destrutivas ou atualizações mock executem em produção:
  ```php
  Schedule::command('test:reset-sandbox')
      ->daily()
      ->environments(['local', 'staging']);
  ```
- Use restrições condicionais dinâmicas (`when()` ou `skip()`) para determinar a execução dinamicamente.
- **Configurações de Ambiente do Totem:** Respeite as configurações dentro de `config/totem.php`. Use variáveis `.env` para alternar parâmetros entre ambientes (`TOTEM_WEB_MIDDLEWARE`, `TOTEM_WEB_ROUTE_PREFIX`, `TOTEM_TABLE_PREFIX`, `TOTEM_DATABASE_CONNECTION`).

### 5. Segurança e Autenticação do Dashboard do Totem
- O dashboard do Laravel Totem é servido no prefixo de rota especificado por `TOTEM_WEB_ROUTE_PREFIX` (o padrão é `/tasks`).
- O acesso deve ser estritamente restrito. **Apenas o closure registrado via `Totem::auth()` protege a rota** — é o único callback consumido pelo middleware `Authenticate` do pacote (`Totem::check($request)` executa exclusivamente `static::$authUsing`, definido por `Totem::auth()`). Implemente-o em `AppServiceProvider.php`:
  ```php
  use Studio\Totem\Totem;

  Totem::auth(function () {
      $user = auth()->user();
      return $user && ($user->is_developer || in_array($user->email, $allowedEmails));
  });
  ```
- O engeapp também define um `Gate::define('viewTotem', ...)` em `AppServiceProvider.php` espelhando o `viewPulse`, mas esse gate é convenção interna do projeto e **não tem nenhum consumidor** (nem back-end, nem front-end) — não é ele que protege o dashboard.
- **Alerta operacional:** se você definir apenas o Gate `viewTotem` e esquecer de chamar `Totem::auth()`, `Totem::check()` cai no fallback `app()->environment('local')` e o dashboard fica liberado sem autenticação em ambiente local (e bloqueado por `abort(403)` em qualquer outro ambiente, mesmo para usuários autorizados).

### 6. Design Padrão de Artisan Command e Chamadas a APIs Externas
- Qualquer comando registrado no Totem ou Laravel deve definir assinaturas explícitas e descritivas.
- Retorne exit codes padrão (`self::SUCCESS` ou `0` para sucesso; `self::FAILURE` ou `1` para falhas).
- **Evitando Bloqueios:** Os comandos não devem bloquear a execução indefinidamente. Se um comando realiza requisições HTTP a APIs externas, defina timeouts explícitos:
  ```php
  use Illuminate\Support\Facades\Http;
  Http::timeout(10)->get('https://api.external.service/data');
  ```
- Para operações extremamente pesadas, desacople o comando do scheduler despachando um Job enfileirado em background.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NUNCA** omita `withoutOverlapping()` para tarefas de limpeza ou sincronização que possam demorar mais do que seu intervalo de execução.
- **NUNCA** use `echo` puro do PHP ou saídas padrão dentro das closures de comando do scheduler; sempre utilize logging estruturado via `Log::channel()` apontando para um canal **existente** em `config/logging.php` (ex.: `jobs` ou `automations`). Não invente canais: `Log::channel('scheduler')` lança `InvalidArgumentException` em runtime porque esse canal não existe no engeapp. Se precisar de um canal dedicado, crie-o antes em `config/logging.php`.
- **NUNCA** exponha a rota do dashboard `/tasks` (ou o prefixo configurado) ao público. Proteja-a atrás de gates de autenticação.
- **NUNCA** agende um comando de alta frequência sem política de retenção — ver seção 3 para as opções (auto-cleanup nativo do Totem vs. deleção agendada de fallback).
- **NÃO** execute chamadas bloqueantes a APIs de terceiros dentro de comandos agendados sem um timeout HTTP explícito.

## Exemplos

### Agendamento em routes/console.php
```php
<?php

use Illuminate\Support\Facades\Schedule;
use Illuminate\Support\Facades\Log;
use App\Jobs\CleanupInactiveUsersJob;

// 1. Comando Artisan agendado com proteção contra sobreposição e logging de saída
Schedule::command('geckodriver:cleanup-ports')
    ->everyFiveMinutes()
    ->withoutOverlapping(10)
    ->runInBackground()
    ->appendOutputTo(storage_path('logs/geckodriver-cleanup.log'))
    ->onFailure(function () {
        Log::channel('jobs')->error('Geckodriver ports cleanup task failed.');
    });

// 2. Queue Job agendado para rodar em um único servidor, restrito à produção
Schedule::job(new CleanupInactiveUsersJob)
    ->dailyAt('02:00')
    ->onOneServer()
    ->environments(['production']);
```
