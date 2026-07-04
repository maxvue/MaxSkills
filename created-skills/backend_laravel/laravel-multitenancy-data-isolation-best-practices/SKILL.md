---
name: laravel-multitenancy-data-isolation-best-practices
description: Use when designing, reviewing, or debugging multi-tenant architectures, data isolation, query scopes, and tenant middleware in Laravel. Triggers on requests involving database filters by tenant id (e.g., solar_company_id, designer_solar_company_id), global Eloquent query scopes, and tenant context resolution.
---

# Boas Práticas de Multi-tenancy e Isolamento de Dados no Laravel

## Objetivo
Estabelecer diretrizes robustas, seguras e escaláveis para o isolamento de dados multi-tenant em aplicações Laravel. Garantir a separação estrita de dados de cliente, projeto e documento usando global query scopes do Eloquent, middleware de resolução de tenant, gerenciadores de contexto e integração com Artisan/Job para prevenir vazamento de dados entre tenants.

## Instruções

### 1. Gerenciamento de Contexto de Tenant (TenantManager)
- Defina um gerenciador singleton thread-safe ou utilize a facade `Context` (Laravel 11+) para manter o estado do tenant ativo durante o ciclo de vida da requisição/processo.
- Implemente um helper ou facade para obter/definir o ID do tenant ativo (ex: o ID de `UserSolarCompany`).
- Exemplo:
  ```php
  namespace App\Services;

  use Illuminate\Support\Facades\Context;

  class TenantManager
  {
      public static function setTenantId(string $tenantId): void
      {
          Context::add('tenant_id', $tenantId);
      }

      public static function getTenantId(): ?string
      {
          return Context::get('tenant_id');
      }

      public static function hasTenant(): bool
      {
          return Context::has('tenant_id');
      }

      public static function forgetTenant(): void
      {
          Context::forget('tenant_id');
      }
  }
  ```

### 2. Middleware de Resolução de Tenant
- Crie um middleware para resolver o tenant ativo a partir do contexto do usuário autenticado (`auth()->user()->solar_company_id`) ou de headers customizados.
- Defina o ID do tenant resolvido no `TenantManager` no início do ciclo de vida da requisição.
- Exemplo:
  ```php
  namespace App\Http\Middleware;

  use Closure;
  use App\Services\TenantManager;
  use Illuminate\Http\Request;
  use Symfony\Component\HttpFoundation\Response;

  class ResolveTenant
  {
      public function handle(Request $request, Closure $next): Response
      {
          if (auth()->check()) {
              $user = auth()->user();
              if ($user->solar_company_id) {
                  TenantManager::setTenantId($user->solar_company_id);
              }
          }

          return $next($request);
      }
  }
  ```

### 3. Traits Reutilizáveis de Tenant e Global Scopes
- Crie uma trait reutilizável (ex: `BelongsToTenant`) para ser usada em models que exigem isolamento de tenant.
- Registre automaticamente um `TenantScope` e conecte-se ao evento `creating` do model para definir o `solar_company_id` automaticamente.
- Exemplo de Trait:
  ```php
  namespace App\Traits;

  use App\Scopes\TenantScope;
  use App\Services\TenantManager;
  use App\Models\User\UserSolarCompany;

  trait BelongsToTenant
  {
      public static function bootBelongsToTenant(): void
      {
          static::creating(function ($model) {
              if (TenantManager::hasTenant() && ! $model->solar_company_id) {
                  $model->solar_company_id = TenantManager::getTenantId();
              }
          });

          static::addGlobalScope(new TenantScope);
      }

      public function tenant()
      {
          return $this->belongsTo(UserSolarCompany::class, 'solar_company_id');
      }
  }
  ```
- Exemplo de Global Scope (`TenantScope`):
  ```php
  namespace App\Scopes;

  use App\Services\TenantManager;
  use Illuminate\Database\Eloquent\Builder;
  use Illuminate\Database\Eloquent\Model;
  use Illuminate\Database\Eloquent\Scope;

  class TenantScope implements Scope
  {
      public function apply(Builder $builder, Model $model): void
      {
          if (TenantManager::hasTenant()) {
              $builder->where($model->getTable() . '.solar_company_id', TenantManager::getTenantId());
          }
      }
  }
  ```

### 4. Scopes Especiais (ex: `designer_solar_company_id` / Projetos)
- Se algumas tabelas utilizam nomes de coluna alternativos (como `designer_solar_company_id` em models `Project`), implemente uma trait customizada (ex: `BelongsToDesignerTenant`) ou configure a coluna dinamicamente no scope.
- Garanta que o scope aponte para o nome de coluna correto na tabela de banco correta para prevenir ambiguidade de SQL durante joins.

### 5. Isolamento de Tenant em Jobs e Filas do Horizon
- Como os background jobs rodam em um contexto CLI sem sessões ou middleware de requisição HTTP, você deve passar o contexto do tenant explicitamente para os queued jobs.
- Injete o ID do tenant ativo no construtor da classe do job e defina o contexto do tenant no método `handle()` do job ou via job middleware.
- Exemplo de Job:
  ```php
  namespace App\Jobs;

  use App\Services\TenantManager;
  use Illuminate\Bus\Queueable;
  use Illuminate\Contracts\Queue\ShouldQueue;
  use Illuminate\Foundation\Bus\Dispatchable;
  use Illuminate\Queue\InteractsWithQueue;
  use Illuminate\Queue\SerializesModels;

  class SyncProjectTelemetry implements ShouldQueue
  {
      use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

      protected string $tenantId;

      public function __construct(string $tenantId)
      {
          $this->tenantId = $tenantId;
      }

      public function handle(): void
      {
          TenantManager::setTenantId($this->tenantId);

          try {
              // Executa operações de banco isoladas por tenant
          } finally {
              TenantManager::forgetTenant();
          }
      }
  }
  ```

### 6. Validação e Policies
- Utilize Form Requests e Policies do Laravel para verificar novamente que os usuários não podem solicitar ou atualizar recursos pertencentes a um tenant diferente.
- Exemplo de validação em Policy:
  ```php
  public function update(User $user, Project $project): bool
  {
      return $user->solar_company_id === $project->designer_solar_company_id;
  }
  ```

## Restrições
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
- **Sem Filtragem de Tenant Hardcoded/Manual:** Evite fazer queries com filtros manuais `->where('solar_company_id', ...)`. Confie na trait `BelongsToTenant` e no seu global scope para prevenir descuidos de desenvolvedor e vazamento de dados.
- **Restauração do Contexto de Tenant:** Sempre limpe ou restaure o contexto do tenant ao final de background jobs, comandos Artisan ou execuções de teste, para evitar vazamentos de memória ou contaminação de contexto entre jobs consecutivos (especialmente sob o Octane).
- **Bypass Explícito de Scope:** Restrinja o bypass do tenant scope usando `withoutGlobalScope(TenantScope::class)` a operações de nível de sistema, dashboards administrativos, ou comandos de console cross-tenant explicitamente aprovados. Documente todas as instâncias de bypass de scope.
- **Restrições de Schema de Banco:** Todas as tabelas específicas de tenant devem ter chaves estrangeiras `solar_company_id` (ou similar) indexadas, definidas como `NOT NULL` com regras de cascade apropriadas em suas migrations.
