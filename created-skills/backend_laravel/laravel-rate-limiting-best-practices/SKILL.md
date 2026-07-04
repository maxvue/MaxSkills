---
name: laravel-rate-limiting-best-practices
description: Use when configuring, optimizing, or debugging rate limits for HTTP routes, APIs, login endpoints, or queues in Laravel. Triggers on defining rate limiters in bootstrap/app.php, using RateLimiter facade, applying throttle middleware, customizing 429 response, and testing route throttling.
---

# Boas Práticas de Rate Limiting no Laravel

## Objetivo
Fornecer diretrizes claras e padrões robustos para implementar, configurar e testar limites de requisições (rate limiting) no Laravel 13. Isso garante a proteção de endpoints (como logins, pagamentos e requisições de IA) contra ataques de brute-force e abuso, otimizando custos de infraestrutura e mantendo a estabilidade da aplicação.

## Instruções

1. **Definindo Rate Limiters no Laravel 13**:
   - No Laravel v11+, os rate limiters são tipicamente definidos dentro de `App\Providers\AppServiceProvider.php` (ou um provider dedicado de rota/segurança), no método `boot`, usando o método `RateLimiter::for`.
   - Use a facade `Illuminate\Support\Facades\RateLimiter`.
   - Sempre agrupe e nomeie os rate limiters semanticamente (ex: `api`, `login`, `ai-inference`, `payment-transactions`).

   ```php
   use Illuminate\Cache\RateLimiting\Limit;
   use Illuminate\Http\Request;
   use Illuminate\Support\Facades\RateLimiter;

   RateLimiter::for('api', function (Request $request) {
       return Limit::perMinute(60)->by($request->user()?->id ?: $request->ip());
   });
   ```

2. **Aplicando o Middleware às Rotas**:
   - Aplique rate limiters a rotas ou grupos de rotas usando o middleware `throttle`, passando o nome do limiter definido.
   - Dentro de `routes/api.php` ou `routes/web.php`:
     ```php
     Route::middleware('throttle:api')->group(function () {
         Route::get('/user', [UserController::class, 'show']);
     });

     Route::middleware('throttle:login')->post('/login', [AuthController::class, 'login']);
     ```

3. **Throttling Dinâmico e Identificação**:
   - Nunca use um limite estático sem diferenciação por usuário/IP, caso contrário um único usuário poderia bloquear a aplicação inteira.
   - Para rotas autenticadas, escopo pelo ID do usuário: `$request->user()?->id`.
   - Para rotas de convidado (como login/reset de senha), escopo pelo endereço IP: `$request->ip()`.
   - Para clientes de API ou integradores, escopo pela API Key ou client ID.
   - Considere limites dinâmicos com base nos papéis (roles) do usuário ou nos planos de assinatura:
     ```php
     RateLimiter::for('api', function (Request $request) {
         $limit = $request->user()?->isPremium() ? 1000 : 100;
         return Limit::perMinute($limit)->by($request->user()?->id ?: $request->ip());
     });
     ```

4. **Personalizando a Resposta 429 Too Many Requests**:
   - Personalize a resposta HTTP 429 para retornar um JSON limpo e padronizado em vez das páginas de exceção HTML padrão do Laravel para rotas de API.
   - Defina headers de resposta e mensagens de erro customizados:
     ```php
     RateLimiter::for('ai-inference', function (Request $request) {
         return Limit::perMinute(5)
             ->by($request->user()?->id ?: $request->ip())
             ->response(function (Request $request, array $headers) {
                 return response()->json([
                     'error' => 'Too Many Requests',
                     'message' => 'You have exceeded your AI request quota. Please retry in ' . $headers['Retry-After'] . ' seconds.',
                 ], 429, $headers);
             });
     });
     ```

5. **Rate Limiting em Filas de Jobs**:
   - Se os jobs interagem com APIs externas com rate limit (ex: gateways de pagamento, provedores externos de IA), use o rate limiter `redis` para controlar a execução dos workers da fila:
     ```php
     use Illuminate\Support\Facades\Redis;

     Redis::throttle('payment-gateway')
         ->allow(10)
         ->every(60)
         ->then(function () {
             // Processa o job de pagamento...
         }, function () {
             // Devolve o job para a fila com um atraso
             return $this->release(30);
         });
     ```

6. **Contornando o Rate Limiting em Ambientes Locais/de Teste**:
   - Para evitar bloquear testes automatizados ou fluxos de desenvolvimento local, permita desabilitar os rate limits via configuração no `.env` ou durante a execução dos testes.
   - Em `AppServiceProvider.php`:
     ```php
     if (app()->runningUnitTests() || config('security.disable_rate_limits')) {
         RateLimiter::for('api', fn () => Limit::none());
     }
     ```

7. **Testando o Throttling com o Pest**:
   - Use os testes de arquitetura e de feature do Pest para verificar se os endpoints têm o throttle aplicado corretamente.
   - Simule requisições consecutivas usando loops e verifique o status code:
     ```php
     it('throttles login requests after 5 attempts', function () {
         // Realiza 5 requisições bem-sucedidas ou com falha
         for ($i = 0; $i < 5; $i++) {
             $response = $this->postJson('/api/login', [
                 'email' => 'user@example.com',
                 'password' => 'wrong-password'
             ]);
             $response->assertStatus(422); // Erro de validação, mas ainda sem throttle
         }

         // A 6ª requisição deve ter o throttle aplicado
         $this->postJson('/api/login', [
             'email' => 'user@example.com',
             'password' => 'wrong-password'
         ])->assertStatus(429);
     });
     ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Sem Locks Crus no Banco de Dados**: NÃO escreva consultas customizadas no banco ou arquivos de lock para contar requisições. Sempre use a facade nativa `RateLimiter` ou o middleware `throttle` do Laravel.
- **Nunca Bloqueie Globalmente**: NÃO defina rate limiters sem um identificador único (como IP ou User ID) usando `by()`, pois isso aplicaria o throttle da rota para todos os usuários globalmente.
- **Resposta JSON em APIs**: Rate limiters aplicados a rotas de API devem retornar respostas JSON com headers padrão de CORS e retry-after, evitando as páginas de erro HTML padrão.
- **Trate Falhas de Cache**: Garanta que o driver de cache esteja corretamente configurado (ex: Redis ou banco de dados) para suportar rate limits. O rate limiting usando o driver de cache `array` não persiste entre as requisições web.

## Exemplos

### Exemplo Ruim: Implementar contagem manual dentro de um Controller
```php
<?php

namespace App\Http\Controllers;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Cache;

class AiController extends Controller
{
    public function generateText(Request $request)
    {
        $key = 'user_ai_limit:' . $request->ip();
        $attempts = Cache::get($key, 0);

        // VIOLAÇÃO: lógica de rate limiting manual dentro do controller.
        // Difícil de escalar, sem headers HTTP adequados e ignora os padrões do Laravel.
        if ($attempts >= 5) {
            return response()->json(['error' => 'Too many requests'], 400);
        }

        Cache::put($key, $attempts + 1, now()->addMinutes(1));

        // Processa a requisição de IA...
    }
}
```

### Exemplo Bom: Definir um Rate Limiter no AppServiceProvider e aplicar o Middleware
```php
// 1. Define em AppServiceProvider.php
namespace App\Providers;

use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        RateLimiter::for('ai-inference', function (Request $request) {
            return Limit::perMinute(5)
                ->by($request->user()?->id ?: $request->ip())
                ->response(function (Request $request, array $headers) {
                    return response()->json([
                        'error' => 'Too Many Requests',
                        'message' => 'AI generation quota exceeded. Try again in ' . $headers['Retry-After'] . ' seconds.',
                    ], 429, $headers);
                });
        });
    }
}

// 2. Aplica em routes/api.php
Route::middleware('throttle:ai-inference')->post('/ai/generate', [AiController::class, 'generateText']);
```
