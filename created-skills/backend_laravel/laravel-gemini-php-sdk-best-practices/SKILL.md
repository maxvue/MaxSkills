---
name: laravel-gemini-php-sdk-best-practices
description: "Use when interacting directly with the Gemini API using the google-gemini-php/laravel SDK, configuring GenerationConfig, utilizing structured outputs (JSON Schemas), handling multimodal inputs (Images, Audio, PDF) using Blob, or managing model calls and exceptions in Laravel."
---

# Objetivo
Garantir integrações robustas, padronizadas e de alto desempenho com a API Gemini usando o SDK `google-gemini-php/laravel` dentro do backend do Engeapp. Isso abrange a estruturação de consultas usando a Facade do Gemini, a definição de saídas JSON rígidas com helpers nativos de schema, o tratamento seguro de entradas multimodais via Blobs em Base64 e a execução de tratamento de erros confiável.

---

# Instruções

### 1. Seleção de Modelo e Uso da Facade
Sempre resolva o modelo Gemini usando a facade `Gemini` para gerenciar as chamadas de modelo. O projeto usa tanto a família 2.5 quanto a 3.x — prefira a 3.x para novos fluxos e mantenha a 2.5 como fallback estável.
- **Modelo principal para operações Rápidas/Padrão:** `gemini-3.1-flash-lite` ou `gemini-3.5-flash` (fallback: `gemini-2.5-flash` / `gemini-2.5-flash-lite`).
- **Modelo principal para raciocínio Complexo:** `gemini-3.1-pro-preview` (fallback: `gemini-2.5-pro`).
- **Método:** Use `Gemini::generativeModel(model: 'model-name')` para iniciar a requisição de geração.
- **Fallback em cascata:** Ao lidar com sobrecarga (503), itere sobre uma lista ordenada de modelos, misturando famílias 3.x e 2.5, como em `app/Jobs/GeminiContentJob.php` (`foreach` sobre `$fallbackModels` chamando `Gemini::generativeModel(...)->withGenerationConfig(...)->generateContent(...)` dentro de um `try/catch (\Throwable $e)`, relançando a última exceção se todos os modelos falharem). `GeminiDocumentService::promptWithFallback` é o equivalente no Laravel AI SDK (`private const FALLBACK_MODELS`, outra arquitetura, sem uso da facade `Gemini`).

```php
use Gemini\Laravel\Facades\Gemini;

$response = Gemini::generativeModel(model: 'gemini-2.5-flash')
    ->generateContent('Your prompt goes here');
```

### 2. Saídas Estruturadas (JSON Schemas)
Quando saídas JSON confiáveis forem necessárias, utilize schemas estruturados. Não confie apenas no texto do prompt; em vez disso, imponha os schemas programaticamente usando `GenerationConfig` e os componentes nativos de definição de schema do SDK.

- **Classes a usar:**
  - `Gemini\Data\GenerationConfig`
  - `Gemini\Data\Schema`
  - `Gemini\Enums\DataType`
  - `Gemini\Enums\ResponseMimeType`
- Configure `responseMimeType` como `ResponseMimeType::APPLICATION_JSON`.
- Construa estruturas aninhadas usando `DataType::OBJECT`, `DataType::ARRAY`, `DataType::STRING`, `DataType::NUMBER`, etc.
- Liste explicitamente os campos obrigatórios sob o parâmetro `required`.

```php
use Gemini\Data\GenerationConfig;
use Gemini\Data\Schema;
use Gemini\Enums\DataType;
use Gemini\Enums\ResponseMimeType;
use Gemini\Laravel\Facades\Gemini;

$generationConfig = new GenerationConfig(
    temperature: 0,
    responseMimeType: ResponseMimeType::APPLICATION_JSON,
    responseSchema: new Schema(
        type: DataType::OBJECT,
        properties: [
            'payment_line' => new Schema(type: DataType::STRING, description: 'Digitized payment line from the bank ticket.'),
            'barcode'      => new Schema(type: DataType::STRING, description: 'Numeric barcode only.'),
            'amount'       => new Schema(type: DataType::NUMBER, description: 'Total value of the ticket.'),
        ],
        required: ['payment_line', 'barcode']
    )
);

$result = Gemini::generativeModel(model: 'gemini-2.5-flash')
    ->withGenerationConfig($generationConfig)
    ->generateContent($promptText);

$data = $result->json();
```

### 3. Entradas Multimodais (Blobs)
Para analisar arquivos locais (PDFs, Imagens, Áudio, Vídeo) sem enviá-los para um storage público, envie-os diretamente como payloads de dados binários codificados em Base64 usando `Blob`.

- **Classes a usar:**
  - `Gemini\Data\Blob`
  - `Gemini\Enums\MimeType`
- **MimeTypes suportados:**
  - Documentos: `MimeType::APPLICATION_PDF`
  - Imagens: `MimeType::IMAGE_JPEG`, `MimeType::IMAGE_PNG`
  - Áudio: `MimeType::AUDIO_MP3`, `MimeType::AUDIO_AAC`, `MimeType::AUDIO_OGG`, `MimeType::AUDIO_FLAC`, `MimeType::AUDIO_AIFF`
  - Vídeo: `MimeType::VIDEO_MP4`, `MimeType::VIDEO_MPEG`, `MimeType::VIDEO_MOV`, `MimeType::VIDEO_WEBM`

```php
use Gemini\Data\Blob;
use Gemini\Enums\MimeType;
use Gemini\Laravel\Facades\Gemini;

$pdfBlob = new Blob(
    mimeType: MimeType::APPLICATION_PDF,
    data: base64_encode(file_get_contents($documentPath))
);

$result = Gemini::generativeModel(model: 'gemini-2.5-flash')
    ->generateContent([
        'Extract information from the attached document.',
        $pdfBlob
    ]);
```

### 4. Tratamento de Exceções e Logging
As chamadas à API Gemini estão sujeitas a latência de rede, rate limits (HTTP 429) ou indisponibilidades temporárias (HTTP 503). Todas as operações devem ser envolvidas com segurança.

- Envolva as chamadas dentro de um bloco `try-catch` capturando `\Throwable`.
- Registre os detalhes no canal específico `gemini` usando `Log::channel('gemini')`.
- Registre a mensagem da exceção, o nome do modelo e o contexto.
- Implemente fallbacks ou tente modelos alternativos em caso de falhas críticas.

```php
use Illuminate\Support\Facades\Log;

try {
    $result = Gemini::generativeModel(model: 'gemini-2.5-flash')
        ->generateContent($promptText);
} catch (\Throwable $e) {
    Log::channel('gemini')->error('Gemini API execution failed.', [
        'message' => $e->getMessage(),
        'trace'   => $e->getTraceAsString(),
    ]);
    
    // Implemente a lógica de fallback ou lance uma exceção tratada
}
```

---

# Restrições
- **Nenhuma Exposição de API Key:** Nunca deixe a API key do Gemini hardcoded. Garanta que a configuração seja carregada por meio de `config('gemini.api_key')` ou variáveis de ambiente padrão.
- **Comentários em Português Brasileiro:** Mantenha a documentação de código, restrições de modelo e comentários inline em **Português Brasileiro** (`pt-BR`), conforme as diretrizes do repositório.

## Idioma da conversa
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão da conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
