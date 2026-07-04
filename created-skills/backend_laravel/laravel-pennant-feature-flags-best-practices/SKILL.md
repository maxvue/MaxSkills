---
name: laravel-pennant-feature-flags-best-practices
description: Use when implementing, configuring, reviewing, testing, or removing feature flags (feature toggles) in Laravel using Laravel Pennant. Triggers on defining features, checking feature status, activating features for specific users or teams, exposing feature flags to the Vue front-end via /api endpoints / MaxPinia stores, and writing feature-flagged unit/feature tests.
---

# Laravel Pennant Feature Flags Best Practices

## Goal
Establish solid guidelines and structured patterns for using Laravel Pennant to manage Feature Flags (feature toggles) in the Laravel/Vue backend of Engeapp. This allows for safe progressive rollouts, quick feature disabling (kill switches), and clean decoupling of experimental features from stable releases.

## Instructions

### 1. Defining Feature Flags
All features must be defined inside a Service Provider. For general features, use `App\Providers\AppServiceProvider` (or a dedicated `FeatureServiceProvider` if the codebase requires a large number of flags).
- Use **kebab-case** for naming feature flags (e.g., `gemini-integration`, `billing-v2`).
- Define the resolving logic in the `boot` method using the `Feature::define` API.

```php
use Laravel\Pennant\Feature;
use App\Models\User;

// Definindo uma feature flag com fallback seguro para usuários comuns
Feature::define('gemini-integration', function (User $user) {
    return $user->isBetaTester() || $user->hasRole('admin');
});
```

### 2. Trait Integration
Ensure that the scope class (typically the `User` model, or `Tenant` if features are scoped by tenant) includes the `HasFeatures` concern.

```php
namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Laravel\Pennant\Concerns\HasFeatures;

class User extends Authenticatable
{
    use HasFeatures; // Trait necessária para relacionar as feature flags ao modelo do usuário
}
```

### 3. Checking Feature Status in Backend
Check feature state using the `Feature` facade or direct model methods.
- **Blade Views:** Use the `@feature` directive.
- **Controllers & Services:** Use `Feature::active()` or `Feature::inactive()`.
- **Route Middleware:** Use the built-in `feature` middleware.

```php
use Laravel\Pennant\Feature;
use Illuminate\Support\Facades\Route;

// Lógica de controle condicional dentro de um controller
if (Feature::active('gemini-integration')) {
    // Executa a lógica da funcionalidade experimental
}

// Aplicação de middleware diretamente nas definições de rotas
Route::middleware('feature:gemini-integration')->group(function () {
    Route::post('/api/ai/generate', [AiController::class, 'generate']);
});
```

### 4. Expor Feature Flags ao Front (Vue via /api + MaxPinia)
O backend é a única fonte de verdade: as features ativas são computadas via `Feature` e expostas por um endpoint `/api/...` (por exemplo, incluídas em `/api/auth/me` ou em um `/api/features` dedicado). O front nunca duplica a lógica de resolução das flags — apenas consome o estado já computado.
- Resolva as flags ativas no backend (ex.: `Feature::all()` ou `Feature::active()` por flag) e retorne em JSON.
- Envie apenas as flags relevantes para a UI; use camelCase nas propriedades JS.

```php
// No controller que serve /api/features (ou dentro do payload de /api/auth/me)
use Laravel\Pennant\Feature;

public function features(Request $request): JsonResponse
{
    // Computa as features ativas para o usuário autenticado (single source of truth no backend)
    return response()->json([
        'features' => [
            'geminiIntegration' => Feature::active('gemini-integration'),
            'billingV2' => Feature::active('billing-v2'),
        ],
    ]);
}
```

No lado Vue, as flags são lidas a partir do estado da store MaxPinia (`@maxvue/max-pinia`), que é populada pela resposta do endpoint `/api/...`:
```javascript
// Lendo as feature flags do estado da store MaxPinia (populada pelo endpoint /api)
import { useFeaturesStore } from '@maxvue/max-pinia';

const featuresStore = useFeaturesStore();
const showAiWidget = featuresStore.features.geminiIntegration;
```

### 5. Testing with Feature Flags
Use Pest PHP to write tests that verify application behavior under different flag states.
- Force flags using `Feature::activateForEveryone` or scope-specific `Feature::for()->activate()`.
- Ensure tests clean up state (handled automatically by Pennant's request cycle, but good practice to assert isolation).

```php
use Laravel\Pennant\Feature;
use App\Models\User;

it('displays premium dashboard when billing-v2 feature is active', function () {
    $user = User::factory()->create();

    // Ativa a feature flag especificamente para este usuário no teste
    Feature::for($user)->activate('billing-v2');

    $this->actingAs($user)
        ->get(route('dashboard'))
        ->assertStatus(200)
        ->assertSee('Painel Premium');
});
```

---

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **NO Inline Flag Logic in Frontend:** Do not implement standalone feature activation logic in Vue; always read flags from the MaxPinia store populated by the /api endpoint.
- **NO Static Configuration Cache for Scope Resolution:** Never resolve scope features using hardcoded configuration arrays that require manual code releases to change. Use Eloquent attributes, roles, or database settings.
- **Strict pt-BR Code Comments:** All code comments inside PHP and JS code examples must be strictly written in Brazilian Portuguese (pt-BR).
- **NO Direct DB Queries for Flags:** Never query the `features` database table directly. Always use the `Feature` facade or `$user->features()` API.
