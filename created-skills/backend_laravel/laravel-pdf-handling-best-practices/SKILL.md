---
name: laravel-pdf-handling-best-practices
description: Use when creating, configuring, rendering, extracting text, converting, or debugging PDF documents. Triggers on PDF generation using DomPDF, mPDF, TCPDF/FPDI, Spatie PDF, spatie/pdf-to-text, and spatie/pdf-to-image.
---

# Boas Práticas de Manipulação de PDF no Laravel

## Objetivo
Estabelecer diretrizes robustas, padrões de código e práticas eficientes em memória para gerar documentos PDF dinâmicos e estáticos, bem como um fluxo de trabalho unificado, de alta performance e resiliente a erros para extrair texto e converter páginas em imagens a partir de arquivos PDF no framework Laravel.

## Instruções

### 1. Geração de PDF

### 1.1 DomPDF (barryvdh/laravel-dompdf)
* Sempre use a facade `Barryvdh\DomPDF\Facade\Pdf` para operações de PDF (`loadView`, `loadHTML`).
* Inclua a meta tag UTF-8 para evitar caracteres quebrados.
* Não use CSS Flexbox ou Grid. Use tabelas e controle a paginação com as propriedades `page-break-*`.
* Declare fontes customizadas usando `@import` ou `@font-face` e defina `isRemoteEnabled` como `true`. Codifique imagens em Base64 em vez de usar URLs remotas.

### 1.2 mPDF (mPDF)
* Instancie com um diretório temporário dedicado e gravável dentro da pasta de storage do Laravel.
* Registre fontes TrueType customizadas configurando `fontDir` e `fontdata`.
* Use tags HTML proprietárias (`<htmlpageheader>`, `<htmlpagefooter>`) para cabeçalhos e rodapés dinâmicos. Não use Flexbox/Grid.

### 1.3 TCPDF e FPDI
* Use classes customizadas específicas (ex: `\App\Classes\PdfEdit()`) e `$pdf->importFile()` para templates estáticos.
* Padronize o posicionamento usando coordenadas X e Y (em milímetros). Não use funções nativas de posicionamento do TCPDF se existirem wrappers.
* Remova ou desabilite as chamadas `$pdf->setGrid()` em produção.

### 1.4 Spatie Laravel PDF
* Não importe as facades `SpatiePdf` e `DomPdf` usando o mesmo alias.
* O Chromium headless suporta CSS moderno (Flexbox, Grid) e controles nativos de paginação.
* Envolva a geração de PDF em blocos `try/catch`.
* NÃO execute consultas pesadas dentro do Blade; faça eager-load dos relacionamentos.

### 2. Extração e Conversão de PDF

### 2.1 Extração de Texto (spatie/pdf-to-text)
* Use `Spatie\PdfToText\Pdf::getText($path)`. Envolva em try-catch para tratar erros de descriptografia, corrupção ou binário.
* Forneça caminhos de binário customizados se o `pdftotext` não estiver no PATH padrão.

### 2.2 Conversão para Imagens (spatie/pdf-to-image)
* Garanta compatibilidade com as APIs v2/v3.
* Converta para `.png` para evitar que o Imagick gere fundos pretos em páginas transparentes.

### 2.3 Processamento em Segundo Plano e Testes
* Para PDFs grandes, sempre despache Jobs enfileirados do Laravel (usando `ShouldQueue`) em vez de processar diretamente nas threads de requisição HTTP.
* Faça o mock de chamadas externas ou use pequenos arquivos PDF dummy para os testes PestPHP.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **NÃO** use URLs remotas absolutas para imagens no DomPDF. Sempre use codificação Base64.
* **NÃO** use CSS Flexbox ou Grid para estruturas de página do DomPDF/mPDF.
* **NÃO** execute processamento de PDF síncrono (conversão/extração pesada de texto) diretamente dentro de uma thread de requisição HTTP. Enfileire-o.
* **NÃO** assuma que o `pdftotext` ou o Ghostscript estão instalados sem as devidas verificações.
* **NÃO** registre em log dados sensíveis do documento durante exceções de extração.
