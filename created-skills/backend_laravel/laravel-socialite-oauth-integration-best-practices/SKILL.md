---
name: laravel-socialite-oauth-integration-best-practices
description: Use ao implementar, refatorar ou depurar o login social OAuth do engeapp com Laravel Socialite (Google/Facebook) via SocialiteController. Cobre config/services.php, rotas social.providers/social.redirect/social.callback em routes/auth.php (grupo guest), find-or-create por e-mail com criação de UserSolarCompany, erros por query-string ?error= e mock do Socialite em testes Pest.
---

# Boas Práticas de Integração OAuth com Laravel Socialite (engeapp)

## Objetivo
Orientar a implementação e manutenção do login social OAuth do engeapp usando `laravel/socialite` (^5.28), fiel ao `SocialiteController` real: provedores Google e Facebook, provisionamento por e-mail com criação da integradora solar, tratamento de erro por query-string e mocking em testes Pest. O frontend Vue (store `useLogin.Store.ts`) consome os endpoints via nomes de rota Ziggy.

## Arquitetura real (leia antes de editar)
- Controller: `app/Http/Controllers/Auth/SocialiteController.php`.
- Rotas: `routes/auth.php`, dentro do grupo `Route::middleware('guest')`.
- Config: `config/services.php` (blocos `google` e `facebook`).
- Consumo no frontend: `resources/Stores/UserStores/useLogin.Store.ts`.
- Allowlist de provedores: constante `PROVIDERS = ['google', 'facebook']` no controller.
- Sessão por cookie no guard `web`: `Auth::login()` + `session()->regenerate()`; ao final redireciona para `/`.
- **NÃO existem colunas `oauth_provider`/`oauth_id` na tabela `users`.** O vínculo é feito por e-mail (find-or-create). Não referencie essas colunas.

## Instruções

1. **Configuração do Driver (`config/services.php`):**
   - Use variáveis de ambiente apenas para `client_id` e `client_secret`.
   - O `redirect` é um **caminho fixo** (`/auth/google/callback`, `/auth/facebook/callback`), não uma env var. Mantenha esse padrão para não divergir da config real.
   - O caminho de callback precisa bater com o registrado no dashboard do provedor.

2. **Rotas OAuth (`routes/auth.php`, grupo `guest`):**
   - Mantenha os três endpoints com os nomes reais: `social.providers`, `social.redirect`, `social.callback`.
   - Elas ficam sob `Route::middleware('guest')` (usam sessão/CSRF do stack `web`) — não crie rotas paralelas em `routes/web.php` com outra nomenclatura.
   - `social.providers` (`GET /auth/providers`) devolve JSON com os ids de provedores que têm `client_id` e `client_secret` configurados; o frontend usa isso para montar os botões sociais.

3. **Provisionamento de usuário (find-or-create por e-mail):**
   - O callback busca `User::where('email', $email)->first()`. Se não existir, cria via `createUserFromSocial()` e dispara `event(new Registered($user))`.
   - A criação roda dentro de `DB::transaction`: cria primeiro uma `UserSolarCompany` (integradora solar) e vincula `solar_company_id` ao `User`.
   - Ao montar o `User`, inclua `phone_number = null` e `international_phone_number = null` via `setRawAttributes()`. Motivo real: o mutator `setPhoneNumberAttribute` faz early-return em `null`, e a coluna tem `DEFAULT '0'` com constraint `UNIQUE` — se o campo for omitido do INSERT, dois usuários sem telefone colidem. Não remova esse contorno.
   - `password` recebe `Hash::make(Str::random(40))` (conta social sem senha utilizável).

4. **Validação de provedor e tratamento de erro (query-string):**
   - Valide o `$provider` contra a allowlist `PROVIDERS` com `in_array(..., true)`. Provider fora da lista → `redirect('/login?error=invalid_provider')`.
   - Envolva `Socialite::driver($provider)->user()` em `try/catch (Throwable)` e, em falha, `redirect('/login?error=oauth_failed')` (evita 500 e cobre `InvalidStateException` e erros do Guzzle).
   - Se o provedor não retornar e-mail → `redirect('/login?error=no_email')`.
   - **Erros são passados por query-string `?error=<código>`, não por session flash.** O frontend (`useLogin.Store.ts`) lê `?error=` e mapeia os códigos `invalid_provider`, `oauth_failed`, `no_email` para mensagens no card de login. Não troque para `->with('error', ...)`.

5. **Integração com o frontend (Vue SPA):**
   - `redirect()` do Socialite devolve `Symfony\...\RedirectResponse` (navegação do navegador para o provedor); os demais retornam `Illuminate RedirectResponse`.
   - O frontend inicia o fluxo com `route('social.redirect', { provider })` (nome Ziggy) via `window.location.href`, e carrega provedores com `apiGetRoute('social.providers')`.
   - Fluxo detalhado do card de login: ver [laravel-vue-login-maxauthcard-best-practices](../../../projects/engeapp/.claude/skills/laravel-vue-login-maxauthcard-best-practices/SKILL.md).

6. **Testes Pest e Mocking do Socialite:**
   - Nunca acesse endpoints OAuth externos nos testes; faça mock do Socialite (facade / contrato `Laravel\Socialite\Contracts\Factory`).
   - Cubra: redirect para o provedor, criação do usuário + `UserSolarCompany` no callback, e os três estados de erro (`invalid_provider`, `oauth_failed`, `no_email`).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), independentemente do idioma do corpo desta skill.
- NÃO referencie colunas `oauth_provider`/`oauth_id` nem uma tabela `social_accounts`: não existem no projeto. O vínculo é por e-mail.
- NÃO configure `redirect` de OAuth via env var; use o caminho fixo como no `config/services.php` real.
- NÃO armazene credenciais brutas de client OAuth no código; `client_id`/`client_secret` vêm do `.env`.
- NÃO deixe exceções do Socialite (incl. `InvalidStateException`) virarem erro 500; capture com `try/catch (Throwable)` e redirecione para `/login?error=oauth_failed`.
- NÃO troque o esquema de erro por session flash: o contrato com o frontend é `?error=<código>` na URL.
- NÃO faça requisições HTTP reais ao provedor nos testes; sempre faça mock do Socialite.

## Consideração de segurança (genérica — NÃO implementada no engeapp)
O engeapp adota **find-or-create puro por e-mail**, sem checar flag de e-mail verificado e sem colunas de provider. É uma escolha deliberada do projeto. Se um dia for necessário endurecer contra sequestro de conta (ex.: exigir `email_verified` do provedor antes de vincular a uma conta preexistente com outro método de login), isso seria uma mudança de arquitetura — não é o comportamento atual e não deve ser descrito como se já existisse.

## Exemplos (fiéis ao código real)

### 1. `config/services.php`
```php
'google' => [
    'client_id'     => env('GOOGLE_CLIENT_ID'),
    'client_secret' => env('GOOGLE_CLIENT_SECRET'),
    'redirect'      => '/auth/google/callback',
],

'facebook' => [
    'client_id'     => env('FACEBOOK_CLIENT_ID'),
    'client_secret' => env('FACEBOOK_CLIENT_SECRET'),
    'redirect'      => '/auth/facebook/callback',
],
```

### 2. Rotas (`routes/auth.php`, grupo `guest`)
```php
Route::middleware('guest')->group(function () : void {
    // ... demais rotas de auth ...
    Route::get('/auth/providers', [SocialiteController::class, 'providers'])->name('social.providers');
    Route::get('/auth/{provider}/redirect', [SocialiteController::class, 'redirect'])->name('social.redirect');
    Route::get('/auth/{provider}/callback', [SocialiteController::class, 'callback'])->name('social.callback');
});
```

### 3. `SocialiteController` (essência)
```php
private const PROVIDERS = ['google', 'facebook'];

// Lista provedores com credenciais configuradas (consumido pelo frontend).
public function providers() : JsonResponse
{
    $enabled = array_values(array_filter(
        self::PROVIDERS,
        fn (string $provider) : bool =>
            ! empty(config("services.{$provider}.client_id"))
            && ! empty(config("services.{$provider}.client_secret")),
    ));

    return response()->json($enabled);
}

public function redirect(string $provider) : SymfonyRedirectResponse
{
    if ( ! in_array($provider, self::PROVIDERS, true)) {
        return redirect('/login?error=invalid_provider');
    }

    return Socialite::driver($provider)->redirect();
}

public function callback(string $provider) : RedirectResponse
{
    if ( ! in_array($provider, self::PROVIDERS, true)) {
        return redirect('/login?error=invalid_provider');
    }

    try {
        $socialUser = Socialite::driver($provider)->user();
    }
    catch (Throwable) {
        return redirect('/login?error=oauth_failed');
    }

    $email = $socialUser->getEmail();

    if ( ! $email) {
        return redirect('/login?error=no_email');
    }

    // Find-or-create por e-mail (sem colunas de provider).
    $user = User::where('email', $email)->first();

    if ( ! $user) {
        $user = $this->createUserFromSocial($socialUser);
        event(new Registered($user));
    }

    Auth::login($user);
    request()->session()->regenerate();

    return redirect('/');
}
```

Provisionamento (dentro de `DB::transaction`): cria a `UserSolarCompany`, monta o `User`
e inclui `phone_number`/`international_phone_number` como `null` via `setRawAttributes()`
para contornar o mutator (early-return em null) e a constraint UNIQUE com DEFAULT '0'.

### 4. Mocking com Pest
```php
use App\Models\User;
use Laravel\Socialite\Facades\Socialite;
use Laravel\Socialite\Two\User as OAuthUser;

it('redireciona para o provedor oauth correto', function () {
    $response = $this->get(route('social.redirect', ['provider' => 'google']));

    $response->assertRedirect();
});

it('autentica e cria o usuario quando o callback retorna dados validos', function () {
    $abstractUser = mock(OAuthUser::class);
    $abstractUser->shouldReceive('getId')->andReturn('google-id-12345');
    $abstractUser->shouldReceive('getName')->andReturn('Test User');
    $abstractUser->shouldReceive('getEmail')->andReturn('test@example.com');
    $abstractUser->shouldReceive('getAvatar')->andReturn(null);

    Socialite::shouldReceive('driver')->with('google')->andReturnSelf();
    Socialite::shouldReceive('user')->andReturn($abstractUser);

    $response = $this->get(route('social.callback', ['provider' => 'google']));

    $response->assertRedirect('/');
    $this->assertDatabaseHas('users', ['email' => 'test@example.com']);
    $this->assertAuthenticated();
});

it('redireciona com erro quando o provedor e invalido', function () {
    $response = $this->get(route('social.redirect', ['provider' => 'twitter']));

    $response->assertRedirect('/login?error=invalid_provider');
});
```
