---
name: laravel-user-impersonation-best-practices
description: "Use when implementing, reviewing, or debugging user impersonation in Engeapp with lab404/laravel-impersonate. Covers impersonate routes, user permissions, and Pinia store integration."
---
## Objetivo
Diretrizes seguras para a impersonação de usuário (login-as) no engeapp usando o pacote `lab404/laravel-impersonate`, fiéis à implementação real: verificação por coluna no banco, rotas nomeadas (Ziggy) e estado exposto ao frontend Vue por rota dedicada consumida via `apiGetRoute`.

# Contexto real do projeto (verdade-base)
- Model `app/Models/User.php` usa o trait `Lab404\Impersonate\Models\Impersonate`. O projeto NÃO sobrescreve `canImpersonate()`/`canBeImpersonated()` — herda os defaults `true` do trait. O controle de acesso é feito pela coluna booleana `can_impersonate` (cast `boolean`), verificada no controller.
- Colunas booleanas relevantes do model: `can_impersonate`, `is_developer`, `is_validated`, `is_technical_manager`. Não existe `is_admin` (a coluna `status` existe — enum `['active','blocked','inactive']` — mas não tem relação com autorização de impersonação; não a use para esse fim).
- Controller: `app/Http/Controllers/User/UserExecuteController.php`.
- Rotas: `routes/web/Web.User.Route.php`.
- Store frontend: `resources/Stores/UserStores/useUser.Store.ts`.
- Banner/UI: `resources/Vue/Layouts/PageLayout/TopMenu/UserSection.vue`.

## Instruções

### 1. Rotas nomeadas (Ziggy)
Use os nomes de rota existentes; não crie endpoints string paralelos.
```php
// routes/web/Web.User.Route.php
Route::post('user/impersonate/start', [UserExecuteController::class, 'makeImpersonate'])->name('user.impersonate.start');
Route::post('user/impersonate/end',   [UserExecuteController::class, 'leaveImpersonation'])->name('user.impersonate.end');
Route::get('user/impersonate/status', [UserExecuteController::class, 'statusImpersonation'])->name('user.impersonate.status');
```
As três ficam dentro do grupo autenticado já existente no arquivo. Mantenha esse contrato: o frontend depende desses nomes.

### 2. Controller — padrão do projeto
O engeapp verifica a permissão pela COLUNA `can_impersonate` diretamente no controller (não usa `abort(403)` nem os métodos de guard do model). Respostas são `response()->json(bool)`. Ao mexer nesse fluxo, siga o mesmo padrão:
```php
// app/Http/Controllers/User/UserExecuteController.php

/**
 * Inicia a impersonação: loga temporariamente como outro usuário.
 */
public function makeImpersonate(Request $request): JsonResponse
{
    $admin = Auth::user();
    if (! $admin) {
        return response()->json(false);
    }

    // Permissão vem da coluna booleana can_impersonate (não de canImpersonate()).
    if ($admin?->can_impersonate) {
        $user = User::findOrFail($request->input('user_id') ?? $request->input('id'));

        // Bloqueia auto-impersonação.
        if ($user->id !== $admin->id) {
            $admin->impersonate($user);

            return response()->json(true);
        }
    }

    return response()->json(false);
}

/**
 * Encerra a impersonação e retorna ao admin original.
 */
public function leaveImpersonation(): JsonResponse
{
    $user = Auth::user();
    $user?->leaveImpersonation();

    return response()->json(true);
}

/**
 * Retorna se a sessão atual está impersonada (bool).
 */
public function statusImpersonation(): JsonResponse
{
    return response()->json(Auth::user()?->isImpersonated());
}
```
Notas fiéis à implementação:
- `makeImpersonate` aceita tanto `user_id` quanto `id` no corpo.
- A permissão é a coluna `can_impersonate`; `is_developer` NÃO participa dessa checagem.
- Nunca retorne dados sensíveis no `status` — apenas o booleano de `isImpersonated()`.

### 3. Frontend — estado via rota dedicada + `apiGetRoute` (Vue SPA + MaxPinia)
NÃO há endpoint `/api/auth/me` expondo `is_impersonating`. O estado é obtido por uma rota nomeada dedicada, consumida na store `useUser` via `apiGetRoute` (Ziggy resolve o nome pontilhado). Mantenha esse caminho.

Na store `resources/Stores/UserStores/useUser.Store.ts`, o flag é um `computedAsync` que só consulta a API quando já há usuário carregado e o GET da store teve sucesso:
```ts
// resources/Stores/UserStores/useUser.Store.ts
const isImpersonated = computedAsync(
    async () => {
        const status_server = getStatus();
        // Só busca o status quando o usuário já está carregado (contrato MaxPinia: status.server.get.is_success, via getStatus()).
        if (data?.value?.id && status_server?.get?.is_success)
            return await apiGetRoute('user.impersonate.status');

        return false;
    },
    false /* estado inicial */
);
// ...
return { data, options, waitRequest, departments_id, isImpersonated, isCached };
```

O início da impersonação (`user.impersonate.start`) tem dois pontos de entrada reais no frontend:
- **Padrão canônico:** `apiPostRoute('user.impersonate.start', { id })`, como em `resources/Vue/Sections/SolarCompany/SectionExpansionSolarCompanyDataTable.vue:70` (`startImpersonate(item.id)`). O payload usa a chave `id` — é por isso que o controller aceita `user_id ?? id`.
- **Desvio legado (não replicar):** `resources/Stores/Setting/useAdminCompanyUsers.Store.ts:73` usa `axios.post(route('user.impersonate.start'), { user_id: userId })` cru, com `route()` em vez de `apiPostRoute`. É um desvio existente a ser migrado para o padrão canônico, não um segundo padrão válido.

No layout, mostre o banner/botão de retorno quando `isImpersonated` for verdadeiro e chame a rota de fim via `apiPostRoute`:
```vue
<!-- resources/Vue/Layouts/PageLayout/TopMenu/UserSection.vue -->
<div v-if="system.user?.isImpersonated" class="impersonated-btn" @click.stop="endImpersonate">
    <!-- rótulo "SAIR / (RETORNAR)" -->
</div>
```
```ts
const endImpersonate = async () => {
    const result_api = await apiPostRoute('user.impersonate.end');
    if (result_api) window.location.href = '/dashboard';
};
```
Regras:
- Rotas por NOME pontilhado (`user.impersonate.status`, `user.impersonate.end`) via `apiGetRoute`/`apiPostRoute` — nunca strings `/api/...`.
- Após encerrar, o projeto força um reload navegando para `/dashboard`, garantindo estado limpo da sessão.
- Todo GET de status passa pela store (contrato MaxPinia); componentes não fazem fetch direto.

### 4. Auditoria de eventos (LGPD) — recomendação, ainda não implementada
O pacote dispara `Lab404\Impersonate\Events\TakeImpersonation` (início) e `Lab404\Impersonate\Events\LeaveImpersonation` (fim). O engeapp ainda NÃO registra listeners para eles. Recomenda-se adicionar auditoria, pois a impersonação contorna o login padrão:
```php
namespace App\Listeners;

use Lab404\Impersonate\Events\TakeImpersonation;
use Illuminate\Support\Facades\Log;

class LogImpersonationStart
{
    public function handle(TakeImpersonation $event): void
    {
        // $event->impersonator e $event->impersonated são instâncias de User.
        Log::channel('security')->info('Impersonação iniciada', [
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
Registre um listener análogo para `LeaveImpersonation` e configure um canal de log `security` dedicado.

### 5. Testes (Pest)
Cubra as restrições reais de autorização. Como o controller responde `json(bool)` (não 403), os testes verificam o corpo/booleano e a troca de identidade:
```php
test('usuário sem can_impersonate não consegue impersonar', function () {
    $user   = User::factory()->create(['can_impersonate' => false]);
    $target = User::factory()->create();

    $this->actingAs($user)
        ->postJson(route('user.impersonate.start'), ['user_id' => $target->id])
        ->assertOk()
        ->assertContent('false'); // controller retorna json(false), não 403
});

test('admin impersona e depois retorna ao usuário original', function () {
    $admin  = User::factory()->create(['can_impersonate' => true]);
    $target = User::factory()->create();

    $this->actingAs($admin)
        ->postJson(route('user.impersonate.start'), ['user_id' => $target->id])
        ->assertOk()
        ->assertContent('true');

    expect(auth()->user()->id)->toBe($target->id);

    $this->postJson(route('user.impersonate.end'))->assertOk();

    expect(auth()->user()->id)->toBe($admin->id);
});

test('admin não pode impersonar a si mesmo', function () {
    $admin = User::factory()->create(['can_impersonate' => true]);

    $this->actingAs($admin)
        ->postJson(route('user.impersonate.start'), ['user_id' => $admin->id])
        ->assertOk()
        ->assertContent('false');
});
```

## Restrições
- **Fonte de permissão única:** autorize por `can_impersonate` no controller; não invente `is_admin` (não existe no model) nem use `status` para esse fim (existe, mas é um enum de estado de conta, não uma flag de autorização).
- **Sem impersonação aninhada (recomendado, NÃO implementado hoje):** o controller atual não verifica se a sessão já está impersonada — `makeImpersonate` só checa `can_impersonate` e auto-impersonação. Se for adicionar o bloqueio, teste `Auth::user()?->isImpersonated()` antes de chamar `impersonate()`.
- **Sem segredos no cliente:** confie nos session drivers do Laravel; nunca guarde hash/credencial do admin em localStorage/cookies.
- **Status enxuto:** `statusImpersonation` retorna apenas o booleano; não vaze dados do impersonador.
- **Comentários em pt-BR** no código.
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), independentemente do idioma do conteúdo desta skill.
