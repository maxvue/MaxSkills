---
name: laravel-authorization-policies-gates
description: "Use when creating or reviewing authorization in Laravel via spatie/laravel-permission. Covers roles/permissions, Gates, multi-tenant Policies (allowedSolarCompanyIds), and Vue SPA MaxPinia integration. Covers objectives and core workflows."
author: Johnattas Conrady Gomes Santana
---
# Laravel Authorization Policies and Gates

## Objetivo
Padronizar a autorização do backend engeapp (Laravel 13 / PHP 8.4). O RBAC real do projeto é o **spatie/laravel-permission** (`"spatie/laravel-permission": "^8.1"`): o `User` usa o trait `HasRoles`, as permissões têm nomes pontilhados em pt (ex.: `projeto.ver`, `projeto.criar`, `documento.enviar`, `usuario.gerenciar`) e o Spatie as registra automaticamente como gates — por isso funcionam em `can:...`. Policies acrescentam escopo multi-tenant. Gates ad-hoc cobrem apenas casos que não mapeiam para um model nem para uma permissão nomeada.

## Instruções

1. **RBAC com spatie/laravel-permission (mecanismo primário)**:
   - O `User` já inclui `use Spatie\Permission\Traits\HasRoles;`. NÃO reimplemente checagem de role/permissão manualmente.
   - Verifique acesso com `hasRole()` / `hasPermissionTo()`:
     ```php
     if ($user->hasRole('global_admin')) {
         return true;
     }

     return $user->hasPermissionTo('projeto.criar');
     ```
   - As permissões são criadas por seeders/migrations do Spatie e o pacote as registra como gates. Assim, um nome de permissão como `projeto.ver` já é utilizável em `Gate::allows('projeto.ver')`, `$user->can('projeto.ver')` e no middleware `can:projeto.ver`.
   - Use nomes de permissão pontilhados em pt-BR (`recurso.acao`), seguindo o padrão existente no projeto.

2. **Policies com escopo multi-tenant**:
   - Coloque policies em `app/Policies/`, nome `{ModelName}Policy` (auto-discovery do Laravel). Exemplos reais: `ProjectPolicy`, `ClientPolicy`.
   - Type-hint estrito do `User` e do model. Dentro da policy, combine role global + permissão nomeada + escopo de tenant. O tenant é resolvido por `User::allowedSolarCompanyIds()`.
   - Espelhe a `ProjectPolicy` real:
     ```php
     <?php

     namespace App\Policies;

     use App\Models\Project\Project;
     use App\Models\User;

     class ProjectPolicy
     {
         public function view(User $user, Project $project) : bool
         {
             if ($user->hasRole('global_admin')) {
                 return true;
             }

             return $this->belongsToTenant($user, $project);
         }

         public function create(User $user) : bool
         {
             return $user->hasPermissionTo('projeto.criar');
         }

         public function uploadDocument(User $user, Project $project) : bool
         {
             if ($user->hasRole('global_admin')) {
                 return $user->hasPermissionTo('documento.enviar');
             }

             return $this->belongsToTenant($user, $project) && $user->hasPermissionTo('documento.enviar');
         }

         /**
          * Resolve o tenant via o cliente do projeto. Projeto órfão (sem cliente) nega por padrão.
          */
         private function belongsToTenant(User $user, Project $project) : bool
         {
             $solarCompanyId = $project->client?->solar_company_id;

             if ($solarCompanyId === null) {
                 return false;
             }

             return in_array($solarCompanyId, $user->allowedSolarCompanyIds(), true);
         }
     }
     ```
   - Por que: role global é atalho de bypass; a permissão nomeada expressa a capacidade; `belongsToTenant` impede que um usuário acesse dados de outra empresa solar. Nunca compare `$user->id === $model->user_id` como regra de autorização — não é o padrão do projeto.

3. **Gates ad-hoc (só quando não há model nem permissão nomeada)**:
   - Use Gates apenas para acessos que não mapeiam para um model Eloquent nem para uma permissão do Spatie — tipicamente painéis de dev/observabilidade.
   - Registre no `boot()` do `AppServiceProvider`. Exemplos reais do projeto:
     ```php
     $allowedEmails = ['gd@homelifesolar.com.br'];

     Gate::define('viewPulse', fn ($user) => $user->is_developer || in_array($user->email, $allowedEmails));
     Gate::define('viewTotem', fn ($user) => $user->is_developer || in_array($user->email, $allowedEmails));
     ```
   - Também existem `viewHorizon` (`HorizonServiceProvider`) e `viewTelescope` (`TelescopeServiceProvider`). Prefira permissão nomeada do Spatie sempre que a ação for de negócio.

4. **Protegendo rotas — middleware `can` com permissão NOMEADA**:
   - A convenção real do engeapp é `can:<permissao.nomeada>`, **sem** parâmetro de model. Não use `can:update,project`.
   - Exemplos reais (`routes/web/Web.Integrador.Routes.php`, `routes/web/Web.AdminUser.Routes.php`):
     ```php
     Route::get('dashboard', [IntegradorDashboardController::class, 'dashboard'])
         ->middleware('can:projeto.ver')->name('dashboard');

     Route::post('clients', [IntegradorClientController::class, 'store'])
         ->middleware('can:projeto.criar')->name('clients.store');

     // Grupo inteiro protegido por uma permissão:
     Route::middleware(['auth', 'verified', 'can:usuario.gerenciar'])
         ->prefix('admin')->name('admin.')
         ->group(function () : void {
             // rotas de administração de usuários
         });
     ```
   - Para autorizar contra uma Policy de um model específico, faça no controller (ver abaixo), não no middleware de rota.

5. **Autorização em nível de controller**:
   - `$this->authorize(...)` só funciona se o controller usar o trait `Illuminate\Foundation\Auth\Access\AuthorizesRequests` — a classe base `App\Http\Controllers\Controller` é vazia (`abstract class Controller {}`), sem esse trait:
     ```php
     use Illuminate\Foundation\Auth\Access\AuthorizesRequests;

     class IntegradorProjectController extends Controller
     {
         use AuthorizesRequests;

         public function update(Request $request, Project $project)
         {
             $this->authorize('view', $project); // dispara ProjectPolicy::view

             $project->update($request->validated());
         }
     }
     ```
   - `Gate::authorize('view', $project);` é uma opção igualmente comum no projeto (usada em `ProjectTrtPaymentController` e `ProjectsInvoiceExecuteController`) e dispensa o trait — prefira-a quando o controller não usar `AuthorizesRequests`. Use middleware `can:permissao.nomeada` para permissões grosseiras e a Policy no controller (por qualquer uma das duas formas) para regras por instância/tenant.

6. **Expondo permissões para a SPA Vue (via store MaxPinia)**:
   - O payload do usuário autenticado já é servido por `UserDataControler::getAuthUserData` (rota nomeada `user.data`, `routes/web/Web.User.Route.php:39`) e consumido pela store real `useUserStore` (`resources/Stores/UserStores/useUser.Store.ts`). Um mapa `can` de permissões com escopo deve ser um acréscimo a esse payload/store existente — não exponha a base inteira de permissões, limite ao que a tela precisa:
     ```php
     public function getAuthUserData(Request $request)
     {
         $user = $request->user();

         return response()->json([
             'user' => $user,
             'can' => [
                 'projeto.criar'    => $user?->can('projeto.criar') ?? false,
                 'documento.enviar' => $user?->can('documento.enviar') ?? false,
             ],
         ]);
     }
     ```
   - No front-end, todo GET passa por uma **store MaxPinia** (`@maxvue/max-pinia`); nunca faça fetch direto no componente e nunca leia permissões de props de página. O contrato real da store: `isCached` (`ref`), `options` computado com `get.route` recebendo o **nome de rota Ziggy pontilhado** (o `apiGetRoute`/plugin resolve internamente via Ziggy), `save` e `key`. Espelhe o formato real:
     ```ts
     export const useUserStore = defineStore('user', () => {
         const isCached: Ref = ref(true);
         // options.get.route é o NOME Ziggy pontilhado, resolvido internamente pelo apiGetRoute
         const options: Ref = computed(() => ({ get: { route: 'user.data' }, save: 'user.save', key: 'user' }));
         const data: Ref<User | null> = ref(null);

         return { options, isCached, data };
     });
     ```
     ```vue
     <script setup lang="ts">
     const user = useUserStore(); // a store carrega o payload em seu estado cacheado
     </script>

     <template>
       <MaxButton v-if="user.data?.can?.['projeto.criar']" @click="openModal">
         Novo Projeto
       </MaxButton>
     </template>
     ```
   - Se um exemplo genérico (nome de rota diferente de `user.data`) for necessário, marque explicitamente o nome como placeholder a implementar — nunca como rota já existente.
   - Use componentes `Max*` de `@maxvue/max-components-ui` (ex.: `MaxButton`), nunca `<button>` nativo, e composables de `@maxvue/max-use` no lugar de vueuse/lodash crus.

7. **Testes com Pest**:
   - Escreva feature tests cobrindo roles/permissões do Spatie e Gates. Espelhe o setup real de `tests/Feature/Integrador/ClientPolicyTest.php`: um `beforeEach` cria as permissões usadas com `Permission::findOrCreate(...)` — sem isso `givePermissionTo` lança `PermissionDoesNotExist`, pois a permissão precisa existir no banco antes de ser atribuída. Quando o teste envolver escopo de tenant, crie `UserSolarCompany` e passe `solar_company_id` + `international_phone_number` único no factory — `UserFactory` não os define, e `allowedSolarCompanyIds()` retorna `[]` sem `solar_company_id`. `Queue::fake()` pode ser citado como prática dos testes existentes, mas não é obrigatório (não há job disparado na criação de `User`).
     ```php
     use Illuminate\Support\Facades\Gate;
     use Spatie\Permission\Models\Permission;

     beforeEach(function () : void {
         Permission::findOrCreate('projeto.criar', 'web');
     });

     it('permite quem tem a permissão projeto.criar', function () {
         $user = User::factory()->create();
         $user->givePermissionTo('projeto.criar');

         expect($user->can('projeto.criar'))->toBeTrue();
     });

     it('nega dashboard do integrador sem projeto.ver', function () {
         $user = User::factory()->create();

         $this->actingAs($user)
             ->get(route('integrador.dashboard'))
             ->assertForbidden();
     });

     it('permite viewPulse a um developer', function () {
         $user = User::factory()->create(['is_developer' => true]);

         expect(Gate::forUser($user)->allows('viewPulse'))->toBeTrue();
     });
     ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- Prefira **roles/permissões nomeadas do Spatie** (`hasRole`/`hasPermissionTo`, `can:permissao.nomeada`) à checagem manual. NÃO escreva `if ($user->role === 'admin')` nem `$user->id === $model->user_id` como regra de autorização.
- NÃO use `can:ability,model` no middleware de rota (não é a convenção do projeto); use `can:permissao.nomeada` na rota e a Policy no controller para regras por instância/tenant.
- NÃO exponha arrays completos e sem escopo de permissões no payload `/api`. Mantenha o mapa `can` mínimo e com escopo ao usuário.
- NÃO pule verificação no backend supondo que o front esconde a UI. O backend é a única fonte de verdade; toda Policy deve resolver o escopo de tenant via `allowedSolarCompanyIds()` quando aplicável.
- NÃO deixe pass-through implícito nas policies: retorne booleanos explícitos (projeto órfão/sem tenant nega por padrão).
