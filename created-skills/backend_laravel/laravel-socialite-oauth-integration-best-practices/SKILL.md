---
name: laravel-socialite-oauth-integration-best-practices
description: Use when implementing, refactoring, or debugging OAuth authentication via Laravel Socialite. Triggers on Socialite driver config, callback routing, user provisioning, state validation, and OAuth testing.
---

# Boas Práticas de Integração OAuth com Laravel Socialite

## Objetivo
Fornecer diretrizes sólidas e padrões seguros para implementar autenticação OAuth usando o Laravel Socialite neste projeto, cobrindo múltiplos drivers (ex: Google, Facebook), provisionamento seguro de usuários, prevenção de CSRF e mocking adequado em testes Pest.

## Instruções
1. **Configuração do Driver (`config/services.php`):**
   - Defina as credenciais de cada provedor usando variáveis de ambiente.
   - Sempre acrescente `_client_id`, `_client_secret` e `_redirect` às variáveis de ambiente.
   - Exemplo de configuração para Google e Facebook:
     ```php
     'google' => [
         'client_id' => env('GOOGLE_CLIENT_ID'),
         'client_secret' => env('GOOGLE_CLIENT_SECRET'),
         'redirect' => env('GOOGLE_REDIRECT_URI'),
     ],
     'facebook' => [
         'client_id' => env('FACEBOOK_CLIENT_ID'),
         'client_secret' => env('FACEBOOK_CLIENT_SECRET'),
         'redirect' => env('FACEBOOK_REDIRECT_URI'),
     ],
     ```

2. **Estrutura de Rotas OAuth:**
   - Defina rotas nomeadas para o processo de redirecionamento e para o endpoint de callback.
   - Garanta que a URL de callback corresponda à registrada no dashboard do provedor OAuth.
   - Restrinja as rotas de callback OAuth ao grupo de middleware `web` para dar suporte ao state da sessão e prevenir ataques CSRF.

3. **Provisionamento Seguro de Usuário e Prevenção de Sequestro de Conta:**
   - **Regra de Segurança Crucial:** Quando um payload de login OAuth chegar, não vincule automaticamente a conta a um usuário existente com base apenas no endereço de email sem verificar se o email foi confirmado pelo provedor OAuth.
   - Verifique se o provedor retorna uma flag indicando a verificação do email (ex: o `email_verified` do Google ou o status de verificado).
   - Se o usuário já existir:
     - Verifique se ele se registrou pelo mesmo provedor OAuth.
     - Se ele se registrou via senha ou por outro provedor, solicite que faça login primeiro e vincule a conta social nas configurações de perfil, em vez de fazer a mesclagem automática (que permite sequestro de conta se um agente malicioso controlar um domínio/email verificado em outro lugar).
   - Use uma relação `social_accounts` separada ou colunas na tabela `users` (`oauth_provider`, `oauth_id`) para rastrear identidades vinculadas de forma segura.

4. **Tratamento de Falhas de State e CSRF:**
   - A verificação do redirecionamento OAuth depende de um parâmetro state para prevenir CSRF.
   - Sempre envolva a lógica de callback do Socialite em um bloco `try-catch` para tratar `Laravel\Socialite\Two\InvalidStateException` ou exceções HTTP gerais do Guzzle.
   - Evite expor uma página de erro 500. Redirecione o usuário de volta para a tela de login com uma mensagem de erro amigável nos dados de flash da sessão.

5. **Controllers de API (SPA):**
   - Mantenha os controllers enxutos. Siga as convenções de [laravel-code-generators-best-practices](../laravel-code-generators-best-practices/SKILL.md).
   - Injete dependências via constructor property promotion quando apropriado.
   - Retorne tokens limpos (ex: personal access tokens do Sanctum) para OAuth baseado em API, ou redirecione para a rota de dashboard da SPA (Vue Router) após setar a sessão.

6. **Testes Pest e Mocking do Socialite:**
   - Nunca acesse endpoints OAuth externos durante testes automatizados.
   - Faça mock do contrato `Laravel\Socialite\Contracts\Factory` usando as capacidades integradas de facade do Socialite ou implementações de mock padrão.
   - Verifique se a criação de usuário, a criação de sessão e os estados de erro são testados de forma abrangente.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- NÃO faça vinculação automática de usuários OAuth a contas de usuário existentes sem verificar se o email foi marcado como verificado pelo provedor.
- NÃO armazene credenciais brutas de cliente OAuth em `config/services.php`; sempre referencie variáveis do `.env`.
- NÃO permita que a `InvalidStateException` propague até um erro de servidor 500; sempre trate-a de forma elegante e redirecione para a página de login.
- NÃO faça requisições HTTP reais ao provedor OAuth nos testes; sempre faça mock da facade do Socialite.

## Exemplos

### 1. Configuração do services.php
```php
// config/services.php
return [
    // ... configurações existentes ...

    'google' => [
        'client_id' => env('GOOGLE_CLIENT_ID'),
        'client_secret' => env('GOOGLE_CLIENT_SECRET'),
        'redirect' => env('GOOGLE_REDIRECT_URI'),
    ],

    'facebook' => [
        'client_id' => env('FACEBOOK_CLIENT_ID'),
        'client_secret' => env('FACEBOOK_CLIENT_SECRET'),
        'redirect' => env('FACEBOOK_REDIRECT_URI'),
    ],
];
```

### 2. Configuração das Rotas OAuth
```php
// routes/web.php
use App\Http\Controllers\Auth\OAuthController;
use Illuminate\Support\Facades\Route;

Route::get('/auth/{provider}/redirect', [OAuthController::class, 'redirectToProvider'])
    ->name('oauth.redirect');

Route::get('/auth/{provider}/callback', [OAuthController::class, 'handleProviderCallback'])
    ->name('oauth.callback');
```

### 3. Implementação do Controller
```php
<?php

namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Models\User;
use Exception;
use Illuminate\Http\RedirectResponse;
use Laravel\Socialite\Facades\Socialite;
use Laravel\Socialite\Two\User as OAuthUser;
use Laravel\Socialite\Two\InvalidStateException;

class OAuthController extends Controller
{
    /**
     * Redireciona o usuário para a página de autorização do provedor.
     */
    public function redirectToProvider(string $provider): RedirectResponse
    {
        if (! in_array($provider, ['google', 'facebook'])) {
            abort(404, 'Provedor de autenticação não suportado.');
        }

        return Socialite::driver($provider)->redirect();
    }

    /**
     * Lida com o retorno de chamada (callback) do provedor de autenticação.
     */
    public function handleProviderCallback(string $provider): RedirectResponse
    {
        if (! in_array($provider, ['google', 'facebook'])) {
            abort(404, 'Provedor de autenticação não suportado.');
        }

        try {
            /** @var \Laravel\Socialite\Two\User $oauthUser */
            $oauthUser = Socialite::driver($provider)->user();
        } catch (InvalidStateException $e) {
            // Trata erros de State CSRF inválido de forma amigável
            return redirect()->route('login')
                ->with('error', 'A autenticação falhou. Por favor, tente novamente.');
        } catch (Exception $e) {
            // Trata falhas gerais de comunicação ou permissões
            return redirect()->route('login')
                ->with('error', 'Não foi possível autenticar usando o provedor.');
        }

        // Prevenção de Account Hijacking (sequestro de contas)
        // Nota: Garanta que o email esteja marcado como verificado pelo provedor
        $emailVerified = $oauthUser->getRaw()['email_verified'] ?? false;
        
        if (! $emailVerified && $provider === 'google') {
            return redirect()->route('login')
                ->with('error', 'O seu email do provedor precisa estar verificado para prosseguir.');
        }

        /** @var User|null $existingUser */
        $existingUser = User::where('email', $oauthUser->getEmail())->first();

        if ($existingUser) {
            // Verifica se o usuário já possui vínculo com este provedor
            if ($existingUser->oauth_provider !== $provider || $existingUser->oauth_id !== $oauthUser->getId()) {
                return redirect()->route('login')
                    ->with('error', 'Este email já está cadastrado com outro método de login. Faça login manualmente e associe esta conta em seu perfil.');
            }

            auth()->login($existingUser);
            session()->regenerate();
            return redirect()->intended('/');
        }

        // Provisionamento seguro de novo usuário
        $newUser = User::create([
            'name' => $oauthUser->getName() ?? $oauthUser->getNickname(),
            'email' => $oauthUser->getEmail(),
            'oauth_provider' => $provider,
            'oauth_id' => $oauthUser->getId(),
            'email_verified_at' => now(), // Assume verificado já que o provedor atestou
        ]);

        auth()->login($newUser);
        session()->regenerate();

        return redirect('/');
    }
}
```

### 4. Mocking com Pest
```php
<?php

use App\Models\User;
use Laravel\Socialite\Facades\Socialite;
use Laravel\Socialite\Two\User as OAuthUser;

it('redireciona para o provedor oauth correto', function () {
    $response = $this->get(route('oauth.redirect', ['provider' => 'google']));

    $response->assertRedirect();
    $this->assertStringContainsString('accounts.google.com', $response->getTargetUrl());
});

it('autentica e cria o usuario quando o callback do oauth retorna dados validos', function () {
    $abstractUser = mock(OAuthUser::class);
    
    $abstractUser->shouldReceive('getId')->andReturn('google-id-12345');
    $abstractUser->shouldReceive('getName')->andReturn('Test User');
    $abstractUser->shouldReceive('getEmail')->andReturn('test@example.com');
    $abstractUser->shouldReceive('getNickname')->andReturn('testuser');
    $abstractUser->shouldReceive('getRaw')->andReturn(['email_verified' => true]);

    Socialite::shouldReceive('driver')
        ->with('google')
        ->andReturnSelf();

    Socialite::shouldReceive('user')
        ->andReturn($abstractUser);

    $response = $this->get(route('oauth.callback', ['provider' => 'google']));

    $response->assertRedirect('/');
    
    $this->assertDatabaseHas('users', [
        'email' => 'test@example.com',
        'oauth_id' => 'google-id-12345',
        'oauth_provider' => 'google',
    ]);
});
```
