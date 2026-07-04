---
name: laravel-ai-bank-ticket-processing-best-practices
description: >-
  Use when creating, modifying, reviewing, or debugging AI-driven bank ticket (boleto) processing workflows in Laravel, orchestrating AgentBankTicketProcessor or AgentAiBilletReader, validating billet data, executing payments via Efí (Gerencianet) SDK, verifying TRT/tax eligibility, or saving payment receipts to projects.
---

# Boas Práticas de Processamento de Boletos Bancários com IA no Laravel

## Objetivo

Estabelecer diretrizes sólidas e padrões consistentes para o processamento seguro, validação, pagamento e arquivamento de boletos bancários - especificamente taxas de homologação de projetos solares e taxas de TRT (Anotação de Responsabilidade Técnica) - usando agentes de IA no backend Laravel do Engeapp.

## Instruções

### 1. Arquitetura de Processamento de Boletos

A automação de boletos é estruturada em torno de dois agentes de IA especializados e três ferramentas correspondentes:

1.  **`AgentAiBilletReader`**: Responsável por extrair código de barras, linha digitável, titular, valor e data de vencimento de arquivos PDF ou imagens (OCR). Implementa `Agent, HasStructuredOutput`.
2.  **`AgentBankTicketProcessor`**: Orquestra o fluxo de pagamento. Implementa `Agent, HasTools`.
3.  **Ferramentas (Tools)**:
    *   `CheckBankTicket`: Valida o código de barras com a API da Efí e confirma se é uma taxa de TRT ou de concessionária válida.
    *   `PayBankTicket`: Executa o pagamento usando o SDK da Efí (Gerencianet).
    *   `SaveBankTicketToProject`: Arquiva o comprovante de pagamento e vincula a transação ao projeto solar correspondente.

### 2. Fluxo de Validação & Regras de Elegibilidade (`CheckBankTicket`)

Antes de executar qualquer transação financeira, o agente DEVE executar a lógica de validação para verificar a elegibilidade:

1.  **Validação de Tipo**: Apenas boletos classificados como TRT (Anotação de Responsabilidade Técnica) ou taxas de aprovação de concessionária de energia são elegíveis para pagamento automatizado. Boletos comerciais gerais (ex: compras de fornecedores, contas de utilidade não relacionadas a concessionárias) DEVEM ser rejeitados.
2.  **Detecção de Duplicatas**: Consulte o banco de dados para garantir que a `line_code` (linha digitável) ou o `bar_code` (código de barras) ainda não foi processado ou pago.
3.  **Limites de Valor**: Defina limites máximos de valor rígidos para pagamentos automatizados (ex: R$ 5.000,00). Qualquer boleto que exceda esse limite deve sinalizar uma solicitação de intervenção humana.

### 3. Orquestração Segura de Pagamento (`PayBankTicket`)

Ao utilizar o SDK da Efí (Gerencianet) (`Efi\EfiPay`) para executar pagamentos:

1.  **Sequenciamento Rígido**: A ferramenta de pagamento `PayBankTicket` NÃO DEVE ser invocada a menos que uma chamada anterior a `CheckBankTicket` tenha retornado explicitamente um status `'success'` e confirmado `'is_trt' => true` (ou elegível).
2.  **Concorrência / Condições de Corrida**: Locks de banco de dados (ex: `sharedLock` ou `lockForUpdate`) devem ser aplicados ao registro do boleto durante a transação de pagamento para evitar despachos duplicados.
3.  **Idempotência**: Passe uma chave de idempotência de pagamento única (derivada do `bar_code` ou do ID do boleto) ao gateway de pagamento para garantir que múltiplas requisições à API não disparem múltiplos pagamentos.
4.  **Tratamento de Erros**:
    *   Capture `EfiException` separadamente para tratar erros de validação de nível de API ou de saldo.
    *   Sempre registre falhas de pagamento com o contexto completo (excluindo detalhes sensíveis como credenciais em texto puro) no canal `emergency` ou `finance`.

### 4. Arquivamento de Comprovante & Vínculo com Projeto (`SaveBankTicketToProject`)

Uma vez que um pagamento é executado com sucesso:

1.  **Integração com Spatie Media Library**: O PDF do comprovante de pagamento (obtido da URL de comprovante do gateway) deve ser baixado e anexado ao model `Project` correspondente (`App\Models\Project\Project`) usando a `MediaLibrary` da Spatie.
2.  **Coleção de Documentos**: Salve-o em uma coleção específica (ex: `'homologation_receipts'` ou `'trt_receipts'`) com propriedades customizadas estruturadas contendo o `transaction_id`, `value` e `payment_date`.
3.  **Atualização do Status do Projeto**: Atualize o status da fase de homologação do projeto com base no boleto pago (ex: marcando a TRT como "Paga").

### 5. Fallback & Intervenção Humana

O fluxo de IA deve transferir o controle para operadores humanos de forma graciosa nos seguintes cenários:
*   Divergências de valor ou data de vencimento entre os dados extraídos e o resultado da verificação da API.
*   A API retorna fundos insuficientes ou erros de autenticação.
*   O boleto não é elegível para pagamento automático (ex: não é uma taxa de TRT ou de concessionária).
*   Qualquer exceção de sistema lançada durante a execução.

Nesses casos, uma notificação no banco de dados ou um alerta no Slack deve ser gerado com detalhes do bloqueio e um link direto para o projeto para upload/revisão manual.

### 6. Boas Práticas de Testes com Pest

Para testar o processamento de boletos com segurança sem realizar transações financeiras reais:

1.  **Mockando o SDK**: Sempre use `Http::fake()` ou mocke a resposta do cliente `EfiPay`.
2.  **Verificação de Estado**: Escreva testes usando o Pest para afirmar que:
    *   Apenas boletos elegíveis transitam para um estado de pago.
    *   Pagamentos duplicados lançam um erro de validação.
    *   Pagamentos que falharam disparam eventos de notificação humana.

```php
it('rejects payments for non-eligible tickets', function () {
    $agent = new AgentBankTicketProcessor();
    // Simula a ferramenta CheckBankTicket retornando is_trt = false
    // Afirma que PayBankTicket nunca é chamada.
});
```

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
1.  **NUNCA** execute `PayBankTicket` sem primeiro invocar `CheckBankTicket` no código de barras do mesmo boleto.
2.  **NUNCA** deixe as credenciais do SDK da Efí fixas no código; sempre obtenha-as via `config('bank.efi_options')` / o helper `efiOptions()` (a fonte real de credenciais neste app), e não `config('services.efi')`.
3.  **NUNCA** processe um pagamento sem um `project_id` verificado correspondente a um projeto ativo no banco de dados.
4.  **NUNCA** registre em log dados brutos de cartão de crédito, chaves de API ou certificados privados.
5.  **NUNCA** pule as queries de verificação de duplicatas antes de executar um pagamento.
