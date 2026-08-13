---
name: laravel-pdf-handling-best-practices
description: "Use when generating, rendering, extracting text, validating, or converting PDFs to images in Engeapp. Covers DomPDF via HasDocument trait, FPDI/TCPDF via PdfEdit, pdfIsValid() validation, and File::createThumbnailFromPdf()."
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
* Ao salvar em disco remoto: salve num caminho temporário (`sys_get_temp_dir()`), calcule o hash e envie com `saveToRemoteDisk(...)`, depois `@unlink` do temporário. O padrão vive em `App\Traits\HasDocument::createInmetro()` (não no controller `Inmetro`, que apenas chama `self::createInmetro(...)`).

### 1.2 TCPDF + FPDI via `App\Classes\PdfEdit` — padrão em uso
Toda edição/montagem sobre templates estáticos passa por `App\Classes\PdfEdit`, que estende `setasign\Fpdi\Tcpdf\Fpdi`. É a classe usada pelos controllers de diagramas unifilares e formulários (ex.: `DiagramUnifilarGeneralController`, `FormInspectionChespController`).

* Instancie via `new PdfEdit`; no construtor ele já aplica `setDefaults()` (margens 0, sem auto page break, header/footer desativados). Alguns fluxos obtêm um conjunto de instâncias prontas via `self::getPdfClasses()` — método estático da trait `App\Traits\HasDocument` (não da própria `PdfEdit`) que devolve um objeto com instâncias de `PdfEdit` (`all`, `inverters`, `modules`), usado nos controllers de documentos (ex.: `Inmetro`, `Datasheet`).
* Importe templates com `importFile(File|string $file, $pages = [], $options = [])` ou `importFiles($files)`. Templates em string resolvem para o disco `pdf_templates`; discos remotos (não-`local`) são lidos para um `StreamReader::createByString`.
* Posicione tudo por coordenadas X/Y em milímetros e use os wrappers da própria classe (`texto()`, `hLine()`, `wLine()`, `drawRect()`, `rectDash()`, `wire()`, `circuit_breaker()` etc.) em vez das primitivas cruas do TCPDF.
* `setGrid()` desenha uma malha de depuração de coordenadas. No código real o uso é misto: alguns controllers deixam a chamada comentada (`// $pdf->setGrid();`, ex.: `FormInspectionEquatorialController`), outros a mantêm ATIVA (ex.: `MemorialAmazonasController`). Não assuma que está sempre desabilitada — verifique e remova/comente antes de publicar layouts finais.
* Trate falhas de parsing: `importFile` captura `PdfParserException | RequestException | PdfReaderException` e retorna `false`; `countPages()` retorna `null` em PDF inválido. Verifique o retorno.

### 1.3 mPDF e spatie/laravel-pdf — instalados, sem uso direto
`mpdf/mpdf` (^8.1) e `spatie/laravel-pdf` (^2.5) constam no `composer.json` mas não têm uso direto (mPDF aparece só como writer do PhpSpreadsheet em `FormRequestEnergisaController`); para PDF novo use 1.1 (DomPDF) ou 1.2 (PdfEdit). Se algum dia adotar `spatie/laravel-pdf`, atenção: o facade do DomPDF já é usado em 3 arquivos do projeto, então importar `Spatie\LaravelPdf\Facades\Pdf` sem alias criaria colisão real de nome.

## 2. Extração e Conversão de PDF

### 2.1 Extração e validação de texto (spatie/pdf-to-text) — padrão em uso
Use `Spatie\PdfToText\Pdf::getText($path)`. O engeapp centraliza a validação no helper `pdfIsValid()` (`app/Helpers/PdfHelper.php`), consumido por jobs como `App\Jobs\Instagram\ThemeExtractionJob`.

* Antes de extrair, valide com `pdfIsValid($path)`: ele checa `file_exists`/`is_readable`/`filesize > 0` e tenta `Pdf::getText`.
* Capture `Spatie\PdfToText\Exceptions\CouldNotExtractText` (e `Exception` genérica) para PDF corrompido/criptografado/sem `pdftotext`.
* Registre falhas em log SEM vazar conteúdo sensível — o padrão é `Log::channel('projects')->error(...)` só com caminho e mensagem.
* Depende do binário `pdftotext` (poppler) no PATH; passe caminho customizado se necessário.

### 2.2 Conversão para imagem (spatie/pdf-to-image) — padrão em uso
Existem dois caminhos distintos e não relacionados de conversão PDF→imagem no engeapp:
1. `App\MediaLibrary\ImageGenerators\Pdf`, registrado em `config/media-library.php`, usado pelo pipeline de conversões do Spatie Media Library.
2. `App\Models\File\File::createThumbnailFromPdf()`, que instancia `Spatie\PdfToImage\Pdf` diretamente e é o padrão real de thumbnail em uso: `new Pdf($this->path)`, depois `resolution(400)->selectPage(1)->format(OutputFormat::Png)->save($temp_path)`, seguido de `resizeImage()` e `@unlink()` do temporário. Não depende do ImageGenerator do Media Library.

* Gere sempre `.png`, não `.jpg`, para evitar que o Imagick produza fundo preto em PDFs com fundo transparente.
* O engeapp usa `spatie/pdf-to-image` `^3.3` (3.4.0 instalado). A API v3 é a única válida: `resolution()`, `selectPage()`, `format(OutputFormat::Png)`, `save()`. Os métodos da v2 (`setResolution`, `setPage`, `setOutputFormat`, `saveImage`) **não existem mais** e lançam `Error: Call to undefined method` — não `Exception`.
* `App\MediaLibrary\ImageGenerators\Pdf` mantém um ramo v2 atrás de `usesPdfToImageV3()` (checagem via `InstalledVersions::satisfies`). Esse ramo é código morto na versão atual; não o tome como referência de API corrente.
* Exige a extensão `Imagick` instalada (`requirementsAreInstalled()` checa `class_exists(Imagick::class)`).

### 2.2.1 Redimensionamento (intervention/image v4)
`resizeImage()` (em `app/Helpers/FilesHelpers.php`) é o helper usado logo após a conversão PDF→imagem e também no thumbnail de imagens.

* O engeapp usa `intervention/image` `^4.2` (4.2.1 instalado). Use `ImageManager::decodePath($path)` — `read()` foi **removido** na v4.
* Os encoders por formato (`toPng()`, `toJpeg()`, `toGif()`, `toTiff()`, `toWebp()`) também saíram. Para gravar em disco, `save($path)` já resolve o encoder pela extensão do destino; para obter os bytes (ex.: base64), use `encodeUsingFileExtension('jpg', quality: 50)`.

### 2.2.2 Erros de API quebrada são `Error`, não `Exception`
Ao chamar um método removido por upgrade de biblioteca, o PHP lança `Error`. Um `catch (Exception $e)` **não** o intercepta.

* Em código acessório disparado por hooks de model (`booted()` do `File` chama `setThumbnail()`/`checkPageNumbersPdf()`), capture `Throwable` — um `Error` ali derruba com 500 a criação inteira do registro, e não apenas a miniatura.
* Cuidado com o efeito de mascaramento: com o `catch` alargado, uma falha seguinte passa a ser engolida silenciosamente. Testes desse caminho devem assertar o **efeito** (o arquivo saiu no disco, com a dimensão esperada), não apenas a ausência de exceção.

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
