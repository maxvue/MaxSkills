---
name: laravel-user-impersonation-best-practices
description: Use when implementing, configuring, reviewing, or securing user impersonation features using lab404/laravel-impersonate. Triggers on login-as actions, impersonation session validation, audit logging for impersonation events, and Vue SPA status helpers via /api endpoints / MaxPinia store.
---

# Goal
Provide solid, secure, and audited guidelines for implementing user impersonation (login-as) using the `lab404/laravel-impersonate` package within the Engeapp/Laravel ecosystem, ensuring compliance with security standards, detailed auditing (LGPD), and frontend communication.

# Instructions

### 1. Model Guards Configuration
Always implement the following authorization methods in the `User` model to guarantee strict role enforcement and prevent privilege escalation:
* **`canImpersonate(): bool`**: Returns true only if the user has the database privilege (e.g., `$this->can_impersonate` column set to true or a developer flag).
* **`canBeImpersonated(): bool`**: Returns false for high-privilege users (such as developers, system administrators, or specific super-users) when checked by a normal user. Also, verify that the impersonated user is not the same as the impersonator.

```php
/**
 * Checks if the current user can impersonate others.
 */
public function canImpersonate(): bool
{
    return (bool) $this->can_impersonate || (bool) $this->is_developer;
}

/**
 * Checks if the current user can be impersonated.
 */
public function canBeImpersonated(): bool
{
    // Do not allow impersonating developers or super administrators
    if ($this->is_developer || $this->is_admin) {
        return false;
    }

    return $this->status === 'active';
}
```

### 2. Audit Logging & Event Handling (LGPD Compliance)
User impersonation bypasses standard login credentials. Thus, every session simulation must be thoroughly audited. 
Create event listeners for the package events and log them into a secure file or database log:
* **`Lab404\Impersonate\Events\TakeImpersonation`**: Dispatched when impersonation starts.
* **`Lab404\Impersonate\Events\LeaveImpersonation`**: Dispatched when impersonation ends.

Log the following structure using `Log::info()` or a dedicated `security` log channel:
* Impersonator ID & Email
* Impersonated ID & Email
* IP Address & User-Agent
* Timestamp

Example Listener:
```php
namespace App\Listeners;

use Lab404\Impersonate\Events\TakeImpersonation;
use Illuminate\Support\Facades\Log;

class LogImpersonationStart
{
    public function handle(TakeImpersonation $event): void
    {
        Log::channel('security')->info('User impersonation started', [
            'impersonator_id'   => $event->impersonator->id,
            'impersonator_mail' => $event->impersonator->email,
            'impersonated_id'   => $event->impersonated->id,
            'impersonated_mail' => $event->impersonated->email,
            'ip_address'        => request()->ip(),
            'user_agent'        => request()->userAgent(),
        ]);
    }
}
```

Register these listeners in your `EventServiceProvider` or `AppServiceProvider`.

### 3. Controller Actions & Route Security
Always secure impersonation controllers and check guards explicitly:
* Group impersonation routes behind `auth` and `verified` middlewares.
* Check `$impersonator->canImpersonate()` and `$impersonated->canBeImpersonated()` inside the action logic, throwing a `403` HTTP exception if unauthorized.

```php
public function startImpersonation(Request $request): JsonResponse
{
    $admin = Auth::user();
    
    if (!$admin || !$admin->canImpersonate()) {
        abort(403, 'Unauthorized action.');
    }

    $targetUser = User::findOrFail($request->input('user_id'));

    if (!$targetUser->canBeImpersonated()) {
        abort(403, 'Target user cannot be impersonated.');
    }

    $admin->impersonate($targetUser);

    return response()->json(['success' => true]);
}
```

### 4. Share Impersonation State with Frontend (Vue SPA via /api + MaxPinia)
To prevent admin confusion and session hijacks, the frontend must clearly display that the session is simulated. Since this is a Laravel API + Vue Router SPA, the impersonation state is exposed through an `/api/...` endpoint and consumed by a MaxPinia (`@maxvue/max-pinia`) store, never through server-side template shared data.

* Expose `is_impersonating` and the impersonator's data in your auth payload endpoint (e.g. include it in `/api/auth/me`). Always derive this server-side from the validated impersonation session, never from a client-supplied flag:

```php
// GET /api/auth/me controller
public function me(Request $request): JsonResponse
{
    $user = $request->user();

    return response()->json([
        'user' => $user,
        // Security: read straight from the lab404 impersonation session,
        // so the flag can only be true when a real session exists.
        'is_impersonating' => $user?->isImpersonated() ?? false,
        'impersonator' => $user?->isImpersonated()
            ? [
                'id'   => $user->getImpersonatorId(),
                'name' => 'Administrator', // Or fetch from the original user model
              ]
            : null,
    ]);
}
```

* In the Vue SPA, the MaxPinia auth store loads `/api/auth/me` and exposes `is_impersonating` + `impersonator` as reactive state.
* Render a global sticky banner whenever the store's `is_impersonating` is `true`, showing the original administrator.
* The banner provides a "voltar ao usuário original" (return to original user) button that calls the route ending the impersonation (`Route::post('user/impersonate/end')`) and then refreshes the store state.

### 5. Testing Best Practices
Write robust Pest feature tests to validate authorization restrictions:
* Verify an unauthorized user receives `403` on impersonation start.
* Verify an administrator can start impersonation and that the current authenticated user changes to the target user.
* Verify leaving impersonation restores the session to the original administrator.

```php
test('unauthorized users cannot impersonate others', function () {
    $user = User::factory()->create(['can_impersonate' => false]);
    $target = User::factory()->create();

    $this->actingAs($user)
        ->postJson(route('user.impersonate.start'), ['user_id' => $target->id])
        ->assertStatus(403);
});

test('administrator can impersonate and then leave impersonation', function () {
    $admin = User::factory()->create(['can_impersonate' => true]);
    $target = User::factory()->create();

    // Start impersonating
    $this->actingAs($admin)
        ->postJson(route('user.impersonate.start'), ['user_id' => $target->id])
        ->assertOk();

    expect(auth()->user()->id)->toBe($target->id);

    // Leave impersonation
    $this->postJson(route('user.impersonate.end'))
        ->assertOk();

    expect(auth()->user()->id)->toBe($admin->id);
});
```

# Constraints
* **No Nested Impersonations**: Never allow an impersonator to impersonate another user recursively.
* **No Persistent Session Storage in Cookies**: Do not store the administrator's password/hash in plain text inside localstorage/cookies. Rely purely on Laravel session drivers.
* **Strict Model Guards**: Never bypass model-level rules (`canImpersonate`/`canBeImpersonated`) even if the controller has custom verification.
* **Follow PHPDoc Location Rule**: Do not write model-specific PHPDoc inline inside models; keep them in separate IDE Helper files.
