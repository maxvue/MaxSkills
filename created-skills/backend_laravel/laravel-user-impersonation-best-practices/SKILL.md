---
name: laravel-user-impersonation-best-practices
description: Use when implementing, configuring, reviewing, or securing user impersonation features using lab404/laravel-impersonate. Triggers on login-as actions, impersonation session validation, audit logging for impersonation events, and Vue SPA status helpers via /api endpoints / MaxPinia store.
---

# Objetivo
Fornecer diretrizes sólidas, seguras e auditadas para implementar a impersonação de usuário (login-as) usando o pacote `lab404/laravel-impersonate` dentro do ecossistema Engeapp/Laravel, garantindo conformidade com padrões de segurança, auditoria detalhada (LGPD) e comunicação com o frontend.

# Instruções

### 1. Configuração dos Guards no Model
Sempre implemente os seguintes métodos de autorização no model `User` para garantir a aplicação estrita de papéis e prevenir escalonamento de privilégios:
* **`canImpersonate(): bool`**: Retorna true somente se o usuário tiver o privilégio no banco de dados (ex: coluna `$this->can_impersonate` definida como true ou uma flag de developer).
* **`canBeImpersonated(): bool`**: Retorna false para usuários de alto privilégio (como developers, administradores de sistema ou super-usuários específicos) quando verificado por um usuário normal. Além disso, verifique se o usuário impersonado não é o mesmo que o impersonador.

```php
/**
 * Verifica se o usuário atual pode impersonar outros.
 */
public function canImpersonate(): bool
{
    return (bool) $this->can_impersonate || (bool) $this->is_developer;
}

/**
 * Verifica se o usuário atual pode ser impersonado.
 */
public function canBeImpersonated(): bool
{
    // Não permite impersonar developers ou super administradores
    if ($this->is_developer || $this->is_admin) {
        return false;
    }

    return $this->status === 'active';
}
```

### 2. Log de Auditoria e Tratamento de Eventos (Conformidade com a LGPD)
A impersonação de usuário contorna as credenciais de login padrão. Portanto, cada simulação de sessão deve ser minuciosamente auditada.
Crie event listeners para os eventos do pacote e registre-os em um arquivo seguro ou em um log de banco de dados:
* **`Lab404\Impersonate\Events\TakeImpersonation`**: Disparado quando a impersonação começa.
* **`Lab404\Impersonate\Events\LeaveImpersonation`**: Disparado quando a impersonação termina.

Registre a seguinte estrutura usando `Log::info()` ou um canal de log `security` dedicado:
* ID e Email do Impersonador
* ID e Email do Impersonado
* Endereço IP e User-Agent
* Timestamp

Exemplo de Listener:
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

Registre esses listeners no seu `EventServiceProvider` ou `AppServiceProvider`.

### 3. Actions de Controller e Segurança de Rotas
Sempre proteja os controllers de impersonação e verifique os guards explicitamente:
* Agrupe as rotas de impersonação atrás dos middlewares `auth` e `verified`.
* Verifique `$impersonator->canImpersonate()` e `$impersonated->canBeImpersonated()` dentro da lógica da action, lançando uma exceção HTTP `403` se não autorizado.

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

### 4. Compartilhar o Estado de Impersonação com o Frontend (Vue SPA via /api + MaxPinia)
Para evitar confusão do admin e sequestros de sessão, o frontend deve exibir claramente que a sessão é simulada. Como isto é uma API Laravel + SPA Vue Router, o estado de impersonação é exposto através de um endpoint `/api/...` e consumido por uma store MaxPinia (`@maxvue/max-pinia`), nunca através de dados compartilhados de template no lado do servidor.

* Exponha `is_impersonating` e os dados do impersonador no endpoint de payload de auth (ex: inclua no `/api/auth/me`). Sempre derive isso no lado do servidor a partir da sessão de impersonação validada, nunca de uma flag fornecida pelo cliente:

```php
// controller GET /api/auth/me
public function me(Request $request): JsonResponse
{
    $user = $request->user();

    return response()->json([
        'user' => $user,
        // Segurança: lê diretamente da sessão de impersonação do lab404,
        // para que a flag só possa ser true quando existe uma sessão real.
        'is_impersonating' => $user?->isImpersonated() ?? false,
        'impersonator' => $user?->isImpersonated()
            ? [
                'id'   => $user->getImpersonatorId(),
                'name' => 'Administrator', // Ou buscar no model do usuário original
              ]
            : null,
    ]);
}
```

* Na SPA Vue, a store de auth do MaxPinia carrega `/api/auth/me` e expõe `is_impersonating` + `impersonator` como estado reativo.
* Renderize um banner global fixo (sticky) sempre que o `is_impersonating` da store for `true`, exibindo o administrador original.
* O banner fornece um botão "voltar ao usuário original" que chama a rota que encerra a impersonação (`Route::post('user/impersonate/end')`) e então atualiza o estado da store.

### 5. Boas Práticas de Teste
Escreva testes de feature robustos com o Pest para validar as restrições de autorização:
* Verifique que um usuário não autorizado recebe `403` ao iniciar a impersonação.
* Verifique que um administrador consegue iniciar a impersonação e que o usuário autenticado atual muda para o usuário alvo.
* Verifique que sair da impersonação restaura a sessão para o administrador original.

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

    // Inicia a impersonação
    $this->actingAs($admin)
        ->postJson(route('user.impersonate.start'), ['user_id' => $target->id])
        ->assertOk();

    expect(auth()->user()->id)->toBe($target->id);

    // Sai da impersonação
    $this->postJson(route('user.impersonate.end'))
        ->assertOk();

    expect(auth()->user()->id)->toBe($admin->id);
});
```

# Restrições
* **Sem Impersonações Aninhadas**: Nunca permita que um impersonador impersone outro usuário recursivamente.
* **Sem Armazenamento Persistente de Sessão em Cookies**: Não armazene a senha/hash do administrador em texto puro dentro de localstorage/cookies. Confie exclusivamente nos session drivers do Laravel.
* **Guards de Model Estritos**: Nunca contorne as regras de nível de model (`canImpersonate`/`canBeImpersonated`) mesmo que o controller tenha verificação customizada.
* **Siga a Regra de Localização do PHPDoc**: Não escreva PHPDoc específico do model inline dentro dos models; mantenha-os em arquivos separados de IDE Helper.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
