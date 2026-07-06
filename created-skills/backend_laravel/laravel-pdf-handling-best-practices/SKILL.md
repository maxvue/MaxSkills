---
name: laravel-pdf-handling-best-practices
description: Use ao gerar, renderizar, extrair texto, validar ou converter PDFs em imagem no Laravel do engeapp. Cobre DomPDF via trait HasDocument (Pdf::loadHTML + isRemoteEnabled), FPDI/TCPDF via App\Classes\PdfEdit (importFile, coordenadas em mm), validação com pdfIsValid()/CouldNotExtractText e conversão em .png por ImageGenerator. Enfileire processamento pesado.
---

# Boas Práticas de Manipulação de PDF no Laravel

## Objetivo
Estabelecer padrões de código eficientes em memória para gerar documentos PDF dinâmicos/estáticos e um fluxo resiliente a erros para extrair texto e converter páginas em imagens, alinhados às implementações reais do engeapp (`barryvdh/laravel-dompdf`, `setasign/fpdi` sobre `tecnickcom/tcpdf`, `spatie/pdf-to-text`, `spatie/pdf-to-image`).

## 1. Geração de PDF

### 1.1 DomPDF (barryvdh/laravel-dompdf) — padrão em uso
Padrão real no engeapp: `App\Traits\HasDocument` e controllers de documentos (ex.: `App\Http\Controllers\Documents\Document\Inmetro`).

* Use a facade `Barryvdh\DomPDF\Facade\Pdf`. O engeapp monta o HTML e chama `Pdf::loadHTML($html)` (também há `loadView`).
* Habilite recursos remotos com `$pdf->setOptions(['isRemoteEnabled' => true])` quando o HTML referencia assets externos.
* Inclua a meta tag UTF-8 para evitar caracteres quebrados.
* Não use CSS Flexbox ou Grid. Use tabelas e controle a paginação com `page-break-*`.
* Prefira imagens em Base64 (data URI) a URLs remotas; para QR Codes, o projeto embute via `getDataUri()`.
* Ao salvar em disco remoto: salve num caminho temporário (`sys_get_temp_dir()`), calcule o hash e envie com `saveToRemoteDisk(...)`, depois `@unlink` do temporário (ver `Inmetro`).

### 1.2 TCPDF + FPDI via `App\Classes\PdfEdit` — padrão em uso
Toda edição/montagem sobre templates estáticos passa por `App\Classes\PdfEdit`, que estende `setasign\Fpdi\Tcpdf\Fpdi`. É a classe usada pelos controllers de diagramas unifilares e formulários (ex.: `DiagramUnifilarGeneralController`, `FormInspectionChespController`).

* Instancie via `PdfEdit` (ou os helpers estáticos como `PdfEdit::getPdfClasses()`); no construtor ele já aplica `setDefaults()` (margens 0, sem auto page break, header/footer desativados).
* Importe templates com `importFile(File|string $file, $pages = [], $options = [])` ou `importFiles($files)`. Templates em string resolvem para o disco `pdf_templates`; discos remotos (não-`local`) são lidos para um `StreamReader::createByString`.
* Posicione tudo por coordenadas X/Y em milímetros e use os wrappers da própria classe (`texto()`, `hLine()`, `wLine()`, `drawRect()`, `rectDash()`, `wire()`, `circuit_breaker()` etc.) em vez das primitivas cruas do TCPDF.
* `setGrid()` desenha uma malha de depuração de coordenadas; mantenha-a comentada em produção (no código real as chamadas `// $this->setGrid();` estão desabilitadas).
* Trate falhas de parsing: `importFile` captura `PdfParserException | RequestException | PdfReaderException` e retorna `false`; `countPages()` retorna `null` em PDF inválido. Verifique o retorno.

### 1.3 mPDF e spatie/laravel-pdf — instalados, sem uso direto (opcional)
`mpdf/mpdf` (^8.1) e `spatie/laravel-pdf` (^2.5) constam no `composer.json`, mas NÃO há geração de PDF direta com eles no código (mPDF aparece só indiretamente como writer do PhpSpreadsheet). Trate esta seção como orientação genérica caso venha a adotá-los; para PDFs novos, prefira os padrões reais 1.1 (DomPDF) e 1.2 (PdfEdit).

* mPDF: instancie com um `tempDir` gravável dentro de `storage/`; registre fontes TrueType via `fontDir`/`fontdata`; cabeçalhos/rodapés com `<htmlpageheader>`/`<htmlpagefooter>`; sem Flexbox/Grid.
* spatie/laravel-pdf (Chromium headless): suporta CSS moderno (Flexbox/Grid) e paginação nativa. Não colida o alias das facades `Spatie\LaravelPdf\Facades\Pdf` e a do DomPDF. Envolva em `try/catch` e faça eager-load das relações antes do Blade.

## 2. Extração e Conversão de PDF

### 2.1 Extração e validação de texto (spatie/pdf-to-text) — padrão em uso
Use `Spatie\PdfToText\Pdf::getText($path)`. O engeapp centraliza a validação no helper `pdfIsValid()` (`app/Helpers/PdfHelper.php`), consumido por jobs como `App\Jobs\Instagram\ThemeExtractionJob`.

* Antes de extrair, valide com `pdfIsValid($path)`: ele checa `file_exists`/`is_readable`/`filesize > 0` e tenta `Pdf::getText`.
* Capture `Spatie\PdfToText\Exceptions\CouldNotExtractText` (e `Exception` genérica) para PDF corrompido/criptografado/sem `pdftotext`.
* Registre falhas em log SEM vazar conteúdo sensível — o padrão é `Log::channel('projects')->error(...)` só com caminho e mensagem.
* Depende do binário `pdftotext` (poppler) no PATH; passe caminho customizado se necessário.

### 2.2 Conversão para imagem (spatie/pdf-to-image) — padrão em uso
A conversão vive no ImageGenerator do Media Library `App\MediaLibrary\ImageGenerators\Pdf` (usado por `App\Models\File\File`).

* Gere sempre `.png`, não `.jpg`, para evitar que o Imagick produza fundo preto em PDFs com fundo transparente.
* Suporte às APIs v2 e v3: detecte a versão com `Composer\InstalledVersions::satisfies(new VersionParser, 'spatie/pdf-to-image', '^3.0')`. v3: `(new Pdf($file))->selectPage($n)->save($img)`. v2: `->setOutputFormat('png')->setPage($n)->saveImage($img)`.
* Exige a extensão `Imagick` instalada (`requirementsAreInstalled()` checa `class_exists(Imagick::class)`).

### 2.3 Processamento em segundo plano e testes
* Para PDFs grandes, despache Jobs enfileirados (`implements ShouldQueue`), como faz `ThemeExtractionJob`, em vez de processar na thread da requisição HTTP.
* Nos testes PestPHP, mocke as chamadas externas ou use pequenos PDFs dummy.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR), independentemente do idioma do corpo desta skill. Comentários de código também em pt-BR.
* **NÃO** use URLs remotas absolutas para imagens no DomPDF; prefira Base64/data URI.
* **NÃO** use CSS Flexbox ou Grid para páginas do DomPDF.
* **NÃO** processe extração/conversão pesada de PDF de forma síncrona na thread HTTP — enfileire.
* **NÃO** assuma `pdftotext` (poppler) ou `Imagick`/Ghostscript instalados sem verificar.
* **NÃO** registre dados sensíveis do documento em exceções de extração.
