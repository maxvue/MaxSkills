---
name: laravel-social-media-oauth-token-lifecycle-management-best-practices
description: "Use when designing, implementing, reviewing, or debugging OAuth token lifecycle management for social media integrations (Facebook, Instagram, LinkedIn, YouTube, TikTok) in Laravel. Triggers on social media credential storage, token encryption/decryption, refresh token flows, expiration checks, invalid or revoked token responses, and scheduling token renewal jobs."
---

# Boas Práticas de Gerenciamento do Ciclo de Vida de Tokens OAuth de Redes Sociais no Laravel

## Objetivo
Estabelecer diretrizes seguras, resilientes e automatizadas para gerenciar access tokens e refresh tokens OAuth de plataformas externas de redes sociais (Facebook, Instagram, LinkedIn, YouTube, TikTok) dentro do backend baseado em Laravel da aplicação SocialMedia.

## Instruções

### 1. Armazenamento Seguro e Criptografia de Tokens
- **Criptografia em Repouso (at Rest)**: Armazene todos os tokens OAuth sensíveis (`access_token`, `refresh_token`, `client_secret`) de forma segura. Use o cast nativo `encrypted:array` do Laravel no model `SocialMediaCredential`:
  ```php
  protected function casts(): array
  {
      return [
          'credentials' => 'encrypted:array',
      ];
  }
  ```
- **Ocultando Campos Sensíveis**: Sempre adicione o atributo `credentials` ao array `$hidden` no model para evitar serialização acidental e exposição em respostas JSON:
  ```php
  protected $hidden = ['credentials'];
  ```
- **Restrições de Unicidade Compostas**: Garanta que cada cliente possa ter apenas um conjunto de credenciais por plataforma usando um índice único composto:
  ```php
  $table->unique(['client_id', 'platform']);
  ```

### 2. Abstração de Driver de Provedor (Strategy Pattern)
- **Definição da Interface**: Defina uma interface ou classe abstrata (ex: `SocialMediaProviderDriver`) para unificar a interface de integração.
  ```php
  interface SocialMediaProviderDriver
  {
      public function refreshToken(SocialMediaCredential $credential): bool;
      public function validateToken(SocialMediaCredential $credential): bool;
      public function fetchProfile(SocialMediaCredential $credential): array;
  }
  ```
- **Estratégia de Implementação**: Crie drivers dedicados para cada plataforma (ex: `FacebookDriver`, `LinkedInDriver`, etc.) que implementem essa interface, resolvendo as requisições de rede e processando as respostas.
- **Factory Manager**: Use uma classe manager para resolver o driver correto em tempo de execução:
  ```php
  $driver = SocialMediaManager::driver($credential->platform);
  ```

### 3. Fluxo Proativo de Expiração e Renovação de Tokens
- **Rastreamento de Expiração**: Armazene um timestamp `expires_at` dentro do array `credentials`.
- **Verificações Proativas de Renovação**: Compare o horário atual com o timestamp `expires_at`. Se um token estiver dentro da janela de renovação (tipicamente 7 dias antes da expiração para tokens de longa duração), marque-o para renovação automática.
- **Job em Background Agendado**: Evite a renovação síncrona de tokens durante as requisições de usuários. Crie um comando agendado ou job em background (`RefreshSocialMediaTokensJob`) que rode periodicamente:
  ```php
  // app/Console/Commands/RefreshSocialMediaTokens.php
  public function handle()
  {
      $nearExpiration = SocialMediaCredential::all()->filter(fn ($cred) => $cred->isNearExpiration());
      foreach ($nearExpiration as $credential) {
          RefreshSocialMediaTokenJob::dispatch($credential);
      }
  }
  ```
- **Integração com Horizon/Filas**: Despache os jobs de refresh de token para uma fila dedicada com rate limits, intervalos de retry e configurações de timeout adequados.

### 4. Tratamento de Tokens Invalidados ou Revogados
- **Fronteira de Exceção**: Capture exceções de client/HTTP da API externa (ex: 401 Unauthorized ou 403 Forbidden) e verifique mensagens de erro que denotem tokens inválidos ou revogados (ex: OAuthException do Facebook, InvalidToken do LinkedIn).
- **Disparo de Evento**: Despache um evento `SocialMediaTokenInvalidated` quando a renovação falhar ou um token for confirmado como revogado:
  ```php
  event(new SocialMediaTokenInvalidated($credential));
  ```
- **Notificação ao Usuário**: Escute esse evento para desabilitar a conexão, registrar o erro e notificar o tenant (agência/cliente) na UI para reconectar sua conta manualmente.

### 5. Testes e Mocking com Pest
- **Mocking de HTTP**: Use `Http::fake()` para interceptar as requisições OAuth de saída.
- **Asserções com Pest**: Escreva testes Pest claros simulando renovações de token bem-sucedidas e falhas:
  ```php
  it('successfully refreshes near-expired token', function () {
      Http::fake([
          'https://api.linkedin.com/v2/*' => Http::response(['access_token' => 'new-token', 'expires_in' => 3600]),
      ]);

      $credential = SocialMediaCredential::factory()->create([
          'platform' => 'linkedin',
          'credentials' => [
              'access_token' => 'old-token',
              'refresh_token' => 'old-refresh',
              'expires_at' => now()->addMinutes(10)->timestamp,
          ],
      ]);

      $driver = new LinkedInDriver();
      $success = $driver->refreshToken($credential);

      expect($success)->toBeTrue();
      expect($credential->fresh()->credentials['access_token'])->toBe('new-token');
  });
  ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- NUNCA armazene credenciais, access tokens ou refresh tokens em texto puro em tabelas do banco de dados ou entradas de log.
- NUNCA envie credenciais ou tokens crus ao frontend nem os exponha em respostas de API.
- NUNCA renove tokens de forma síncrona dentro de requisições HTTP padrão; sempre use jobs agendados ou filas.
- NUNCA engula (swallow) exceções da API de refresh; registre-as e notifique o cliente/usuário quando ação manual for necessária.
