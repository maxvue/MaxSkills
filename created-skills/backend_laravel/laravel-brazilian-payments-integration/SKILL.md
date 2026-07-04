---
name: laravel-brazilian-payments-integration
description: Use when configuring, debugging, or creating payment integrations with Brazilian gateways (Asaas, Efí, Banco Inter, Mercado Pago). Triggers on creating customers, generating invoices (Pix, Boleto, Credit Card, Bolix), checking payment status, and handling webhooks from these providers.
---

# Integração de Pagamentos Brasileiros com Laravel

## Objetivo
Padronizar e proteger a integração de gateways de pagamento brasileiros (Asaas, Efí/Gerencianet, Banco Inter, Mercado Pago) dentro do ecossistema de backend do Engeapp. Esta skill garante a adesão estrita aos padrões de conector `BaseApi`, pipelines de dados tipados usando Spatie Laravel Data (DTOs), status robustos baseados em Enums, validação segura de assinatura/token de webhooks e práticas dedicadas de logging.

## Instruções

### 1. Arquitetura de Integração BaseApi e Inicialização de SDK
Todas as interações com APIs devem ser roteadas por meio de um namespace de integração dedicado que estende `BaseApi` (por exemplo, `app/Http/Integrations/{Gateway}/`), exceto quando SDKs específicos forem obrigatórios (como o da Efí).
- **Arquivos**:
  - `Connector.php`: O conector de integração em PHP.
  - `Attributes.json`: Definição das regras de validação para os payloads.
  - `EndPoints.json`: Declaração das hierarquias de endpoints.
- **Asaas** (aspiracional — NÃO integrado hoje no engeapp; não há SDK do Asaas no `composer.json` nem `config('services.asaas.*')`): trate como referência de arquitetura. Ao efetivamente adicioná-lo, crie PRIMEIRO a configuração/credenciais (`config('services.asaas.*')`) e o namespace de conector. Sandbox `https://sandbox.asaas.com/api/v3`, Produção `https://api.asaas.com/api/v3`. Use o header `access_token`. Para detalhes específicos da integração com o Asaas, consulte [references/asaas.md](references/asaas.md).
- **Efí**: Instancie o SDK da Efí (`EfiPay`) usando parâmetros de configuração via `config('bank.efi_options')`. O caminho do certificado é resolvido dinamicamente via `resolveLocalDiskPath()`.
- **Banco Inter**: Use o SDK oficial **`inter-co/pj-sdk-php`** (no `composer.json`) — NÃO implemente mTLS manualmente nem acesse `/oauth/v2/token` diretamente. Instancie a classe de entrada `Inter\Sdk\sdkLibrary\InterSdk` com `(string $environment, string $clientId, string $clientSecret, string $certificate, string $certificatePassword)`; o SDK trata o handshake mTLS e o ciclo de vida do token OAuth internamente. Acesse os domínios por meio de seus accessors: `$sdk->billing()`, `$sdk->pix()`, `$sdk->banking()`. Resolva as credenciais e o caminho do certificado a partir da configuração (por exemplo, `config('bank.inter_*')` + `resolveLocalDiskPath()`); os certificados ficam em `storage/app/certificates/`.
- **Mercado Pago**: Atualmente NÃO integrado no engeapp — não existe SDK do Mercado Pago nem `config('services.mercadopago.*')` no projeto. Trate isso como aspiracional: adicioná-lo requer instalar PRIMEIRO o SDK do Mercado Pago (e sua configuração/credenciais). Uma vez instalado, implemente um `MercadoPagoService` para a lógica de negócio, isolando o conector, e resolva as credenciais via `config('services.mercadopago.access_token')`.

### 2. Mapeamento de Payload e Dados usando DTOs
Garanta que todos os payloads enviados ou recebidos dos gateways de pagamento sejam mapeados via objetos de transferência de dados do Spatie Laravel Data.
- Armazene os DTOs em namespaces específicos, por exemplo, `app/Data/Asaas/`, `app/Data/Inter/`.
- Use Constructor Property Promotion para todas as propriedades e garanta type hints estritos.

### 3. Mapeamento de Enums
Mapeie métodos de pagamento e status de transações usando Backed Enums decorados com `#[TypeScript]` para sincronização de tipos com o frontend.
- por exemplo, `AsaasBillingType` (`BOLETO`, `CREDIT_CARD`, `PIX`, `UNDEFINED`), `AsaasPaymentStatus`.

### 4. Segurança de Webhooks e Processamento Assíncrono
Os webhooks devem ser recebidos por meio de rotas dedicadas apontando para controllers específicos.
- **Asaas** (aplica-se apenas quando o SDK/config forem adicionados — veja §1; não está configurado hoje): `POST /api/webhooks/asaas`. Valide se o header `asaas-access-token` corresponde ao token de webhook resolvido da config (ex.: `config('services.asaas.webhook_token')`, a ser criado junto com a integração).
- **Efí**: `POST /api/bank/efi/webhook/{secure_code}`. Verifique o token contra `webhook_code_bolix` ou `webhook_code_link` no model `Payments`.
- **Banco Inter**: `POST /api/bank/inter/webhook/{secure_token}`. ATENÇÃO: NÃO existe hoje `config('bank.inter_webhook_token')` — o `config/bank.php` só define `inter_ambient`, `inter_client_id`, `inter_client_secret`, `inter_certificate_path` e `inter_certificate_password`. Portanto, o segredo de validação do webhook Inter está **a definir**: adicione uma chave dedicada em `config/bank.php` (ex.: `inter_webhook_token` a partir de uma env) antes de comparar, ou valide o segmento `{secure_token}` da rota contra um token persistido no model `Payments` (mesmo padrão do Efí). O Banco Inter também assina/autentica webhooks via mTLS — valide o certificado do cliente quando aplicável.
- **Mercado Pago** (aplica-se apenas quando o SDK for adicionado — veja §1; não está configurado hoje): Valide o header `x-signature` ou os query params de segurança usando o Webhook Signing Secret do Mercado Pago.

**Regra de Processamento para Todos os Gateways:**
- **Não processe os payloads de webhook de forma síncrona.**
- Armazene o payload bruto na tabela `bank_webhooks` com status `pending`, e então despache um job em background (por exemplo, `ProcessInterWebhookJob`, `ProcessEfiWebhookJob`, `ProcessMercadoPagoWebhookJob`).
- Retorne uma resposta HTTP imediata (por exemplo, `200 OK`) para evitar timeouts e notificações duplicadas.
- Implemente idempotência verificando o status no banco de dados antes de processar.

### 5. Tratamento de Exceções e Logging Dedicado
- Envolva todas as chamadas externas em blocos try-catch. Capture exceções específicas (por exemplo, `EfiException`) e exceções genéricas de rede.
- Lance exceções customizadas para tratar falhas transacionais ou de validação de API.
- Registre a atividade usando canais de log dedicados definidos em `config/logging.php` (por exemplo, `asaas`, `efi`, `inter`, `mercadopago`).
- Evite falhas silenciosas. Garanta que existam comandos de sincronização de failover/fallback (por exemplo, `SyncEfiPaymentsStatusCommand` CLI).

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- **NÃO** faça requisições HTTP brutas para APIs fora da estrutura de integração `BaseApi` ou dos SDKs aprovados.
- **NÃO** processe eventos de webhook de forma síncrona. Sempre enfileire-os para evitar timeouts.
- **NÃO** ignore a verificação de assinatura ou token nos webhooks.
- **NÃO** deixe credenciais, client IDs, secrets ou caminhos de certificado hardcoded.
- **NÃO** registre em log parâmetros sensíveis de cartão de crédito (CVV, números completos de cartão) ou chaves de autenticação brutas.
- **NÃO** permita o processamento duplicado do mesmo evento de pagamento. Implemente locks transacionais ou chaves únicas.
- **NÃO** use comentários inline ou blocos PHPDoc em inglês no código PHP. Todos os comentários e a documentação PHP devem estar estritamente em Português Brasileiro (pt-BR).
