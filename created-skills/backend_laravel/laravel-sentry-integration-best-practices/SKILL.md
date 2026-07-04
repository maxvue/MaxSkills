---
name: laravel-sentry-integration-best-practices
description: Use when integrating, configuring, or debugging Sentry in a Laravel application. Triggers on Sentry SDK installation, configuring Sentry config files, adding custom breadcrumbs, capturing exceptions with Sentry::captureException, and setting up performance APM/tracing.
---

# Objetivo
Fornecer diretrizes sólidas e padrões consistentes para rastreamento de erros em tempo real e Monitoramento de Performance de Aplicações (APM) usando o Sentry no backend Laravel da aplicação.

# Instruções

> **⚠️ O Sentry ainda NÃO faz parte do engeapp:** `sentry/sentry-laravel` não está instalado (não consta no `composer.json`, não existe `config/sentry.php`). Trate esta skill como um guia de integração **a partir do zero** — as seções seguintes (inclusive "manter `sentry/sentry-laravel` ativo nos queue workers") descrevem o estado-alvo após a instalação, e não uma integração já existente. Comece pelo `composer require` abaixo.

### 1. Instalação e Inicialização
Instale o SDK oficial do Sentry para Laravel:
```bash
composer require sentry/sentry-laravel
```

Publique o arquivo de configuração:
```bash
php artisan sentry:publish --dsn=YOUR_SENTRY_DSN
```
Este comando adiciona a variável `SENTRY_LARAVEL_DSN` ao seu arquivo `.env` e cria o arquivo `config/sentry.php`.

### 2. Integração de Exceptions no Laravel 11+
Integre o handler do Sentry na configuração do exception handler localizada em `bootstrap/app.php`:
```php
use Sentry\Laravel\Integration;

return Application::configure(basePath: dirname(__DIR__))
    // ...
    ->withExceptions(function (Exceptions $exceptions) {
        Integration::handles($exceptions);
    })->create();
```

### 3. Integração de Canal de Log
Configure o Sentry como um canal de log em `config/logging.php` para capturar logs:
```php
'channels' => [
    'stack' => [
        'driver' => 'stack',
        'channels' => explode(',', env('LOG_STACK', 'single,sentry')),
        'ignore_exceptions' => false,
    ],

    'sentry' => [
        'driver' => 'sentry',
        'level' => env('LOG_LEVEL', 'error'), // Send only errors and above to Sentry automatically
        'bubble' => true,
    ],
],
```

### 4. Configuração Específica por Ambiente (`.env`)
Configure o comportamento do Sentry dependendo do ambiente:
```env
SENTRY_LARAVEL_DSN="https://key@sentry.io/project"
SENTRY_TRACES_SAMPLE_RATE=0.1
SENTRY_PROFILES_SAMPLE_RATE=0.1
```
- Em ambientes de **produção** de alto tráfego, mantenha o `SENTRY_TRACES_SAMPLE_RATE` baixo (ex.: `0.05` a `0.1`) para evitar rate limiting e cotas excessivas.
- Em **staging/desenvolvimento**, ele pode ser definido como `1.0` (100%) para fins de depuração.

### 5. Enriquecimento de Contexto
Enriqueça as exceptions com o contexto do usuário autenticado, informações de tenant ou tags de ambiente.

#### A. Contexto Global do Usuário (Middleware / Service Provider)
Configure o rastreamento de contexto dentro de `App\Providers\AppServiceProvider` ou de um `SentryServiceProvider` customizado:
```php
use Sentry\State\Scope;
use function Sentry\configureScope;

public function boot(): void
{
    if (app()->bound('sentry')) {
        configureScope(function (Scope $scope): void {
            if (auth()->check()) {
                $scope->setUser([
                    'id' => auth()->id(),
                    'email' => auth()->user()?->email,
                    'username' => auth()->user()?->name,
                ]);
            }
            
            $scope->setTag('environment', app()->environment());
            $scope->setTag('php_version', phpversion());
        });
    }
}
```

#### B. Tags Dinâmicas e Metadados Extras
Adicione tags para agrupar e filtrar issues, e dados extras para um diagnóstico mais aprofundado:
```php
use Sentry\State\Scope;
use function Sentry\configureScope;

configureScope(function (Scope $scope) use ($tenantId, $apiVersion): void {
    $scope->setTag('tenant_id', $tenantId);
    $scope->setTag('api_version', $apiVersion);
    $scope->setExtra('payload_details', ['step' => 'execution', 'retries' => 3]);
});
```

### 6. Breadcrumbs Customizados
Registre breadcrumbs para rastrear os eventos que ocorreram imediatamente antes da exception:
```php
use Sentry\Breadcrumb;
use function Sentry\addBreadcrumb;

addBreadcrumb(new Breadcrumb(
    level: Breadcrumb::LEVEL_INFO,
    type: Breadcrumb::TYPE_DEFAULT,
    category: 'payment',
    message: 'Processing invoice payment',
    metadata: [
        'invoice_id' => $invoice->id,
        'gateway' => 'asaas',
    ]
));
```

### 7. Captura Manual de Exceptions
Use a Facade `Sentry` para capturar exceptions não-fatais em blocos `try/catch`:
```php
use Sentry\Laravel\Facade as Sentry;

try {
    $this->paymentService->charge($invoice);
} catch (PaymentException $e) {
    Sentry::captureException($e);
    // Continue application flow
}
```

### 8. Monitoramento do Horizon e de Filas
O Sentry monitora automaticamente as filas do Laravel. Garanta o seguinte:
- Mantenha `sentry/sentry-laravel` ativo nos queue workers (Octane/Horizon).
- Personalize os nomes das transações dos jobs de fila para que apareçam claramente na aba Performance.
- Nos jobs de fila, anexe o ID do payload do job ou o contexto do usuário durante a execução.

### 9. Sanitização e Dados Sensíveis (Prevenção de PII)
Evite que dados sensíveis do cliente (senhas, detalhes de cartão bancário, tokens de autenticação, etc.) vazem para o Sentry.

#### A. Configurar Sanitização Padrão
Defina `send_default_pii` como `false` em `config/sentry.php`:
```php
'send_default_pii' => false,
```

#### B. Filtro Avançado de Requisição (hook `before_send`)
Sanitize payloads ou parâmetros de query dentro de `config/sentry.php`:
```php
'before_send' => function (\Sentry\Event $event): ?\Sentry\Event {
    $request = $event->getRequest();
    
    if (isset($request['data'])) {
        $sensitiveFields = ['password', 'password_confirmation', 'credit_card', 'token', 'cvv'];
        foreach ($sensitiveFields as $field) {
            if (isset($request['data'][$field])) {
                $request['data'][$field] = '[FILTERED]';
            }
        }
        $event->setRequest($request);
    }
    
    return $event;
},
```

# Restrições
- NÃO envie PII (Informações de Identificação Pessoal) sob nenhuma circunstância. Garanta que credenciais, detalhes de cartão de crédito e tokens de autenticação sejam filtrados via `before_send` ou definindo `send_default_pii => false`.
- NÃO defina `traces_sample_rate` como `1.0` em ambientes de produção de alto tráfego. Mantenha-o entre `0.01` e `0.20` para evitar rate limiting, custos elevados e sobrecarga de performance.
- NÃO capture exceptions HTTP comuns e esperadas, como `ValidationException`, `AuthenticationException` ou `ModelNotFoundException`, que fazem parte do fluxo padrão. Configure-as na lista `dont_report` do Exception Handler ou na configuração `ignore_exceptions` do Sentry.
- NÃO bloqueie a execução para relatórios de exception. Sempre verifique se as chamadas ao Sentry não causam degradação crítica de serviço caso os servidores do Sentry estejam offline.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill esteja escrito.
