---
name: laravel-gemini-php-sdk-best-practices
description: Use when interacting directly with the Gemini API using the google-gemini-php/laravel SDK, configuring GenerationConfig, utilizing structured outputs (JSON Schemas), handling multimodal inputs (Images, Audio, PDF) using Blob, or managing model calls and exceptions in Laravel.
---

# Goal
Ensure robust, standardized, and high-performance integrations with the Gemini API using the `google-gemini-php/laravel` SDK within the Engeapp backend. This covers structuring queries using the Gemini Facade, defining rigid JSON outputs with native schema helpers, safely handling multimodal inputs via Base64 Blobs, and executing reliable error handling.

---

# Instructions

### 1. Model Selection & Facade Usage
Always resolve the Gemini model using the `Gemini` facade to manage model calls.
- **Primary Model for Fast/Standard operations:** `gemini-2.5-flash` or `gemini-2.5-flash-lite`.
- **Primary Model for Complex reasoning:** `gemini-2.5-pro` or similar advanced models.
- **Method:** Use `Gemini::generativeModel(model: 'model-name')` to initiate the generation request.

```php
use Gemini\Laravel\Facades\Gemini;

$response = Gemini::generativeModel(model: 'gemini-2.5-flash')
    ->generateContent('Your prompt goes here');
```

### 2. Structured Outputs (JSON Schemas)
When reliable JSON outputs are required, leverage structured schemas. Do not rely on prompt phrasing alone; instead, enforce schemas programmatically using `GenerationConfig` and the SDK's native schema definition components.

- **Classes to use:**
  - `Gemini\Data\GenerationConfig`
  - `Gemini\Data\Schema`
  - `Gemini\Enums\DataType`
  - `Gemini\Enums\ResponseMimeType`
- Configure `responseMimeType` as `ResponseMimeType::APPLICATION_JSON`.
- Build nested structures using `DataType::OBJECT`, `DataType::ARRAY`, `DataType::STRING`, `DataType::NUMBER`, etc.
- Explicitly list required fields under the `required` parameter.

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

$data = json_decode($result->text(), true);
```

### 3. Multimodal Inputs (Blobs)
To analyze local files (PDFs, Images, Audio, Video) without uploading them to public storage, send them directly as Base64-encoded binary data payloads using `Blob`.

- **Classes to use:**
  - `Gemini\Data\Blob`
  - `Gemini\Enums\MimeType`
- **Supported MimeTypes:**
  - Documents: `MimeType::APPLICATION_PDF`
  - Images: `MimeType::IMAGE_JPEG`, `MimeType::IMAGE_PNG`
  - Audio: `MimeType::AUDIO_MP3`, `MimeType::AUDIO_AAC`, `MimeType::AUDIO_OGG`, `MimeType::AUDIO_FLAC`, `MimeType::AUDIO_AIFF`
  - Video: `MimeType::VIDEO_MP4`, `MimeType::VIDEO_MPEG`, `MimeType::VIDEO_MOV`, `MimeType::VIDEO_WEBM`

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

### 4. Exception Handling & Logging
Gemini API calls are susceptible to network latency, rate limits (HTTP 429), or temporary outages (HTTP 503). All operations must be safely wrapped.

- Wrap calls inside a `try-catch` block catching `\Throwable`.
- Log details inside the specific `gemini` channel using `Log::channel('gemini')`.
- Log the exception message, model name, and context.
- Implement fallbacks or try alternative models in case of critical failures.

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
    
    // Implement fallback logic or throw a managed exception
}
```

---

# Constraints
- **No API Key Exposure:** Never hardcode the Gemini API key. Ensure configuration is loaded through `config('gemini.api_key')` or standard environment variables.
- **Memory Efficiency:** Avoid storing massive files in memory. Ensure Base64 payloads are processed and garbage-collected efficiently.
- **Required Fields in Schema:** When defining structured outputs, always pass the array of required keys to ensure the schema validator guarantees their presence in the final output.
- **Brazilian Portuguese Comments:** Keep code documentation, model constraints, and inline comments in **Brazilian Portuguese** (`pt-BR`) as per repository guidelines.
