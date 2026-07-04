---
name: laravel-authorization-policies-gates
description: Use when creating, modifying, or reviewing Laravel authorization logic, including Policies, Gates, role-based access control, route protection, and exposing user permissions to the Vue SPA front-end via /api endpoints consumed by MaxPinia stores. Triggers on gate definitions, policy classes, authorize calls, and 'can' middleware.
---

# Laravel Authorization Policies and Gates

## Objetivo
Estabelecer diretrizes, convenções e padrões para implementar lógica de autorização (policies e gates) no Laravel, protegendo rotas e ações de controller, e expondo as permissões do usuário para o front-end da SPA Vue via endpoints /api consumidos por stores MaxPinia no ecossistema Engeapp.

## Instruções

1. **Policies Eloquent**:
   - Crie policies para todos os models Eloquent principais. Coloque-as no diretório `app/Policies/` e nomeie seguindo o padrão `{ModelName}Policy`.
   - Use o auto-discovery de policies do Laravel sempre que possível, mantendo a estrutura de namespace padrão.
   - Implemente os métodos de recurso padrão (`viewAny`, `view`, `create`, `update`, `delete`) e faça type-hint estrito tanto do `User` quanto do model alvo.
   - Exemplo de estrutura de Policy:
     ```php
     <?php

     namespace App\Policies;

     use App\Models\User;
     use App\Models\Project;

     class ProjectPolicy
     {
         /**
          * Determina se o usuário pode visualizar o projeto.
          */
         public function view(User $user, Project $project): bool
         {
             return $user->id === $project->user_id || $user->is_developer;
         }

         /**
          * Determina se o usuário pode atualizar o projeto.
          */
         public function update(User $user, Project $project): bool
         {
             return $user->id === $project->user_id;
         }
     }
     ```

2. **Gates Globais**:
   - Use Gates para autorização de ações que não mapeiam diretamente para um model Eloquent (ex.: dashboards de administração do sistema, acesso a ferramentas de desenvolvedor).
   - Registre os Gates no método `boot` do `AppServiceProvider.php` (ou um `AuthServiceProvider.php` dedicado, se for complexo).
   - Exemplo de definição de Gate:
     ```php
     use Illuminate\Support\Facades\Gate;

     Gate::define('viewPulse', function (User $user) {
         return $user->is_developer || in_array($user->email, ['gd@homelifesolar.com.br']);
     });
     ```

3. **Protegendo Rotas**:
   - Proteja as rotas usando o middleware `can`, referenciando a ability da policy e passando o nome do parâmetro da rota.
   - Exemplo de roteamento web/API:
     ```php
     Route::put('/projects/{project}', [ProjectController::class, 'update'])
         ->middleware('can:update,project');
     ```

4. **Autorização em Nível de Controller**:
   - Garanta que a autorização seja chamada explicitamente dentro dos controllers antes de executar operações, caso o middleware de rota seja insuficiente.
   - Use os métodos helper do controller ou a facade `Gate` diretamente:
     ```php
     public function update(Request $request, Project $project)
     {
         $this->authorize('update', $project);

         // Alternativamente: Gate::authorize('update', $project);

         $project->update($request->validated());
     }
     ```

5. **Integração com Vue (via /api + store MaxPinia)**:
   - Exponha as permissões de autorização para o front-end da SPA Vue por meio de um endpoint `/api/...` dedicado (ex.: incluído no payload de `/api/auth/me` ou `/api/user`), consumido por uma store MaxPinia.
   - O backend calcula um mapa de permissões com escopo para o usuário autenticado e o retorna a partir de um controller. Evite retornar toda a base de permissões; limite as permissões dinamicamente ao que o usuário requer.
   - Exemplo de controller retornando o mapa de permissões:
     ```php
     // GET /api/auth/me
     public function me(Request $request)
     {
         $user = $request->user();

         return response()->json([
             'user' => $user,
             'can' => [
                 'viewPulse' => $user?->can('viewPulse') ?? false,
                 'createProject' => $user?->can('create', Project::class) ?? false,
             ],
         ]);
     }
     ```
   - Na SPA Vue, consuma esse endpoint via uma store MaxPinia (`@maxvue/max-pinia`) e leia as permissões a partir do estado da store (e não das props da página). Use os helpers `route()` do Ziggy para resolução de rotas do Laravel.
     ```vue
     <script setup lang="ts">
     import { useAuthStore } from '@/stores/auth' // store @maxvue/max-pinia

     const auth = useAuthStore() // a store carrega /api/auth/me em seu estado
     </script>

     <template>
       <button v-if="auth.can.createProject" @click="openModal">
         Novo Projeto
       </button>
     </template>
     ```

6. **Testes com Pest**:
   - Escreva feature tests para verificar os controles de segurança e garantir que policies e gates se comportem corretamente sob diferentes papéis de usuário.
   - Exemplo de estrutura de teste com Pest:
     ```php
     it('allows a developer to view pulse', function () {
         $user = User::factory()->create(['is_developer' => true]);

         expect(Gate::forUser($user)->allows('viewPulse'))->toBeTrue();
     });

     it('denies a regular user from updating another user project', function () {
         $owner = User::factory()->create();
         $otherUser = User::factory()->create();
         $project = Project::factory()->create(['user_id' => $owner->id]);

         $this->actingAs($otherUser)
             ->put(route('projects.update', $project), ['name' => 'New Name'])
             ->assertForbidden();
     });
     ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill está escrito.
- NÃO faça hardcode de lógica de verificação de permissão ou papel diretamente dentro de views Blade, views Vue ou lógica de controller (ex.: `if ($user->role === 'admin')`). Encapsule toda a lógica dentro de Policies e Gates.
- NÃO exponha arrays completos e sem escopo de permissões no payload do endpoint `/api`. Mantenha o payload de autorização do frontend mínimo e com escopo.
- NÃO pule verificações de autorização no backend partindo da suposição de que o frontend esconde os elementos de UI não autorizados. O backend é a única fonte de verdade para autorização.
- NÃO permita pass-through padrão nas policies. Sempre retorne booleanos explícitos ou estados de exceção.
