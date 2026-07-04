---
name: laravel-tiktok-api-integration-best-practices
description: Use when implementing, reviewing, or debugging TikTok API integrations, managing TikTok OAuth v2 authentication flows, uploading and publishing videos using the TikTok Content Posting API, retrieving user profile metrics, handling TikTok webhooks, or processing rate limit responses in Laravel. Triggers on files modifying TikTokService, TikTokController, or TikTok OAuth drivers.
---

# Boas Práticas de Integração da API do TikTok com Laravel

## Objetivo
Estabelecer diretrizes seguras, robustas e resilientes para integrar a API v2 do TikTok, gerenciar tokens OAuth v2 de longa duração, executar uploads de vídeo resumíveis em chunks, tratar rate limits e processar notificações de webhook dentro do backend baseado em Laravel da aplicação Engeapp/SocialMedia.

## Instruções

### 1. OAuth v2 do TikTok e Gerenciamento de Tokens
- **Segurança e Armazenamento**: Siga as diretrizes de criptografia em `laravel-social-media-oauth-token-lifecycle-management-best-practices`. Criptografe todas as credenciais do TikTok (`access_token`, `refresh_token`, `client_key`, `client_secret`) dentro do model `SocialMediaCredential` usando o cast `encrypted:array`.
- **Ciclos de Vida de Expiração dos Tokens**:
  - `access_token`: Válido por 24 horas.
  - `refresh_token`: Válido por 365 dias.
- **Comando de Renovação Proativa**: Agende um comando que roda a cada 12 horas (via Laravel Scheduler) para renovar automaticamente os access tokens que se aproximam da janela de expiração (por exemplo, dentro de 4 horas).
  ```php
  // app/Console/Commands/RefreshTikTokTokens.php
  public function handle()
  {
      $credentials = SocialMediaCredential::where('platform', 'tiktok')->get();
      foreach ($credentials as $credential) {
          if ($credential->isNearExpiration(14400)) { // 4 horas em segundos
              RefreshTikTokTokenJob::dispatch($credential);
          }
      }
  }
  ```
- **Abstração de Driver**: Implemente um driver Socialite customizado ou estenda um provider manager de OAuth do TikTok (`TikTokDriver`) implementando a interface unificada `SocialMediaProviderDriver`.

### 2. Arquitetura do Conector BaseApi
Todas as requisições à API do TikTok devem herdar da estrutura nativa `BaseApi`. Defina a integração em `app/Http/Integrations/TikTok/`:
- **Connector (`Connector.php`)**: Estende `BaseApi` e define a URL base `https://open.tiktokapis.com/`. Deve implementar `getAccessToken()` para injetar o token OAuth v2 ativo no header `Authorization: Bearer`.
- **Definição de Attributes (`Attributes.json`)**: Valide os parâmetros de query/body, como `video_size`, `chunk_size`, `title`, `privacy_level`.
- **Mapeamento de Endpoints (`EndPoints.json`)**:
  ```json
  {
    "video": {
      "init": {
        "end_point": "v2/post/publish/video/init/",
        "method": "POST",
        "description": "Initialize a resumable chunked video upload"
      },
      "uploadChunk": {
        "end_point": "v2/post/publish/video/upload/",
        "method": "PUT",
        "description": "Upload a specific chunk of the video"
      }
    }
  }
  ```

### 3. Uploads de Vídeo em Chunks (Resumable Upload)
O TikTok exige uploads de vídeo em chunks (resumíveis) para uma transferência de vídeo confiável. A sequência de upload envolve três etapas executadas de forma assíncrona:
1. **Inicializar o Upload (`init`)**:
   - Envie os metadados do vídeo (`video_size`, `total_chunk_count`) ao endpoint de inicialização para receber a `upload_url` e um identificador único.
2. **Loop de Upload de Chunks (`uploadChunk`)**:
   - Divida o arquivo de vídeo em chunks. O tamanho recomendado de chunk fica entre 5MB e 64MB (de acordo com as especificações do TikTok).
   - Cada chunk deve ser enviado à `upload_url` gerada usando uma requisição `PUT` com os cabeçalhos apropriados:
     - `Content-Range: bytes START_BYTE-END_BYTE/TOTAL_SIZE`
     - `Content-Type: video/mp4`
   - Implemente isso em um Job assíncrono do Laravel (`UploadTikTokVideoChunksJob`) para evitar o bloqueio das requisições.
3. **Configuração da Fila do Horizon**:
   - Atribua o job de upload de chunks à fila `default`.
   - Use políticas de backoff padrão para tratar timeouts temporários de upload: `$tries = 3` e `$backoff = [30, 60, 120]`.

### 4. Rate Limiting e Tratamento de Erros
- **Rate Limit (Respostas 429)**: Use a estratégia de backoff exponencial definida em `laravel-jobs-queues-horizon-best-practices`. Se uma requisição ao TikTok retornar `429 Too Many Requests`, devolva o job à fila com um delay:
  ```php
  public function handle()
  {
      try {
          $response = $this->tiktokConnector->publishVideo(...);
      } catch (RateLimitException $e) {
          $this->release(300); // Aguarde 5 minutos antes de tentar novamente
          return;
      }
  }
  ```
- **Revogação de Token (Respostas 401/403)**: Se a API do TikTok lançar um erro indicando que o token foi revogado, despache um evento `SocialMediaTokenInvalidated` para notificar o tenant via Reverb a se reautenticar.

### 5. Tratamento de Webhooks
- **Verificação**: O TikTok envia uma assinatura de verificação nos cabeçalhos da requisição de webhook. Verifique o payload da assinatura contra o Client Secret configurado antes de processar.
- **Processamento Assíncrono**:
  - Aceite o payload do webhook e retorne imediatamente uma resposta `200 OK` ao servidor do TikTok.
  - Despache um job (`ProcessTikTokWebhookJob`) para a fila `webhooks` (`->onQueue('webhooks')`) para tratar os dados do evento (por exemplo, processamento de upload de vídeo concluído ou falhado).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- NUNCA execute uploads de chunks de vídeo de forma síncrona dentro de requisições HTTP padrão.
- NUNCA registre em log tokens OAuth brutos ou client secrets.
- NUNCA faça cache de respostas de erro (HTTP 4xx ou 5xx) retornadas pela API do TikTok.
- SEMPRE use a estrutura nativa `BaseApi` e `Connector` para as comunicações HTTP com o TikTok.
- SEMPRE verifique IDs de publicação existentes para garantir idempotência e evitar postagens duplicadas.
