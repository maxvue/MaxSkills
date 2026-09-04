---
name: laravel-services-best-practices
description: "Use when creating, refactoring, or reviewing Laravel Service classes, applying Single Responsibility Principle, dependency injection, and standardized error handling. Provides end-to-end guidance, reference architectures, and practical patterns for laravel services best practices."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Services no Laravel

## Objetivo
Estabelecer diretrizes limpas, testáveis e consistentes para criar e manter classes de Service no Laravel, garantindo que os controllers permaneçam enxutos, a lógica de negócio seja centralizada e a injeção de dependência seja utilizada corretamente.

## Instruções

1. **Arquitetura e Localização dos Arquivos**:
   - Salve todas as classes de service em `app/Services/` (ex: `app/Services/TrelloService.php`).
   - Use o namespace `App\Services`.
   - Nomeie os arquivos usando o sufixo `Service` (ex: `PaymentService.php`).
   - **Este é o padrão default do projeto para lógica de domínio**: o codebase usa `app/Services` (não há camada `app/Actions`). Concentre a lógica de negócio em Services; não crie classes Action de operação única.

2. **Princípio da Responsabilidade Única (SRP)**:
   - Cada classe de Service deve focar em um único domínio ou em um conjunto de ações de negócio intimamente relacionadas.
   - Para operações altamente complexas, use services especializados (ex: `ProjectDeletionService.php`).

3. **Injeção de Dependência**:
   - Injete as dependências necessárias (repositories, outros services, clients de API) via construtor.
   - Use o constructor property promotion do PHP 8 para declarar e atribuir as dependências.
   - Nunca resolva dependências manualmente usando as funções helper `app()` ou `resolve()` dentro dos métodos se elas puderem ser injetadas.

4. **Assinaturas de Métodos e Data Transfer Objects (DTOs)**:
   - Evite passar arrays crus e não validados ou objetos de request diretamente para os métodos do Service.
   - Use Data Transfer Objects (DTOs) tipados para os parâmetros de entrada. No projeto os DTOs ficam em `app/Data/` (namespace `App\Data`, ex.: `App\Data\OrderData`).
   - Defina tipos de retorno explícitos (DTO, Model, Collection, array, etc.) para todos os métodos públicos.

5. **Tratamento de Erros e Logging**:
   - Padronize as falhas de lógica de negócio lançando Exceptions customizadas e específicas do domínio, em vez de retornar false ou strings de erro.
   - Capture exceções de nível de infraestrutura (ex: requisições HTTP, deadlocks de banco de dados) e as encapsule/relance como exceções de domínio quando apropriado.
   - Registre as falhas usando a facade `Log` com mensagens descritivas e arrays de contexto, evitando declarações genéricas.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Sem acoplamento a Controller/HTTP**: Não referencie variáveis de request HTTP (`request()`), sessions ou helpers de redirect dentro das classes de Service.
- **Sem lógica de apresentação de View**: Services não devem renderizar HTML, retornar respostas JSON nem construir componentes de UI.
- **Sem acúmulo de estado estático**: Evite declarar propriedades públicas estáticas que persistam entre requisições, para manter a compatibilidade com o Octane.

## Exemplos

### Exemplo: Implementação padrão de um Service no Laravel
```php
<?php

namespace App\Services;

use App\Data\OrderData;
use App\Models\Order;
use App\Services\Payment\GatewayService;
use App\Exceptions\PaymentFailedException;
use Illuminate\Support\Facades\Log;
use Throwable;

class OrderProcessingService
{
    // Constructor Property Promotion do PHP 8
    public function __construct(
        protected GatewayService $gateway
    ) {}

    /**
     * Processa e finaliza um pedido de cliente.
     *
     * @param Order $order
     * @param OrderData $data
     * @return Order
     * @throws PaymentFailedException
     */
    public function process(Order $order, OrderData $data): Order
    {
        try {
            // Encapsulamento da lógica de negócio
            $paymentResult = $this->gateway->charge($order, $data->paymentDetails);

            if (!$paymentResult->successful()) {
                throw new PaymentFailedException("Payment rejected: " . $paymentResult->getErrorMessage());
            }

            $order->update([
                'status' => 'paid',
                'transaction_id' => $paymentResult->getTransactionId(),
            ]);

            return $order;
        } catch (Throwable $e) {
            Log::error('Order processing failed', [
                'order_id' => $order->id,
                'error' => $e->getMessage(),
            ]);

            if ($e instanceof PaymentFailedException) {
                throw $e;
            }

            throw new PaymentFailedException('An unexpected error occurred during payment processing.', 0, $e);
        }
    }
}
```
