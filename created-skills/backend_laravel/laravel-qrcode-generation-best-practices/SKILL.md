---
name: laravel-qrcode-generation-best-practices
description: Use when generating, customizing, rendering, or testing QR Codes in the Laravel backend using endroid/qr-code. Triggers on QR Code generation, SVG/PNG outputs, base64 encoding for APIs/Blade, and adding logos or labels to QR Codes.
---

# Boas Práticas de Geração de QR Code no Laravel

## Objetivo
Estabelecer padrões e diretrizes limpos para gerar, customizar, renderizar e testar QR Codes usando o pacote `endroid/qr-code` (v6.0) dentro do backend Laravel do Engeapp.

## Instruções

### 1. Geração Básica usando o Builder
Sempre use o construtor `Builder` com argumentos nomeados para construir seu QR Code. Ele lida internamente com a instanciação dos componentes QR Code, Logo e Label.

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

### 2. Opções de Saída e Renderização
Renderize o QR Code gerado com base nos requisitos de entrega (resposta de API, e-mail ou view Blade):

* **Data URI em Base64** (Melhor para incorporar diretamente em tags `<img>` do HTML ou retornar em payloads de API):
  ```php
  // Obtém a URI de dados em Base64
  $dataUri = $result->getDataUri(); // Retorna: "data:image/png;base64,..."
  ```
* **String Binária Crua e Mime Type** (Melhor para downloads diretos de arquivo ou streaming de respostas HTTP):
  ```php
  // Obtém a string binária e o MimeType
  $binary = $result->getString();
  $mimeType = $result->getMimeType(); // Retorna: "image/png"
  ```
* **Persistência em Arquivo** (Melhor para armazenamento em disco ou cache de arquivos):
  ```php
  // Salva o arquivo de imagem gerado no storage
  $result->saveToFile(storage_path('app/public/qrcodes/pix-payment.png'));
  ```

### 3. Customizações de Logo e Label
Ao adicionar elementos de branding ou labels aos QR Codes, siga estes padrões:

* **Posicionamento do Logo**: Você deve definir `ErrorCorrectionLevel::High` para garantir que o QR code permaneça legível quando coberto pelo logo.
* **Punchout**: Opcionalmente, habilite `logoPunchoutBackground: true` para limpar os módulos por baixo do logo.
* **Rotulagem**: Configure o alinhamento e as fontes com cuidado.

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

### 4. Cache e Performance
A geração de QR Code é intensiva em CPU. Para dados estáticos (ex: links de pagamento estáticos, links de perfil de cliente), cacheie a representação Base64 ou armazene os arquivos gerados diretamente.

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

### 5. Escrevendo Testes com Pest PHP
Garanta que qualquer serviço ou controller que gere QR Codes esteja devidamente coberto por testes de integração/feature. Evite testar a lógica de terceiros; em vez disso, verifique a estrutura, os formatos e os pontos de integração.

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

## Restrições
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
* NÃO use a factory estática legada `Builder::create()` da v5 (removida na v6). Sempre construa o QR Code através do construtor `Builder` com argumentos nomeados (`new Builder(writer: ..., data: ..., ...)`) e chame `->build()`.
* NÃO use níveis de correção de erro baixos ou médios (`ErrorCorrectionLevel::Low`, `ErrorCorrectionLevel::Medium`) ao incorporar um logo no QR code. Você deve usar `ErrorCorrectionLevel::High`.
* NÃO faça geração de QR Code dinamicamente a cada requisição sem cache, se o conteúdo for estático.
* NÃO faça hardcode de caminhos de arquivo; sempre resolva os diretórios de caminho usando funções helper do Laravel (ex: `storage_path()`, `public_path()`).
* NÃO escreva casos de teste no estilo PHPUnit. Siga as convenções de teste Pest PHP do projeto, escrevendo asserções com a API funcional `expect()`.
