---
name: laravel-digital-signatures-integration
description: Use when designing, implementing, or modifying electronic and digital signature integrations (such as Autentique or Clicksign) within the Laravel codebase. It covers document upload/creation, signer configuration, secure webhook handling, and background job processing for signed documents.
---

# Integração de Assinaturas Digitais no Laravel

## Objetivo
Estabelecer padrões de desenvolvimento seguros, robustos e consistentes para integrar assinaturas eletrônicas e digitais via APIs de terceiros dentro do backend Laravel do ecossistema Engeapp. O **Autentique** é a integração real do projeto (pacote `vinicinbgs/autentique-v2` instalado). O **Clicksign** NÃO está instalado no engeapp hoje — é apresentado apenas como padrão de integração opcional/genérico (mesmo tratamento dado a google-calendar/lighthouse): use-o como referência caso venha a ser adotado, instalando primeiro as credenciais/config correspondentes.

## Instruções

### 1. Configuração Inicial
Sempre armazene as credenciais de API no `.env` e carregue-as via `config/services.php`. Nunca acesse `env()` diretamente fora dos arquivos de configuração.
Nunca deixe tokens de API ou segredos de webhook fixos no código (hardcode) em classes de service ou controllers.

### 2. Arquitetura de Service
Crie classes de Service dedicadas (ex.: `ClicksignService`, `SignatureService`) para encapsular todas as operações da API.
- Injete configurações ou clientes de API usando constructor property promotion quando aplicável.
- Para o Clicksign, use a facade `Http` do Laravel para fazer as requisições à API. Não use curl bruto ou SDKs externos de terceiros.
- Para o Autentique, use apropriadamente o cliente GraphQL/Document fornecido.
- Registre as falhas usando um canal de logging dedicado (ex.: `autentique`, `clicksign`), especificando um contexto claro.

### 3. Processamento Assíncrono de Webhooks
**Nunca processe webhooks de forma síncrona** para evitar timeouts HTTP. Sempre valide o webhook, extraia os identificadores necessários do payload e despache um job na fila (ex.: `ProcessClicksignWebhookJob`, `ReloadPowerAttorneyStatusJob`) para lidar com a lógica de negócio, sincronização de status ou download de arquivos.

## Instruções Específicas do Autentique

### Criação de Documento e Configuração do Signatário
Ao despachar um documento para assinaturas, use o cliente Documents do Autentique. Defina os signatários de forma clara, incluindo o método de entrega (ex.: WhatsApp).

```php
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
            $documentModel->save();
        }
    }
}
```

### Validação Segura de Webhook (Autentique)
Sempre valide as requisições de webhook recebidas contra o segredo de webhook configurado. O segredo deve ser comparado usando comparação de string em tempo constante (`hash_equals`) para prevenir ataques de timing.

```php
private function isValidToken(Request $request, string $secret): bool
{
    $token = $request->bearerToken();
    if (!$token) {
        return false;
    }
    return hash_equals($secret, $token);
}
```

### Construir Histórico Linear de Assinaturas
Ao recuperar os detalhes do documento, mapeie o array de assinaturas para um rastro de histórico linear a fim de expor o progresso em tempo real para o frontend.

## Instruções Específicas do Clicksign (integração opcional — não instalada no engeapp)

> Clicksign é apresentado como padrão de integração genérico/aspiracional. Não há SDK nem `config('services.clicksign.*')` no projeto hoje; adote-o somente após instalar as credenciais/config. Os exemplos abaixo servem como referência de arquitetura.

### Métodos do Service Clicksign
Faça upload de documentos, crie signatários e adicione signatários aos documentos usando a facade HTTP.

```php
// Exemplo: Adicionar signatário ao documento
public function addSignerToDocument(string $documentKey, string $signerKey, string $signAs = 'sign'): array
{
    $response = Http::withToken($this->token)
        ->post("{$this->baseUrl}/api/v1/lists", [
            'list' => [
                'document_key' => $documentKey,
                'signer_key' => $signerKey,
                'sign_as' => $signAs,
            ],
        ]);

    if ($response->failed()) {
        Log::channel('clicksign')->error('Failed to associate signer with document', [
            'document_key' => $documentKey,
            'signer_key' => $signerKey,
            'status' => $response->status(),
            'body' => $response->json(),
        ]);
        $response->throw();
    }

    return $response->json();
}
```

### Tratamento de Webhook e Validação de Assinatura (Clicksign)
- O Clicksign envia webhooks usando `POST`.
- A autenticidade do payload do webhook é validada usando o header `X-Hook-Signature` (assinatura HMAC SHA256 do corpo da requisição).

```php
public function handle(Request $request): Response
{
    $signature = $request->header('X-Hook-Signature');
    $secret = config('services.clicksign.webhook_secret');
    $payload = $request->getContent();

    if (empty($signature) || empty($secret)) {
        return response('Unauthorized', 401);
    }

    $computedSignature = hash_hmac('sha256', $payload, $secret);

    if (!hash_equals($computedSignature, $signature)) {
        return response('Unauthorized', 401);
    }

    $data = $request->json()->all();
    ProcessClicksignWebhookJob::dispatch($data);

    return response('Webhook processed successfully', 200);
}
```

### Download Resiliente de Documento Assinado (Geral/Clicksign)
Ao receber uma notificação de status assinado, busque o PDF assinado de forma segura e salve-o usando a abstração `Storage` do Laravel. Implemente um Queue Job com retentativas automáticas para downloads resilientes.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
- **Sem Processamento Síncrono de Webhook:** Sempre delegue o processamento do payload do webhook, o download de documentos e as verificações de status para jobs em fila em background.
- **Validação Estrita de Webhook:** Nunca pule a verificação do `X-Hook-Signature` (Clicksign) ou do Token (Autentique). Sempre use `hash_equals()` para comparação em tempo constante a fim de prevenir ataques de timing.
- **Segredos Baseados em Config:** Não deixe URLs, tokens ou segredos de webhook fixos no código (hardcode).
- **Use o Cliente HTTP do Laravel (Para APIs REST):** Não use comandos PHP `curl_*` brutos. Sempre use a facade `Http` do Laravel ao se comunicar via REST.
- **Logging Dedicado:** Todos os eventos, erros e falhas de validação devem ser registrados em seus respectivos canais de log.
