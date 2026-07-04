---
name: laravel-finance-coupons-discounts-best-practices
description: Use when creating, modifying, applying, or validating discount coupons (cupons de desconto), referral usage rules, or financial discounts (descontos financeiros) in Laravel. Triggers on coupon validation logic, payment discount adjustments, coupon-project associations, and discount expiration checks.
---

# Boas Práticas de Cupons e Descontos Financeiros no Laravel

## Objetivo
Estabelecer diretrizes sólidas e padrões consistentes para criar, validar, aplicar e auditar cupons de desconto e descontos financeiros no backend Laravel do Engeapp, prevenindo condições de corrida, erros de arredondamento e resgates ilegítimos.

## Instruções

### 1. Lógica de Validação de Cupom
Sempre use o método estático `FinanceDiscountCoupons::getCouponByCode($code, $project_id)` para resolver e validar um código de cupom. Ao implementar ou revisar a lógica de validação, garanta que:
- **Status Ativo:** O cupom deve estar ativo (`active = true`).
- **Expiração:** Verifique se o horário atual é posterior à data de expiração (`expiration`).
- **Limite Global de Uso:** A contagem total de usos (`count_use` via `uses()->count()`) não deve exceder a quantidade total permitida do cupom (`amount`).
- **Limite por Empresa/Integrador:** Verifique se a contagem de usos da empresa solar excede o limite máximo permitido por integrador (`limit_use`).
- **Restrições de Público:** Se `reference_use` estiver definido, verifique se ele corresponde ao ID da empresa solar ou ao ID do cliente.

### 2. Aplicação Segura & Concorrência (Condições de Corrida)
Quando um cupom é aplicado durante o checkout, condições de corrida podem permitir que um cupom seja usado além de seus limites se múltiplas requisições ocorrerem simultaneamente.
- **Transações de Banco de Dados:** Sempre envolva a criação do pagamento, a validação do cupom e o registro de uso do cupom dentro de uma transação de banco de dados:
  ```php
  use Illuminate\Support\Facades\DB;

  DB::transaction(function () use ($code, $projectId, $paymentData) {
      // 1. Busca o cupom com lock for update para evitar alterações concorrentes
      $coupon = FinanceDiscountCoupons::where('code', $code)
          ->lockForUpdate()
          ->first();

      // 2. Realiza as validações...
      
      // 3. Cria o pagamento e registra o uso do cupom
  });
  ```
- **Pessimistic Locking:** Use `.lockForUpdate()` ao consultar o cupom para bloquear checkouts concorrentes de lerem contagens de uso obsoletas.

### 3. Cálculos de Desconto com Precisão (BRL)
Para prevenir diferenças de arredondamento de centavos ao aplicar valores de desconto (fixos ou percentuais):
- **Evite Float:** Não use cálculos com float puro para operações financeiras.
- **Verificação de Tipo:** Distinga claramente entre descontos percentuais (`type_discount === 'percent'`) e descontos de valor fixo (`type_discount === 'value'`).
- **Precisão de Cálculo:** Calcule com funções BCMath (`bcmul`/`bcadd`/`bcsub`/`bcdiv` com `scale` explícito de 2) em vez de aritmética de float, tratando os valores como strings antes de armazená-los nos campos de pagamento:
  ```php
  // Trabalhe com strings e scale = 2 para evitar imprecisões de ponto flutuante
  if ($coupon->type_discount === 'percent') {
      // desconto = total * (percentual / 100)
      $discountValue = bcdiv(bcmul((string) $totalAmount, (string) $coupon->value, 2), '100', 2);
      $totalAmount = bcsub((string) $totalAmount, $discountValue, 2);
  } elseif ($coupon->type_discount === 'value') {
      $totalAmount = bcsub((string) $totalAmount, (string) $coupon->value, 2);
  }
  ```

### 4. Auditoria e Registro de Uso
Toda vez que um cupom for aplicado com sucesso, registre o histórico na tabela `finance_discounts_coupon_use`:
- Mapeie as relações explicitamente: `payment_id`, `coupon_id`, `project_id`, `client_id`, `solar_company_id` e `coupon_code`.
- Não confie apenas na hidratação automática por eventos se isso puder ser feito de forma limpa durante a criação.

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **SEM Escritas de Banco em Eventos de Leitura:** NUNCA invoque `$model->save()` ou operações de escrita no banco dentro de eventos de model do Eloquent que disparam em leitura (como hooks de leitura `retrieved` ou `booted`). Fazer isso cria queries recursivas, problemas massivos de performance e locks de escrita em queries `select` simples.
- **Atribuições de Atributos:** NUNCA confunda atribuições de relacionamento (ex: atribuir IDs de cliente ou de empresa a `project_id` por engano). Verifique as atribuições com cuidado:
  ```php
  // RUIM: Sobrescrevendo project_id em vez de definir client_id
  $model->project_id = $model->payment->project->client_id;

  // BOM: Atribuindo às propriedades corretas
  $model->client_id = $model->payment->project->client_id;
  $model->solar_company_id = $model->payment->project->client->solar_company_id;
  ```
- **Comparação de Float:** Nunca realize comparações diretas de igualdade em floats ao validar saldos remanescentes.
