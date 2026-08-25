---
name: laravel-socialite-oauth-integration-best-practices
description: "Use when implementing or debugging social login OAuth with Laravel Socialite (Google/Facebook). Covers services.php, routes/auth.php, UserSolarCompany creation, and Pest mocking."
author: Johnattas Conrady Gomes Santana
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
   - A criação roda dentro de `DB::transaction`: primeiro busca `$designer = User::where('key_url', 'engetec')->first()` e cria uma `UserSolarCompany` (integradora solar) com `user_designer = $designer?->id`, `company_name`/`email`/`project_mails` vindos do usuário social; depois vincula `solar_company_id` ao `User`.
   - Ao montar o `User` via `fill()`, além de `name`/`email`/`avatar`/`password`, sempre inclua `user_group_id = '01jnpabdcfgbgee7pdfdr23p1c'` (ULID hardcoded do grupo padrão), `privacy = true`, `status = 'active'`, `is_validated = false` e `settings = ['width' => 450]`.
   - Em seguida, inclua `phone_number = null` e `international_phone_number = null` via `setRawAttributes()`. Motivo real: o mutator `setPhoneNumberAttribute` faz early-return em `null`, e a coluna tem `DEFAULT '0'` com constraint `UNIQUE` — se o campo for omitido do INSERT, dois usuários sem telefone colidem. Não remova esse contorno.
   - `password` recebe `Hash::make(Str::random(40))` (conta social sem senha utilizável).

4. **Validação de provedor e tratamento de erro (query-string):**
   - Valide o `$provider` contra a allowlist `PROVIDERS` com `in_array(..., true)`. Provider fora da lista → `redirect('/login?error=invalid_provider')`.
   - Envolva `Socialite::driver($provider)->user()` em `try/catch (Throwable)` e, em falha, `redirect('/login?error=oauth_failed')` (evita 500 e cobre `InvalidStateException` e erros do Guzzle).
   - Se o provedor não retornar e-mail → `redirect('/login?error=no_email')`.
   - **Erros são passados por query-string `?error=<código>`, não por session flash.** O frontend (`useLogin.Store.ts`) lê `?error=` e mapeia os códigos `invalid_provider`, `oauth_failed`, `no_email` para mensagens no card de login. Não troque para `->with('error', ...)`.

5. **Integração com o frontend (Vue SPA):**
   - `redirect()` do Socialite devolve `Symfony\...\RedirectResponse` (navegação do navegador para o provedor); os demais retornam `Illuminate RedirectResponse`.
   - O frontend inicia o fluxo com `route('social.redirect', { provider })` (nome Ziggy) via `window.location.href`, e carrega provedores com `apiGetRoute('social.providers')`.
   - Fluxo detalhado do card de login: ver [laravel-vue-login-maxauthcard-best-practices](../laravel-vue-login-maxauthcard-best-practices/SKILL.md).

6. **Testes Pest e Mocking do Socialite:**
   - Nunca acesse endpoints OAuth externos nos testes; faça mock do Socialite (facade / contrato `Laravel\Socialite\Contracts\Factory`).
   - Cubra: redirect para o provedor, criação do usuário + `UserSolarCompany` no callback, e os três estados de erro (`invalid_provider`, `oauth_failed`, `no_email`).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- NÃO armazene credenciais brutas de client OAuth no código; `client_id`/`client_secret` vêm do `.env`.
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

### 3. Mocking com Pest
```php
use App\Models\User;
use Laravel\Socialite\Contracts\Provider;
use Laravel\Socialite\Contracts\User as SocialiteUser;
use Laravel\Socialite\Facades\Socialite;

test('redirect para provider válido redireciona ao provedor', function () {
    $driver = Mockery::mock(Provider::class);
    $driver->shouldReceive('redirect')->andReturn(redirect('https://accounts.google.com/o/oauth2'));
    Socialite::shouldReceive('driver')->with('google')->andReturn($driver);

    $this->get('/auth/google/redirect')->assertRedirect();
});

test('callback autentica e cria o usuario quando os dados sao validos', function () {
    $socialUser = Mockery::mock(SocialiteUser::class);
    $socialUser->shouldReceive('getEmail')->andReturn('test@example.com');
    $socialUser->shouldReceive('getName')->andReturn('Test User');
    $socialUser->shouldReceive('getAvatar')->andReturn('https://example.com/avatar.png');
    $socialUser->shouldReceive('getId')->andReturn('social-123');

    $driver = Mockery::mock(Provider::class);
    $driver->shouldReceive('user')->andReturn($socialUser);
    Socialite::shouldReceive('driver')->with('google')->andReturn($driver);

    $response = $this->get(route('social.callback', ['provider' => 'google']));

    $response->assertRedirect('/');
    $this->assertDatabaseHas('users', ['email' => 'test@example.com']);
    $this->assertAuthenticated();
});
```
