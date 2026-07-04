---
name: laravel-action-classes-best-practices
description: Use when designing, writing, reviewing, or debugging Action classes (Single Responsibility classes) in a Laravel application. Triggers on files under app/Actions, custom action classes execution, dependency injection within actions, and transactions management inside single-action workflows.
---

# Objetivo
Garantir que a lógica de negócio seja isolada em classes de Ação (Action) de Responsabilidade Única (Single Responsibility) limpas, testáveis e reutilizáveis dentro da aplicação Laravel, separando fluxos de trabalho complexos dos controllers, models e jobs.

> **Nota sobre a convenção do projeto:** o código do EngeApp/Maxdmin organiza a lógica de negócio em `app/Services` (lógica de domínio agrupada), e **não** em `app/Actions`. Prefira `laravel-services-best-practices` como padrão para este projeto. Fronteira: uma **Action** é uma única operação discreta e invocável (`execute()`); um **Service** agrupa lógica de domínio coesa entre múltiplos métodos. Só introduza `app/Actions` quando você deliberadamente precisar de uma classe autônoma de operação única e puder justificar a divergência da convenção de Services do projeto.

# Instruções
1. **Localização e Nomenclatura de Arquivos:**
   - Armazene todas as classes de ação dentro do diretório `app/Actions` (crie-o caso não exista).
   - Use PascalCase para o nome da classe e adicione o sufixo `Action` (ex.: `CreateInvoiceAction.php`, `ProcessPaymentAction.php`).
   - Coloque-as em subdiretórios se organizadas por subdomínio (ex.: `app/Actions/Billing/CreateInvoiceAction.php`).

2. **Responsabilidade Única e Ponto de Entrada:**
   - Cada ação deve representar uma única transação ou tarefa de negócio.
   - Exponha exatamente um método público chamado `execute()`.
   - Outros métodos dentro da classe devem ser helpers `private` ou `protected`.

3. **Injeção de Dependência:**
   - Injete dependências estáticas (services, classes de repositório, clientes de API, outras actions) via construtor `__construct()`.
   - Passe dados dinâmicos (models, valores escalares, DTOs) como parâmetros para o método `execute()`.

4. **Tratamento de Entrada (Sem HTTP Requests):**
   - Nunca passe um objeto HTTP Request (`Illuminate\Http\Request`) para uma action.
   - Extraia os dados nos controllers/requests e passe tipos escalares, Models Eloquent ou Data Transfer Objects (DTOs, como as classes do Spatie Data) para o `execute()`.

5. **Transações de Banco de Dados:**
   - Se a action realiza múltiplas operações de escrita (inserts, updates, deletes), envolva a lógica em uma transação de banco de dados usando `DB::transaction()` para garantir atomicidade.
   - Baseie-se em `laravel-database-eloquent-best-practices` para as interações com o banco de dados.

6. **Tratamento de Erros e Exceções:**
   - Lance exceções específicas do domínio (ex.: `PaymentFailedException`) quando regras de negócio forem violadas.
   - Deixe o chamador (Controller, Job, Command) tratar como a exceção é reportada ou exibida ao usuário.

7. **Relação com Services:**
   - Consulte `laravel-services-best-practices` para as fronteiras arquiteturais. Use *Services* para coordenar múltiplos domínios ou quando múltiplos métodos são coesos. Use *Actions* para fluxos de trabalho de negócio discretos e de ação única.

# Restrições
- NÃO defina múltiplos pontos de entrada ou métodos públicos em uma classe Action.
- NÃO acesse session, cookie ou headers da request diretamente dentro de uma Action.
- NÃO gere respostas HTML nem retorne objetos `JsonResponse` a partir de uma Action. Retorne dados brutos, Models ou DTOs.
- NÃO suprima erros com blocos `catch` vazios. Todas as exceções devem ser tratadas, logadas ou relançadas.

# Exemplos
### Definição da Classe Action
```php
<?php

namespace App\Actions\Billing;

use App\Models\User;
use App\Models\Invoice;
use App\Services\PaymentGatewayService;
use App\Data\InvoiceData;
use Illuminate\Support\Facades\DB;
use App\Exceptions\BillingException;

class CreateInvoiceAction
{
    // Injeta a dependência do serviço de gateway de pagamento
    public function __construct(
        protected PaymentGatewayService $gateway
    ) {}

    /**
     * Executa o fluxo de criação de fatura.
     *
     * @param User $user
     * @param InvoiceData $data
     * @return Invoice
     * @throws BillingException
     */
    public function execute(User $user, InvoiceData $data): Invoice
    {
        return DB::transaction(function () use ($user, $data) {
            // 1. Cobra o usuário via gateway externo
            $charge = $this->gateway->charge($user, $data->amount);

            if (!$charge->successful()) {
                throw new BillingException("Payment failed: " . $charge->errorMessage());
            }

            // 2. Cria o registro da fatura
            $invoice = $user->invoices()->create([
                'amount' => $data->amount,
                'due_at' => $data->dueAt,
                'status' => 'paid',
                'transaction_id' => $charge->transactionId(),
            ]);

            return $invoice;
        });
    }
}
```

### Chamando a Action em um Controller
```php
<?php

namespace App\Http\Controllers;

use App\Http\Requests\InvoiceStoreRequest;
use App\Actions\Billing\CreateInvoiceAction;
use Illuminate\Http\JsonResponse;

class InvoiceController extends Controller
{
    public function store(
        InvoiceStoreRequest $request,
        CreateInvoiceAction $createInvoiceAction
    ): JsonResponse {
        $user = $request->user();
        
        // Extrai o DTO a partir da request
        $invoiceData = $request->toDto();

        // Executa a action
        $invoice = $createInvoiceAction->execute($user, $invoiceData);

        return response()->json([
            'message' => 'Invoice created successfully.',
            'data' => $invoice,
        ], 201);
    }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill está escrito.
