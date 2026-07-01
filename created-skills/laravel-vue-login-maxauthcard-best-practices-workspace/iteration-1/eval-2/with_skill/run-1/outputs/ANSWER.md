# Login social com Laravel Socialite (Google + Facebook)

Implementei o backend de login social por sessão para o nosso stack (engeapp/Maxdmin Laravel 13, com Ziggy). Seguem os arquivos e as decisões.

## Arquivos entregues

- `SocialiteController.php` → `app/Http/Controllers/Auth/SocialiteController.php`
- `routes-auth.php` → trecho para `routes/auth.php`
- `config-services.php` → trecho para `config/services.php`

## O que o controller faz

Três ações, alinhadas ao contrato de rotas da skill:

1. **`providers()`** — retorna em JSON apenas os provedores com credenciais configuradas (`['google', 'facebook']` ou subconjunto). É o que o frontend consome via `route('social.providers')` para montar os botões do `MaxAuthCard`. Quem não tem `client_id`/`client_secret` no `config/services.php` simplesmente não aparece.

2. **`redirect($provider)`** — valida o `provider` contra a allowlist (`['google','facebook']`, retornando 404 fora dela) e dispara `Socialite::driver($provider)->redirect()`. No frontend isso é navegação total do navegador (`window.location.href = route('social.redirect', { provider })`), não XHR.

3. **`callback($provider)`** — também valida a allowlist, captura o usuário do provedor e:
   - Trata erro de OAuth (try/catch → `redirect('/login?error=oauth_error')`).
   - Exige e-mail (`redirect('/login?error=no_email')` se faltar).
   - **Cria a conta automaticamente no primeiro acesso** via `User::firstOrCreate` pela chave `email`, com `name` do provedor, `email_verified_at = now()` e **senha aleatória** (`Str::random(32)`) — a coluna `password` é NOT NULL e a conta social não usa senha local.
   - Faz **`Auth::login($user, true)`** — autenticação por **sessão** (guard `web`), com cookie de "lembrar-me" — e redireciona com `redirect()->intended('/')`.

## Pontos-chave do stack respeitados

- **Sessão, não token.** Uso `Auth::login` (guard `web`), coerente com `SESSION_DRIVER=database`. Nada de emitir token.
- **Rotas nomeadas para o Ziggy.** `social.providers`, `social.redirect`, `social.callback` — os mesmos nomes que o frontend referencia. Renomear quebraria o `route()` silenciosamente, então mantive o contrato.
- **Allowlist de provider** em todas as rotas que recebem `{provider}`, evitando 500 do Socialite com strings arbitrárias.
- **Find-or-create** com senha aleatória, sem deixar `password` nulo.
- **Erros de OAuth tratados** com redirect para `/login?error=...`, para a UI exibir a mensagem.

## Notas de integração (fora do escopo deste código)

- O `password` vai como string crua porque o `User` model usa o cast `'password' => 'hashed'`; se o seu model não tiver esse cast, troque por `bcrypt(Str::random(32))`.
- As rotas sociais ficam no grupo `middleware('guest')` junto com `login` (já existente em `routes/auth.php`).
- Configure no `.env` as variáveis `GOOGLE_*` e `FACEBOOK_*`; o `redirect` deve apontar para `/auth/{provider}/callback`.
- CSRF/SPA stateful (Sanctum) e o frontend (MaxAuthCard, store, guard) são cobertos pela skill e suas skills irmãs — aqui ficou só o backend social pedido.
