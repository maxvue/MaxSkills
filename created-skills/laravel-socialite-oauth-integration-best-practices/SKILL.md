---
name: laravel-socialite-oauth-integration-best-practices
description: Use when implementing, refactoring, or debugging OAuth authentication via Laravel Socialite. Triggers on Socialite driver config, callback routing, user provisioning, state validation, and OAuth testing.
---

# Laravel Socialite OAuth Integration Best Practices

## Goal
Provide solid guidelines and secure standards for implementing OAuth authentication using Laravel Socialite in this project, covering multiple drivers (e.g., Google, Microsoft Azure AD), secure user provisioning, CSRF prevention, and proper mocking in Pest tests.

## Instructions
1. **Driver Configuration (`config/services.php`):**
   - Define credentials for each provider using environment variables.
   - Always append `_client_id`, `_client_secret`, and `_redirect` to environment variables.
   - Example configuration for Google and Azure AD:
     ```php
     'google' => [
         'client_id' => env('GOOGLE_CLIENT_ID'),
         'client_secret' => env('GOOGLE_CLIENT_SECRET'),
         'redirect' => env('GOOGLE_REDIRECT_URI'),
     ],
     'azure' => [
         'client_id' => env('AZURE_CLIENT_ID'),
         'client_secret' => env('AZURE_CLIENT_SECRET'),
         'redirect' => env('AZURE_REDIRECT_URI'),
         'tenant' => env('AZURE_TENANT_ID'),
     ],
     ```

2. **OAuth Routing Structure:**
   - Define named routes for the redirect process and the callback endpoint.
   - Ensure the callback URL matches the one registered in the OAuth provider dashboard.
   - Restrict OAuth callback routes to the `web` middleware group to support session state and prevent CSRF attacks.

3. **Secure User Provisioning & Account Hijacking Prevention:**
   - **Crucial Security Rule:** When an OAuth login payload arrives, do not automatically link the account to an existing user based solely on the email address without verifying if the email has been confirmed by the OAuth provider.
   - Check if the provider returns a flag indicating email verification (e.g., Google's `email_verified` or verified status).
   - If the user already exists:
     - Check if they registered via the same OAuth provider.
     - If they registered via password or another provider, prompt them to log in first and link the social account in their profile settings, rather than auto-merging (which allows account hijacking if a malicious actor controls a verified domain/email elsewhere).
   - Use a separate `social_accounts` relation or columns on the `users` table (`oauth_provider`, `oauth_id`) to track linked identities securely.

4. **Handling State & CSRF Failures:**
   - OAuth redirect verification relies on a state parameter to prevent CSRF.
   - Always wrap the Socialite callback logic in a `try-catch` block to handle `Laravel\Socialite\Two\InvalidStateException` or general Guzzle HTTP exceptions.
   - Avoid exposing a 500 error page. Redirect the user back to the login screen with a user-friendly error message in the session flash data.

5. **API Controllers (SPA):**
   - Keep controllers thin. Follow [laravel-code-generators-best-practices](file:///home/johnattas/GitHub/Skills/created-skills/laravel-code-generators-best-practices/SKILL.md) conventions.
   - Inject dependencies via constructor property promotion where appropriate.
   - Return clean tokens (e.g., Sanctum personal access tokens) for API-based OAuth, ou redirect to the SPA dashboard route (Vue Router) após setar a sessão.

6. **Pest Testing & Socialite Mocking:**
   - Never hit external OAuth endpoints during automated tests.
   - Mock the `Laravel\Socialite\Contracts\Factory` contract using Socialite's built-in facade capabilities or standard mock implementations.
   - Verify that user creation, session creation, and error states are tested comprehensively.

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- Do NOT perform auto-linking of OAuth users to existing user accounts without verifying that the email was marked as verified by the provider.
- Do NOT store raw OAuth client credentials in `config/services.php`; always reference `.env` variables.
- Do NOT allow `InvalidStateException` to bubble up to a 500 server error; always handle it gracefully and redirect to the login page.
- Do NOT make actual HTTP requests to the OAuth provider in tests; always mock the Socialite facade.

## Examples

### 1. services.php Configuration
```php
// config/services.php
return [
    // ... configurações existentes ...

    'google' => [
        'client_id' => env('GOOGLE_CLIENT_ID'),
        'client_secret' => env('GOOGLE_CLIENT_SECRET'),
        'redirect' => env('GOOGLE_REDIRECT_URI'),
    ],
];
```

### 2. OAuth Route Setup
```php
// routes/web.php
use App\Http\Controllers\Auth\OAuthController;
use Illuminate\Support\Facades\Route;

Route::get('/auth/{provider}/redirect', [OAuthController::class, 'redirectToProvider'])
    ->name('oauth.redirect');

Route::get('/auth/{provider}/callback', [OAuthController::class, 'handleProviderCallback'])
    ->name('oauth.callback');
```

### 3. Controller Implementation
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
        if (! in_array($provider, ['google', 'microsoft'])) {
            abort(404, 'Provedor de autenticação não suportado.');
        }

        return Socialite::driver($provider)->redirect();
    }

    /**
     * Lida com o retorno de chamada (callback) do provedor de autenticação.
     */
    public function handleProviderCallback(string $provider): RedirectResponse
    {
        if (! in_array($provider, ['google', 'microsoft'])) {
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

### 4. Mocking with Pest
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
