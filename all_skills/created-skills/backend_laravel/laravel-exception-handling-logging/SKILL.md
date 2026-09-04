---
name: laravel-exception-handling-logging
description: "Use when defining, refactoring, or debugging exception handling and logging in Engeapp. Covers custom Exceptions (ShouldntReport, failed() job callback), context()/render()/report(), logging channels, defensive try-catch in services."
author: Johnattas Conrady Gomes Santana
---
# Tratamento de Exceções & Logging no Laravel (engeapp)

## Objetivo
Padronizar tratamento de exceções e logging estruturado no backend Laravel 13 do engeapp, para que integrações externas e jobs de fila falhem de forma controlada, sem catches vazios nem ruído de log/auto-report.

## Instruções

### 1. Criando Exceptions Customizadas
*   **Comando Artisan**: Gere exceptions com `php artisan make:exception {ExceptionName} --no-interaction`.
*   **Dados Contextuais**: Adicione um método `context()` para capturar automaticamente o estado relevante quando a exception for reportada:
    ```php
    public function context(): array
    {
        return [
            'lead_id' => $this->leadId,
            'api_endpoint' => $this->endpoint,
        ];
    }
    ```
*   **Renderização para APIs**: Se a exception deve virar resposta HTTP, implemente `render($request)`:
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
*   **Reporting Customizado**: Só implemente `report()` na exception se precisar de lógica própria (ex.: Slack, Discord, analytics). Caso contrário, deixe o handler global do Laravel (`bootstrap/app.php`) capturar e logar.

### 2. Exceptions de Retry de Job com `ShouldntReport` (padrão do engeapp)
Este é o padrão efetivamente adotado no projeto para agentes de IA em jobs de fila. Use quando o job deve ser **retentado** pela fila, mas tentativas intermediárias **não** devem gerar auto-report/Gotify.

*   **A exception implementa `ShouldntReport`** e é mínima — sem `context()`/`render()`/`report()`. Ex.: `app/Exceptions/AgentAiIncompleteException.php`:
    ```php
    use Illuminate\Contracts\Debug\ShouldntReport;

    // Retentada pela fila normalmente, mas ignorada pelo report global (Gotify/auto-report).
    class AgentAiIncompleteException extends \RuntimeException implements ShouldntReport {}
    ```
*   **O report definitivo vai no `failed()` do Job**, não no handler global. O trait `HasAgentAiRequest` expõe `reportFinalAgentFailure()`, chamado só quando o job esgota TODAS as tentativas:
    ```php
    public function failed(?\Throwable $exception): void
    {
        Log::channel('gemini')->error('CopywriterReviewerJob: Falha após todas as tentativas', [
            'event_id' => $this->event->id,
            'error'    => $exception?->getMessage(),
        ]);

        $this->reportFinalAgentFailure($exception, $this->event);
    }
    ```
*   `reportFinalAgentFailure()` só reporta em `production`, deduplica por `file_error`/`line_error` (máx. 5) e cria um registro `Bug` com `auto_created => true` — espelhando o auto-report do handler global (`bootstrap/app.php`), que é pulado para exceptions `ShouldntReport`.

### 3. Práticas de Logging Estruturado
*   **Canais dedicados**: Use os canais já definidos em `config/logging.php` para cada integração/domínio em vez do canal padrão. Canais reais do projeto incluem: `whatsapp`, `gemini`, `ai`, `trello`, `efi`, `autentique`, `anticaptcha`, `projects`, `jobs_errors`, `jobs_faileds`.
*   **Contexto em array**: Sempre passe dados como array de contexto, nunca concatenados em string — mantém as ferramentas de análise de log limpas:
    ```php
    // Bom
    Log::channel('whatsapp')->error('Falha ao enviar template promocional', [
        'lead_id' => $lead->id,
        'phone'   => $lead->phone,
        'error'   => $exception->getMessage(),
    ]);

    // Ruim
    Log::channel('whatsapp')->error("Falha ao enviar para lead " . $lead->id . " - Erro: " . $exception->getMessage());
    ```
*   **Evite dados sensíveis**: Nunca logue tokens de autenticação, dados brutos de cartão, senhas ou credenciais de clientes.

### 4. Try-Catch Defensivo em Services
*   **Integração defensiva**: Envolva chamadas a APIs externas (clientes HTTP, SDKs) em try-catch.
*   **Sem falha silenciosa**: No catch, logue os detalhes no canal certo e relance uma exception descritiva — nunca deixe o catch vazio:
    ```php
    try {
        $response = Http::timeout(5)->post($url, $payload);
    } catch (\Throwable $e) {
        Log::channel('efi')->error('Falha de conexão com a API', [
            'url'       => $url,
            'exception' => $e->getMessage(),
        ]);
        throw new IntegrationException('Não foi possível acessar a API Efí', 0, $e);
    }
    ```

## Restrições
*   **NUNCA** use catch vazio (`catch (\Throwable $e) {}`) que esconde o erro sem logar nem reportar.
*   **NÃO** logue dados sensíveis (senhas, tokens, número completo de cartão).
*   **NÃO** use os canais padrão (`single`, `daily`) para logs de integração/domínio; use/crie um canal dedicado em `config/logging.php`.
*   **NÃO** faça auto-report/Gotify para exceptions de retry de job — marque-as com `ShouldntReport` e reporte no `failed()`.
*   **NÃO** escreva comentários inline explicando catches triviais; deixe nomes de exception e método expressarem a lógica.

## Idioma da Conversa
Comunique-se com o usuário humano sempre em português (pt-BR), independentemente do idioma em que o corpo desta skill esteja escrito. Comentários de código também em pt-BR.
