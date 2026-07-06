---
name: laravel-rate-limiting-best-practices
description: Use ao configurar, otimizar ou depurar limites de requisições (rate limiting) para rotas HTTP, APIs, login ou filas no Laravel 13. Aciona ao definir limiters nomeados em App\Providers\AppServiceProvider via RateLimiter::for, aplicar o middleware throttle (nomeado ou inline throttle:6,1), fazer throttling manual em FormRequest (tooManyAttempts/hit/clear), customizar a resposta 429 e testar no Pest.
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
     ```
   - Para limites simples que não precisam de um limiter nomeado, use a forma inline `throttle:<tentativas>,<minutos>`. Este é o padrão adotado no engeapp para rotas sensíveis de verificação de e-mail (`routes/auth.php`):
     ```php
     Route::get('verify-email/{id}/{hash}', VerifyEmailController::class)
         ->middleware(['signed', 'throttle:6,1'])
         ->name('verification.verify');

     Route::post('email/verification-notification', [EmailVerificationNotificationController::class, 'store'])
         ->middleware('throttle:6,1')
         ->name('verification.send');
     ```

3. **Throttling manual dentro de um FormRequest (padrão do login no engeapp)**:
   - Para fluxos que precisam contar apenas tentativas com FALHA (ex.: login por brute-force), o padrão Breeze faz o throttling dentro do próprio `FormRequest`, e NÃO via limiter nomeado em `AppServiceProvider`. No engeapp isso vive em `app/Http/Requests/Auth/LoginRequest.php`, consumido pela rota `POST /login_request` (`->name('login')`).
   - Antes de autenticar, verifique o limite; em cada falha, incremente (`hit`); no sucesso, limpe (`clear`). Escope a chave por e-mail + IP.
     ```php
     use Illuminate\Auth\Events\Lockout;
     use Illuminate\Support\Facades\RateLimiter;
     use Illuminate\Support\Str;
     use Illuminate\Validation\ValidationException;

     public function ensureIsNotRateLimited(): void
     {
         // 5 tentativas com falha por chave antes de bloquear
         if (! RateLimiter::tooManyAttempts($this->throttleKey(), 5)) {
             return;
         }

         event(new Lockout($this));
         RateLimiter::availableIn($this->throttleKey());

         throw ValidationException::withMessages([]);
     }

     public function authenticate(): void
     {
         $this->ensureIsNotRateLimited();

         if (! Auth::attempt($credentials, $this->boolean('remember'))) {
             RateLimiter::hit($this->throttleKey()); // conta só a falha
             throw ValidationException::withMessages([]);
         }

         RateLimiter::clear($this->throttleKey()); // sucesso zera o contador
     }

     public function throttleKey(): string
     {
         return Str::transliterate(Str::lower($this->string('email')) . '|' . $this->ip());
     }
     ```

4. **Throttling Dinâmico e Identificação**:
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

5. **Personalizando a Resposta 429 Too Many Requests**:
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

6. **Rate Limiting em Filas de Jobs**:
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

7. **Contornando o Rate Limiting em Ambientes Locais/de Teste**:
   - Para evitar bloquear testes automatizados ou fluxos de desenvolvimento local, permita desabilitar os rate limits durante a execução dos testes.
   - `app()->runningUnitTests()` já cobre o cenário de testes sem exigir configuração extra. Se quiser também uma flag por ambiente, crie você mesmo a chave (ela NÃO existe no engeapp: não há `config/security.php`) — publique um `config/security.php` retornando `['disable_rate_limits' => env('DISABLE_RATE_LIMITS', false)]` antes de referenciá-la.
   - Em `AppServiceProvider.php`:
     ```php
     // config('security.disable_rate_limits') pressupõe um config/security.php criado por você.
     if (app()->runningUnitTests() || config('security.disable_rate_limits')) {
         RateLimiter::for('api', fn () => Limit::none());
     }
     ```

8. **Testando o Throttling com o Pest**:
   - Use os testes de feature do Pest para verificar se os endpoints têm o throttle aplicado corretamente.
   - Simule requisições consecutivas usando loops e verifique o status code. No engeapp o login é `POST /login_request` (`->name('login')`) e o throttling do `LoginRequest` dispara `ValidationException` (HTTP 422) até estourar o limite — a 6ª tentativa apenas acrescenta a mensagem de lockout, sem trocar o status. Prefira asserir contra o nome de rota (`route('login')`) e checar a mensagem/evento de bloqueio:
     ```php
     it('bloqueia o login após 5 tentativas com falha', function () {
         for ($i = 0; $i < 5; $i++) {
             $this->postJson(route('login'), [
                 'email'    => 'user@example.com',
                 'password' => 'senha-errada',
             ])->assertStatus(422); // credenciais inválidas, ainda sem lockout
         }

         // A partir daqui o RateLimiter marca lockout (evento Lockout + availableIn).
         Illuminate\Support\Facades\Event::fake();
         $this->postJson(route('login'), [
             'email'    => 'user@example.com',
             'password' => 'senha-errada',
         ])->assertStatus(422);
     });
     ```
   - Para rotas com o middleware `throttle` nomeado ou inline (ex.: `throttle:6,1`), aí sim a resposta esperada após o limite é HTTP 429; teste o status code diretamente.

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
