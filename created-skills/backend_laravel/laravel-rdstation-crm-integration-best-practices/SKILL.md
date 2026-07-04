---
name: laravel-rdstation-crm-integration-best-practices
description: Use when creating, reviewing, or debugging integrations with the RD Station CRM API, handling OAuth2 authentication flow (access/refresh tokens), sending solar project lead data, or managing webhook responses (won deals) within the Engeapp Laravel backend. Triggers on CRM sync jobs, OAuth token storage, and webhook controllers.
---

# Laravel RD Station CRM Integration Best Practices

## Objetivo
Estabelecer diretrizes sólidas, padrões e standards arquiteturais para criar, manter e depurar uma integração resiliente, segura e performática entre o backend Laravel do Engeapp e a API do RD Station CRM (incluindo webhooks).

## Instruções

### 1. Design da Classe de Integração (Extensão de `BaseApi`)
- Estenda a classe `App\Http\Integrations\BaseApi` para chamar APIs externas.
- Crie um namespace dedicado: `App\Http\Integrations\RdStation`.
- Estruture a pasta de integração com:
  - `RdStationCrmApi.php` (A classe de integração principal que estende `BaseApi`).
  - `Attributes.json` (Mapeamento dos campos obrigatórios).
  - `EndPoints.json` (Mapeamento de endpoints, métodos HTTP e regras).
- Resolva dinamicamente a base URL ativa dentro de `defineComputedBaseUrl()` para os ambientes de sandbox/produção.

### 2. Fluxo de Autenticação OAuth2 Resiliente
- Mantenha uma tabela no banco de dados (ex.: `rd_station_oauth_tokens`) para armazenar os tokens OAuth2 dinamicamente: `access_token`, `refresh_token` e `expires_at`.
- Sobrescreva o método `getAccessToken()` na sua classe `RdStationCrmApi` para:
  1. Recuperar os dados do token ativo a partir do banco de dados.
  2. Se o token estiver expirado ou próximo de expirar (ex.: dentro de 5 minutos), obter um novo token usando o fluxo de `refresh_token`.
  3. Atualizar e persistir as novas credenciais de token de volta ao banco de dados de forma segura.
  4. Cachear o `access_token` ativo usando a camada de cache do Laravel com um TTL adequado.

### 3. Sincronização Assíncrona via Horizon & Filas
- Nunca execute chamadas à API do CRM de forma síncrona durante requisições HTTP. Sempre despache jobs para a fila.
- Implemente a interface `ShouldQueue` em todos os jobs de sincronização (ex.: `SyncLeadToRdStationJob`).
- Trate o Rate Limiting (HTTP 429) de forma graciosa:
  - Capture `RequestException` ou falhas de resposta HTTP.
  - Implemente lógica de retry com backoff exponencial:
    ```php
    public int $tries = 5;

    public function backoff(): array
    {
        return [10, 30, 90, 270, 810];
    }
    ```
- Execute as operações de sincronização dentro de transações de banco de dados seguras ao atualizar o status do lead/projeto localmente.

### 4. Processamento Idempotente de Webhooks
- Roteie as requisições de webhook recebidas (ex.: oportunidade ganha) para um `RdStationWebhookController` dedicado.
- Valide o payload recebido usando um Form Request customizado (`RdStationWebhookRequest`).
- Garanta segurança transacional e idempotência usando transações de banco de dados e constraints únicas:
  - Verifique se o projeto/negócio já foi processado ou criado localmente (usando o ID da oportunidade do RD Station CRM) antes de criar novos registros no banco de dados.
  - Envolva a conversão do lead, a criação do cliente e o início do projeto/homologação dentro de:
    ```php
    DB::transaction(function () use ($data) {
        // ... Verifica se já existe ...
        // ... Cria o Cliente ...
        // ... Cria o Projeto & a Homologação ...
    });
    ```

### 5. Mocking e Testes (Pest PHP)
- Escreva testes unitários e de feature usando Pest PHP.
- Não faça requisições reais à API durante os testes. Mocke as respostas da API do RD Station CRM usando `Http::fake()`:
  ```php
  Http::fake([
      'api.rd.services/*' => Http::response(['status' => 'success'], 200),
  ]);
  ```
- Use factories para configurar os estados dos models (ex.: `Lead` ou `Project`) antes de testar os jobs de sincronização.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o próprio conteúdo/corpo desta skill está escrito.
- **SEM Hardcoding Estático:** Nunca faça hardcode de credenciais, URLs ou chaves de cliente. Sempre as recupere de arquivos `config()`, que referenciam variáveis do `.env`.
- **SEM Chamadas Síncronas de API:** Não faça chamadas de API diretamente de controllers ou models; delegue todas as chamadas de rede da integração a queue workers.
- **SEM Retries Cegos:** Nunca tente requisições infinitamente sem backoff exponencial, caso contrário os headers de rate limit serão esgotados e pode ocorrer bloqueio de IP.
