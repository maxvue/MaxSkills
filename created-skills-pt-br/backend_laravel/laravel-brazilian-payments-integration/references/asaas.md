# Integração de Pagamentos Asaas com Laravel

> **Status:** o Asaas **está configurado e em uso** no engeapp — `config/services.php` define `asaas.api_key` (env `ASAAS_KEY`) e `asaas.base_url` (env `ASAAS_BASE_URL`, default `https://api-sandbox.asaas.com`) —, porém **apenas para recarga de celular**: `App\Services\CellChargeService` chama `/v3/mobilePhoneRecharges` via facade `Http`, consumido por `CellChargeCommand` e coberto por testes. **Cobranças, clientes, Pix/Boleto e webhook do Asaas não existem hoje** — não há controller, rota, Job nem DTO em `app/Data/Asaas`. O que descreve essa parte abaixo é **aspiracional**.

## Objetivo
Estabelecer padrões claros, seguros e resilientes para estender a integração Asaas no backend do Engeapp: seguir o padrão que a integração existente já adota, usar DTOs (Spatie Laravel Data) para tipar payloads, aplicar segurança de webhook e registrar operações transacionais para auditoria.

## Estrutura

O padrão real do Asaas no projeto é um **Service em `app/Services/` usando o facade `Http`** — veja `App\Services\CellChargeService`. Ao adicionar cobranças/clientes, siga esse mesmo padrão em vez de introduzir um conector `BaseApi`:

```php
Http::baseUrl((string) config('services.asaas.base_url'))
    ->acceptJson()
    ->timeout(15)
    ->withHeaders(['access_token' => $apiKey]);
```

Se, ainda assim, houver motivo para um conector dedicado em `app/Http/Integrations/Asaas/` (padrão descrito pela skill **`laravel-api-integration-patterns`**), a convenção de nomes do projeto é nomear o arquivo pelo gateway (`Asaas.php`), com `Attributes.json` (regras de validação: `name`, `cpfCnpj`, `billingType`, `value`, `dueDate`, `customer`) e `EndPoints.json` (Customers, Payments, Subscriptions). Note que `BaseApi` não é regra universal — só as integrações de WhatsApp o estendem, e o conector da Efí não.

### Particularidades da API Asaas

- **Base URL:** o host é `https://api.asaas.com` (produção) ou `https://api-sandbox.asaas.com` (sandbox, default de `ASAAS_BASE_URL`). O `/v3` é **prefixo de path** das chamadas (ex.: `/v3/customers`, `/v3/payments`), não parte do host base.
- **Autenticação:** o Asaas usa o header `access_token` (não `Bearer`), com o valor resolvido de `config('services.asaas.api_key')` — a convenção de chaves deste gateway em `config/services.php` é `api_key`/`base_url`; não existe chave `token`. Se optar por um conector `BaseApi`, será preciso sobrescrever o ponto de injeção de header (que emite `Bearer`) preservando o comportamento de cache (`withCache`/`withoutCache`/`clearCache`) — veja `laravel-api-integration-patterns` para a assinatura exata.

## Segurança de webhooks

O webhook do Asaas notifica atualizações em tempo real (pagamento recebido, cobrança vencida etc.). Ao implementá-lo:

- **Autenticação:** confira o header `asaas-access-token` contra um segredo de webhook vindo da config. Essa chave **ainda não existe** — `config/services.php` só traz `asaas.api_key` e `asaas.base_url`; crie-a a partir de uma env seguindo a convenção do gateway (ex.: `services.asaas.webhook_token`). Se não conferir, aborte com `401`.
- **DTOs:** mapeie o payload do webhook com classes Spatie Data para consistência estrutural.
- **Processamento assíncrono:** o controller deve apenas persistir/enfileirar o payload (na tabela `bank_webhooks`, status `pending`) e responder `200 OK` imediatamente; atualizações pesadas e notificações vão para um Job em background (ex.: um futuro `ProcessAsaasWebhookJob`), seguindo o mesmo padrão de `ProcessEfiWebhookJob`.

## Restrições
- **NÃO** ignore a verificação do token de webhook: são endpoints públicos e vulneráveis a payloads maliciosos.
- **NÃO** execute operações longas de forma síncrona no handler do webhook (renderização de PDF, múltiplas chamadas externas). Enfileire Jobs para evitar timeouts.
- **NÃO** armazene dados de cartão de crédito localmente. Envie requisições PCI-compliant diretamente ao Asaas e guarde apenas dados mascarados ou tokens de transação retornados.
- **NÃO** deixe credenciais hardcoded; resolva-as via `config/services.php` a partir de variáveis de ambiente.
- **NÃO** use comentários inline ou PHPDoc em inglês no código PHP. Todos os comentários e documentação PHP devem estar estritamente em pt-BR.
