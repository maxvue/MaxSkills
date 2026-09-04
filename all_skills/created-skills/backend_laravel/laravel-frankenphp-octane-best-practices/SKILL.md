---
name: laravel-frankenphp-octane-best-practices
description: "Use when configuring, deploying, or debugging Laravel Octane on FrankenPHP in production, writing stateless PHP code, avoiding memory leaks, managing singletons, and tuning Caddyfile workers. Provides end-to-end guidance, reference architectures, and practical patterns for laravel frankenphp octane best practices."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Laravel Octane (FrankenPHP)

## Objetivo
Fornecer diretrizes, configurações e estratégias para executar, fazer deploy e depurar o Laravel Octane com sucesso, garantindo alta performance, deploys sem downtime e prevenindo memory leaks ou poluição de estado em ambientes de memória persistente. No engeapp o servidor Octane efetivamente usado é o **FrankenPHP** (`.env`/`.env.example` definem `OCTANE_SERVER=frankenphp`, e o script de dev executa `php artisan octane:start --port=4003 --admin-port=4004`, sendo `--admin-port` uma flag específica do FrankenPHP). O default do `config/octane.php` é `'server' => env('OCTANE_SERVER', 'roadrunner')`, mas ele é sobrescrito pelo `.env`; portanto a orientação principal foca no FrankenPHP. RoadRunner/Swoole são alternativas suportadas.

## Instruções

1. **Isolamento de Estado e Prevenção de Memory Leaks**:
   - Garanta que os service providers registrem serviços da aplicação que mantêm estado específico de requisição (como usuário atual, sessão, configuração dinâmica) usando `$this->app->scoped()` em vez de `$this->app->singleton()`. Um binding `scoped` atua como um singleton durante a duração de uma única requisição, mas é destruído e recriado em requisições subsequentes.
   - Se utilizar serviços customizados que persistem estado entre requisições, implemente resetters customizados ou registre classes de reset em `octane.listeners` (lógica de reset via eventos) e nos bindings de `octane.flush` (bindings que devem ser re-resolvidos a cada requisição, descartados antes de cada nova requisição). `octane.warm`, por outro lado, apenas pré-aquece bindings no boot do worker e não serve para reset de estado — não confunda as duas chaves de `config/octane.php`.
   - Limpe manualmente quaisquer arrays ou collections estáticos ao final de um ciclo de requisição escutando o evento `RequestTerminated` do Octane ou definindo uma classe resetter customizada. Nunca declare propriedades estáticas que acumulam dados entre ciclos de requisição (ex: `public static array $cache = [];`) sem resetá-las.
   - **Resolver closures em singletons**: Se um serviço realmente precisa ser um singleton mas necessita de dados específicos da requisição, nunca injete o container da aplicação (`$app`), o `Request` HTTP, o repositório de config (`$config`) ou o gerenciador de sessão (`$session`) diretamente em seu construtor. Injete uma resolver closure (ex: `fn () => $app['request']`) ou resolva dinamicamente dentro dos métodos via helpers (`request()`, `config()`, `auth()`) ou facades.
   - **Estado de pacotes de terceiros**: Verifique que pacotes que mantêm estado interno sejam resetados entre requisições. Se um pacote não for Octane-aware, adicione sua lógica de reset ao array `octane.listeners` sob o evento `RequestReceived`.
   - **Concorrência**: são duas APIs distintas, não confunda. `Octane::concurrently()` despacha via `ProvidesConcurrencySupport`, que só usa dispatcher paralelo (Swoole) quando `Swoole\Http\Server` está disponível; sob **FrankenPHP** (sem Swoole, o runtime real do engeapp — `php -m` não lista `swoole`, `composer.json` não tem `swoole/roadrunner`) ele cai no `SequentialTaskDispatcher` e executa as closures **sequencialmente no mesmo worker** — sem paralelismo nem isolamento. Já a facade `Concurrency` do framework (`Concurrency::run(...)`/`Concurrency::defer(...)`) é outro mecanismo: driver default `'process'`, que dispara processos PHP separados (sem herdar container/estado da requisição). Paralelismo real de `Octane::concurrently()` só existe com Swoole.

2. **Configuração do Worker do FrankenPHP (runtime principal)**:
   - Inicie o worker com:
     `php artisan octane:start --server=frankenphp --workers=4 --max-requests=10000`
     (com `OCTANE_SERVER=frankenphp` no `.env`, a flag `--server` é opcional). O script de dev do projeto usa `php artisan octane:start --port=4003 --admin-port=4004`.
   - **Não escreva o Caddyfile à mão.** O próprio Octane gera e gerencia o Caddyfile a partir do stub `vendor/laravel/octane/src/Commands/stubs/Caddyfile`, parametrizado por variáveis de ambiente (`CADDY_SERVER_WORKER_DIRECTIVE`, `APP_PUBLIC_PATH`, `CADDY_SERVER_ADMIN_PORT` etc.). O engeapp NÃO possui Caddyfile manual — controle os workers exclusivamente pelas **flags de CLI** do comando `octane:start` (`--workers`, `--max-requests`, `--admin-port`), não editando o Caddyfile. **Atenção:** `.env.example` define `OCTANE_WORKERS=auto` e `OCTANE_MAX_REQUESTS=1000`, mas essas variáveis são inertes — nada em `vendor/laravel/octane/` nem em `config/octane.php` as lê (o config só usa `env()` para `OCTANE_SERVER` e `OCTANE_HTTPS`). Os defaults reais vêm das flags do próprio comando (`StartFrankenPhpCommand`: `--admin-port=2019`, `--workers=auto`, `--max-requests=500`). Não presuma que ajustar essas envs muda o comportamento do worker.
   - Estrutura real gerada pelo Octane (referência, para entender o que a ferramenta produz): os workers do FrankenPHP são declarados no **bloco global** (`frankenphp { worker { ... } }`), e o bloco do site usa a diretiva `php_server` para rotear e servir assets estáticos. Um subdiretivo `frankenphp { num_workers N }` dentro do bloco do site NÃO é sintaxe válida.
     ```caddyfile
     {
         # Bloco GLOBAL: workers do FrankenPHP são declarados aqui
         frankenphp {
             worker {
                 file "{$APP_PUBLIC_PATH}/frankenphp-worker.php"
                 {$CADDY_SERVER_WORKER_DIRECTIVE}
             }
         }
     }

     {$CADDY_SERVER_SERVER_NAME} {
         route {
             root * "{$APP_PUBLIC_PATH}"
             encode zstd br gzip
             php_server {
                 index frankenphp-worker.php
                 try_files {path} frankenphp-worker.php
                 resolve_root_symlink
             }
         }
     }
     ```
   - Use a opção `--max-requests` para reiniciar automaticamente os workers depois que eles processam um número definido de requisições, mitigando memory leaks lentos de bibliotecas de terceiros.

3. **Alternativa opcional: RoadRunner ou Swoole**:
   - `config/octane.php:41` tem `'server' => env('OCTANE_SERVER', 'roadrunner')` como default, sobrescrito pelo `.env` para `frankenphp`. Trocar de runtime é apenas mudar `OCTANE_SERVER`; as regras de statelessness desta skill valem igualmente para os três servidores (FrankenPHP, RoadRunner, Swoole).

4. **Deploy (padrão real: Supervisor + restart, não reload)**:
   - O Octane roda sob **Supervisor** no engeapp (programa `octane-engeapp:octane-engeapp_00`). O deploy usa a task `octane:restart` (`deploy.php:187-197`), registrada explicitamente na lista de tasks do `deploy()` (`deploy.php:362`) — não há hook `after(...)` para ela (o único `after()` do arquivo é `after('deploy:failed', 'deploy:unlock')`).
   - A task faz um **restart deliberado**, não um `octane:reload`: `supervisorctl stop octane-engeapp:octane-engeapp_00` → `fuser -k 8000/tcp` (mitigação: o FrankenPHP pode deixar a porta presa) → `sleep 2` → `supervisorctl start octane-engeapp:octane-engeapp_00`. Não trate isso como um problema a corrigir — é a mitigação deliberada do projeto para a porta presa; não substitua por `octane:reload`/systemd/`SIGHUP` a menos que peçam explicitamente.
   - `octane:reload` existe como opção genérica do Octane, mas não é usado no engeapp (zero ocorrências no repositório fora de `vendor`/`node_modules`) — não exija sua adoção.
   - Exemplo real (Deployer), no formato do projeto:
     ```php
     // Em deploy.php
     task('octane:restart', function () : void {
         run('sudo /usr/bin/supervisorctl stop octane-engeapp:octane-engeapp_00 2>/dev/null || true');
         run('sudo fuser -k 8000/tcp 2>/dev/null || true');
         run('sleep 2');
         run('sudo /usr/bin/supervisorctl start octane-engeapp:octane-engeapp_00');
     })->desc('Reiniciar Laravel Octane');

     // Entrada na lista explícita de tasks do deploy:
     desc('Deploy completo do EngeApp');
     task('deploy', [
         // ...
         'octane:restart',
         'horizon:restart',
         'reverb:restart',
         // ...
     ]);
     ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Sem armazenamento direto de request**: NÃO armazene o objeto `Request` atual em singletons ou propriedades de classe que persistem entre requisições.
- **Sem estado não gerenciado**: Nunca use superglobais do PHP (`$_GET`, `$_POST`, `$_SERVER`, `$_SESSION`) ou variáveis `global` diretamente; sempre use os objetos do ciclo de vida da requisição do Laravel.
- **Sem propriedades estáticas não gerenciadas**: NÃO adicione a arrays/collections estáticos durante uma requisição sem resetá-los ao final da requisição.
- **Restart via Supervisor**: siga o padrão real do projeto (task `octane:restart`: stop → `fuser -k 8000/tcp` → sleep → start). Não substitua por `octane:reload`/systemd sem pedido explícito — é mitigação deliberada, não um bug a corrigir.

## Exemplos

### Exemplo: Registrando um Serviço com Estado Corretamente
```php
// Em AppServiceProvider.php
// RUIM: Registrar serviço dependente de requisição como singleton
$this->app->singleton(TenantManager::class, function ($app) {
    return new TenantManager($app['request']->getHost());
});

// BOM: Registrar serviço dependente de requisição como scoped
$this->app->scoped(TenantManager::class, function ($app) {
    return new TenantManager($app['request']->getHost());
});
```

### Exemplo Ruim: Um Singleton armazenando estado específico da requisição em seu construtor
```php
<?php

namespace App\Services;

use Illuminate\Http\Request;

class PaymentService
{
    protected Request $request;

    // VIOLAÇÃO: Injetar Request diretamente no construtor de um Singleton.
    // Este Request persistirá entre requisições/usuários subsequentes!
    public function __construct(Request $request)
    {
        $this->request = $request;
    }

    public function processPayment()
    {
        $ip = $this->request->ip();
        // Lógica de processamento de pagamento...
    }
}
```

### Bom Exemplo: Singleton refatorado com uma resolver closure
```php
<?php

namespace App\Services;

use Closure;
use Illuminate\Http\Request;

class PaymentService
{
    // Injetar uma Closure resolvedora do request
    public function __construct(
        protected Closure $requestResolver
    ) {}

    public function processPayment()
    {
        /** @var Request $request */
        $request = ($this->requestResolver)();
        $ip = $request->ip();
        // Lógica de processamento de pagamento...
    }
}

// Binding no Service Provider:
$this->app->singleton(PaymentService::class, function ($app) {
    return new PaymentService(fn () => $app['request']);
});
```
