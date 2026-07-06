---
name: laravel-ai-bank-ticket-processing-best-practices
description: >-
  Use ao criar, modificar, revisar ou depurar o fluxo de IA de pagamento de boletos (TRT/homologação) no Laravel do engeapp, orquestrando AgentBankTicketProcessor (localiza projeto via GetProjectByClientName/GetProjectByDocument, valida com CheckBankTicket, paga com PayBankTicket, arquiva com SaveBankTicketToProject) ou o AgentAiBilletReader (OCR), usando o SDK Efí e credenciais via efiOptions().
---

# Boas Práticas de Processamento de Boletos Bancários com IA no Laravel

## Objetivo

Estabelecer diretrizes para o processamento, validação, pagamento e arquivamento de boletos bancários — especificamente taxas de homologação de projetos solares e taxas de TRT (Anotação de Responsabilidade Técnica) — usando agentes de IA no backend Laravel do engeapp.

> **Estado atual do código (importante):** as ferramentas de negócio (`CheckBankTicket`, `PayBankTicket`, `SaveBankTicketToProject`) hoje são **mocks/stubs**: instanciam `EfiPay(efiOptions())` mas retornam dados fixos (as chamadas reais `payDetailBarCode`/`payRequestBarCode` estão comentadas, o `transaction_id` vem de `uniqid()`, e o arquivamento tem apenas um `TODO`). As seções abaixo marcadas como **[A implementar]** são recomendações para quando o fluxo real for construído, não o comportamento vigente. Ao trabalhar nessas ferramentas, respeite as regras aqui antes de ligar a API de verdade.

## Instruções

### 1. Arquitetura de Processamento de Boletos

A automação é estruturada em torno de dois agentes de IA e **cinco** ferramentas registradas em `AgentBankTicketProcessor::tools()`:

1.  **`AgentAiBilletReader`** (`app/Ai/Agents/AgentAiBilletReader.php`): extrai código de barras, linha digitável, titular, valor e vencimento de PDFs/imagens (OCR). Implementa `Agent, HasStructuredOutput`.
2.  **`AgentBankTicketProcessor`** (`app/Ai/Agents/AgentBankTicketProcessor.php`): orquestra o fluxo. Implementa `Agent, HasTools`. Provider Gemini (`gemini-2.5-flash`), `Temperature(0.2)`, `MaxSteps(50)`, `Timeout(240)`.
3.  **Ferramentas (Tools)** em `app/Ai/Tools/`:
    *   `GetProjectByClientName`: busca projetos pelo nome/razão social do cliente (`LIKE` em `client.name`/`fantasy_name`).
    *   `GetProjectByDocument`: busca projetos pelo documento (CPF/CNPJ) do cliente; limpa a máscara com `preg_replace` antes do `LIKE`.
    *   `CheckBankTicket`: consulta a linha digitável na API da Efí e indica se é um boleto TRT válido para pagamento.
    *   `PayBankTicket`: executa o pagamento pelo SDK da Efí (Gerencianet).
    *   `SaveBankTicketToProject`: arquiva o comprovante/registro do boleto no projeto (`App\Models\Project\Project`).

### 2. Fluxo de Trabalho do Agente (ordem obrigatória)

As `instructions()` do `AgentBankTicketProcessor` definem o fluxo — respeite esta ordem ao alterar o agente:

1.  **Localizar o projeto do cliente PRIMEIRO** usando `GetProjectByClientName` ou `GetProjectByDocument`. Esta é uma etapa/ferramenta obrigatória: sem um `project_id` resolvido não há como arquivar o comprovante. Não pule esse passo.
2.  **Validar** o boleto com `CheckBankTicket`. Se a resposta não for TRT/elegível, interrompa o fluxo e avise o usuário — não tente pagar.
3.  **Pagar** com `PayBankTicket` somente após o `CheckBankTicket` confirmar elegibilidade.
4.  **Arquivar** com `SaveBankTicketToProject`, referenciando o `project_id` correto obtido no passo 1.

### 3. Validação & Regras de Elegibilidade (`CheckBankTicket`)

O contrato atual: `schema` recebe `linha_digitavel`; o retorno é um JSON com `status`, `is_trt`, `data` (valor, vencimento, linha digitável) e `message`.

Regras a garantir quando a lógica real for implementada **[A implementar]**:

1.  **Validação de Tipo**: apenas boletos TRT ou taxas de aprovação de concessionária são elegíveis para pagamento automatizado. Boletos comerciais gerais DEVEM ser rejeitados. Hoje o mock sempre devolve `is_trt => true` — não confie nisso ao ligar a API.
2.  **Detecção de Duplicatas [A implementar]**: antes de pagar, consultar o banco para garantir que a linha digitável/código de barras ainda não foi processado. Essa verificação **ainda não existe** no código.
3.  **Limites de Valor [A implementar]**: definir teto para pagamento automatizado; acima dele, sinalizar intervenção humana.

### 4. Orquestração de Pagamento (`PayBankTicket`)

O contrato atual: `schema` recebe `linha_digitavel` e `valor`; instancia `new EfiPay(efiOptions())`, mas a chamada `payRequestBarCode` está comentada e o retorno é um mock com `transaction_id` de `uniqid()` e uma `comprovante_url` fictícia.

Ao implementar o pagamento real com `Efi\EfiPay`:

1.  **Sequenciamento Rígido**: `PayBankTicket` não deve ser invocado sem que `CheckBankTicket` do mesmo boleto tenha confirmado elegibilidade (`is_trt`/`success`).
2.  **Concorrência [A implementar]**: aplicar locks (`sharedLock`/`lockForUpdate`) ao registro do boleto durante o pagamento para evitar despacho duplicado. Não implementado hoje.
3.  **Idempotência [A implementar]**: passar uma chave de idempotência derivada do código de barras/ID do boleto ao gateway. Não implementado hoje.
4.  **Tratamento de Erros**: o código já captura `EfiException` e `\Exception` separadamente, retornando JSON de erro. Ao registrar falhas em log, use um canal **existente** — `efi` (dedicado à integração Efí) ou `emergency`. **Não** existe canal `finance` em `config/logging.php`. Nunca registre credenciais/certificados em texto puro.

### 5. Arquivamento de Comprovante (`SaveBankTicketToProject`)

Contrato atual: `schema` recebe `project_id` (int), `transaction_id` (string) e `comprovante_url` (nullable). A ferramenta faz `Project::find($projectId)`, retorna erro se não achar, e **hoje é um stub** — há apenas um `TODO: Implementar a lógica real para anexar o documento`; nenhuma mídia é gravada.

Ao implementar o arquivamento real **[A implementar]**:

1.  **Spatie MediaLibrary**: o model `App\Models\Project\Project` implementa `HasMedia`/`InteractsWithMedia` com `registerMediaCollections`, então baixar o PDF do comprovante e anexá-lo via MediaLibrary é o caminho aplicável.
2.  **Coleção de Documentos**: salvar em uma coleção específica, confirmando os nomes reais das collections registradas no model antes de usar (não presuma nomes).
3.  **Propriedades customizadas**: guardar `transaction_id`, `value` e `payment_date` nas custom properties da mídia.
4.  **Status do Projeto**: atualizar a fase de homologação/TRT do projeto conforme o boleto pago.

### 6. Fallback & Intervenção Humana

O fluxo deve transferir o controle para operadores humanos quando:
*   houver divergência de valor/vencimento entre dados extraídos e o resultado da verificação;
*   a API retornar fundos insuficientes ou erro de autenticação;
*   o boleto não for elegível (não-TRT/concessionária);
*   qualquer exceção de sistema for lançada.

Nesses casos, gerar uma notificação (banco de dados ou alerta) com o motivo do bloqueio e um link para o projeto para revisão manual.

### 7. Testes com Pest

Para testar sem transações financeiras reais:

1.  **Mockar o SDK**: use `Http::fake()` ou mocke a resposta do `EfiPay` (lembrando que as tools já retornam mocks hoje).
2.  **Verificação de Estado**: afirme que apenas boletos elegíveis chegam ao estado pago, que duplicatas são barradas (quando essa checagem existir) e que falhas disparam a notificação humana.

```php
it('rejects payments for non-eligible tickets', function () {
    $agent = new AgentBankTicketProcessor();
    // Simula CheckBankTicket retornando is_trt = false
    // Afirma que PayBankTicket nunca é chamada.
});
```

## Restrições

- **Idioma:** sempre se comunique com o usuário humano em Português (pt-BR), independentemente do idioma do corpo desta skill. Comentários de código em pt-BR.
1.  **NUNCA** execute `PayBankTicket` sem antes invocar `CheckBankTicket` no mesmo boleto e confirmar elegibilidade.
2.  **NUNCA** deixe credenciais da Efí fixas no código; obtenha-as via `efiOptions()` / `config('bank.efi_options')` (a fonte real neste app), **não** `config('services.efi')`.
3.  **NUNCA** salve um comprovante sem antes resolver o `project_id` via `GetProjectByClientName`/`GetProjectByDocument`.
4.  **NUNCA** registre em log dados brutos de cartão, chaves de API ou certificados privados; use os canais reais `efi` ou `emergency`.
5.  **AO IMPLEMENTAR** o pagamento real, não pule a verificação de duplicatas nem os locks/idempotência — hoje inexistentes, mas exigidos antes de tocar dinheiro de verdade.
