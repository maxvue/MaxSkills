---
name: laravel-context-metadata-tracking-best-practices
description: Use when implementing, refactoring, or debugging Laravel Context (Illuminate\Support\Facades\Context) to track request metadata, share state between HTTP requests and queued Jobs, configure context logging, or sanitize context keys in a stateless environment. Triggers on Context::add(), Context::get(), Context::pull(), log context configuration, and sharing request metadata.
---

# Boas Práticas de Rastreamento de Metadados com Laravel Context

## Objetivo
Estabelecer diretrizes sólidas, padrões e boas práticas para implementar, depurar e gerenciar metadados de contexto de request/job usando a Facade nativa Context do Laravel (`Illuminate\Support\Facades\Context`) dentro do ecossistema Engeapp.

## Instruções

### 1. Inicialização do Contexto da Requisição via Middleware
Sempre capture metadados específicos da requisição em um middleware global ou específico de rota.
- **Trace ID:** Procure por um header `X-Trace-Id` ou `X-Request-Id` de entrada. Se estiver ausente, gere um novo UUID.
- **Informações de Autenticação:** Armazene o ID e a role do usuário autenticado, mas garanta que estejam sanitizados e não vazem dados sensíveis.
- **IP & User Agent:** Armazene metadados que ajudem a correlacionar logs.

Exemplo de Middleware:
```php
namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Context;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;

class CaptureRequestMetadata
{
    public function handle(Request $request, Closure $next): Response
    {
        Context::add([
            'trace_id' => $request->header('X-Trace-Id') ?? (string) Str::uuid(),
            'user_id' => $request->user()?->id,
            'ip_address' => $request->ip(),
        ]);

        $response = $next($request);

        // Opcional: incluir o trace_id nos headers da resposta
        $response->headers->set('X-Trace-Id', Context::get('trace_id'));

        return $response;
    }
}
```

### 2. Compartilhando o Contexto com Queued Jobs
O Laravel propaga automaticamente os dados do `Context` para jobs enfileirados.
- Confie na propagação nativa do Context para jobs de fila.
- Evite passar manualmente trace IDs como parâmetros do job se eles já estiverem armazenados no Context.
- Ao escrever listeners de fila, use `Context::get('trace_id')` para rastrear o processamento assíncrono.

### 3. Integração & Configuração de Logs
Configure o formatador de log do Laravel para exibir os metadados de contexto automaticamente.
- Defina um formatador Monolog customizado ou use a configuração de logging padrão do Laravel para anexar o contexto.
- Mantenha as chaves planas e descritivas para facilitar a consulta de logs em ferramentas como Elasticsearch, AWS CloudWatch ou visualizadores de log locais.

### 4. Gerenciamento de Memória & Compatibilidade com Laravel Octane
Como o Engeapp roda sobre Laravel Octane, a persistência de estado entre requisições deve ser tratada com cuidado.
- O Laravel limpa automaticamente o estado da facade `Context` após cada requisição ao rodar sobre Octane.
- No entanto, se você armazenar estado em propriedades estáticas customizadas ou singletons, precisará resetá-los manualmente usando listeners de eventos do Octane (`tick` ou request terminators) ou evitá-los por completo em favor do `Context`.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- **SEM Dados Sensíveis:** Nunca armazene senhas, API keys, números completos de cartão de crédito ou informações de identificação pessoal (PII) diretamente no Context.
- **SEM Objetos Grandes:** Não armazene instâncias pesadas de models Eloquent ou arrays massivos no Context. Armazene IDs (ex.: `user_id`, `project_id`) no lugar.
- **Evite Sobrescrever:** Garanta que bibliotecas de terceiros ou pacotes internos não sobrescrevam chaves do sistema como `trace_id`, usando prefixação estruturada (ex.: `engeapp:trace_id`) se houver possibilidade de colisão de namespace.
- **Mantenha-o Stateless:** Não use o Context como substituto da HTTP Session ou do Cache. Ele dura apenas pelo ciclo de vida de uma única execução de requisição/processo.
