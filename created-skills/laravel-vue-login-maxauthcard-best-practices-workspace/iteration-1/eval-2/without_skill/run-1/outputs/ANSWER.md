# Login social com Laravel Socialite (Google + Facebook) — autenticação por sessão

Implementei o backend de login social para o stack Laravel 13 com guard `web` (sessão),
rotas nomeadas para o Ziggy e criação automática de usuário no primeiro acesso.

## Arquivos entregues

| Arquivo | O que é |
|---|---|
| `SocialiteController.php` | Controller com `redirect()` e `callback()`, find-or-create do usuário e login por sessão. Caminho final: `app/Http/Controllers/Auth/SocialiteController.php` |
| `routes-auth.php` | Trecho a colar em `routes/auth.php` — rotas **nomeadas** e restringidas por provedor |
| `config-services.php` | Trecho a colar em `config/services.php` — credenciais Google/Facebook |
| `migration-add-social-columns.php` | Migration de apoio (colunas `provider`, `provider_id`, tokens, `avatar`) |

## Passos para instalar

1. **Pacote** (não rodei aqui, conforme pedido):
   ```bash
   composer require laravel/socialite
   ```

2. **Credenciais** no `.env`:
   ```env
   GOOGLE_CLIENT_ID=
   GOOGLE_CLIENT_SECRET=
   GOOGLE_REDIRECT_URI="${APP_URL}/auth/google/callback"

   FACEBOOK_CLIENT_ID=
   FACEBOOK_CLIENT_SECRET=
   FACEBOOK_REDIRECT_URI="${APP_URL}/auth/facebook/callback"
   ```
   Cadastre essas mesmas URLs de callback no Google Cloud Console e no Meta for Developers.

3. **Migration**: copie o conteúdo para uma migration e rode `php artisan migrate`.
   Adicione os novos campos ao `$fillable` do `App\Models\User`:
   `provider`, `provider_id`, `provider_token`, `provider_refresh_token`, `avatar`.
   (`provider_token` e `provider_refresh_token` também no `$hidden`.)

4. **Rotas e config**: cole os trechos nos respectivos arquivos.

## Por que está assim (decisões)

- **Sessão, não token/stateless**: o `callback()` usa `Socialite::driver($provider)->user()`
  *sem* `->stateless()`, porque dependemos do `state` guardado na sessão (proteção CSRF do
  fluxo OAuth). Após resolver o usuário faço `Auth::login($user, remember: true)` no guard
  `web` e `session()->regenerate()` para evitar **session fixation**. Isso encaixa no guard
  `web` configurado por padrão.

- **Rotas nomeadas para o Ziggy**: `auth.social.redirect` e `auth.social.callback`. No Vue:
  ```js
  window.location.href = route('auth.social.redirect', { provider: 'google' })
  // ou 'facebook'
  ```
  O `redirect` é um navigation real do browser (não XHR), porque o OAuth precisa redirecionar
  para o domínio do provedor. Por isso uso `window.location.href` e não `fetch`/axios.

- **Restrição de provedor em dois níveis**: as rotas usam `whereIn('provider', [...])` e o
  controller revalida com `ensureProviderIsAllowed()` (`abort 404`). Isso impede que alguém
  acione um driver não configurado via `/auth/qualquercoisa/redirect`.

- **Find-or-create em 3 camadas** dentro de `findOrCreateUser()`:
  1. Já vinculado a `(provider, provider_id)` → atualiza tokens/avatar e retorna.
  2. Existe usuário com o mesmo **e-mail** → vincula o provedor à conta existente
     (evita conta duplicada e account-takeover por e-mail já cadastrado).
  3. **Primeiro acesso** → cria o usuário automaticamente, com `email_verified_at = now()`
     (o e-mail já foi validado pelo provedor OAuth) e uma senha aleatória de 40 chars
     (a conta loga só via social; a senha existe apenas para satisfazer o schema).

- **Tratamento de erro**: `InvalidStateException` (sessão expirada / CSRF) redireciona de
  volta para `login` com mensagem amigável em vez de estourar 500.

## Observações

- O redirect pós-login usa `redirect()->intended(route('dashboard'))`. Ajuste o nome da rota
  de destino conforme o seu projeto.
- As rotas estão no grupo `middleware('guest')`; ajuste se quiser permitir vincular provedor
  a um usuário já autenticado.
- Para Facebook, o e-mail pode vir vazio se o usuário não conceder a permissão de e-mail; o
  código já lida com `email` nulo, mas vale exibir um aviso no frontend nesse caso.
