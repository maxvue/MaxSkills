---
name: laravel-docx-generation-phpword
description: Use when generating, formatting, or exporting Word documents (.docx) using PhpWord, managing templates, injecting variables, or configuring headers/footers in Laravel.
---

# laravel-docx-generation-phpword

## Goal
Provide solid guidelines and structured patterns for creating, reading, editing, and exporting Word documents (`.docx`) using the `phpoffice/phpword` library within the Laravel/Engeapp ecosystem. Ensure consistent document styling, safe template variable replacement, dynamic image embedding, and efficient memory management to prevent memory leaks and corrupted XML files.

---

## Instructions

### 1. Basic Setup & Bootstrapping
- Install the package using Composer: `composer require phpoffice/phpword`.
- Always wrap PHPWord operations in `try-catch` blocks and use Laravel's standard logging (`Log::error`) for processing failures, as physical file access and ZipArchive operations can fail due to file permissions or corrupt templates.
- Define a dedicated temporary directory in `config/filesystems.php` or use `storage_path('app/temp')` for PHPWord's working files to avoid permission issues in serverless or containerized environments.

### 2. Using `TemplateProcessor` Safely
- For pre-styled corporate templates, always prefer `PhpOffice\PhpWord\TemplateProcessor`.
- **XML Sanitization:** Raw input containing HTML-sensitive characters (`&`, `<`, `>`, `"`) can corrupt the underlying `document.xml` file. Always escape values using `htmlspecialchars($value, ENT_QUOTES, 'UTF-8')` before injecting them:
  ```php
  $templateProcessor->setValue('client_name', htmlspecialchars($clientName, ENT_QUOTES, 'UTF-8'));
  ```
- **Line Breaks:** Standard newline characters (`\n`) are ignored in Word. Replace them with PHPWord's line break element or use the XML tag `<w:br/>` via `setValue`:
  ```php
  $formattedText = str_replace("\n", '</w:t><w:br/><w:t>', htmlspecialchars($text, ENT_QUOTES, 'UTF-8'));
  $templateProcessor->setValue('description', $formattedText);
  ```
- **Cloning Rows & Blocks:** Use `cloneRow` and `cloneBlock` for repeating tables or dynamic sections (e.g., repeating item lists or dynamic attachments).
  ```php
  $templateProcessor->cloneRow('item_id', count($items));
  foreach ($items as $index => $item) {
      $rowNum = $index + 1;
      $templateProcessor->setValue("item_id#{$rowNum}", $item->id);
      $templateProcessor->setValue("item_name#{$rowNum}", htmlspecialchars($item->name, ENT_QUOTES, 'UTF-8'));
  }
  ```

### 3. Dynamic Image Insertion
- When injecting images into template placeholders (e.g., `${image_placeholder}`), use `setImageValue` with correct proportions to prevent squishing or bloating:
  ```php
  $templateProcessor->setImageValue('image_placeholder', [
      'path' => $imagePath,
      'width' => 300,
      'height' => 200,
      'ratio' => false // Set to true to preserve aspect ratio based on width
  ]);
  ```
- Always check if the image file exists (`file_exists($imagePath)`) before trying to inject it. If it does not exist, inject a placeholder image or a descriptive text fallback to prevent exceptions.

### 4. Dynamic Table Styling and Formatting (PHPWord Native)
- When generating documents from scratch, define reusable table styles using `PhpOffice\PhpWord\SimpleType\TblWidth`.
- Use a dedicated configuration file or reference `resources/table_styles.json` for corporate themes (borders, alternating row backgrounds, and specific fonts).
- Use `gridSpan` to merge cells horizontally and `vMerge` to merge cells vertically.
  ```php
  $table->addCell(2000, ['vMerge' => 'restart'])->addText('Merged Category');
  $table->addCell(4000, ['gridSpan' => 2])->addText('Spanned Columns');
  ```

### 5. Memory Management & File Response
- Generating large documents with multiple high-resolution images can easily exceed memory limits. Ensure you optimize images before embedding (e.g., using Spatie Image or Intervention Image) and call PHP's garbage collector if batch-processing documents.
- Always output the generated file using Laravel's binary response, clean up local temporary files after the response completes or via queue jobs:
  ```php
  $tempFile = tempnam(sys_get_temp_dir(), 'docx');
  $templateProcessor->saveAs($tempFile);

  return response()->download($tempFile, 'report.docx')->deleteFileAfterSend(true);
  ```

---

## Constraints
- **NO Direct Controller Output:** Never perform heavy document generation synchronously inside controllers. If document generation takes more than 2 seconds (e.g., generating high-photo lauds), dispatch a Queue Job and notify the user via WebSockets/Reverb.
- **NO Unescaped Raw HTML:** Do not pass raw HTML strings directly into `setValue()`. The XML parser will fail and MS Word will complain that the file is corrupt. Use specialized HTML parsers (like `Html::addHtml`) or escape/strip tags first.
- **NO Hardcoded Paths:** Do not hardcode filesystem paths for templates or output files. Always use `storage_path()` or `resource_path()`.
- **NO Resource Leaks:** Never leave temporary files generated during the process on the server disk. Use `deleteFileAfterSend(true)` or register a cleanup hook.

---

## Examples

### Complete Laravel Controller Pattern
```php
namespace App\Http\Controllers;

use App\Models\TechnicalLaud;
use Illuminate\Http\Response;
use PhpOffice\PhpWord\TemplateProcessor;
use PhpOffice\PhpWord\Exception\Exception as PhpWordException;
use Illuminate\Support\Facades\Log;
use Symfony\Component\HttpFoundation\BinaryFileResponse;

class LaudExportController extends Controller
{
    public function export(TechnicalLaud $laud): BinaryFileResponse
    {
        $templatePath = resource_path('templates/laud_template.docx');
        
        if (!file_exists($templatePath)) {
            abort(404, 'Laud template file not found.');
        }

        try {
            $templateProcessor = new TemplateProcessor($templatePath);

            // 1. Simple Values Escaped
            $templateProcessor->setValue('laud_number', htmlspecialchars($laud->number, ENT_QUOTES, 'UTF-8'));
            $templateProcessor->setValue('client_name', htmlspecialchars($laud->client->name, ENT_QUOTES, 'UTF-8'));

            // 2. Multiline Text with Word Line Breaks
            $formattedDescription = str_replace(
                "\n", 
                '</w:t><w:br/><w:t>', 
                htmlspecialchars($laud->description, ENT_QUOTES, 'UTF-8')
            );
            $templateProcessor->setValue('description', $formattedDescription);

            // 3. Dynamic Image Injection
            if ($laud->cover_image && file_exists(storage_path("app/public/{$laud->cover_image}"))) {
                $templateProcessor->setImageValue('cover_photo', [
                    'path' => storage_path("app/public/{$laud->cover_image}"),
                    'width' => 450,
                    'height' => 300,
                    'ratio' => true
                ]);
            } else {
                $templateProcessor->setValue('cover_photo', 'No photo attached');
            }

            // 4. Repeating Rows (Measurements)
            $measurements = $laud->measurements;
            $templateProcessor->cloneRow('m_id', count($measurements));
            foreach ($measurements as $index => $measurement) {
                $row = $index + 1;
                $templateProcessor->setValue("m_id#{$row}", $measurement->id);
                $templateProcessor->setValue("m_voltage#{$row}", number_format($measurement->voltage, 2, ',', '.'));
                $templateProcessor->setValue("m_current#{$row}", number_format($measurement->current, 2, ',', '.'));
            }

            // Save to temp file
            $tempFile = tempnam(sys_get_temp_dir(), 'laud_');
            $templateProcessor->saveAs($tempFile);

            return response()->download($tempFile, "Laud_{$laud->number}.docx")
                ->deleteFileAfterSend(true);

        } catch (PhpWordException $e) {
            Log::error('Failed to generate Word document', [
                'laud_id' => $laud->id,
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            
            abort(500, 'Error generating document. Please contact support.');
        }
    }
}
```
