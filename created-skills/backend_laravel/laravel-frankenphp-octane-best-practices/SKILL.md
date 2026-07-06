---
name: laravel-frankenphp-octane-best-practices
description: "Use when configuring, deploying, or debugging Laravel Octane on FrankenPHP (used in engeapp; also RoadRunner/Swoole), and when writing or reviewing PHP for Octane statelessness. Triggers on Octane config, FrankenPHP/Caddyfile worker setup, deploy scripts restarting Octane, and singletons, static properties, memory leaks, or shared-state leakage between requests."
---

# Boas Práticas de Laravel Octane (FrankenPHP)

## Objetivo
Fornecer diretrizes, configurações e estratégias para executar, fazer deploy e depurar o Laravel Octane com sucesso, garantindo alta performance, deploys sem downtime e prevenindo memory leaks ou poluição de estado em ambientes de memória persistente. No engeapp o servidor Octane efetivamente usado é o **FrankenPHP** (`.env`/`.env.example` definem `OCTANE_SERVER=frankenphp`, e o script de dev executa `php artisan octane:start --port=4003 --admin-port=4004`, sendo `--admin-port` uma flag específica do FrankenPHP). O default do `config/octane.php` é `'server' => env('OCTANE_SERVER', 'roadrunner')`, mas ele é sobrescrito pelo `.env`; portanto a orientação principal foca no FrankenPHP. RoadRunner/Swoole são alternativas suportadas.

## Instruções

1. **Isolamento de Estado e Prevenção de Memory Leaks**:
   - Garanta que os service providers registrem serviços da aplicação que mantêm estado específico de requisição (como usuário atual, sessão, configuração dinâmica) usando `$this->app->scoped()` em vez de `$this->app->singleton()`. Um binding `scoped` atua como um singleton durante a duração de uma única requisição, mas é destruído e recriado em requisições subsequentes.
   - Se utilizar serviços customizados que persistem estado entre requisições, implemente resetters customizados ou registre classes de reset em `octane.listeners` ou `octane.warm` dentro de `config/octane.php`.
   - Limpe manualmente quaisquer arrays ou collections estáticos ao final de um ciclo de requisição escutando o evento `RequestTerminated` do Octane ou definindo uma classe resetter customizada. Nunca declare propriedades estáticas que acumulam dados entre ciclos de requisição (ex: `public static array $cache = [];`) sem resetá-las.
   - **Resolver closures em singletons**: Se um serviço realmente precisa ser um singleton mas necessita de dados específicos da requisição, nunca injete o container da aplicação (`$app`), o `Request` HTTP, o repositório de config (`$config`) ou o gerenciador de sessão (`$session`) diretamente em seu construtor. Injete uma resolver closure (ex: `fn () => $app['request']`) ou resolva dinamicamente dentro dos métodos via helpers (`request()`, `config()`, `auth()`) ou facades.
   - **Estado de pacotes de terceiros**: Verifique que pacotes que mantêm estado interno sejam resetados entre requisições. Se um pacote não for Octane-aware, adicione sua lógica de reset ao array `octane.listeners` sob o evento `RequestReceived`.
   - **Concorrência / `Octane::concurrently`**: Ao executar tarefas via a facade `Concurrency` (`Concurrency::run(...)` / `Concurrency::defer(...)`) ou `Octane::concurrently()`, lembre-se de que elas executam em processos worker isolados. Garanta que as conexões de banco de dados e a integridade transacional sejam mantidas corretamente dentro de cada tarefa concorrente.

2. **Configuração do Worker do FrankenPHP (runtime principal)**:
   - O FrankenPHP é o servidor efetivamente usado no engeapp (`.env` define `OCTANE_SERVER=frankenphp`, sobrescrevendo o default `roadrunner` do `config/octane.php`). Inicie-o com:
     `php artisan octane:start --server=frankenphp --workers=4 --max-requests=10000`
     (com `OCTANE_SERVER=frankenphp` no `.env`, a flag `--server` é opcional). O script de dev do projeto usa `php artisan octane:start --port=4003 --admin-port=4004` — a flag `--admin-port` é específica do FrankenPHP e expõe o endpoint de administração/reload do worker.
   - **Não escreva o Caddyfile à mão.** O próprio Octane gera e gerencia o Caddyfile a partir do stub `vendor/laravel/octane/src/Commands/stubs/Caddyfile`, parametrizado por variáveis de ambiente (`CADDY_SERVER_WORKER_DIRECTIVE`, `APP_PUBLIC_PATH`, `CADDY_SERVER_ADMIN_PORT` etc.). O engeapp NÃO possui Caddyfile manual — controle os workers pelas flags de CLI (`--workers`, `--max-requests`, `--admin-port`) e pelas variáveis de ambiente, não editando o Caddyfile.
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
   - Relevante apenas se você trocar o runtime. O RoadRunner é o valor default do `config/octane.php`, mas o engeapp o sobrescreve para FrankenPHP no `.env`. Para usá-lo, defina `OCTANE_SERVER=roadrunner` e inicie com `php artisan octane:start --server=roadrunner --workers=4 --max-requests=10000`.
   - O RoadRunner é distribuído como um único binário `rr` (instalado via `./vendor/bin/rr get-binary` ou o pacote `spiral/roadrunner-cli`) e é controlado por um arquivo de config `.rr.yaml` na raiz do projeto. O Octane gerencia/gera esse arquivo; mantenha-o em sincronia com suas flags `--workers`/`--port` e evite editar manualmente valores que o Octane deriva das flags de CLI.
   - O Swoole também é suportado via `OCTANE_SERVER=swoole`; as regras de statelessness abaixo se aplicam identicamente aos três servidores.

4. **Deploy e Reloads sem Downtime**:
   - Ao realizar um deploy, não simplesmente mate o servidor. Em vez disso, recarregue os workers de forma graciosa.
   - Use o comando Artisan de reload em seu script de deploy:
     ```bash
     php artisan octane:reload
     ```
   - Garanta que seu workflow de deploy (ex: deployer, scripts bash) chame `octane:reload` após cachear config, rotas e views.
   - Se estiver executando o Octane (RoadRunner ou FrankenPHP) como um serviço systemd, configure o systemd para suportar reloads graciosos (ex: enviando `SIGHUP`/`SIGUSR1`, ou executando `octane:reload`, para recarregar os workers sem descartar requisições em andamento).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Sem armazenamento direto de request**: NÃO armazene o objeto `Request` atual em singletons ou propriedades de classe que persistem entre requisições.
- **Sem estado não gerenciado**: Nunca use superglobais do PHP (`$_GET`, `$_POST`, `$_SERVER`, `$_SESSION`) ou variáveis `global` diretamente; sempre use os objetos do ciclo de vida da requisição do Laravel.
- **Sem propriedades estáticas não gerenciadas**: NÃO adicione a arrays/collections estáticos durante uma requisição sem resetá-los ao final da requisição.
- **Sem restarts abruptos durante tráfego de usuários**: NÃO execute `octane:stop` seguido de `octane:start` em scripts de deploy de produção a menos que necessário, pois isso causa downtime. Sempre prefira `octane:reload`.

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
    // OPÇÃO A: Injetar uma Closure resolvedora do request
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

### Bom Exemplo: Singleton resolvendo estado dinamicamente (stateless)
```php
<?php

namespace App\Services;

class PaymentService
{
    // OPÇÃO B: Nenhuma dependência no construtor. Resolva os helpers dinamicamente.
    public function __construct() {}

    public function processPayment()
    {
        // Resolve o request dinamicamente por chamada de método
        $ip = request()->ip();
        // Lógica de processamento de pagamento...
    }
}
```

### Exemplo: Reload Gracioso em Script do Deployer
```php
// Em deploy.php (Deployer)
task('deploy:octane_reload', function () {
    run('{{bin/php}} {{release_path}}/artisan octane:reload');
})->desc('Reload Laravel Octane workers gracefully');

after('deploy:publish', 'deploy:octane_reload');
```
