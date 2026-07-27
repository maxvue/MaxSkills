# Security Best Practices

## Mass Assignment Protection

Every model must define `$fillable` (whitelist) or `$guarded` (blacklist).

Preferred for new models — explicit whitelist:
```php
class User extends Model
{
    protected $fillable = [
        'name',
        'email',
        'password',
    ];
}
```

**Convenção existente no engeapp:** cerca de 36 models instalados usam `protected $guarded = []`
(ex.: `SupportTemplate`, `ProjectEvaluation`, `PriceTable`, `UserGroup`), enquanto a maioria (~94)
usa `$fillable`. O padrão `$guarded = []` delega a proteção contra dados não confiáveis à validação
(Form Request) antes do `create`/`update`. Ao editar ou estender esses models, mantenha a
consistência com o arquivo; ao criar models novos, prefira `$fillable`.

O risco de mass assignment com `$guarded = []` é real e continua valendo o alerta quando o payload
chega direto do usuário:

Incorrect:
```php
// Qualquer coluna enviada pelo cliente é preenchida — inclusive is_admin
$user->update($request->all());
```

Correct:
```php
// Apenas o que o Form Request validou
$user->update($request->validated());
```

Nunca passe `$request->all()` para `create()`/`update()` — em model algum, com `$fillable` ou
`$guarded`. Ver `rules/validation.md`.

## Authorize Every Action

Use policies or gates in controllers. Never skip authorization.

Incorrect:
```php
public function update(UpdatePostRequest $request, Post $post)
{
    $post->update($request->validated());
}
```

Correct:
```php
public function update(UpdatePostRequest $request, Post $post)
{
    Gate::authorize('update', $post);

    $post->update($request->validated());
}
```

Or via Form Request:

```php
public function authorize(): bool
{
    return $this->user()->can('update', $this->route('post'));
}
```

## Prevent SQL Injection

Always use parameter binding. Never interpolate user input into queries.

Incorrect:
```php
DB::select("SELECT * FROM users WHERE name = '{$request->name}'");
```

Correct:
```php
User::where('name', $request->name)->get();

// Raw expressions with bindings
User::whereRaw('LOWER(name) = ?', [strtolower($request->name)])->get();
```

## Proteção CSRF

O engeapp é uma SPA Vue 3 (Vue Router, sem Inertia): a maior parte das requisições sai via axios, sem forms Blade. A proteção CSRF depende do cookie `XSRF-TOKEN`, que o axios reenvia automaticamente no header; garanta que o cliente HTTP esteja configurado para isso e que as rotas estateful passem pelo middleware de sessão. Além disso, o projeto envia o token explicitamente: `resources/Stores/Setting/useSystem.Store.ts` expõe `headerRequests` com o header `X-CSRF-TOKEN` e `withCredentials: true`. Rotas de webhook são isentas em `bootstrap/app.php` via `$middleware->validateCsrfTokens(except: ['onlyoffice/callback/*', 'voip/webhook', 'voip/agent/result'])` — ao adicionar um webhook novo, isente-o ali (e proteja-o por assinatura/token próprio).

Referência genérica do framework (raramente aplicável aqui): em views Blade servidas pelo servidor, use `{{ }}` para escape de saída (nunca `{!! !!}` com conteúdo do usuário) e inclua `@csrf` em todos os forms POST/PUT/DELETE.

## Rate Limit Auth and API Routes

Apply `throttle` middleware to authentication and API routes.

```php
RateLimiter::for('login', function (Request $request) {
    return Limit::perMinute(5)->by($request->ip());
});

Route::post('/login', LoginController::class)->middleware('throttle:login');
```

## Validate File Uploads

Validate extension, MIME type, and size. The `mimes` rule checks extensions; use `mimetypes` for actual MIME type validation. Never trust client-provided filenames.

```php
public function rules(): array
{
    return [
        'avatar' => ['required', 'image', 'mimes:jpg,jpeg,png,webp', 'max:2048'],
    ];
}
```

Store with generated filenames:

```php
$path = $request->file('avatar')->store('avatars', 'public');
```

## Keep Secrets Out of Code

Never commit `.env`. Access secrets via `config()` only — ver `rules/config.md` ("`env()` Only in Config Files") para o exemplo Incorrect/Correct.

## Audit Dependencies

Run `composer audit` periodically to check for known vulnerabilities in dependencies. Automate this in CI to catch issues before deployment.

```bash
composer audit
```

## Encrypt Sensitive Database Fields

Use `encrypted` cast for API keys/tokens and mark the attribute as `hidden`.

Incorrect:
```php
class Integration extends Model
{
    protected function casts(): array
    {
        return [
            'api_key' => 'string',
        ];
    }
}
```

Correct:
```php
class Integration extends Model
{
    protected $hidden = ['api_key', 'api_secret'];

    protected function casts(): array
    {
        return [
            'api_key' => 'encrypted',
            'api_secret' => 'encrypted',
        ];
    }
}
```
