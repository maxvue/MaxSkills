---
name: laravel-exception-handling-logging
description: Use when defining, refactoring, or debugging exception handlers, custom Exceptions, logging structures, and monolog configurations in Laravel. Triggers on custom exception creation, try-catch blocks for API integrations, logging errors or warnings, and error reporting configurations.
---

# Tratamento de Exceções & Logging no Laravel

## Objetivo
Estabelecer padrões padronizados para tratamento de exceções e logging estruturado no ecossistema Laravel do Engeapp. Isso garante que APIs externas e jobs internos tratem erros de forma elegante, sem falhas silenciosas ou poluição de logs.

## Instruções

### 1. Criando Exceptions Customizadas
*   **Comando Artisan**: Gere exceptions usando `php artisan make:exception {ExceptionName} --no-interaction`.
*   **Dados Contextuais**: Adicione um método `context()` à classe da exception para capturar automaticamente o estado relevante quando a exception for reportada:
    ```php
    public function context(): array
    {
        return [
            'lead_id' => $this->leadId,
            'api_endpoint' => $this->endpoint,
        ];
    }
    ```
*   **Renderização para APIs**: Se a exception deve ser retornada via resposta de API, implemente um método `render($request)`:
    ```php
    public function render($request): \Illuminate\Http\JsonResponse
    {
        return response()->json([
            'success' => false,
            'error' => 'INTEGRATION_ERROR',
            'message' => $this->getMessage(),
        ], 422);
    }
    ```
*   **Reporting Customizado**: Só implemente `report()` se você precisar de lógica customizada (ex.: enviar para Slack, Discord ou analytics específicos). Caso contrário, deixe o exception handler global do Laravel capturar e logar.

### 2. Práticas de Logging Estruturado
*   **Canais de Integração**: Configure e use canais específicos em `config/logging.php` para integrações de terceiros (ex.: `whatsapp`, `gemini`, `autentique`). Evite logar detalhes de integração no canal padrão.
*   **Contexto de Log**: Sempre passe parâmetros como arrays de contexto em vez de concatená-los em strings. Isso mantém as ferramentas de análise de log limpas:
    ```php
    // Bom
    Log::channel('whatsapp')->error('Failed to send promotional template message', [
        'lead_id' => $lead->id,
        'phone' => $lead->phone,
        'error' => $exception->getMessage()
    ]);

    // Ruim
    Log::channel('whatsapp')->error("Failed to send template to lead " . $lead->id . " - Error: " . $exception->getMessage());
    ```
*   **Evite Dados Sensíveis**: Não faça log de tokens de autenticação, dados brutos de cartão de crédito, senhas ou credenciais de clientes.

### 3. Tratamento Elegante com Try-Catch em Services
*   **Integração Defensiva**: Sempre envolva chamadas a APIs externas (ex.: clientes HTTP, SDKs) em um bloco try-catch.
*   **Evite Falhas Silenciosas**: Ao capturar um erro, não deixe o bloco catch vazio. Faça log dos detalhes e lance uma exception customizada descritiva.
    ```php
    try {
        $response = Http::timeout(5)->post($url, $payload);
    } catch (\Throwable $e) {
        Log::channel('service_name')->error('API Connection failed', [
            'url' => $url,
            'exception' => $e->getMessage(),
        ]);
        throw new ServiceIntegrationException('Unable to reach Service API', 0, $e);
    }
    ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
*   **NUNCA** use blocos catch vazios (`catch (\Throwable $e) {}`) que escondem erros sem logar ou reportar.
*   **NÃO** faça log de dados sensíveis do usuário (senhas, tokens de autenticação, números completos de cartão).
*   **NÃO** use canais de log padrão (`single`, `daily`) para logs específicos de integrações de terceiros; sempre use/crie um canal dedicado.
*   **NÃO** escreva comentários inline explicando blocos catch básicos; deixe os nomes padronizados de exceptions e métodos expressarem a lógica.
