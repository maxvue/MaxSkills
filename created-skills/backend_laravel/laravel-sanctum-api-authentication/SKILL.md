---
name: laravel-sanctum-api-authentication
description: Use when configuring, implementing, securing, or debugging API authentication using Laravel Sanctum. Triggers on Sanctum token creation, SPA cookie authentication, Sanctum middleware, and API token guard configurations.
---

# Autenticação de API com Laravel Sanctum

## Objetivo
Estabelecer diretrizes sólidas e boas práticas para implementar autenticação de API e SPA usando o Laravel Sanctum no ecossistema Engeapp, garantindo segurança, performance e testes consistentes.

## Instruções

### 1. Configuração de Autenticação Stateful para SPA
A autenticação stateful é usada para o front-end do Engeapp (Vue SPA com Vue Router, SPA pura) para permitir requisições autenticadas baseadas em cookie e seguras por sessão.

- **Habilite o Middleware Stateful do Sanctum**:
  Em `bootstrap/app.php` (Laravel 13), anexe o middleware stateful ao grupo de middleware `web`:
  ```php
  $middleware->web(append: [
      \Laravel\Sanctum\Http\Middleware\EnsureFrontendRequestsAreStateful::class,
  ]);
  ```

- **Configure as Variáveis de Ambiente**:
  Configure os domínios stateful e as definições de domínio de sessão no seu arquivo `.env`:
  ```env
  SANCTUM_STATEFUL_DOMAINS=localhost,127.0.0.1,localhost:3000,engeapp.test
  SESSION_DOMAIN=.engeapp.test
  ```

- **Inicialização do Cookie CSRF**:
  Antes de fazer uma requisição de login a partir da SPA, solicite o cookie CSRF para inicializar a sessão:
  ```javascript
  axios.get('/sanctum/csrf-cookie').then(response => {
      // Prossiga com a requisição de login
  });
  ```

### 2. Personal Access Tokens (Autenticação de API)
Personal Access Tokens (PATs) são usados para aplicações mobile, integrações de terceiros e rotas de API headless.

- **Configure o Model User**:
  Garanta que o model `User` importe e use a trait `HasApiTokens`:
  ```php
  namespace App\Models;

  use Illuminate\Foundation\Auth\User as Authenticatable;
  use Laravel\Sanctum\HasApiTokens;

  class User extends Authenticatable
  {
      use HasApiTokens;
  }
  ```

- **Emita Tokens**:
  Crie um token com habilidades/escopos opcionais para o usuário autenticado:
  ```php
  $token = $user->createToken('api-token', ['read:projects', 'write:projects']);
  
  // Retorna o token em texto puro para o cliente (visível apenas uma vez)
  return response()->json([
      'token' => $token->plainTextToken
  ]);
  ```

- **Verifique Habilidades (Rota ou Controller)**:
  Verifique as habilidades do token antes de permitir o acesso a recursos:
  ```php
  if ($request->user()->tokenCan('write:projects')) {
      // Prossiga com a modificação
  }
  ```

- **Revogue Tokens**:
  Revogue tokens para logout ou rotação de chaves:
  ```php
  // Revoga o token atualmente em uso
  $request->user()->currentAccessToken()->delete();

  // Revoga todos os tokens do usuário
  $user->tokens()->delete();
  ```

### 3. Testando Autenticação com Pest
Siga estes padrões para autenticar requisições de API nos seus feature tests.

- **Autenticação por Token de API (Pest)**:
  Use `Sanctum::actingAs` para mockar um usuário com habilidades de token específicas:
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

- **Autenticação por Cookie de SPA**:
  Use o `$this->actingAs` padrão para testes normais de rotas web/SPA:
  ```php
  test('user can access dashboard', function () {
      $user = User::factory()->create();

      $response = $this->actingAs($user)->get('/dashboard');

      $response->assertStatus(200);
  });
  ```

### 4. Hardening de Segurança e Limpeza (Pruning)
- **Limpeza de Tokens**:
  Agende a limpeza de tokens expirados dentro de `routes/console.php` (Laravel 13) ou no seu provider de agendamento:
  ```php
  use Illuminate\Support\Facades\Schedule;

  Schedule::command('sanctum:prune-expired --hours=24')->daily();
  ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Nunca exponha o token em texto puro** em quaisquer respostas ou logs após sua criação inicial.
- **Não use autenticação stateful por cookie** para webhooks externos ou APIs de terceiros. Sempre use Personal Access Tokens.
- **Não pule a verificação CSRF** em rotas que usam autenticação de sessão stateful baseada em cookie.
- **Nunca armazene tokens brutos** em logs de usuário ou serviços de relatório de erros.
