---
name: laravel-service-providers-dependency-injection-best-practices
description: "Use when creating or registering Laravel Service Providers, binding services (bind, singleton, scoped) to the Container, PHP 8 constructor property promotion, dependency injection, and Octane memory safety."
author: Johnattas Conrady Gomes Santana
---
## Objetivo

Fornecer diretrizes claras e robustas e padrões de implementação para registrar serviços via Service Providers e resolvê-los usando injeção de dependência no Laravel, garantindo especificamente compatibilidade com ambientes stateless de alta performance como o Laravel Octane.

## Instruções

### 1. Criação e Registro de Service Provider
- Use o Artisan para gerar novos Service Providers:
  ```bash
  php artisan make:provider SignatureServiceProvider --no-interaction
  ```
- Garanta que o novo provider esteja registrado no arquivo `bootstrap/providers.php` (o arquivo padrão de registro de providers do Laravel 11+). No engeapp esse arquivo lista os providers reais do projeto (`AppServiceProvider`, `HorizonServiceProvider`, `SignatureServiceProvider`, `TelescopeServiceProvider`, `TypeScriptTransformerServiceProvider`).

### 2. Escolhendo o Tempo de Vida Correto do Binding
Escolha o método apropriado de registro no container com base no ciclo de vida do objeto:
- **`bind`**: Use quando uma nova instância distinta do serviço é necessária toda vez que ele é resolvido.
- **`singleton`**: Use quando uma única instância compartilhada deve ser reutilizada durante todo o ciclo de vida da aplicação.
  - *Cuidado*: No Laravel Octane, um singleton persiste entre múltiplas requisições de usuário.
- **`scoped`**: Use quando uma única instância é necessária por requisição/ciclo, mas deve ser descartada e reconstruída na próxima requisição. Este é o padrão mais seguro para serviços que carregam dados específicos da requisição.

### 3. Segurança de Memória no Octane e Bindings Stateless
Para prevenir vazamentos de memória e poluição de estado entre requisições no Octane:
- **Nunca** injete o container `Application`, o `Request`, a `Session`, ou o repositório de `Config` diretamente no construtor de um singleton.
- **Sempre** resolva instâncias específicas de requisição de forma lazy usando uma closure dentro do binding do singleton, ou registre o serviço como `scoped`:
  ```php
  // Ruim: resolve o request uma vez no boot da aplicação e o mantém para sempre
  $this->app->singleton(MyService::class, function ($app) {
      return new MyService($app['request']);
  });

  // Bom: resolve o request atual dinamicamente quando o serviço é consumido
  $this->app->singleton(MyService::class, function () {
      return new MyService(fn () => request());
  });

  // Bom: registrado como scoped, então uma nova instância é criada para cada nova requisição.
  // Receber $app['request'] aqui é aceitável justamente porque a instância é descartada
  // a cada requisição (diferente de um singleton, onde isso vazaria estado entre requisições).
  // O engeapp não usa `scoped` hoje — todos os bindings reais são `bind` (veja Exemplos).
  $this->app->scoped(MyService::class, function ($app) {
      return new MyService($app['request']);
  });
  ```
- Não armazene estado nem acrescente dados a propriedades estáticas em serviços registrados como singletons.

### 4. Injeção de Dependência e Promoção de Construtor do PHP 8
- Sempre use **Constructor Property Promotion** para injeção de dependência limpa e legível:
  ```php
  public function __construct(
      protected PaymentGateway $gateway,
      protected LoggerInterface $logger,
  ) {}
  ```

### 5. Escrevendo Testes de Resolução do Container
Verifique que seus bindings resolvem corretamente a partir do Service Container usando Pest. Exemplo baseado no binding real do `SignatureServiceProvider` (serviço de assinatura digital Autentique):
```php
use vinicinbgs\Autentique\Documents;

test('resolve o cliente de assinatura Autentique a partir do container', function () {
    $service = app(Documents::class);

    expect($service)->toBeInstanceOf(Documents::class);
});
```

# Exemplos

### Exemplo: O SignatureServiceProvider real do engeapp
Este é o provider real do projeto. Ele registra o cliente de assinatura digital (Autentique) com `bind`, resolvendo o token de config de forma lazy dentro da closure — nova instância a cada resolução, sem estado compartilhado entre requisições:
```php
<?php

namespace App\Providers;

use Illuminate\Support\ServiceProvider;

class SignatureServiceProvider extends ServiceProvider
{
    /**
     * Register services.
     */
    public function register() : void
    {
        // bind: cada resolução cria uma nova instância; o token é lido dentro da closure.
        $this->app->bind(
            \vinicinbgs\Autentique\Documents::class,
            fn () => new \vinicinbgs\Autentique\Documents((string) config('services.autentique.token'))
        );
    }

    /**
     * Bootstrap services.
     */
    public function boot() : void
    {
        //
    }
}
```

### Exemplo: Consumindo o Serviço Registrado via DI
```php
<?php

namespace App\Http\Controllers;

use vinicinbgs\Autentique\Documents;
use Illuminate\Http\JsonResponse;

class SignatureController extends Controller
{
    // Constructor Property Promotion do PHP 8 — o container injeta o binding automaticamente.
    public function __construct(
        protected Documents $documents
    ) {}

    public function show(string $documentId) : JsonResponse
    {
        return response()->json(
            $this->documents->listById($documentId)
        );
    }
}
```

## Restrições

- **NÃO** use `singleton` para qualquer serviço que processe ou mantenha dados específicos de requisição, a menos que as dependências sejam resolvidas usando closures.
- **NÃO** mute propriedades estáticas em classes dentro do container.
- **NÃO** instancie serviços manualmente usando `new` dentro de Controllers ou Models se eles devem ser gerenciados e injetados pelo container.
- **NÃO** contorne a injeção via construtor em favor do helper `app()` dentro de classes de serviço (prefira DI adequada via construtor).

## Idioma
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
