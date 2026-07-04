---
name: laravel-pennant-feature-flags-best-practices
description: Use when implementing, configuring, reviewing, testing, or removing feature flags (feature toggles) in Laravel using Laravel Pennant. Triggers on defining features, checking feature status, activating features for specific users or teams, exposing feature flags to the Vue front-end via /api endpoints / MaxPinia stores, and writing feature-flagged unit/feature tests.
---

# Laravel Pennant Feature Flags Best Practices

## Objetivo
Estabelecer diretrizes sólidas e padrões estruturados para usar o Laravel Pennant no gerenciamento de Feature Flags (feature toggles) no backend Laravel/Vue do Engeapp. Isso permite rollouts progressivos seguros, desabilitação rápida de features (kill switches) e um desacoplamento limpo de features experimentais em relação aos releases estáveis.

## Instruções

> **⚠️ Instale primeiro — Pennant ainda NÃO faz parte do engeapp:** `laravel/pennant` não está instalado (aparece apenas como `suggest`; não existe `config/pennant.php`). Antes de qualquer coisa:
> ```bash
> composer require laravel/pennant
> php artisan vendor:publish --provider="Laravel\Pennant\PennantServiceProvider"   # cria config/pennant.php
> php artisan migrate   # cria a tabela `features` (driver database)
> ```
> Nenhuma das APIs abaixo (`Feature::define`, `HasFeatures`, `@feature`, middleware `feature:`) existe até a instalação.

### 1. Definindo Feature Flags
Todas as features devem ser definidas dentro de um Service Provider. Para features gerais, use o `App\Providers\AppServiceProvider` (ou um `FeatureServiceProvider` dedicado, se o código exigir um grande número de flags).
- Use **kebab-case** para nomear as feature flags (ex.: `gemini-integration`, `billing-v2`).
- Defina a lógica de resolução no método `boot` usando a API `Feature::define`.

```php
use Laravel\Pennant\Feature;
use App\Models\User;

// Definindo uma feature flag com fallback seguro para usuários comuns
Feature::define('gemini-integration', function (User $user) {
    return $user->isBetaTester() || $user->hasRole('admin');
});
```

### 2. Integração da Trait
Garanta que a classe de escopo (tipicamente o model `User`, ou `Tenant` se as features tiverem escopo por tenant) inclua a concern `HasFeatures`.

```php
namespace App\Models;

use Illuminate\Foundation\Auth\User as Authenticatable;
use Laravel\Pennant\Concerns\HasFeatures;

class User extends Authenticatable
{
    use HasFeatures; // Trait necessária para relacionar as feature flags ao modelo do usuário
}
```

### 3. Verificando o Status da Feature no Backend
Verifique o estado da feature usando a facade `Feature` ou os métodos diretos do model.
- **Views Blade:** Use a diretiva `@feature`.
- **Controllers & Services:** Use `Feature::active()` ou `Feature::inactive()`.
- **Middleware de Rota:** Use o middleware `feature` embutido.

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

No lado Vue, as flags são lidas a partir de uma store MaxPinia **definida pelo próprio projeto** com `defineStore` (o pacote `@maxvue/max-pinia` NÃO exporta nenhuma store pronta de features — você cria a sua). A store faz o GET no endpoint `/api/...` e expõe o estado já computado pelo backend:
```javascript
// stores/useFeaturesStore.ts — store MaxPinia definida no projeto (não vem pronta da lib)
import { defineStore } from '@maxvue/max-pinia';

export const useFeaturesStore = defineStore('features', {
  // GET em /api/features; o backend é a única fonte de verdade das flags
  get: () => apiGetRoute('/api/features'),
  state: () => ({ features: {} as Record<string, boolean> }),
});
```
```javascript
// Consumindo a store definida acima em um componente
import { useFeaturesStore } from '@/stores/useFeaturesStore';

const featuresStore = useFeaturesStore();
const showAiWidget = featuresStore.features.geminiIntegration;
```

### 5. Testando com Feature Flags
Use Pest PHP para escrever testes que verifiquem o comportamento da aplicação sob diferentes estados de flag.
- Force as flags usando `Feature::activateForEveryone` ou `Feature::for()->activate()` específico de escopo.
- Garanta que os testes limpem o estado (tratado automaticamente pelo ciclo de request do Pennant, mas é uma boa prática afirmar o isolamento).

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

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill está escrito.
- **SEM Lógica de Flag Inline no Frontend:** Não implemente lógica standalone de ativação de feature no Vue; sempre leia as flags a partir da store MaxPinia populada pelo endpoint /api.
- **SEM Cache de Configuração Estática para Resolução de Escopo:** Nunca resolva features de escopo usando arrays de configuração hardcoded que exijam releases de código manuais para mudar. Use atributos Eloquent, papéis (roles) ou configurações no banco de dados.
- **Comentários de Código Estritamente em pt-BR:** Todos os comentários de código dentro dos exemplos PHP e JS devem ser escritos estritamente em Português Brasileiro (pt-BR).
- **SEM Queries Diretas ao Banco para Flags:** Nunca consulte a tabela `features` do banco de dados diretamente. Sempre use a facade `Feature` ou a API `$user->features()`.
