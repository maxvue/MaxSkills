---
name: laravel-brazilian-payments-integration
description: "Use when integrating, configuring, or debugging Brazilian payment gateways in Engeapp. Covers Efí SDK (EfiPay, efiOptions, ProcessEfiWebhookJob), Asaas HTTP service for mobile recharges (CellChargeService), Banco Inter webhook placeholders, and webhook idempotency patterns."
author: Johnattas Conrady Gomes Santana
---
# Integração de Pagamentos Brasileiros com Laravel

## Objetivo
Padronizar e proteger a integração de gateways de pagamento brasileiros (Efí/Gerencianet, Asaas, Banco Inter, Mercado Pago) dentro do ecossistema de backend do Engeapp: escolher o padrão de conector correto entre os que o projeto realmente usa, tipar payloads com Spatie Laravel Data (DTOs), status baseados em Enums, validação segura de assinatura/token de webhooks e logging dedicado.

## Instruções

### 1. Padrões de conector e inicialização de SDK
Não existe um padrão único de integração no engeapp — existem **três**, e o correto é seguir o que o gateway em questão já usa:

1. **SDK oficial** — Efí: `new EfiPay(efiOptions())` ou `new EfiPay(config('bank.efi_options'))` em `app/Services/Bank/` (`EfiPaymentStatus.php`, `EfiPaymentStatusChecker.php`), Jobs e controllers.
2. **Conector manual em `app/Http/Integrations/{Gateway}/`** — Efí: `App\Http\Integrations\Efi\Efi`, que **não** estende `BaseApi`; usa `use EndPointsTrait;` e `Http::withOptions(['cert' => $this->certificate_path])->withToken(...)` diretamente.
3. **Service em `app/Services/` com o facade `Http`** — Asaas: `App\Services\CellChargeService` usa `Http::baseUrl(config('services.asaas.base_url'))->acceptJson()->timeout(15)->withHeaders(['access_token' => $apiKey])`.

`BaseApi` é o padrão para conectores genéricos, mas **não é regra universal para pagamentos**: no app inteiro só duas classes o estendem, ambas de WhatsApp (`Whapi`, `Whatsapp`). Ao estender um gateway existente, siga o padrão que ele já adota em vez de migrá-lo para `BaseApi`.

> **Status das integrações no engeapp (aplica-se a todas as seções abaixo):** **Efí** está plenamente integrado. **Asaas** está configurado e em uso em produção (`config/services.php` traz `asaas.api_key` e `asaas.base_url`), porém **apenas para recarga de celular** (`App\Services\CellChargeService`, endpoints `/v3/mobilePhoneRecharges`, consumido por `CellChargeCommand` e coberto por testes) — **não existe** uso de Asaas para clientes/cobranças/Pix/Boleto, nem rota ou controller de webhook Asaas, nem DTOs em `app/Data/Asaas`; essa parte é aspiracional. **Banco Inter** é parcialmente configurado (SDK e credenciais existem, mas a implementação ainda é um placeholder). **Mercado Pago** é aspiracional — não há SDK/pacote nem `config('services.mercadopago.*')` no projeto.

- **Arquivos de um conector em `app/Http/Integrations/{Gateway}/`**:
  - `{Gateway}.php` (ex.: `Efi.php`, `Whapi.php`, `Whatsapp.php`): o conector de integração em PHP, nomeado pelo gateway.
  - `Attributes.json`: Definição das regras de validação para os payloads.
  - `EndPoints.json`: Declaração das hierarquias de endpoints.
- **Asaas**: o host base é `https://api-sandbox.asaas.com` (sandbox, default de `ASAAS_BASE_URL` em `config/services.php`) ou `https://api.asaas.com` (produção); `/v3` é **prefixo de path** nas chamadas (ex.: `/v3/customers`), não parte do host. Autenticação pelo header `access_token` com `config('services.asaas.api_key')`. A convenção de chaves deste gateway em `config/services.php` é `api_key`/`base_url` — não existe chave `token`. Para detalhes de cobranças/webhook (ainda inexistentes), consulte [references/asaas.md](references/asaas.md).
- **Efí**: Instancie o SDK da Efí (`EfiPay`) usando parâmetros de configuração via `config('bank.efi_options')`. O caminho do certificado é resolvido dinamicamente via `resolveLocalDiskPath()`.
- **Banco Inter** (parcialmente configurado — SDK e credenciais existem, mas a integração ainda é um placeholder): hoje `app/Services/Bank/InterPaymentExecute.php` traz apenas `public static function createBolix(): void {}` vazio; NÃO há nenhuma instanciação de `InterSdk` no projeto. Ao efetivamente implementar, use o SDK oficial **`inter-co/pj-sdk-php`** (já no `composer.json`) — NÃO implemente mTLS manualmente nem acesse `/oauth/v2/token` diretamente. Instancie a classe de entrada `Inter\Sdk\sdkLibrary\InterSdk` com `(string $environment, string $clientId, string $clientSecret, string $certificate, string $certificatePassword)`; o SDK trata o handshake mTLS e o ciclo de vida do token OAuth internamente. Acesse os domínios por meio de seus accessors: `$sdk->billing()`, `$sdk->pix()`, `$sdk->banking()`. As credenciais já existem em `config/bank.php` (`inter_ambient`, `inter_client_id`, `inter_client_secret`, `inter_certificate_path`, `inter_certificate_password`); resolva o caminho do certificado via `resolveLocalDiskPath()`.
- **Mercado Pago** (aspiracional — veja o aviso de status acima): uma vez instalado o SDK, implemente um `MercadoPagoService` para a lógica de negócio, isolando o conector, e resolva as credenciais via `config('services.mercadopago.access_token')`.

### 2. Mapeamento de Payload e Dados usando DTOs
Garanta que todos os payloads enviados ou recebidos dos gateways de pagamento sejam mapeados via objetos de transferência de dados do Spatie Laravel Data.
- Armazene os DTOs em namespaces específicos por domínio dentro de `app/Data/` (ex.: `app/Data/Finance/`, `app/Data/Webhook/`). Hoje NÃO existem pastas `app/Data/Asaas/` nem `app/Data/Inter/`; crie-as ao efetivar cada integração.
- Use Constructor Property Promotion para todas as propriedades e garanta type hints estritos.

### 3. Mapeamento de Enums
Mapeie métodos de pagamento e status de transações usando Backed Enums decorados com `#[TypeScript]` para sincronização de tipos com o frontend.
- Exemplos de nomenclatura (aspiracional — veja o aviso de status acima): `AsaasBillingType` (`BOLETO`, `CREDIT_CARD`, `PIX`, `UNDEFINED`), `AsaasPaymentStatus`. Esses enums **não existem** em `app/Enums/` hoje; são o nome a adotar quando a integração de cobranças Asaas for efetivada.

### 4. Segurança de Webhooks e Processamento Assíncrono
Os webhooks devem ser recebidos por meio de rotas dedicadas apontando para controllers específicos.
- **Asaas** (aspiracional — não há rota nem controller de webhook Asaas hoje; veja §1): `POST /api/webhooks/asaas`. Valide se o header `asaas-access-token` corresponde ao token de webhook resolvido da config. Essa chave **ainda não existe** — `config/services.php` só define `asaas.api_key` e `asaas.base_url`; crie-a seguindo a convenção do gateway no projeto (ex.: `services.asaas.webhook_token`, a partir de uma env).
- **Efí**: `POST /api/webhook/efi/{secure_code}` (rota nomeada `post.efi.webhook`, em `routes/api/api.webhooks.Routes.php`; há também `put.efi.webhook` e `get.efi.webhook` para o mesmo caminho). Aponta para `App\Http\Controllers\Api\Whatsapp\WebhookController@index`. Verifique o token contra `webhook_code_bolix` ou `webhook_code_link` no model `Payments`.
- **Banco Inter** (NÃO existe hoje): não há rota de webhook do Inter registrada em `routes/` nem um `ProcessInterWebhookJob` em `app/Jobs/`. Ao criar, siga o padrão do Efí: registre `POST /api/webhook/inter/{secure_token}` em `api.webhooks.Routes.php`. O segredo de validação também está **a definir** — `config/bank.php` só traz `inter_ambient`, `inter_client_id`, `inter_client_secret`, `inter_certificate_path` e `inter_certificate_password` (sem `inter_webhook_token`). Adicione uma chave dedicada em `config/bank.php` a partir de uma env antes de comparar, ou valide o segmento `{secure_token}` contra um token persistido no model `Payments` (mesmo padrão do Efí). O Banco Inter também assina/autentica webhooks via mTLS — valide o certificado do cliente quando aplicável.
- **Mercado Pago** (aspiracional — veja §1): Valide o header `x-signature` ou os query params de segurança usando o Webhook Signing Secret do Mercado Pago.

**Regra de Processamento para Todos os Gateways:**
- **Não processe os payloads de webhook de forma síncrona.**
- Armazene o payload bruto na tabela `bank_webhooks` com status `pending`, e então despache um job em background. Hoje só existe `App\Jobs\ProcessEfiWebhookJob`; para novos gateways, siga esse mesmo padrão (ex.: um futuro `ProcessInterWebhookJob`).
- Retorne uma resposta HTTP imediata (por exemplo, `200 OK`) para evitar timeouts e notificações duplicadas.
- Implemente idempotência verificando o status no banco de dados antes de processar.

### 5. Tratamento de Exceções e Logging Dedicado
- Envolva todas as chamadas externas em blocos try-catch. Capture exceções específicas (por exemplo, `EfiException`) e exceções genéricas de rede.
- Lance exceções customizadas para tratar falhas transacionais ou de validação de API.
- Registre a atividade usando canais de log dedicados definidos em `config/logging.php`. Hoje só existe o canal `efi` (`config/logging.php:285`); ao adicionar novos gateways (ex.: `inter`, `asaas`, `mercadopago`), crie o canal dedicado correspondente antes de usá-lo.
- Evite falhas silenciosas. Garanta que existam comandos de sincronização de failover/fallback (por exemplo, `SyncEfiPaymentsStatusCommand` CLI).

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- **NÃO** improvise um quarto padrão de integração: use o SDK oficial, o conector em `app/Http/Integrations/{Gateway}/` ou o Service com `Http::baseUrl` — o que o gateway já adota (§1). Chamadas HTTP soltas espalhadas por controllers/jobs ficam fora de qualquer um dos três.
- **NÃO** processe eventos de webhook de forma síncrona. Sempre enfileire-os para evitar timeouts.
- **NÃO** ignore a verificação de assinatura ou token nos webhooks.
- **NÃO** deixe credenciais, client IDs, secrets ou caminhos de certificado hardcoded.
- **NÃO** registre em log parâmetros sensíveis de cartão de crédito (CVV, números completos de cartão) ou chaves de autenticação brutas.
- **NÃO** permita o processamento duplicado do mesmo evento de pagamento. Implemente locks transacionais ou chaves únicas.
- **NÃO** use comentários inline ou blocos PHPDoc em inglês no código PHP. Todos os comentários e a documentação PHP devem estar estritamente em Português Brasileiro (pt-BR).
