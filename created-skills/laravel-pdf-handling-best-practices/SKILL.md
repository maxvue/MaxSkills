---
name: laravel-pdf-handling-best-practices
description: Use when creating, configuring, rendering, extracting text, converting, or debugging PDF documents. Triggers on PDF generation using DomPDF, mPDF, TCPDF/FPDI, Spatie PDF, spatie/pdf-to-text, and spatie/pdf-to-image.
---

# Laravel PDF Handling Best Practices

## Goal
Establish robust guidelines, coding standards, and memory-efficient practices for generating dynamic and static PDF documents, as well as a unified, high-performance, and error-resilient workflow for extracting text and converting pages to images from PDF files in the Laravel framework.

## Instructions

### 1. PDF Generation

### 1.1 DomPDF (barryvdh/laravel-dompdf)
* Always use the `Barryvdh\DomPDF\Facade\Pdf` facade for PDF operations (`loadView`, `loadHTML`).
* Include UTF-8 meta tag to prevent broken characters.
* Do not use CSS Flexbox or Grid. Use tables and control pagination with `page-break-*` properties.
* Declare custom fonts using `@import` or `@font-face` and set `isRemoteEnabled` to `true`. Base64 encode images instead of using remote URLs.

### 1.2 mPDF (mPDF)
* Instantiate with a dedicated, writable temporary directory inside Laravel's storage folder.
* Register custom TrueType fonts by configuring `fontDir` and `fontdata`.
* Use proprietary HTML tags (`<htmlpageheader>`, `<htmlpagefooter>`) for dynamic headers and footers. Do not use Flexbox/Grid.

### 1.3 TCPDF and FPDI
* Use specific custom classes (e.g., `\App\Classes\PdfEdit()`) and `$pdf->importFile()` for static templates.
* Standardize placement using X and Y coordinates (in millimeters). Do not use native TCPDF positioning functions if wrappers exist.
* Remove or disable `$pdf->setGrid()` calls in production.

### 1.4 Spatie Laravel PDF
* Do not import `SpatiePdf` and `DomPdf` facades using the same alias.
* Headless Chromium supports modern CSS (Flexbox, Grid) and native pagination controls.
* Wrap PDF generation in `try/catch` blocks.
* Do NOT perform heavy queries inside Blade; eager-load relationships.

### 2. PDF Extraction & Conversion

### 2.1 Extracting Text (spatie/pdf-to-text)
* Use `Spatie\PdfToText\Pdf::getText($path)`. Wrap in try-catch to handle decryption, corruption, or binary errors.
* Provide custom binary paths if `pdftotext` is not in the default PATH.

### 2.2 Converting to Images (spatie/pdf-to-image)
* Ensure compatibility with v2/v3 APIs.
* Convert to `.png` to prevent Imagick from generating black backgrounds on transparent pages.

### 2.3 Background Processing & Testing
* For large PDFs, always dispatch queued Laravel Jobs (using `ShouldQueue`) instead of processing directly inside HTTP Request threads.
* Mock external calls or use small dummy PDF assets for PestPHP tests.

## Constraints
* **DO NOT** use absolute remote URLs for images in DomPDF. Always use Base64 encoding.
* **DO NOT** use CSS Flexbox or Grid for DomPDF/mPDF page structures.
* **DO NOT** perform synchronous PDF processing (conversion/heavy text extraction) directly inside an HTTP Request thread. Queue it.
* **DO NOT** assume `pdftotext` or Ghostscript is installed without proper checks.
* **DO NOT** log sensitive document data during extraction exceptions.
