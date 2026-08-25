---
name: laravel-gemini-file-api-media-integration-best-practices
description: "Use when managing media uploads and multimodal processing via Google AI File API with Gemini SDK in Laravel. Covers video, audio, or PDF file processing, temp uploads, active state polling, and cleanup. Covers objectives and core workflows."
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Fornecer diretrizes robustas, seguras e eficientes em memória para fazer upload e gerenciar grandes arquivos de mídia (vídeos, faixas de áudio longas, PDFs grandes) usando a Google AI File API com o Gemini PHP SDK dentro de aplicações Laravel. Isso evita problemas de alto consumo de memória causados por payloads Base64 e garante interações multimodais confiáveis com a IA.

---

## Instruções

### 1. Determinando Quando Usar File API vs. Blobs (Inline Data) vs. Laravel AI SDK
- **Use Inline Blobs (Base64):** Para arquivos pequenos (< 20MB), como imagens padrão, pequenos documentos PDF e trechos curtos de áudio. Isso é mais rápido, pois não requer uma etapa intermediária de upload. Consulte [laravel-gemini-php-sdk-best-practices](../laravel-gemini-php-sdk-best-practices/SKILL.md).
- **Use a Google File API (`Gemini::files()`):** Apenas para vídeo e mídia grande (> 20MB) que o Laravel AI SDK do projeto não cobre. Essencial para prevenir o esgotamento de memória do PHP (`Allowed memory size exhausted`) e permanecer dentro dos limites de payload da requisição.
- **Quando NÃO usar (caminho canônico do engeapp):** para PDFs, imagens e áudio processados por agentes, o engeapp usa o Laravel AI SDK (`Laravel\Ai\Files\LocalDocument`/`LocalImage`/`LocalAudio`, ver `App\Services\Ai\GeminiDocumentService`), não `Gemini::files()`. O pacote `laravel/ai` (`vendor/laravel/ai/src/Files/`) já cobre Audio, Document e Image (variantes Local/Remote/Stored/Base64) — não existe classe Video, que é o único nicho real onde a File API se justifica.

### 2. Sempre Execute o Pipeline Dentro de um Job em Fila
O pipeline completo (upload → polling → generateContent → delete) deve rodar dentro de um Job `implements ShouldQueue` processado pelo Horizon, seguindo o padrão de `app/Jobs/GeminiContentJob.php` (com `$tries`/`$backoff` configurados), nunca no ciclo request/response. O engeapp roda sob Octane (`laravel/octane`), onde um `sleep()` de dezenas de segundos no polling travaria o worker.

### 3. Fazendo Upload de Arquivos para a Google File API
Resolva o cliente da File API através da facade `Gemini`. Use caminhos locais do servidor ou streams de armazenamento temporário da facade `Storage` do Laravel para executar o upload.

```php
use Gemini\Laravel\Facades\Gemini;
use Gemini\Enums\MimeType;
use Illuminate\Support\Facades\Storage;

// Exemplo 1: Upload a partir de um caminho local direto
$filePath = storage_path('app/temp/marketing-video.mp4');
$uploadedFile = Gemini::files()->upload(
    filename: $filePath,
    mimeType: MimeType::VIDEO_MP4,
    displayName: 'Client Marketing Video'
);

// Exemplo 2: Se o arquivo estiver no S3/MinIO, baixe-o localmente antes de subir para a File API
$tempLocalPath = tempnam(sys_get_temp_dir(), 'gemini_upload_');
file_put_contents($tempLocalPath, Storage::disk('s3')->get('briefings/audio_recording.mp3'));

$uploadedAudio = Gemini::files()->upload(
    filename: $tempLocalPath,
    mimeType: MimeType::AUDIO_MP3,
    displayName: 'Client Briefing Audio'
);
```

### 4. Polling de Status Ativo (Monitorando o Estado de Processamento)
Arquivos grandes (especialmente vídeos e arquivos de áudio pesados) exigem processamento no backend da Google AI antes de poderem ser analisados pelo Gemini. Você deve fazer polling na API de metadados até que o estado do arquivo seja `ACTIVE`.

```php
use Gemini\Enums\FileState;
use Illuminate\Support\Facades\Log;

$maxRetries = 10;
$retryDelaySeconds = 3;
$attempts = 0;

do {
    sleep($retryDelaySeconds);
    
    // Atualiza os metadados do arquivo usando a URI ou o nome retornado
    $meta = Gemini::files()->metadataGet($uploadedFile->uri);
    $attempts++;
    
    if ($meta->state === FileState::Active) {
        break;
    }
    
    if ($meta->state === FileState::Failed) {
        throw new \RuntimeException("Google File API processing failed for: {$uploadedFile->name}");
    }
    
} while ($attempts < $maxRetries);

if ($meta->state !== FileState::Active) {
    throw new \RuntimeException("Timeout waiting for Google File API processing to complete.");
}
```

### 5. Passando Arquivos Enviados para os Modelos Gemini
Para consultar a IA sobre o arquivo enviado, passe uma instância de `Gemini\Data\UploadedFile` como parte do array de conteúdo para `generateContent` ou `streamGenerateContent`.

```php
use Gemini\Data\UploadedFile;
use Gemini\Enums\MimeType;

$result = Gemini::generativeModel(model: 'gemini-2.5-flash')
    ->generateContent([
        'Analise este vídeo e identifique possíveis pontos de atenção na paleta de cores e transições.',
        new UploadedFile(
            fileUri: $uploadedFile->uri,
            mimeType: MimeType::VIDEO_MP4
        )
    ]);

$responseContent = $result->text();
```

### 6. Limpeza e Exclusão de Arquivos Obrigatórias
Sempre limpe os arquivos no armazenamento da Google File API para reforçar a privacidade de dados, proteger a propriedade intelectual e evitar exceder o limite de armazenamento/cota da sua organização. Utilize blocos `try-finally` para garantir a exclusão do arquivo.

```php
use Illuminate\Support\Facades\Log;

$uploadedFile = null;
$tempLocalPath = null;

try {
    // 1. Upload
    $uploadedFile = Gemini::files()->upload(
        filename: $tempLocalPath,
        mimeType: MimeType::VIDEO_MP4,
        displayName: 'Client Marketing Video'
    );

    // 2. Poll do Status
    // (ver seção 4)

    // 3. Gerar Conteúdo
    // (ver seção 5)

} finally {
    // Apaga o arquivo temporário local, se existir
    if ($tempLocalPath && file_exists($tempLocalPath)) {
        unlink($tempLocalPath);
    }
    
    // Deleta o arquivo da Google File API se o upload ocorreu com sucesso
    if ($uploadedFile) {
        try {
            Gemini::files()->delete($uploadedFile->uri);
        } catch (\Throwable $cleanupException) {
            Log::channel('gemini')->warning("Failed to delete remote file from Google File API: {$uploadedFile->uri}", [
                'error' => $cleanupException->getMessage()
            ]);
        }
    }
}
```

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
- **Nunca Faça Hardcode de Segredos:** API Keys e config de autenticação nunca devem ser colocadas em arquivos-fonte. Mantenha os parâmetros de ambiente usando a config do Laravel.
- **Limpeza Estrita no Finally:** Garanta que tanto os arquivos temporários locais quanto as entradas remotas da Google File API sejam deletados usando blocos `finally`, protegendo contra exceções de geração de conteúdo com falha.
- **MimeTypes Polimórficos de Arquivo:** Verifique novamente se o enum `MimeType` correto corresponde à extensão do arquivo antes de executar `upload()`.
- **Timeout do Cliente HTTP:** O SDK Gemini usa `config('gemini.request_timeout')`, com padrão de 30 segundos (`GEMINI_REQUEST_TIMEOUT`). Para uploads de vídeos grandes ou arquivos de mídia pesados, aumente esse valor via `.env` — o padrão de 30s é insuficiente para os cenários que justificam o uso da File API.
- **Comentários em Português Brasileiro:** Garanta que os comentários de código e explicações inline sejam escritos em **português brasileiro** (`pt-BR`) conforme as diretrizes do repositório.
