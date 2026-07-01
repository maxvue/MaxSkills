---
name: laravel-authorization-policies-gates
description: Use when creating, modifying, or reviewing Laravel authorization logic, including Policies, Gates, role-based access control, route protection, and exposing user permissions to the Vue SPA front-end via /api endpoints consumed by MaxPinia stores. Triggers on gate definitions, policy classes, authorize calls, and 'can' middleware.
---

# Laravel Authorization Policies and Gates

## Goal
Establish guidelines, conventions, and standards for implementing authorization logic (policies and gates) in Laravel, protecting routes and controller actions, and exposing user permissions to the Vue SPA front-end via /api endpoints consumed by MaxPinia stores in the Engeapp ecosystem.

## Instructions

1. **Eloquent Policies**:
   - Create policies for all primary Eloquent models. Place them in the `app/Policies/` directory and name them following the `{ModelName}Policy` pattern.
   - Use Laravel's policy auto-discovery where possible by keeping the standard namespace structure.
   - Implement standard resource methods (`viewAny`, `view`, `create`, `update`, `delete`) and strictly type-hint both the `User` and the target model.
   - Example Policy structure:
     ```php
     <?php

     namespace App\Policies;

     use App\Models\User;
     use App\Models\Project;

     class ProjectPolicy
     {
         /**
          * Determine whether the user can view the project.
          */
         public function view(User $user, Project $project): bool
         {
             return $user->id === $project->user_id || $user->is_developer;
         }

         /**
          * Determine whether the user can update the project.
          */
         public function update(User $user, Project $project): bool
         {
             return $user->id === $project->user_id;
         }
     }
     ```

2. **Global Gates**:
   - Use Gates for action authorization that doesn't map directly to an Eloquent model (e.g., system admin dashboards, access to developer tools).
   - Register Gates in the `boot` method of the `AppServiceProvider.php` (or a dedicated `AuthServiceProvider.php` if complex).
   - Example Gate definition:
     ```php
     use Illuminate\Support\Facades\Gate;

     Gate::define('viewPulse', function (User $user) {
         return $user->is_developer || in_array($user->email, ['gd@homelifesolar.com.br']);
     });
     ```

3. **Protecting Routes**:
   - Secure routes using the `can` middleware, referencing the policy ability and passing the route parameter name.
   - Example web/API routing:
     ```php
     Route::put('/projects/{project}', [ProjectController::class, 'update'])
         ->middleware('can:update,project');
     ```

4. **Controller-Level Authorization**:
   - Ensure authorization is explicitly called within controllers before executing operations if route middleware is insufficient.
   - Use controller helper methods or the `Gate` facade directly:
     ```php
     public function update(Request $request, Project $project)
     {
         $this->authorize('update', $project);

         // Alternatively: Gate::authorize('update', $project);

         $project->update($request->validated());
     }
     ```

5. **Vue Integration (via /api + MaxPinia store)**:
   - Expose authorization permissions to the Vue SPA front-end through a dedicated `/api/...` endpoint (e.g., included in the `/api/auth/me` or `/api/user` payload), consumed by a MaxPinia store.
   - The backend computes a scoped permission map for the authenticated user and returns it from a controller. Avoid returning the entire database of permissions; scope permissions dynamically to what the user requires.
   - Example controller returning the permission map:
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
   - In the Vue SPA, consume this endpoint via a MaxPinia store (`@maxvue/max-pinia`) and read permissions from the store state (not from page props). Use Ziggy `route()` helpers for Laravel route resolution.
     ```vue
     <script setup lang="ts">
     import { useAuthStore } from '@/stores/auth' // @maxvue/max-pinia store

     const auth = useAuthStore() // store loads /api/auth/me into its state
     </script>

     <template>
       <button v-if="auth.can.createProject" @click="openModal">
         Novo Projeto
       </button>
     </template>
     ```

6. **Pest Testing**:
   - Write feature tests to verify security controls and ensure policies and gates behave correctly under different user roles.
   - Example testing structure with Pest:
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

## Constraints
- Do NOT hardcode permission or role checking logic directly inside Blade views, Vue views, or controller logic (e.g., `if ($user->role === 'admin')`). Encapsulate all logic inside Policies and Gates.
- Do NOT expose full, un-scoped permissions arrays in the `/api` endpoint payload. Keep the frontend authorization payload minimal and scoped.
- Do NOT skip authorization checks in the backend under the assumption that the frontend hides unauthorized UI elements. The backend is the single source of truth for authorization.
- Do NOT allow default pass-through on policies. Always return explicit booleans or exception states.
