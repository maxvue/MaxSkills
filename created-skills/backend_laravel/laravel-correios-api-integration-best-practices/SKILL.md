---
name: laravel-correios-api-integration-best-practices
description: Use when creating, refactoring, reviewing, or debugging integrations with the official Correios API. Triggers on authentication token management, caching strategies for postal codes (CEP), parcel tracking, shipping rate calculations, and handling Correios network timeouts or authentication failures.
---

# Boas Práticas de Integração com a API dos Correios no Laravel

## Objetivo
Estabelecer diretrizes sólidas e consistentes para integrar, consumir e depurar a API oficial dos Correios no backend Laravel do ecossistema Engeapp. Isso garante renovação dinâmica e resiliente de token de autenticação, cache seguro de códigos postais (CEPs), tratamento robusto de exceções e compatibilidade com ambientes de execução stateless como o Laravel Octane.

## Instruções

### 1. Gerenciamento Dinâmico de Token & Compatibilidade com Octane
*   **Não Persista Tokens no Estado da Instância**: Evite armazenar o token ativo dentro de propriedades do serviço sem verificações de validação. Em ambientes stateless (Laravel Octane), serviços registrados como singletons persistem entre requisições. Armazenar um token diretamente em uma propriedade pode causar falhas de autenticação se o token expirar na API enquanto permanece no estado em memória.
*   **Resolução Baseada em Cache**: Sempre resolva o token dinamicamente a partir do cache. Garanta que o TTL do cache esteja alinhado com a validade do token dos Correios (geralmente 24 horas).
*   **Fluxo de Auto-Renovação**: Quando o token estiver ausente ou expirado, busque um novo, armazene-o no cache e retorne-o. Se a requisição do token falhar, lance uma exceção customizada e limpe quaisquer valores parciais do cache.

### 2. Estratégias de Cache para Códigos Postais (CEP)
*   **Evite Requisições Redundantes**: Armazene os detalhes de endereço obtidos por CEP no cache por 24 horas (`now()->addHours(24)`) ou mais, dependendo dos requisitos de negócio.
*   **Faça Cache Apenas de Dados Decodificados**: Armazene a representação em array bruto do endereço no cache. 
*   **Previna Erros de Método em Runtime**: Nunca invoque o método `json()` diretamente sobre dados recuperados do cache. Uma vez em cache, o valor é retornado como um array simples. Garanta que você verifique a estrutura antes de extrair valores.

### 3. Tratamento Gracioso de Exceções e Logging
*   **Timeout & Retries do Cliente HTTP**: Sempre imponha um timeout (ex: 5 segundos) e considere usar retries para instabilidades temporárias de rede:
    ```php
    Http::timeout(5)->retry(3, 100)
    ```
*   **Logging Estruturado**: Registre todas as falhas de conexão e de API em um canal de log dedicado (ex: `Log::channel('correios')`) usando um array de contexto. Nunca concatene valores sensíveis ou dinâmicos na string da mensagem de log.
*   **Exceções Customizadas**: Evite falhas silenciosas ou o retorno de valores vazios genéricos. Lance uma exceção específica do domínio (ex: `CorreiosIntegrationException`) quando a API estiver inacessível, as credenciais forem inválidas ou as respostas estiverem malformadas.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
*   **NUNCA** silencie exceções HTTP ou falhas de conexão retornando `null` sem registrar o erro com contexto completo.
*   **NÃO** invoque métodos de resposta HTTP (como `json()`) sobre arrays lidos do cache.
*   **NÃO** armazene o token de autenticação em propriedades estáticas de classe ou propriedades de instância sem um mecanismo para renová-lo quando ele expirar no cache.
*   **NÃO** acople os serviços de integração dos Correios diretamente a variáveis de requisição HTTP (`request()`) ou à lógica de geração de views.

## Exemplos

### Implementação Resiliente do CorreiosService

```php
<?php

namespace App\Services;

use App\Exceptions\CorreiosIntegrationException;
use Illuminate\Http\Client\Response;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Throwable;

class CorreiosService
{
    protected string $baseUrl;
    protected string $user;
    protected string $code;

    public function __construct()
    {
        $this->baseUrl = config('api.correios.base_url');
        $this->user = config('api.correios.user');
        $this->code = config('api.correios.code');
    }

    /**
     * Resolve o token de autenticação dinamicamente, aproveitando o cache.
     *
     * @return string
     * @throws CorreiosIntegrationException
     */
    public function getToken(): string
    {
        $token = Cache::get('correios_api_token');

        if (!$token) {
            $token = $this->fetchNewToken();
            // Faz cache do token por 24 horas
            Cache::put('correios_api_token', $token, now()->addHours(24));
        }

        return $token;
    }

    /**
     * Busca um novo token de autenticação da API dos Correios.
     *
     * @return string
     * @throws CorreiosIntegrationException
     */
    protected function fetchNewToken(): string
    {
        $url = $this->baseUrl . '/token/v1/autentica';

        try {
            $response = Http::timeout(5)
                ->withBasicAuth($this->user, $this->code)
                ->post($url);

            if ($response->failed()) {
                Log::channel('correios')->error('Correios authentication failed', [
                    'status' => $response->status(),
                    'body' => $response->body(),
                ]);

                throw new CorreiosIntegrationException('Failed to authenticate with Correios API.');
            }

            $token = $response->json('token');

            if (!$token) {
                throw new CorreiosIntegrationException('Correios authentication response did not contain a token.');
            }

            return $token;
        } catch (Throwable $e) {
            if ($e instanceof CorreiosIntegrationException) {
                throw $e;
            }

            Log::channel('correios')->error('Unexpected error during Correios authentication', [
                'exception' => $e->getMessage(),
            ]);

            throw new CorreiosIntegrationException('Unexpected authentication error.', 0, $e);
        }
    }

    /**
     * Consulta os detalhes de endereço por CEP.
     *
     * @param string $cep
     * @return array
     * @throws CorreiosIntegrationException
     */
    public function getCep(string $cep): array
    {
        // Supondo que os helpers 'cepIsNotValid' e 'cepOnlyNumber' estejam disponíveis
        if (cepIsNotValid($cep)) {
            return [];
        }

        $cep = cepOnlyNumber($cep);
        $cacheKey = 'correios_api_ceps_' . $cep;

        return Cache::remember($cacheKey, now()->addHours(24), function () use ($cep) {
            $url = $this->baseUrl . '/cep/v1/enderecos/' . $cep;

            try {
                $token = $this->getToken();
                $response = Http::timeout(5)
                    ->withToken($token)
                    ->get($url);

                if ($response->status() === 404) {
                    return [];
                }

                if ($response->failed()) {
                    Log::channel('correios')->error('Correios CEP query failed', [
                        'cep' => $cep,
                        'status' => $response->status(),
                        'body' => $response->body(),
                    ]);

                    throw new CorreiosIntegrationException("Failed to query CEP {$cep} from Correios.");
                }

                return $response->json() ?? [];
            } catch (Throwable $e) {
                if ($e instanceof CorreiosIntegrationException) {
                    throw $e;
                }

                Log::channel('correios')->error('Unexpected error during Correios CEP query', [
                    'cep' => $cep,
                    'exception' => $e->getMessage(),
                ]);

                throw new CorreiosIntegrationException("Unexpected error querying CEP {$cep}.", 0, $e);
            }
        });
    }
}
```
