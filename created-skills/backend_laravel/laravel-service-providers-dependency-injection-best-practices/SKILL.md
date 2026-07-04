---
name: laravel-service-providers-dependency-injection-best-practices
description: Use when creating, modifying, or registering Laravel Service Providers, binding services (bind, singleton, scoped) to the Service Container, resolving dependencies via dependency injection, or ensuring memory safety and Octane compatibility in singleton bindings.
---

# Objetivo

Fornecer diretrizes claras e robustas e padrões de implementação para registrar serviços via Service Providers e resolvê-los usando injeção de dependência no Laravel, garantindo especificamente compatibilidade com ambientes stateless de alta performance como o Laravel Octane.

# Instruções

### 1. Criação e Registro de Service Provider
- Use o Artisan para gerar novos Service Providers:
  ```bash
  php artisan make:provider PaymentServiceProvider --no-interaction
  ```
- Garanta que o novo provider esteja registrado no arquivo `bootstrap/providers.php` (o arquivo padrão de registro de providers do Laravel 11+).

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

  // Bom: registrado como scoped, então uma nova instância é criada para cada nova requisição
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
- Garanta que todos os parâmetros tenham declarações de tipo explícitas e tipos de retorno.
- Evite deixar construtores vazios, sem parâmetros.

### 5. Escrevendo Testes de Resolução do Container
Verifique que seus bindings resolvem corretamente a partir do Service Container usando Pest:
```php
use App\Services\PaymentGateway;
use App\Contracts\PaymentGatewayContract;

test('it resolves payment gateway contract to payment gateway service', function () {
    $service = app(PaymentGatewayContract::class);
    
    expect($service)->toBeInstanceOf(PaymentGateway::class);
});
```

# Exemplos

### Exemplo: Um PaymentServiceProvider Seguro
```php
<?php

namespace App\Providers;

use App\Contracts\PaymentGatewayContract;
use App\Services\AutentiquePaymentGateway;
use Illuminate\Support\ServiceProvider;
use Illuminate\Contracts\Foundation\Application;

class PaymentServiceProvider extends ServiceProvider
{
    /**
     * Register services.
     */
    public function register(): void
    {
        // Usa scoped para garantir que cada requisição receba sua própria instância,
        // prevenindo a exposição de token entre requisições.
        $this->app->scoped(PaymentGatewayContract::class, function (Application $app) {
            return new AutentiquePaymentGateway(
                token: (string) config('services.autentique.token'),
                // Wrapper de resolução lazy para info da requisição, se necessário
                requestIp: fn () => request()->ip()
            );
        });
    }
}
```

### Exemplo: Consumindo o Serviço Registrado
```php
<?php

namespace App\Http\Controllers;

use App\Contracts\PaymentGatewayContract;
use Illuminate\Http\JsonResponse;

class PaymentController extends Controller
{
    // Constructor Property Promotion do PHP 8
    public function __construct(
        protected PaymentGatewayContract $paymentGateway
    ) {}

    public function process(): JsonResponse
    {
        $result = $this->paymentGateway->charge(100.00);

        return response()->json([
            'success' => $result->isSuccess(),
            'transaction_id' => $result->getTransactionId(),
        ]);
    }
}
```

# Restrições

- **NÃO** use `singleton` para qualquer serviço que processe ou mantenha dados específicos de requisição, a menos que as dependências sejam resolvidas usando closures.
- **NÃO** mute propriedades estáticas em classes dentro do container.
- **NÃO** instancie serviços manualmente usando `new` dentro de Controllers ou Models se eles devem ser gerenciados e injetados pelo container.
- **NÃO** contorne a injeção via construtor em favor do helper `app()` dentro de classes de serviço (prefira DI adequada via construtor).

## Restrições
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
