---
name: laravel-sanctum-api-authentication
description: Use when configuring, implementing, securing, or debugging API authentication using Laravel Sanctum. Triggers on Sanctum token creation, SPA cookie authentication, Sanctum middleware, and API token guard configurations.
---

# Laravel Sanctum API Authentication

## Goal
Establish solid guidelines and best practices for implementing API and SPA authentication using Laravel Sanctum in the Engeapp ecosystem, ensuring security, performance, and consistent testing.

## Instructions

### 1. Stateful SPA Authentication Configuration
Stateful authentication is used for the Engeapp front-end (Vue SPA com Vue Router, SPA pura) to allow cookie-based, session-safe authenticated requests.

- **Enable Sanctum Stateful Middleware**:
  In `bootstrap/app.php` (Laravel 13), append the stateful middleware to the `web` middleware group:
  ```php
  $middleware->web(append: [
      \Laravel\Sanctum\Http\Middleware\EnsureFrontendRequestsAreStateful::class,
  ]);
  ```

- **Configure Environment Variables**:
  Configure stateful domains and session domain settings in your `.env` file:
  ```env
  SANCTUM_STATEFUL_DOMAINS=localhost,127.0.0.1,localhost:3000,engeapp.test
  SESSION_DOMAIN=.engeapp.test
  ```

- **CSRF Cookie Initialization**:
  Before making a login request from the SPA, request the CSRF cookie to initialize the session:
  ```javascript
  axios.get('/sanctum/csrf-cookie').then(response => {
      // Proceed with the login request
  });
  ```

### 2. Personal Access Tokens (API Authentication)
Personal Access Tokens (PATs) are used for mobile applications, third-party integrations, and headless API routes.

- **Configure User Model**:
  Ensure the `User` model imports and uses the `HasApiTokens` trait:
  ```php
  namespace App\Models;

  use Illuminate\Foundation\Auth\User as Authenticatable;
  use Laravel\Sanctum\HasApiTokens;

  class User extends Authenticatable
  {
      use HasApiTokens;
  }
  ```

- **Issue Tokens**:
  Create a token with optional abilities/scopes for the authenticated user:
  ```php
  $token = $user->createToken('api-token', ['read:projects', 'write:projects']);
  
  // Return the plain text token to the client (only visible once)
  return response()->json([
      'token' => $token->plainTextToken
  ]);
  ```

- **Verify Abilities (Route or Controller)**:
  Check for token abilities before allowing access to resources:
  ```php
  if ($request->user()->tokenCan('write:projects')) {
      // Proceed with modification
  }
  ```

- **Revoke Tokens**:
  Revoke tokens for logging out or cycling keys:
  ```php
  // Revoke the token currently in use
  $request->user()->currentAccessToken()->delete();

  // Revoke all tokens for the user
  $user->tokens()->delete();
  ```

### 3. Testing Authenication with Pest
Follow these patterns to authenticate API requests in your feature tests.

- **API Token Authentication (Pest)**:
  Use `Sanctum::actingAs` to mock a user with specific token abilities:
  ```php
  use App\Models\User;
  use Laravel\Sanctum\Sanctum;

  test('authenticated user can list projects', function () {
      $user = User::factory()->create();
      
      Sanctum::actingAs(
          $user,
          ['read:projects']
      );

      $response = $this->getJson('/api/projects');

      $response->assertStatus(200);
  });
  ```

- **SPA Cookie Authentication**:
  Use standard `$this->actingAs` for normal web/SPA route testing:
  ```php
  test('user can access dashboard', function () {
      $user = User::factory()->create();

      $response = $this->actingAs($user)->get('/dashboard');

      $response->assertStatus(200);
  });
  ```

### 4. Security Hardening and Pruning
- **Token Pruning**:
  Schedule the pruning of expired tokens inside `routes/console.php` (Laravel 13) or your schedule provider:
  ```php
  use Illuminate\Support\Facades\Schedule;

  Schedule::command('sanctum:prune-expired --hours=24')->daily();
  ```

## Constraints
- **Never expose the plain text token** in any responses or logs after its initial creation.
- **Do not use stateful cookie authentication** for external webhooks or third-party APIs. Always use Personal Access Tokens.
- **Do not skip CSRF verification** on routes using stateful cookie-based session authentication.
- **Never store raw tokens** in user logs or error reporting services.
