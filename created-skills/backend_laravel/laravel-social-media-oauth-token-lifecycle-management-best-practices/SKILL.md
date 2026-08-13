---
name: laravel-social-media-oauth-token-lifecycle-management-best-practices
description: "Use when managing social media credentials (Meta: Instagram/Facebook) in Engeapp. Covers SocialMediaCredential model (encrypted access_token, token_expires_at), manual rotation via Ziggy routes, and MetaService resolution."
---
# Ciclo de Vida das Credenciais de Redes Sociais (Meta) no Laravel

## Objetivo
Guiar o armazenamento seguro, a rotação e a invalidação dos tokens de publicação em redes sociais no engeapp, fiel ao módulo real: as credenciais são **digitadas manualmente pelo gestor** e persistidas por empresa (tenant) em `calendar_social_media_credentials`, sendo consumidas pelo `MetaService`.

> **Escopo real:** apenas **Meta (Instagram + Facebook)** está implementado. Ancore-se nestes arquivos:
> - `app/Models/Calendar/SocialMediaCredential.php`
> - `database/migrations/*_create_calendar_social_media_credentials_table.php`
> - `app/Http/Controllers/Calendar/SocialMediaCredentialController.php`
> - `app/Services/SocialMedia/Meta/MetaService.php` (+ `MetaRequestTrait.php`)
> - `database/factories/Calendar/SocialMediaCredentialFactory.php` e `tests/Feature/SocialMedia/MetaIntegrationTest.php`
>
> Não existem drivers para LinkedIn, YouTube ou TikTok — o catálogo exposto pelo controller é `['Instagram', 'Facebook']`. Qualquer outro canal seria uma extensão futura, não um padrão vigente. O login social (`laravel/socialite`) é assunto separado, coberto por `laravel-socialite-oauth-integration-best-practices`; ele não fornece os tokens de publicação usados aqui.

## Instruções

### 1. Schema e Criptografia em Repouso
- **Cast de coluna, não de blob:** o token vive na própria coluna `access_token` (`text`, nullable) com cast escalar `encrypted` — não há campo `credentials` nem `encrypted:array`. Use a **propriedade** `$casts` (convenção do projeto), não o método `casts()`:
  ```php
  // app/Models/Calendar/SocialMediaCredential.php
  protected $casts = [
      'access_token'     => 'encrypted',   // cifrado em repouso
      'token_expires_at' => 'datetime',    // coluna própria, consultável por SQL
      'params'           => 'array',
      'is_active'        => 'boolean',
  ];

  // Impede serialização acidental do token em respostas JSON.
  protected $hidden = ['access_token'];
  ```
- **Expiração consultável:** por `token_expires_at` ser coluna dedicada (`dateTime` nullable) e não estar dentro de um blob cifrado, filtre por SQL (`where('token_expires_at', '<=', now()->addDays(7))`). Nada de varrer a tabela e comparar em PHP.
- **Metadados livres em `params`:** dados não sensíveis do canal (JSON) ficam em `params`; o identificador da conta externa (`ig_user_id` / `page_id`) tem coluna própria, `external_account_id`.

### 2. Unicidade e Isolamento Multi-Tenant
- O tenant é a **empresa solar** (`solar_company_id`), nunca um `client_id`. Cada empresa tem no máximo uma credencial por API do catálogo `EventApi`:
  ```php
  $table->unique(['solar_company_id', 'event_api_id'], 'sm_credentials_company_api_unique');
  ```
- Toda leitura parte do tenant do usuário autenticado: `SocialMediaCredential::where('solar_company_id', Auth::user()?->solar_company_id)`.
- A plataforma **não** é uma coluna `platform`: ela vem da relação `eventApi(): BelongsTo(EventApi::class, 'event_api_id')`. Para filtrar por nome, use `whereHas('eventApi', fn ($q) => $q->whereRaw('LOWER(name) = ?', [mb_strtolower($apiName)]))`.

### 3. Cadastro e Rotação Manual do Token
- **Origem do token:** o gestor cola o token no formulário; o backend valida como string livre e faz `updateOrCreate` pela chave do tenant:
  ```php
  // app/Http/Controllers/Calendar/SocialMediaCredentialController.php
  SocialMediaCredential::updateOrCreate(
      ['solar_company_id' => $solarCompanyId, 'event_api_id' => $validated['event_api_id']],
      $attributes,
  );
  ```
- **Sobrescrita parcial:** só grave `access_token` quando o campo vier preenchido. Isso permite ajustar a conta externa ou o status `is_active` sem exigir que o gestor redigite o token:
  ```php
  if ( ! empty($validated['access_token'])) {
      $attributes['access_token'] = $validated['access_token'];
  }
  ```
- **Rotação = novo POST:** não existe refresh token nem job/comando de renovação automática no projeto. A rotação acontece quando o gestor salva um token novo pela rota Ziggy `social_media.credentials.save`; a listagem usa `social_media.credentials.data`.
- Se um dia for necessário avisar sobre vencimento, apoie-se em `token_expires_at` + `is_active` numa consulta agendada — a coluna existe justamente para isso, mas hoje **nenhum código de aplicação a lê**.

### 4. Nunca Devolver o Token ao Front-end
- O endpoint de leitura devolve apenas um indicador de presença, preservando o sigilo:
  ```php
  'has_token' => ! empty($credential?->access_token),
  ```
- Exponha ao front `event_api_id`, `api_name`, `icon`, `external_account_id`, `is_active` e `has_token` — nada mais. O `$hidden` do model é a segunda linha de defesa, não a primeira.

### 5. Resolução do Token no Serviço
- A resolução é **estática, por credencial ou por empresa**, sem Manager nem `driver()`:
  ```php
  $service = MetaService::forCredential($credential);           // token + external_account_id da credencial
  $service = MetaService::forCompany($solarCompanyId, 'Instagram'); // credencial ativa da empresa; fallback config('api.meta_token')
  ```
- `forCompany()` filtra por `is_active = true` e cai no token global de `config/api.php` quando a empresa não tem credencial — logo, `null` significa "nenhuma autenticação disponível". Cheque `isUsable()` antes de publicar.
- O prefixo do token decide o host: tokens `IG` (Instagram Login) vão para `graph.instagram.com`, os demais para `graph.facebook.com`. Guardar o token errado para a API errada é a causa mais comum de 400/190 — valide o prefixo ao cadastrar.

### 6. Token Inválido ou Revogado
- A camada de transporte (`MetaRequestTrait::send`) **não lança exceção**: ela registra `Log::warning` em respostas `failed()` e devolve o corpo decodificado, normalizando falhas de transporte como `['error' => ...]`. Portanto, quem chama precisa inspecionar o retorno:
  ```php
  $resposta = $service->publish->publishContainer($containerId);

  if (isset($resposta['error'])) {
      // Token revogado/expirado (ex.: OAuthException, code 190) → desativar e pedir novo cadastro.
      $credential->update(['is_active' => false]);
      // notifique o gestor para colar um token novo em social_media.credentials.save
  }
  ```
- Os códigos e tipos de erro da Meta (`OAuthException`, `code 190`) e os prazos de validade de tokens de longa duração são **convenções externas da plataforma**, não fatos do código — confirme na documentação oficial vigente antes de codificar limiares.

### 7. Testes
- Use a `SocialMediaCredentialFactory` (que já preenche `access_token`, `token_expires_at`, `is_active`) e `Http::fake()` sobre `graph.facebook.com` / `graph.instagram.com`. O exemplo de referência é `tests/Feature/SocialMedia/MetaIntegrationTest.php`; os padrões de fake/sequence/assertSent estão em `laravel-pest-testing-best-practices`.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- NUNCA envie o `access_token` ao frontend nem o exponha em respostas de API; devolva apenas `has_token`.
- NUNCA ignore o `['error' => ...]` retornado pelos handlers da Meta; registre-o e sinalize ao gestor quando for necessário recadastrar o token.
