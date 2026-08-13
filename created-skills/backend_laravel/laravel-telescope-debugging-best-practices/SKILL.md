---
name: laravel-telescope-debugging-best-practices
description: "Use when configuring, optimizing, or debugging with Laravel Telescope in Engeapp. Covers config/telescope.php watchers, TelescopeServiceProvider filters, hideSensitiveRequestDetails, viewTelescope gate, and entry pruning."
---
# Objetivo
Padronizar como configurar, otimizar e depurar com o Laravel Telescope no engeapp, garantindo telemetria útil (queries, requests, jobs, exceções, comandos, cache) sem inchar o banco nem vazar dados sensíveis. O engeapp usa `laravel/telescope ^5.20`.

# Como o Telescope está montado no engeapp

## 1. Registro do provider
O `App\Providers\TelescopeServiceProvider` é registrado **incondicionalmente** em `bootstrap/providers.php` (padrão Laravel 11+/13), junto dos demais providers da aplicação:
```php
// bootstrap/providers.php
return [
    App\Providers\AppServiceProvider::class,
    App\Providers\HorizonServiceProvider::class,
    App\Providers\SignatureServiceProvider::class,
    App\Providers\TelescopeServiceProvider::class,
    App\Providers\TypeScriptTransformerServiceProvider::class,
];
```
Não registre o provider dentro de um bloco `if ($this->app->environment('local'))` no `register()`, e não registre `Laravel\Telescope\TelescopeServiceProvider` manualmente — o provider da aplicação já estende `TelescopeApplicationServiceProvider`. O Telescope roda em **todos** os ambientes; o que muda por ambiente é o que ele **grava**, controlado por `Telescope::filter()` (ver seção 2), e a **chave mestra** `TELESCOPE_ENABLED` no `.env` (`config/telescope.php` → `'enabled' => env('TELESCOPE_ENABLED', true)`).

## 2. Controle de gravação por ambiente (`Telescope::filter` + `Telescope::night`)
O mecanismo real de restrição está no `register()` do provider, não em registro condicional. Fora do ambiente `local`, apenas entradas relevantes são gravadas:
```php
// app/Providers/TelescopeServiceProvider.php
public function register() : void
{
    Telescope::night();

    $this->hideSensitiveRequestDetails();

    $isLocal = $this->app->environment('local');

    Telescope::filter(fn (IncomingEntry $entry) => $isLocal ||
               $entry->isReportableException() ||
               $entry->isFailedRequest() ||
               $entry->isFailedJob() ||
               $entry->isScheduledTask() ||
               $entry->hasMonitoredTag());
}
```
- `Telescope::night()` aplica o tema escuro por padrão.
- `Telescope::filter(...)`: em `local` grava tudo; nos demais ambientes grava só exceções reportáveis, requests/jobs falhos, tarefas agendadas e entradas com tag monitorada. Mantenha esse contrato ao ajustar filtros — não passe a gravar tudo em produção.

## 3. Sanitização de dados sensíveis (`hideSensitiveRequestDetails`)
`hideSensitiveRequestDetails()` é um **método protected** do provider (não uma chamada estática do Telescope). Ele faz early-return em `local` (onde não há sanitização, para facilitar debug) e só fora de `local` chama os métodos estáticos que escondem parâmetros/headers:
```php
// app/Providers/TelescopeServiceProvider.php
protected function hideSensitiveRequestDetails() : void
{
    if ($this->app->environment('local')) {
        return;
    }

    Telescope::hideRequestParameters(['_token']);

    Telescope::hideRequestHeaders([
        'cookie',
        'x-csrf-token',
        'x-xsrf-token',
    ]);
}
```
Ao lidar com novos payloads sensíveis (senhas, segredos de integração, PII), **adicione as chaves reais a estas listas** dentro de `hideSensitiveRequestDetails()`. Não confunda o método (que decide o quê/quando) com as chamadas estáticas `Telescope::hideRequestParameters()` / `Telescope::hideRequestHeaders()` (que efetivam a ocultação).

## 4. Gate de acesso (`viewTelescope`)
O acesso ao dashboard fora de `local` é controlado pelo gate `viewTelescope` no método `gate()`. Hoje a lista de e-mails está vazia (só `local` acessa):
```php
protected function gate() : void
{
    Gate::define('viewTelescope', fn (User $user) => in_array($user->email, [
        //
    ]));
}
```
Para liberar acesso em ambientes não locais, inclua os e-mails autorizados nessa lista — nunca afrouxe o gate para retornar `true` sem verificação.

# Configuração dos watchers (`config/telescope.php`)
Valores reais em uso no engeapp (confirme antes de alterar):
- **QueryWatcher:** `'slow' => 100` (ms, marca queries lentas) e `'ignore_packages' => true` (foca nas queries da aplicação).
- **ModelWatcher:** `'hydrations' => true`. Introduz overhead em grandes operações Eloquent; mantenha ligado para investigar hidratação/memória e desligue se virar gargalo local.
- **RequestWatcher:** `'size_limit' => env('TELESCOPE_RESPONSE_SIZE_LIMIT', 64)` (KB). Reduza via env se respostas grandes estiverem inchando as tabelas.
- **GateWatcher:** também usa `'ignore_packages' => true`.
- **DumpWatcher:** habilitado (`TELESCOPE_DUMP_WATCHER`), com `'always' => env('TELESCOPE_DUMP_WATCHER_ALWAYS', false)`.
- Cada watcher tem sua própria env (`TELESCOPE_QUERY_WATCHER`, `TELESCOPE_CACHE_WATCHER`, etc.); desabilite watchers de alta frequência via env se o overhead atrapalhar o desenvolvimento.

# Poda e tamanho do banco
As tabelas `telescope_entries`, `telescope_entries_tags` e `telescope_monitoring` crescem rápido. **Atualmente não há agendamento de `telescope:prune` em `routes/console.php`** — se a base crescer, adicione um:
```php
// routes/console.php
use Illuminate\Support\Facades\Schedule;

Schedule::command('telescope:prune --hours=24')->daily();
```
Alternativas: rodar `php artisan telescope:prune` manualmente, ou trocar `TELESCOPE_DRIVER` para um driver mais leve se o custo de escrita virar gargalo local.

# Restrições
- Não passe a gravar todas as entradas fora de `local`: preserve o contrato do `Telescope::filter()` (só exceções/requests/jobs falhos, tarefas agendadas e tags monitoradas).
- Não afrouxe o gate `viewTelescope`; libere acesso não local apenas incluindo e-mails específicos na lista.
- Nunca registre credenciais, segredos de integração, certificados mTLS ou senhas nos parâmetros/cabeçalhos do Telescope — estenda `hideSensitiveRequestDetails()` quando surgirem novos campos sensíveis.
- Use `TELESCOPE_ENABLED=false` (ou as envs de watcher) para silenciar o Telescope ao rodar migrations/testes quando o ruído/overhead atrapalhar.
- Comentários de código sempre em pt-BR.
- **Idioma:** comunique-se com o usuário humano sempre em Português (pt-BR).
