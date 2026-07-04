---
name: laravel-google-calendar-integration-best-practices
description: Use when integrating, configuring, or debugging Google Calendar API operations in Laravel, including OAuth token management, event scheduling for technical visits, calendar sync, and webhook handling. Triggers on Spatie Google Calendar usage, API requests to Google Calendar, and event sync jobs.
---

# Boas Práticas de Integração do Google Calendar com Laravel

## Objetivo
Estabelecer padrões limpos, seguros e resilientes para integrar e sincronizar eventos com a API do Google Calendar dentro do backend Laravel do Engeapp. Isso inclui configurar service accounts, gerenciar tokens OAuth específicos de usuário, transferir a comunicação com a API para background jobs e tratar exceções da API de forma elegante.

## Instruções

> **⚠️ Estado atual no engeapp:** NEM `google/apiclient` NEM `spatie/laravel-google-calendar` estão instalados (não constam no `composer.json`). A lógica de calendário real do projeto vive em serviços próprios: `app/Services/Calendar/EventInsightsService.php`, `app/Services/Calendar/EventPublishingService.php` e `app/Services/Calendar/ThemeScheduleService.php` — comece por eles. As classes de SDK citadas abaixo (`Google\Client`, `Google\Service\Calendar`, etc.) só funcionam **após** rodar `composer require` do pacote correspondente; até lá, trate-as como caminho opcional a ser habilitado explicitamente, não como algo já disponível.

### 1. Instalação e Seleção do Pacote
* **Instale primeiro:** os pacotes de SDK abaixo NÃO estão no projeto. Antes de usar qualquer classe `Google\*`, rode `composer require` do pacote escolhido e configure as credenciais.
* Por padrão, use o Google API Client oficial (`google/apiclient`) para operações OAuth de baixo nível ou complexas multi-tenant — requer `composer require google/apiclient`.
* Para configurações simples, de conta única, ou baseadas em service account (ex: um calendário corporativo central), utilize o popular wrapper `spatie/laravel-google-calendar` — requer `composer require spatie/laravel-google-calendar`.
* Garanta que os pacotes estejam declarados no `composer.json` e devidamente configurados.

### 2. Gerenciamento Seguro de Credenciais
* **JSON da Service Account:** Nunca faça commit do arquivo JSON de credenciais do Google diretamente no repositório. Carregue o conteúdo do JSON a partir de uma variável de ambiente (ex: `GOOGLE_SERVICE_ACCOUNT_JSON` ou `GOOGLE_CALENDAR_AUTH_PROFILES_SERVICE_ACCOUNT_CREDENTIALS_JSON`) ou armazene-o em um caminho seguro definido no `.env`.
* **Tokens OAuth de Usuário:** Se estiver integrando calendários individuais de usuários (OAuth 2.0), armazene os refresh tokens, access tokens e expirações em uma tabela de banco de dados segura.
  * Sempre criptografe os tokens em repouso. Use o cast do Eloquent do Laravel:
    ```php
    protected function casts(): array
    {
        return [
            'access_token' => 'encrypted',
            'refresh_token' => 'encrypted',
        ];
    }
    ```

### 3. Arquitetura de Classes de Serviço
* Envolva todas as interações com o Google Calendar dentro de classes de Serviço dedicadas sob `App\Services` (ex: `App\Services\GoogleCalendarService`) em conformidade com `laravel-services-best-practices`.
* Injete dependências via construtor e resolva o Google Client usando o Service Container do Laravel.
* Exemplo de instanciação dinâmica do Google Client para OAuth específico de usuário (**requer `composer require google/apiclient` — as classes `Google\*` não existem no projeto até a instalação**):
  ```php
  namespace App\Services;

  use Google\Client;
  use Google\Service\Calendar;
  use App\Models\UserCalendarConnection;

  class GoogleCalendarService
  {
      protected Client $client;

      public function __construct()
      {
          $this->client = new Client();
          $this->client->setClientId(config('services.google.client_id'));
          $this->client->setClientSecret(config('services.google.client_secret'));
      }

      public function forConnection(UserCalendarConnection $connection): self
      {
          $this->client->setAccessToken([
              'access_token' => $connection->access_token,
              'refresh_token' => $connection->refresh_token,
              'expires_in' => $connection->expires_in,
              'created' => $connection->updated_at->timestamp,
          ]);

          if ($this->client->isAccessTokenExpired()) {
              $newToken = $this->client->fetchAccessTokenWithRefreshToken($connection->refresh_token);
              $connection->update([
                  'access_token' => $newToken['access_token'],
                  'expires_in' => $newToken['expires_in'],
              ]);
          }

          return $this;
      }
      
      // Operações CRUD do calendário vão aqui
  }
  ```

### 4. Processamento em Background (Filas)
* Nunca execute chamadas à API do Google Calendar de forma síncrona durante requisições HTTP (ex: diretamente dentro de um Controller).
* Despache todas as tarefas de criação, atualização e exclusão como Jobs enfileirados implementando `ShouldQueue`, em conformidade com `laravel-jobs-queues-horizon-best-practices`.
* Defina uma estratégia de backoff exponencial e configure o número máximo de tentativas no Job para lidar com rate limits e falhas temporárias de rede:
  ```php
  public int $tries = 5;

  public function backoff(): array
  {
      return [60, 300, 900, 1800]; // 1m, 5m, 15m, 30m
  }
  ```

### 5. Idempotência e Prevenção de Duplicatas
* Para prevenir duplicatas de agendamento, armazene o `google_event_id` no banco de dados de domínio local (ex: dentro da tabela `technical_visits` ou `appointments`).
* Ao sincronizar, verifique se um `google_event_id` já existe:
  * Se **existir**: Faça uma chamada de API de `update`.
  * Se **não existir**: Faça uma chamada de API de `insert` e salve o ID do evento retornado imediatamente no model local.

### 6. Tratamento de Exceções e Alertas
* Capture `Google\Service\Exception` e exceções gerais de rede (`GuzzleHttp\Exception\TransferException`) explicitamente dentro dos seus serviços/jobs.
* Trate falhas de autenticação (ex: token revogado pelo usuário) marcando a conexão como inválida localmente e alertando o usuário, em vez de falhar o queue job indefinidamente.
* Registre falhas de API com dados de contexto estruturados usando as diretrizes padrão de logging:
  ```php
  Log::error('Google Calendar Sync Failed', [
      'user_id' => $user->id,
      'error' => $exception->getMessage(),
      'code' => $exception->getCode(),
  ]);
  ```

## Restrições
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
* **Sem Chamadas de API Síncronas:** Absolutamente nenhuma requisição HTTP à API do Google Calendar é permitida durante requisições web síncronas.
* **Sem Tokens em Texto Puro:** Não armazene access tokens ou refresh tokens em texto puro no banco de dados.
* **Sem credenciais hardcoded:** Credenciais (client IDs, secrets, detalhes de service account) nunca devem estar hardcoded em arquivos PHP.
* **Sempre Vincule os IDs:** Sempre salve o ID do evento do Google Calendar no banco de dados local imediatamente após a criação, para prevenir a criação de eventos duplicados em retentativas de job.
