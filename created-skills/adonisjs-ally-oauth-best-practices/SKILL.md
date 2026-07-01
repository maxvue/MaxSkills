---
name: adonisjs-ally-oauth-best-practices
description: Use ao configurar, implementar ou depurar login social (OAuth2) com AdonisJS Ally para os provedores Google e Facebook, com rotas /auth/:provider/redirect e /auth/:provider/callback, tratamento de accessDenied/hasError, find-or-create de usuário por email e login via session guard web. Dispara em configuração do Ally, tratamento de callback e fluxo de login social.
---

# Melhores Práticas de Autenticação Social com AdonisJS Ally (Google + Facebook)

## Objetivo
Fornecer diretrizes claras, padrões de código e etapas de depuração para implementar autenticação social OAuth2 robusta e segura no AdonisJS v6 com `@adonisjs/ally`, alinhado ao fluxo real do projeto: provedores **Google** e **Facebook**, autenticação **session-based** (guard `web`, sessões persistidas no banco, 30 dias), find-or-create de usuário por email e redirects exatos. Sem Ziggy/Inertia.

## Instruções

### 1. Ambiente e Configuração
* **Validação de Variáveis de Ambiente**: Declare e valide os IDs de cliente, segredos e URLs de callback de cada provedor no `start/env.ts`:
  ```typescript
  GOOGLE_CLIENT_ID: Env.schema.string(),
  GOOGLE_CLIENT_SECRET: Env.schema.string(),
  GOOGLE_CALLBACK_URL: Env.schema.string(),
  FACEBOOK_CLIENT_ID: Env.schema.string(),
  FACEBOOK_CLIENT_SECRET: Env.schema.string(),
  FACEBOOK_CALLBACK_URL: Env.schema.string(),
  ```
* **Definição de Configuração**: Configure `google` e `facebook` em `config/ally.ts` com `defineConfig` e os helpers `services.google` / `services.facebook`. Use o segundo argumento de `env.get` como fallback `''` para não quebrar o boot quando uma credencial estiver ausente:
  ```typescript
  import env from '#start/env';
  import { defineConfig, services } from '@adonisjs/ally';

  const allyConfig = defineConfig({
      google: services.google({
          clientId: env.get('GOOGLE_CLIENT_ID', ''),
          clientSecret: env.get('GOOGLE_CLIENT_SECRET', ''),
          callbackUrl: env.get('GOOGLE_CALLBACK_URL', '')
      }),
      facebook: services.facebook({
          clientId: env.get('FACEBOOK_CLIENT_ID', ''),
          clientSecret: env.get('FACEBOOK_CLIENT_SECRET', ''),
          callbackUrl: env.get('FACEBOOK_CALLBACK_URL', '')
      })
  });

  export default allyConfig;

  declare module '@adonisjs/ally/types' {
      interface SocialProviders extends InferSocialProviders<typeof allyConfig> {}
  }
  ```

### 2. Endpoint de Provedores Disponíveis
* Exponha `GET /auth/providers` para o frontend descobrir quais provedores estão configurados, baseando-se na presença das variáveis de ambiente. Só lista o provedor cujo `*_CLIENT_ID` está definido:
  ```typescript
  import env from '#start/env';

  async providers({ response }: HttpContext) {
      const list: string[] = [];
      if (env.get('GOOGLE_CLIENT_ID')) list.push('google');
      if (env.get('FACEBOOK_CLIENT_ID')) list.push('facebook');
      return response.json(list);
  }
  ```

### 3. Redirecionamento (`GET /auth/:provider/redirect`)
* Valide que `params.provider` pertence ao conjunto suportado `{ google, facebook }` antes de usar o driver; rejeite com `badRequest` caso contrário. Em seguida, retorne o redirect do Ally:
  ```typescript
  async redirect({ ally, params, response }: HttpContext) {
      const provider = params.provider as 'google' | 'facebook';
      if (provider !== 'google' && provider !== 'facebook') return response.badRequest('Invalid provider');

      return ally.use(provider).redirect();
  }
  ```
* **Escopos/parâmetros customizados** (opcional): passe uma callback para `redirect` quando precisar de escopos extras ou de `prompt`:
  ```typescript
  return ally.use('google').redirect((request) => {
      request.scopes(['userinfo.profile', 'userinfo.email']);
      request.param('prompt', 'select_account');
  });
  ```

### 4. Callback Resiliente (`GET /auth/:provider/callback`)
Ordem obrigatória do tratamento, refletindo o fluxo real. Cada falha redireciona para `/login` com um `error` específico na query string:

1. **Validar o provider** (mesmo guard do redirect).
2. **`driver.accessDenied()`** — usuário negou a autorização → `/login?error=access_denied`.
3. **`driver.hasError()`** — erro genérico do OAuth → `/login?error=oauth_error`.
4. **Buscar o usuário** com `driver.user()`.
5. **Exigir email** — sem email não há identidade local → `/login?error=no_email`.

```typescript
async callback({ ally, params, response, auth }: HttpContext) {
    const provider = params.provider as 'google' | 'facebook';
    if (provider !== 'google' && provider !== 'facebook') return response.badRequest('Invalid provider');

    const driver = ally.use(provider);

    if (driver.accessDenied()) return response.redirect('/login?error=access_denied');

    if (driver.hasError()) return response.redirect('/login?error=oauth_error');

    const socialUser = await driver.user();

    if (!socialUser.email) return response.redirect('/login?error=no_email');

    // ... find-or-create + login (seção 5)
}
```

> `accessDenied()` cobre o cancelamento explícito da autorização; `hasError()` cobre os demais erros do callback (state inválido, parâmetros faltando etc.). Verifique ambos **antes** de chamar `driver.user()`.

### 5. Find-or-Create por Email e Login (Session Guard `web`)
* **Vinculação por email (somente se verificado pelo provedor)**: o email é a chave de identidade, mas vincular um login social a uma conta local existente **apenas pelo email** é um vetor de account-hijacking — um atacante com um email social *não verificado* igual ao de uma conta existente assumiria essa conta. Antes de vincular, exija que o provedor tenha verificado o email. O Google expõe `email_verified` em `socialUser.original.email_verified`; o Facebook só retorna emails de contas confirmadas, mas trate ausência como não-verificado:
  ```typescript
  const emailVerified = socialUser.original?.email_verified === true || provider === 'facebook';
  let user = await User.findBy('email', socialUser.email);

  // conta local já existe + email não comprovadamente verificado → não vincule automaticamente
  if (user && !emailVerified) return response.redirect('/login?error=email_not_verified');

  if (!user) user = await User.create({
      email: socialUser.email,
      fullName: socialUser.name,
      password: randomBytes(16).toString('hex')
  });

  await auth.use('web').login(user);

  return response.redirect('/projects');
  ```
* **Senha aleatória obrigatória**: o modelo `User` exige `password`, mas contas sociais não têm senha local. Gere um valor aleatório com `randomBytes(16).toString('hex')` (import `from 'node:crypto'`). O hash é aplicado pelo hook do modelo; o usuário nunca usa essa senha para login direto.
* **Login session-based**: use `auth.use('web').login(user)`. A sessão é persistida no banco (guard `web`, validade de 30 dias). Após o login, redirecione para `/projects`.

### 6. Tokens de Acesso (opcional)
* Se for necessário chamar a API do provedor após o login (ex.: Google ou Meta Graph), armazene `socialUser.token.token`, `token.refreshToken` e `token.expiresAt` em uma tabela própria vinculada ao usuário. Mantenha os tokens **somente no servidor**; nunca os exponha ao frontend.

## Restrições
* **NUNCA** chame `driver.user()` sem antes verificar `driver.accessDenied()` **e** `driver.hasError()`, nessa ordem.
* **SEMPRE** valide `params.provider` contra `{ google, facebook }` tanto no `redirect` quanto no `callback`, retornando `badRequest` para valores inesperados.
* **MANTENHA** os redirects de erro exatos do fluxo: `/login?error=access_denied`, `/login?error=oauth_error`, `/login?error=no_email`, `/login?error=email_not_verified`; e o sucesso em `/projects`.
* **NÃO** crie um usuário sem email — sempre redirecione para `/login?error=no_email` quando `socialUser.email` estiver ausente.
* **USE** o guard `web` (`auth.use('web').login(user)`) para login social; o projeto é session-based, sem tokens de API/JWT no fluxo de login.
* **NÃO** codifique as URLs de callback no `config/ally.ts`; sempre via variáveis de ambiente.
* **NÃO** exponha tokens brutos de provedores externos ao frontend.
