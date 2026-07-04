---
name: laravel-docx-generation-phpword
description: Use when generating, formatting, or exporting Word documents (.docx) using PhpWord, managing templates, injecting variables, or configuring headers/footers in Laravel.
---

# laravel-docx-generation-phpword

## Objetivo
Fornecer diretrizes sólidas e padrões estruturados para criar, ler, editar e exportar documentos Word (`.docx`) usando a biblioteca `phpoffice/phpword` dentro do ecossistema Laravel/Engeapp. Garantir estilização consistente de documentos, substituição segura de variáveis de template, incorporação dinâmica de imagens e gerenciamento eficiente de memória para prevenir vazamentos de memória e arquivos XML corrompidos.

---

## Instruções

### 1. Configuração Básica e Bootstrapping
- Instale o pacote usando o Composer: `composer require phpoffice/phpword`.
- Sempre envolva as operações do PHPWord em blocos `try-catch` e use o logging padrão do Laravel (`Log::error`) para falhas de processamento, pois o acesso físico a arquivos e as operações do ZipArchive podem falhar devido a permissões de arquivo ou templates corrompidos.
- Defina um diretório temporário dedicado em `config/filesystems.php` ou use `storage_path('app/temp')` para os arquivos de trabalho do PHPWord, a fim de evitar problemas de permissão em ambientes serverless ou em contêineres.

### 2. Usando `TemplateProcessor` com Segurança
- Para templates corporativos pré-estilizados, sempre prefira `PhpOffice\PhpWord\TemplateProcessor`.
- **Sanitização de XML:** Input cru contendo caracteres sensíveis ao HTML (`&`, `<`, `>`, `"`) pode corromper o arquivo `document.xml` subjacente. Sempre escape os valores usando `htmlspecialchars($value, ENT_QUOTES, 'UTF-8')` antes de injetá-los:
  ```php
  $templateProcessor->setValue('client_name', htmlspecialchars($clientName, ENT_QUOTES, 'UTF-8'));
  ```
- **Quebras de Linha:** Caracteres de nova linha padrão (`\n`) são ignorados no Word. Substitua-os pelo elemento de quebra de linha do PHPWord ou use a tag XML `<w:br/>` via `setValue`:
  ```php
  $formattedText = str_replace("\n", '</w:t><w:br/><w:t>', htmlspecialchars($text, ENT_QUOTES, 'UTF-8'));
  $templateProcessor->setValue('description', $formattedText);
  ```
- **Clonando Linhas e Blocos:** Use `cloneRow` e `cloneBlock` para tabelas repetidas ou seções dinâmicas (ex: listas de itens repetidas ou anexos dinâmicos).
  ```php
  $templateProcessor->cloneRow('item_id', count($items));
  foreach ($items as $index => $item) {
      $rowNum = $index + 1;
      $templateProcessor->setValue("item_id#{$rowNum}", $item->id);
      $templateProcessor->setValue("item_name#{$rowNum}", htmlspecialchars($item->name, ENT_QUOTES, 'UTF-8'));
  }
  ```

### 3. Inserção Dinâmica de Imagens
- Ao injetar imagens em placeholders de template (ex: `${image_placeholder}`), use `setImageValue` com proporções corretas para evitar achatamento ou distorção:
  ```php
  $templateProcessor->setImageValue('image_placeholder', [
      'path' => $imagePath,
      'width' => 300,
      'height' => 200,
      'ratio' => false // Defina como true para preservar a proporção com base na largura
  ]);
  ```
- Sempre verifique se o arquivo de imagem existe (`file_exists($imagePath)`) antes de tentar injetá-lo. Se ele não existir, injete uma imagem placeholder ou um texto descritivo de fallback para prevenir exceções.

### 4. Estilização e Formatação Dinâmica de Tabelas (PHPWord Nativo)
- Ao gerar documentos do zero, defina estilos de tabela reutilizáveis usando `PhpOffice\PhpWord\SimpleType\TblWidth`.
- Use um arquivo de configuração dedicado ou referencie `resources/table_styles.json` para temas corporativos (bordas, fundos de linha alternados e fontes específicas).
- Use `gridSpan` para mesclar células horizontalmente e `vMerge` para mesclar células verticalmente.
  ```php
  $table->addCell(2000, ['vMerge' => 'restart'])->addText('Merged Category');
  $table->addCell(4000, ['gridSpan' => 2])->addText('Spanned Columns');
  ```

### 5. Gerenciamento de Memória e Resposta de Arquivo
- Gerar documentos grandes com múltiplas imagens de alta resolução pode facilmente exceder os limites de memória. Certifique-se de otimizar as imagens antes de incorporá-las (ex: usando Spatie Image ou Intervention Image) e chame o garbage collector do PHP se estiver processando documentos em lote.
- Sempre entregue o arquivo gerado usando a resposta binária do Laravel e limpe os arquivos temporários locais após a conclusão da resposta ou via queue jobs:
  ```php
  $tempFile = tempnam(sys_get_temp_dir(), 'docx');
  $templateProcessor->saveAs($tempFile);

  return response()->download($tempFile, 'report.docx')->deleteFileAfterSend(true);
  ```

---

## Restrições
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
- **SEM Saída Direta no Controller:** Nunca faça geração pesada de documentos de forma síncrona dentro de controllers. Se a geração do documento levar mais de 2 segundos (ex: gerando laudos com muitas fotos), despache um Queue Job e notifique o usuário via WebSockets/Reverb.
- **SEM HTML Cru Sem Escape:** Não passe strings de HTML cru diretamente para `setValue()`. O parser de XML falhará e o MS Word reclamará que o arquivo está corrompido. Use parsers de HTML especializados (como `Html::addHtml`) ou escape/remova as tags primeiro.
- **SEM Caminhos Hardcoded:** Não faça hardcode de caminhos de filesystem para templates ou arquivos de saída. Sempre use `storage_path()` ou `resource_path()`.
- **SEM Vazamento de Recursos:** Nunca deixe arquivos temporários gerados durante o processo no disco do servidor. Use `deleteFileAfterSend(true)` ou registre um hook de limpeza.

---

## Exemplos

### Padrão Completo de Controller Laravel
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

            // 1. Valores simples com escape
            $templateProcessor->setValue('laud_number', htmlspecialchars($laud->number, ENT_QUOTES, 'UTF-8'));
            $templateProcessor->setValue('client_name', htmlspecialchars($laud->client->name, ENT_QUOTES, 'UTF-8'));

            // 2. Texto multilinha com quebras de linha do Word
            $formattedDescription = str_replace(
                "\n", 
                '</w:t><w:br/><w:t>', 
                htmlspecialchars($laud->description, ENT_QUOTES, 'UTF-8')
            );
            $templateProcessor->setValue('description', $formattedDescription);

            // 3. Injeção dinâmica de imagem
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

            // 4. Linhas repetidas (medições)
            $measurements = $laud->measurements;
            $templateProcessor->cloneRow('m_id', count($measurements));
            foreach ($measurements as $index => $measurement) {
                $row = $index + 1;
                $templateProcessor->setValue("m_id#{$row}", $measurement->id);
                $templateProcessor->setValue("m_voltage#{$row}", number_format($measurement->voltage, 2, ',', '.'));
                $templateProcessor->setValue("m_current#{$row}", number_format($measurement->current, 2, ',', '.'));
            }

            // Salva em arquivo temporário
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
