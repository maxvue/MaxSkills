---
name: laravel-task-scheduling-best-practices
description: Use when creating, configuring, auditing, or debugging Laravel task schedules (Schedule) in routes/console.php, managing cron jobs, preventing overlapping processes, configuring background executions, handling task outputs, logging scheduler errors, optimizing recurrent backend tasks, and configuring/maintaining Studio Totem for task management.
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
- **Prefira o auto-cleanup nativo por tarefa.** Cada tarefa do Totem tem os campos `auto_cleanup_num` e `auto_cleanup_type` (colunas na tabela `tasks`, editáveis pela própria UI do Totem no formulário da tarefa). O método `Task::autoCleanup()` roda automaticamente após cada execução: com `auto_cleanup_num > 0` ele poda a `task_results` daquela tarefa, ou mantendo apenas os N resultados mais recentes (`auto_cleanup_type = 'results'`), ou apagando resultados mais antigos que N dias (qualquer outro `auto_cleanup_type`). Configure essa retenção por tarefa na UI em vez de agendar deleções manuais — isso mantém a poda vinculada à tarefa e limitada ao seu próprio histórico.
- **Poda manual só como fallback.** O Totem **não** expõe comando artisan de limpeza (registra apenas `schedule:list` e `totem:assets`). Portanto, use uma deleção agendada apenas para schedules que NÃO passam pelo Totem (registrados direto em `routes/console.php`), ou para uma varredura global de segurança:
  ```php
  // routes/console.php — fallback para o que não é gerenciado pelo Totem
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
- O acesso deve ser estritamente restrito. Implemente a autorização da rota em `AppServiceProvider.php` usando `Totem::auth()` e o gate `viewTotem`:
  ```php
  use Studio\Totem\Totem;
  use Illuminate\Support\Facades\Gate;

  Gate::define('viewTotem', fn ($user) => $user->is_developer || in_array($user->email, $allowedEmails));

  Totem::auth(function () {
      $user = auth()->user();
      return $user && ($user->is_developer || in_array($user->email, $allowedEmails));
  });
  ```

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
- **NUNCA** escreva processamento pesado, requisições HTTP ou consultas cruas ao banco de dados diretamente dentro das closures de `routes/console.php`. Sempre delegue a um Artisan command ou a um Job de fila.
- **NUNCA** omita `withoutOverlapping()` para tarefas de limpeza ou sincronização que possam demorar mais do que seu intervalo de execução.
- **NUNCA** execute comandos sem especificar limites de ambiente se eles modificam dados de teste ou fazem mock de integrações com APIs externas.
- **NUNCA** use `echo` puro do PHP ou saídas padrão dentro das closures de comando do scheduler; sempre utilize logging estruturado via `Log::channel()` apontando para um canal **existente** em `config/logging.php` (ex.: `jobs` ou `automations`). Não invente canais: `Log::channel('scheduler')` lança `InvalidArgumentException` em runtime porque esse canal não existe no engeapp. Se precisar de um canal dedicado, crie-o antes em `config/logging.php`.
- **NUNCA** exponha a rota do dashboard `/tasks` (ou o prefixo configurado) ao público. Proteja-a atrás de gates de autenticação.
- **NUNCA** agende um comando de alta frequência sem configurar uma política de retenção de logs correspondente. Para tarefas gerenciadas pelo Totem, prefira o auto-cleanup nativo por tarefa (`auto_cleanup_num`/`auto_cleanup_type`, configurável na UI); para o restante, use uma deleção agendada na `task_results` (o Totem não tem comando `totem:cleanup`).
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
