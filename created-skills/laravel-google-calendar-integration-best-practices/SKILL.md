---
name: laravel-google-calendar-integration-best-practices
description: Use when integrating, configuring, or debugging Google Calendar API operations in Laravel, including OAuth token management, event scheduling for technical visits, calendar sync, and webhook handling. Triggers on Spatie Google Calendar usage, API requests to Google Calendar, and event sync jobs.
---

# Laravel Google Calendar Integration Best Practices

## Goal
Establish clean, secure, and resilient standards for integrating and synchronizing events with the Google Calendar API within the Engeapp Laravel backend. This includes configuring service accounts, managing user-specific OAuth tokens, offloading API communication to background jobs, and handling API exceptions gracefully.

## Instructions

### 1. Installation & Package Selection
* Default to using the official Google API Client (`google/apiclient`) for low-level or complex multi-tenant OAuth operations.
* For simple, single-account, or service account-based configurations (e.g., a central corporate calendar), utilize the popular wrapper `spatie/laravel-google-calendar`.
* Ensure packages are declared in `composer.json` and properly configured.

### 2. Secure Credentials Management
* **Service Account JSON:** Never commit the Google credentials JSON file directly to the repository. Load the JSON content from an environment variable (e.g., `GOOGLE_SERVICE_ACCOUNT_JSON` or `GOOGLE_CALENDAR_AUTH_PROFILES_SERVICE_ACCOUNT_CREDENTIALS_JSON`) or store it in a secure path defined in `.env`.
* **User OAuth Tokens:** If integrating individual user calendars (OAuth 2.0), store the refresh tokens, access tokens, and expirations in a secure database table.
  * Always encrypt tokens at rest. Use Laravel's Eloquent cast:
    ```php
    protected function casts(): array
    {
        return [
            'access_token' => 'encrypted',
            'refresh_token' => 'encrypted',
        ];
    }
    ```

### 3. Service Classes Architecture
* Wrap all Google Calendar interactions inside dedicated Service classes under `App\Services` (e.g., `App\Services\GoogleCalendarService`) complying with `laravel-services-best-practices`.
* Inject dependencies via the constructor and resolve the Google Client using the Laravel Service Container.
* Example of dynamic Google Client instantiation for user-specific OAuth:
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
      
      // Calendar CRUD operations go here
  }
  ```

### 4. Background Processing (Queues)
* Never execute Google Calendar API calls synchronously during HTTP requests (e.g., directly inside a Controller).
* Dispatch all creation, update, and deletion tasks as queued Jobs implementing `ShouldQueue`, matching `laravel-jobs-queues-horizon-best-practices`.
* Define an exponential backoff strategy and set max tries on the Job to handle rate limits and temporary network failures:
  ```php
  public int $tries = 5;

  public function backoff(): array
  {
      return [60, 300, 900, 1800]; // 1m, 5m, 15m, 30m
  }
  ```

### 5. Idempotency & Duplicate Prevention
* To prevent scheduling duplicates, store the `google_event_id` in the local domain database (e.g., inside `technical_visits` or `appointments` table).
* When syncing, check if a `google_event_id` already exists:
  * If **exists**: Perform an `update` API call.
  * If **not exists**: Perform an `insert` API call, and save the returned event ID immediately to the local model.

### 6. Exception Handling and Alerting
* Catch `Google\Service\Exception` and general network exceptions (`GuzzleHttp\Exception\TransferException`) explicitly inside your services/jobs.
* Handle authentication failures (e.g., token revoked by user) by marking the connection as invalid locally and alerting the user, rather than failing the queue job endlessly.
* Log API failures with structured context data using standard logging guidelines:
  ```php
  Log::error('Google Calendar Sync Failed', [
      'user_id' => $user->id,
      'error' => $exception->getMessage(),
      'code' => $exception->getCode(),
  ]);
  ```

## Constraints
* **No Synchronous API Calls:** Absolutely no Google Calendar HTTP API requests are allowed during synchronous web requests.
* **No Plain-Text Tokens:** Do not store plain-text access or refresh tokens in the database.
* **No hardcoded credentials:** Credentials (client IDs, secrets, service account details) must never be hardcoded in PHP files.
* **Always Bind IDs:** Always save the Google Calendar event ID to the local database immediately after creation to prevent duplicate event creation on job retries.
