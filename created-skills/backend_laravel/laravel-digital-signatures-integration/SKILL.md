---
name: laravel-digital-signatures-integration
description: "Use when designing or modifying digital signature integrations (Autentique, Clicksign) in Laravel. Covers document upload, signers, secure webhooks, and background job processing. Covers objectives and core workflows."
---
# Integração de Assinaturas Digitais no Laravel

## Objetivo
Estabelecer padrões de desenvolvimento seguros, robustos e consistentes para integrar assinaturas eletrônicas e digitais via APIs de terceiros dentro do backend Laravel do ecossistema Engeapp. O **Autentique** é a integração real do projeto (pacote `vinicinbgs/autentique-v2` instalado). O **Clicksign** NÃO está instalado no engeapp hoje — é apresentado apenas como padrão de integração opcional/genérico (mesmo tratamento dado a google-calendar/lighthouse): use-o como referência caso venha a ser adotado, instalando primeiro as credenciais/config correspondentes.

## Instruções

### 1. Configuração Inicial
Sempre armazene as credenciais de API no `.env` e carregue-as via `config/services.php`. Nunca acesse `env()` diretamente fora dos arquivos de configuração.

### 2. Arquitetura de Service
Crie classes de Service dedicadas (ex.: `ClicksignService`, `SignatureService`) para encapsular todas as operações da API.
- Injete configurações ou clientes de API usando constructor property promotion quando aplicável.
- Para o Clicksign, use a facade `Http` do Laravel para fazer as requisições à API. Não use curl bruto ou SDKs externos de terceiros.
- Para o Autentique, use apropriadamente o cliente GraphQL/Document fornecido.
- Registre as falhas usando um canal de logging dedicado. Hoje só o canal `autentique` existe de fato em `config/logging.php`; `clicksign` é apenas o nome sugerido para quando essa integração for instalada (ver seção Clicksign abaixo) — não use `Log::channel('clicksign')` sem antes registrar o canal, ou ele quebra em runtime.

**Registre o cliente `Documents` no container.** O construtor de `vinicinbgs\Autentique\Documents` recebe o token por argumento (`__construct(string $token = null, ...)`); sem esse argumento o token fica `null` e a API lança `EmptyTokenException`. Por isso, injetar `Documents` direto no service (via property promotion) só funciona porque há um binding explícito no service provider passando o token da config. Sempre registre esse binding antes de depender da injeção:

```php
// app/Providers/SignatureServiceProvider.php
public function register(): void
{
    $this->app->bind(
        \vinicinbgs\Autentique\Documents::class,
        fn () => new \vinicinbgs\Autentique\Documents((string) config('services.autentique.token'))
    );
}
```

### 3. Processamento Assíncrono de Webhooks
**Nunca processe webhooks de forma síncrona** para evitar timeouts HTTP. Sempre valide o webhook, extraia os identificadores necessários do payload e despache um job na fila (ex.: `ProcessClicksignWebhookJob`, `ReloadPowerAttorneyStatusJob`) para lidar com a lógica de negócio, sincronização de status ou download de arquivos.

## Instruções Específicas do Autentique

### Criação de Documento e Configuração do Signatário
Ao despachar um documento para assinaturas, use o cliente Documents do Autentique. Defina os signatários de forma clara, incluindo o método de entrega (ex.: WhatsApp).

```php
use App\Classes\PhoneClass;
use App\Models\Project\ProjectPowerOfAttorneyDocument;
use vinicinbgs\Autentique\Documents;

class SignatureService
{
    public function __construct(private readonly Documents $documents) {}

    public function sendToAutentique(ProjectPowerOfAttorneyDocument $documentModel, string $filePath, ?string $phone = null): void
    {
        $attributes = [
            'document' => ['name' => 'PROCURAÇÃO - ' . $documentModel->project->client->name],
            'signers'  => [
                ['email' => 'contato@enge.tec.br', 'action' => 'SIGN'],
                [
                    'phone' => '+' . ($documentModel->send_to ?? $documentModel->project->client->international_phone_number), 
                    'delivery_method' => 'DELIVERY_METHOD_WHATSAPP', 
                    'action' => 'SIGN'
                ],
            ],
            'file' => $filePath,
        ];

        $response = $this->documents->create($attributes);
        $documentId = data_get($response, 'data.createDocument.id');

        if ($documentId) {
            $documentModel->uuid_doc = (string) $documentId;
            // Normaliza e persiste o telefone efetivamente usado no envio — não descarte esse efeito colateral.
            $documentModel->send_to = PhoneClass::getFormattedNumber($phone ?? $documentModel->project?->client->phone_number);
            $documentModel->save();
        }
    }
}
```

### Validação Segura de Webhook (Autentique)
O Autentique autentica o webhook por Bearer token no header `Authorization`. A validação é **condicional ao segredo estar configurado** (`config('services.autentique.webhook_secret')`): se o segredo existir, exija e valide o token; se estiver vazio, o webhook é aceito sem validação de token (comportamento real do `AutentiqueWebhookController`). Quando o token for exigido e inválido, responda **403** (não 401). Compare o segredo com `hash_equals` para prevenir ataques de timing.

```php
public function handle(Request $request): JsonResponse
{
    $secret = (string) config('services.autentique.webhook_secret');

    // Só valida o token quando há segredo configurado
    if ($secret && ! $this->isValidToken($request, $secret)) {
        Log::channel('autentique')->warning('Webhook Autentique: token de autenticação inválido', [
            'ip' => $request->ip(),
        ]);

        return response()->json(['error' => 'Token inválido'], 403);
    }

    // ... extrai event.type / document.id e despacha o job (ver abaixo)
}

private function isValidToken(Request $request, string $secret): bool
{
    $token = $request->bearerToken();
    if (! $token) {
        return false;
    }
    return hash_equals($secret, $token);
}
```

Após validar, extraia o tipo de evento e o `document.id` do payload (o controller lê tanto `event.data.document.id` quanto os formatos alternativos `data.document.id`/`document.id`), localize o `ProjectPowerOfAttorneyDocument` por `uuid_doc` e despache `ReloadPowerAttorneyStatusJob::dispatch($powerOfAttorney->id)` para sincronizar o status de forma assíncrona.

### Construir Histórico Linear de Assinaturas
Ao recuperar os detalhes do documento, mapeie o array de assinaturas para um rastro de histórico linear a fim de expor o progresso em tempo real para o frontend. No `SignatureService` real, isso é feito por `buildSignatureHistory()` (monta uma lista ordenada de eventos `created → sent → delivered → opened → viewed → signed`, com `refused` adicional se houve recusa; cada item no formato `{status, msg, date, done}`) e `resolveLatestStatus()` (varre esse histórico e retorna o último item com `done = true`). Siga esse mesmo par de responsabilidades (montar histórico linear + resolver status mais recente) ao trabalhar nessa área.

### Download Resiliente de Documento Assinado
Ao receber uma notificação de status assinado, busque o PDF assinado de forma segura e salve-o usando a abstração `Storage` do Laravel, com um Queue Job com retentativas automáticas (`ReloadPowerAttorneyStatusJob` usa `$tries = 4` e `backoff(): [30, 60, 120]`).

> **Estado atual do fetch, não o alvo:** hoje `handleSignedDocument` (`SignatureService.php:255`) baixa o PDF com `@file_get_contents($fileSigned)` — sem timeout e com supressão de erro (`@`) — e não com a facade `Http`. É dívida técnica conhecida: migre para `Http::timeout(...)->get(...)` quando tocar nesse trecho. A regra "sempre use a facade Http" (ver Restrições) continua sendo o alvo a seguir em código novo.

## Instruções Específicas do Clicksign (integração opcional — não instalada no engeapp)

> Clicksign é apresentado como padrão de integração genérico/aspiracional. Não há SDK, `ClicksignService`, `config('services.clicksign.*')`, canal de log `clicksign` nem `ProcessClicksignWebhookJob` no projeto hoje (confirmado por busca no código-fonte, fora vendor/node_modules). Adote-o somente após instalar as credenciais/config; o resumo abaixo é só a referência de arquitetura, não código existente.

Ao implementar: use a facade `Http` do Laravel (`Http::withToken($this->token)->post(...)`) para as chamadas REST (upload de documentos, criação/associação de signatários), com log de falha em canal dedicado (registre `clicksign` em `config/logging.php` antes de usá-lo). Para o webhook: o Clicksign envia `POST` com o header `X-Hook-Signature` (HMAC SHA256 do corpo da requisição usando o segredo de `config('services.clicksign.webhook_secret')`); valide com `hash_equals($computedSignature, $signature)` e responda `401` quando a assinatura for inválida ou o segredo/assinatura estiverem ausentes, antes de despachar o job de processamento assíncrono.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
- **Validação Estrita de Webhook:** Sempre que houver segredo configurado, valide o webhook antes de processá-lo — `X-Hook-Signature` (Clicksign) ou Bearer token (Autentique). No Autentique a validação é condicional: só ocorre quando `services.autentique.webhook_secret` está definido, e a resposta a token inválido é 403. Sempre use `hash_equals()` para comparação em tempo constante a fim de prevenir ataques de timing.
- **Segredos Baseados em Config:** Não deixe URLs, tokens ou segredos de webhook fixos no código (hardcode).
- **Use o Cliente HTTP do Laravel (Para APIs REST):** Não use comandos PHP `curl_*` brutos. Sempre use a facade `Http` do Laravel ao se comunicar via REST.
- **Logging Dedicado:** Todos os eventos, erros e falhas de validação devem ser registrados em seus respectivos canais de log.
