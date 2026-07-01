---
name: laravel-qrcode-generation-best-practices
description: Use when generating, customizing, rendering, or testing QR Codes in the Laravel backend using endroid/qr-code. Triggers on QR Code generation, SVG/PNG outputs, base64 encoding for APIs/Blade, and adding logos or labels to QR Codes.
---

# Laravel QR Code Generation Best Practices

## Goal
Establish clean standards and guidelines for generating, customizing, rendering, and testing QR Codes using the `endroid/qr-code` package (v6.0) inside the Engeapp Laravel backend.

## Instructions

### 1. Basic Generation using the Builder
Always use the `Builder` constructor with named arguments to construct your QR Code. It internally handles instantiation of the QR Code, Logo, and Label components.

```php
use Endroid\QrCode\Builder\Builder;
use Endroid\QrCode\Encoding\Encoding;
use Endroid\QrCode\ErrorCorrectionLevel;
use Endroid\QrCode\Writer\PngWriter;

// Criação básica de QR Code no formato PNG
$result = (new Builder(
    writer: new PngWriter(),
    data: 'https://engeapp.com.br',
    encoding: new Encoding('UTF-8'),
    errorCorrectionLevel: ErrorCorrectionLevel::High,
    size: 300,
    margin: 10,
))->build();
```

### 2. Output & Rendering Options
Render the generated QR Code based on the delivery requirements (API response, email, or Blade view):

* **Base64 Data URI** (Best for embedding directly into HTML `<img>` tags or returning in API payloads):
  ```php
  // Obtém a URI de dados em Base64
  $dataUri = $result->getDataUri(); // Retorna: "data:image/png;base64,..."
  ```
* **Raw Binary String & Mime Type** (Best for direct file downloads or streaming HTTP responses):
  ```php
  // Obtém a string binária e o MimeType
  $binary = $result->getString();
  $mimeType = $result->getMimeType(); // Retorna: "image/png"
  ```
* **File Persistence** (Best for disk storage or caching files):
  ```php
  // Salva o arquivo de imagem gerado no storage
  $result->saveToFile(storage_path('app/public/qrcodes/pix-payment.png'));
  ```

### 3. Logo and Label Customizations
When adding branding elements or labels to QR Codes, follow these standards:

* **Logo Placement**: You must set `ErrorCorrectionLevel::High` to ensure the QR code remains readable when covered by the logo.
* **Punchout**: Optionally enable `logoPunchoutBackground: true` to clear the modules underneath the logo.
* **Labeling**: Configure alignment and fonts carefully.

```php
use Endroid\QrCode\Builder\Builder;
use Endroid\QrCode\Encoding\Encoding;
use Endroid\QrCode\ErrorCorrectionLevel;
use Endroid\QrCode\Label\Font\OpenSans;
use Endroid\QrCode\Label\LabelAlignment;
use Endroid\QrCode\Writer\PngWriter;

$result = (new Builder(
    writer: new PngWriter(),
    data: 'https://engeapp.com.br/pay/pix-123',
    encoding: new Encoding('UTF-8'),
    errorCorrectionLevel: ErrorCorrectionLevel::High, // Essencial quando há logo
    size: 300,
    margin: 15,
    logoPath: public_path('images/logo-engeapp.png'),
    logoResizeToWidth: 60,
    logoPunchoutBackground: true,
    labelText: 'Escaneie para pagar',
    labelFont: new OpenSans(12),
    labelAlignment: LabelAlignment::Center,
))->build();
```

### 4. Caching & Performance
QR Code generation is CPU intensive. For static data (e.g. static payment links, customer profile links), cache the Base64 representation or store the generated files directly.

```php
use Illuminate\Support\Facades\Cache;

// Faz cache do QR Code em Base64 por 24 horas
$qrCodeBase64 = Cache::remember("qrcode:payment:{$paymentId}", now()->addDay(), function () use ($payload) {
    return (new Builder(
        writer: new PngWriter(),
        data: $payload,
        size: 300,
    ))->build()->getDataUri();
});
```

### 5. Writing Tests with Pest PHP
Ensure that any service or controller generating QR Codes is properly covered by integration/feature tests. Avoid testing third-party logic; instead, assert the structure, formats, and integration points.

```php
use Endroid\QrCode\Builder\Builder;
use Endroid\QrCode\Writer\PngWriter;
use Endroid\QrCode\Writer\Result\ResultInterface;

test('deve gerar um qr code pix valido no formato png', function () {
    // Executa a lógica de geração
    $result = (new Builder(
        writer: new PngWriter(),
        data: '00020101021226870014br.gov.bcb.pix...',
        size: 200,
    ))->build();

    // Asserções
    expect($result)->toBeInstanceOf(ResultInterface::class);
    expect($result->getMimeType())->toBe('image/png');
    expect($result->getString())->not->toBeEmpty();
    expect($result->getDataUri())->toStartWith('data:image/png;base64,');
});
```

## Constraints
* Do NOT use the legacy v5 `Builder::create()` static factory (removed in v6). Always construct the QR Code via the `Builder` constructor with named arguments (`new Builder(writer: ..., data: ..., ...)`) and call `->build()`.
* Do NOT use low or medium error correction levels (`ErrorCorrectionLevel::Low`, `ErrorCorrectionLevel::Medium`) when embedding a logo in the QR code. You must use `ErrorCorrectionLevel::High`.
* Do NOT perform QR Code generation dynamically on every request without caching if the content is static.
* Do NOT hardcode file paths; always resolve path directories using Laravel helper functions (e.g. `storage_path()`, `public_path()`).
* Do NOT write PHPUnit-style test cases. Follow the project's Pest PHP testing conventions, writing assertions with the functional `expect()` API.
