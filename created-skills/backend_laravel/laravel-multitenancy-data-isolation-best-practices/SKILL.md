---
name: laravel-multitenancy-data-isolation-best-practices
description: "Use ao projetar, revisar ou depurar o isolamento multi-company do engeapp (Laravel 13). O tenant é a solar_company_id do cliente. Cobre o local scope scopeForUserTenant(Builder, User), o helper User::allowedSolarCompanyIds() (própria + companies atendidas quando projetista) e Policies que resolvem o tenant via cliente. Acione em filtros por solar_company_id ou forUserTenant."
---

# Isolamento de Dados Multi-company no EngeApp

## Objetivo
Garantir que cada usuário só enxergue dados (clientes, projetos, documentos) das solar companies às quais tem acesso. O engeapp NÃO usa global scopes de tenant, trait `BelongsToTenant`, `TenantManager`/`Context` nem middleware de resolução de tenant. O padrão real e testado é um **local scope explícito** (`scopeForUserTenant`) combinado com o helper `User::allowedSolarCompanyIds()`, aplicado nos controllers e revalidado nas Policies.

## Modelo de acesso (verdade-base)
- O "tenant" de um registro é a `solar_company_id` do **cliente** (`clients.solar_company_id`).
- O acesso é **multi-company**, não single-tenant: um usuário pode enxergar várias companies ao mesmo tempo.
- `User::allowedSolarCompanyIds()` (`app/Models/User.php`) retorna a lista de IDs acessíveis:
  - a própria `solar_company_id` do usuário; **mais**
  - se a company for **projetista** (`UserSolarCompany::isProjetista()`), as `attendedCompanies()` (integradoras atendidas) via `array_merge`.
- Por isso um usuário projetista pode ter múltiplas companies atendidas simultaneamente (ver regra normativa completa em Restrições).

```php
// app/Models/User.php — retorna a própria company + (se projetista) as atendidas
public function allowedSolarCompanyIds(): array
{
    if (! $this->solar_company_id) {
        return [];
    }

    $ids = [$this->solar_company_id];
    $company = $this->solar_company()->first();

    if ($company && $company->isProjetista()) {
        $ids = array_merge($ids, $company->attendedCompanies()->pluck('id')->all());
    }

    return $ids;
}
```

## Instruções

### 1. Local scope `scopeForUserTenant(Builder $query, User $user)`
Cada model isolável define um scope que filtra pelas companies acessíveis. É a fonte primária de isolamento em listagens/queries.

- **Client** filtra pela própria coluna `solar_company_id`:
  ```php
  // app/Models/Client/Client.php
  public function scopeForUserTenant(Builder $query, User $user): Builder
  {
      return $query->whereIn($this->getTable() . '.solar_company_id', $user->allowedSolarCompanyIds());
  }
  ```
- **Project** não filtra pela própria coluna: resolve o tenant **via o cliente**, com `whereHas`:
  ```php
  // app/Models/Project/Project.php
  public function scopeForUserTenant(Builder $query, User $user): Builder
  {
      $ids = $user->allowedSolarCompanyIds();

      return $query->whereHas('client', fn (Builder $q) => $q->whereIn('clients.solar_company_id', $ids));
  }
  ```
  Prefixe a coluna com o nome da tabela (`clients.solar_company_id`, `$this->getTable().'.solar_company_id'`) para evitar ambiguidade de SQL em joins.

### 2. Aplicar o scope nos controllers
Chame o scope no ponto de entrada da query. Ele recebe o usuário autenticado explicitamente — NÃO há resolução implícita por middleware/contexto.

```php
// app/Http/Controllers/Integrador/IntegradorClientController.php
$clients = Client::forUserTenant($request->user())
    ->/* ... demais filtros/ordenação ... */
    ->get();
```

### 3. Revalidar nas Policies (defesa em profundidade)
Além do scope na listagem, valide o acesso a um registro individual na Policy, usando `in_array(..., allowedSolarCompanyIds(), true)`. Admins globais têm bypass explícito.

- **ProjectPolicy** resolve o tenant pelo cliente do projeto (não por `designer_solar_company_id`):
  ```php
  // app/Policies/ProjectPolicy.php
  public function view(User $user, Project $project): bool
  {
      if ($user->hasRole('global_admin')) {
          return true;
      }

      return $this->belongsToTenant($user, $project);
  }

  private function belongsToTenant(User $user, Project $project): bool
  {
      $solarCompanyId = $project->client?->solar_company_id;

      // Projeto órfão (sem cliente) nega por padrão.
      if ($solarCompanyId === null) {
          return false;
      }

      return in_array($solarCompanyId, $user->allowedSolarCompanyIds(), true);
  }
  ```
- **ClientPolicy** compara a coluna do próprio cliente:
  ```php
  // app/Policies/ClientPolicy.php
  return in_array($client->solar_company_id, $user->allowedSolarCompanyIds(), true);
  ```

### 4. Preenchimento de colunas de company na criação
O `Project` deriva suas colunas de company **a partir do cliente** no hook `creating` (`app/Models/Project/Project.php`, dentro de `booted()`), não de um contexto de tenant da requisição. Note que `projects` usa `designer_solar_company_id` (não possui `solar_company_id`).

```php
static::creating(static function (self $model): void {
    $model->designer_id = $model->client?->solar_company?->designer?->id ?? '01jn...';
    $model->designer_solar_company_id = $model->client?->solar_company?->id ?? '01jn...';
    // ...
});
```
Ao criar registros isoláveis, garanta que a `solar_company_id` do cliente esteja correta; as colunas derivadas do projeto seguem dela.

### 5. Isolamento em Jobs e comandos
Jobs/comandos rodam sem request nem usuário autenticado. Como o isolamento aqui é explícito (scope recebe `User`, ou você filtra por `whereIn(...allowedSolarCompanyIds())`), passe o `User` ou a lista de IDs de company que o job deve processar de forma explícita — não confie em nenhum contexto global de tenant, pois ele não existe no projeto.

## Restrições
- **Idioma:** Comunique-se com o usuário humano sempre em português (pt-BR), independentemente do idioma do corpo desta skill.
- **Não introduza infraestrutura de tenant inexistente:** o projeto conscientemente NÃO usa global scope, trait `BelongsToTenant`, `TenantManager`/`Context` nem middleware `ResolveTenant`. Não crie esses artefatos nem refatore o padrão `forUserTenant` para eles.
- **`whereIn` por company é deliberado, não "filtro manual a evitar":** o isolamento é feito com `->whereIn(..., $user->allowedSolarCompanyIds())` de forma explícita e testada. Preserve esse padrão; não substitua por igualdade única (`where('solar_company_id', $id)`), que quebraria a visão do projetista sobre companies atendidas.
- **Sempre resolver o tenant do Project via cliente:** use `whereHas('client', ...)` no scope e `$project->client?->solar_company_id` na Policy. Nunca compare `$user->solar_company_id === $project->designer_solar_company_id` (falso-negativo para projetistas).
- **Bypass:** o único bypass legítimo é a role `global_admin` nas Policies. Documente qualquer outro acesso cross-company.
- **Schema:** colunas de isolamento (`clients.solar_company_id`, `projects.designer_solar_company_id`) devem estar indexadas nas migrations.

## Testes de referência
`tests/Feature/Integrador/SolarCompanyScopeTest.php` cobre o comportamento esperado:
- integrador vê só clientes da própria company;
- projetista vê a própria + as companies atendidas (`Client::forUserTenant($user)->count()`).
Espelhe esses casos ao alterar o scope ou o helper.
