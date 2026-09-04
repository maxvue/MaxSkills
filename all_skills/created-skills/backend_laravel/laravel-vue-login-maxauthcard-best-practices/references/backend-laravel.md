# Backend Laravel 13 — Login (sessão + Socialite)

Código de referência para o fluxo de login do ecossistema engeapp. Autenticação **por sessão + cookie** (guard `web`, `SESSION_DRIVER=database`), Socialite para login social. Rotas **nomeadas** (o Ziggy expõe ao frontend). **Não** há Sanctum SPA stateful, `withXSRFToken` no Axios nem endpoint `/sanctum/csrf-cookie` neste projeto — a proteção CSRF vem do cookie de sessão + meta tag `csrf-token` do blade.

## 1. Rotas — `routes/auth.php`

```php
use App\Http\Controllers\Auth\AuthenticatedSessionController;
use App\Http\Controllers\Auth\SocialiteController;
use Illuminate\Support\Facades\Route;

Route::middleware('guest')->group(function () {
    Route::post('login_request', [AuthenticatedSessionController::class, 'store'])->name('login');

    // Login social (nomes consumidos pelo frontend via Ziggy)
    Route::get('auth/providers', [SocialiteController::class, 'providers'])->name('social.providers');
    Route::get('auth/{provider}/redirect', [SocialiteController::class, 'redirect'])->name('social.redirect');
    Route::get('auth/{provider}/callback', [SocialiteController::class, 'callback'])->name('social.callback');
});

Route::middleware('auth')->group(function () {
    Route::post('logout', [AuthenticatedSessionController::class, 'destroy'])->name('logout');
});
```

> O endpoint `user.data` / `user.save` (store MaxPinia) vive nas rotas de usuário do app, não aqui.

## 2. Divisão de responsabilidade: controller converte o telefone, request autentica

Ponto central (fiel ao código real): o **controller** converte o telefone para o formato
internacional e faz o `merge` ANTES de chamar `$request->authenticate()`. O `LoginRequest`
apenas autentica, escolhendo a credencial por **sentinelas** que o frontend envia quando o
campo não se aplica (`email = 'undefined@enge.tec.br'` quando o usuário entrou por telefone;
`phone_number = 'undefined'`/`null` quando entrou por e-mail — ver `useLogin.Store.ts`).

`app/Http/Controllers/Auth/AuthenticatedSessionController.php`

```php
namespace App\Http\Controllers\Auth;

use App\Classes\PhoneClass; // namespace real: App\Classes (NÃO App\Support)
use App\Http\Controllers\Controller;
use App\Http\Requests\Auth\LoginRequest;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class AuthenticatedSessionController extends Controller
{
    public function store(LoginRequest $request): RedirectResponse
    {
        // Converte o telefone para o formato internacional ANTES de autenticar.
        $phone_number = $request->input('phone_number')
            ? PhoneClass::getInternationalPhoneNumber($request->input('phone_number'))
            : null;

        $request->merge(['phone_number' => $phone_number]);
        $request->authenticate();

        $request->session()->regenerate(); // previne session fixation

        return redirect('/');
    }

    public function destroy(Request $request): RedirectResponse
    {
        Auth::guard('web')->logout();       // guard web (sessão), não token
        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return redirect('/');
    }
}
```

## 3. `LoginRequest` — e-mail OU telefone + rate limiting

`app/Http/Requests/Auth/LoginRequest.php`

```php
namespace App\Http\Requests\Auth;

use App\Classes\PhoneClass; // namespace real: App\Classes (NÃO App\Support)
use Illuminate\Auth\Events\Lockout;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\Facades\Validator;
use Illuminate\Support\Str;
use Illuminate\Validation\ValidationException;

class LoginRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'email'    => ['required', 'string', 'email'],
            'password' => ['required', 'string'],
        ];
    }

    /**
     * Autentica por e-mail OU telefone internacional.
     * O telefone já chega convertido (o controller fez o merge).
     */
    public function authenticate(): void
    {
        $this->ensureIsNotRateLimited();

        // E-mail é ignorado se for a sentinela 'undefined@enge.tec.br' ou inválido.
        $validator = Validator::make(
            ['email' => $this->input('email')],
            ['email' => 'required|email'],
        );

        $email = ! $validator->fails() && $this->input('email') !== 'undefined@enge.tec.br'
            ? $this->input('email')
            : null;

        // Telefone é ignorado se for a sentinela 'undefined' ou null.
        $phone = $this->input('phone_number') !== 'undefined' && $this->input('phone_number') !== null
            ? $this->input('phone_number')
            : null;

        if (! $email && ! $phone) {
            throw ValidationException::withMessages([]);
        }

        // Telefone tem prioridade quando presente; senão, e-mail.
        $credentials = $phone !== null
            ? [
                'international_phone_number' => PhoneClass::getInternationalPhoneNumber($phone),
                'password'                   => $this->input('password'),
            ]
            : [
                'email'    => $email,
                'password' => $this->input('password'),
            ];

        if (! Auth::attempt($credentials, $this->boolean('remember'))) {
            RateLimiter::hit($this->throttleKey());
            throw ValidationException::withMessages([]);
        }

        RateLimiter::clear($this->throttleKey());
    }

    public function ensureIsNotRateLimited(): void
    {
        if (! RateLimiter::tooManyAttempts($this->throttleKey(), 5)) {
            return;
        }

        event(new Lockout($this));
        RateLimiter::availableIn($this->throttleKey());

        throw ValidationException::withMessages([]);
    }

    public function throttleKey(): string
    {
        return Str::transliterate(Str::lower($this->string('email')) . '|' . $this->ip());
    }
}
```

## 4. Login social — `SocialiteController`

`app/Http/Controllers/Auth/SocialiteController.php`

```php
namespace App\Http\Controllers\Auth;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Auth\Events\Registered;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\RedirectResponse;
use Illuminate\Support\Facades\Auth;
use Laravel\Socialite\Facades\Socialite;
use Throwable;

class SocialiteController extends Controller
{
    private const PROVIDERS = ['google', 'facebook'];

    /** Lista só provedores com credenciais configuradas (consumido pelo frontend). */
    public function providers(): JsonResponse
    {
        $enabled = array_values(array_filter(self::PROVIDERS, function (string $p) {
            return filled(config("services.$p.client_id"))
                && filled(config("services.$p.client_secret"));
        }));

        return response()->json($enabled);
    }

    public function redirect(string $provider): RedirectResponse
    {
        // Provider fora da allowlist volta ao login com código de erro (não abort 404).
        if (! in_array($provider, self::PROVIDERS, true)) {
            return redirect('/login?error=invalid_provider');
        }
        return Socialite::driver($provider)->redirect();
    }

    public function callback(string $provider): RedirectResponse
    {
        if (! in_array($provider, self::PROVIDERS, true)) {
            return redirect('/login?error=invalid_provider');
        }

        try {
            $social = Socialite::driver($provider)->user();
        } catch (Throwable $e) {
            return redirect('/login?error=oauth_failed');
        }

        if (! $social->getEmail()) {
            return redirect('/login?error=no_email');
        }

        // Find-or-create por e-mail. No engeapp o create é manual (via createUserFromSocial):
        // cria também a UserSolarCompany vinculada, gera senha aleatória e usa setRawAttributes
        // para incluir phone_number=null no INSERT (contorna o mutator e a constraint UNIQUE).
        $user = User::where('email', $social->getEmail())->first();
        if (! $user) {
            $user = $this->createUserFromSocial($social);
            event(new Registered($user));
        }

        Auth::login($user);
        request()->session()->regenerate(); // previne session fixation
        return redirect('/');
    }
}
```

`config/services.php`:

```php
'google' => [
    'client_id'     => env('GOOGLE_CLIENT_ID'),
    'client_secret' => env('GOOGLE_CLIENT_SECRET'),
    'redirect'      => env('GOOGLE_REDIRECT_URI'),
],
'facebook' => [
    'client_id'     => env('FACEBOOK_CLIENT_ID'),
    'client_secret' => env('FACEBOOK_CLIENT_SECRET'),
    'redirect'      => env('FACEBOOK_REDIRECT_URI'),
],
```

> Para drivers além de Google/Facebook, provisionamento seguro de usuário, validação de `state` e mock em Pest, ver a skill `laravel-socialite-oauth-integration-best-practices`.

## 5. Sessão, usuário e migrations

- **Sessão:** `SESSION_DRIVER=database`, tabela `sessions` (id, user_id, ip_address, user_agent, payload, last_activity). `config/session.php`: `same_site = lax`, `http_only = true`, `secure` conforme ambiente.
- **User model:** estende `Authenticatable`, usa `HasUlids`, cast `'password' => 'hashed'`, colunas `email` (unique), `phone_number` / `international_phone_number` (unique). `email`, `phone_number` no `$fillable`; `password`/`remember_token` no `$hidden`.
- **CSRF (sem Sanctum SPA stateful):** o engeapp **não** usa Sanctum stateful, `withXSRFToken` no Axios nem `GET /sanctum/csrf-cookie`. A autenticação é sessão + cookie no guard `web`. A cadeia real de CSRF: `csrf_token()` é serializado no payload de `user.data` (`UserDataControler.php`) → store MaxPinia `useUser` → `useSystemStore.token`/`headerRequests` (header `X-CSRF-TOKEN` + `withCredentials`). A meta tag `csrf-token` existe nos blades, mas o front não a lê. Os helpers do `@maxvue/max-use` (`apiGetRoute`/`apiPostRoute`) já injetam headers e `withCredentials` — não anexe o header CSRF à mão nas chamadas de API. A única exceção com header manual (`XSRF-TOKEN`) são os widgets de upload que fazem HTTP próprio (`FileManager.vue`, `FilesCss.vue`).

## Armadilhas

- Esquecer `session()->regenerate()` após login (session fixation).
- Nomear a rota de login diferente de `login` e quebrar `route('login')` no frontend.
- Não validar o `provider` do social contra allowlist (rota aceita qualquer string → erro 500 do Socialite). Fora da allowlist, o engeapp redireciona para `/login?error=invalid_provider`.
- Divergir os códigos de erro do redirect (`invalid_provider`, `oauth_failed`, `no_email`) das chaves de `SOCIAL_ERROR_MESSAGES` no `useLogin.Store.ts`, ou redirecionar para `/` em vez de `/login` — o card nunca mostra a mensagem. Sempre redirecione para `/login?error=<código mapeado no store>`.
- Criar usuário social sem `password` (a coluna é NOT NULL) — gere senha aleatória.
- Confiar só em `email` no login quando o usuário entrou por telefone — trate ambos no `LoginRequest`.
