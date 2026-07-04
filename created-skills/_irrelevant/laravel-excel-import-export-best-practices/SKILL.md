---
name: laravel-excel-import-export-best-practices
description: >-
  Use when creating, reviewing, or debugging Excel import and export features in Laravel using the Maatwebsite/Laravel-Excel package. Triggers on model imports, exports, chunk reading, queueable imports/exports, validation rules in imports, and custom formatting.
---

# Boas Práticas de Importação e Exportação de Excel no Laravel

## Objetivo

Fornecer diretrizes padronizadas, de alta performance e seguras em relação a memória para implementar recursos de importação e exportação de planilhas no framework Laravel usando o pacote `maatwebsite/excel`. Esta skill garante que importações e exportações evitem esgotamento de memória (OOM), previnam padrões de query N+1, aproveitem as filas do Laravel via Horizon, validem dados brutos corretamente e formatem as saídas de acordo com os padrões brasileiros e internacionais.

## Instruções

### 1. Exportação de Excel (Exports) — Estrutura Obrigatória

Ao exportar dados de um banco de dados, **NUNCA** carregue o conjunto de dados inteiro em memória usando `FromCollection`, a menos que o tamanho da collection seja garantidamente extremamente pequeno (menos de 100 linhas). Em vez disso, use `FromQuery` combinado com eager loading.

#### Esqueleto Padrão da Classe de Export
Crie classes de export usando `php artisan make:export ModelExport --model=Model`.

```php
<?php

namespace App\Exports;

use App\Models\Equipment;
use Illuminate\Database\Eloquent\Builder;
use Maatwebsite\Excel\Concerns\FromQuery;
use Maatwebsite\Excel\Concerns\Exportable;
use Maatwebsite\Excel\Concerns\WithMapping;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithColumnFormatting;
use PhpOffice\PhpSpreadsheet\Shared\Date;
use PhpOffice\PhpSpreadsheet\Style\NumberFormat;

class EquipmentsExport implements FromQuery, WithMapping, WithHeadings, WithColumnFormatting
{
    use Exportable;

    public function __construct(
        protected array $filters = []
    ) {}

    /**
     * Define a query para exportação. Faça eager load das relações para evitar problemas de N+1.
     */
    public function query(): Builder
    {
        return Equipment::query()
            ->with(['client', 'category']) // SEMPRE faça eager load das relações
            ->when($this->filters['client_id'] ?? null, function ($query, $clientId) {
                $query->where('client_id', $clientId);
            });
    }

    /**
     * Define os cabeçalhos da planilha de exportação.
     * 
     * @return array<int, string>
     */
    public function headings(): array
    {
        return [
            'ID',
            'Equipment Name',
            'Category',
            'Client Name',
            'Creation Date',
            'Monthly Cost',
        ];
    }

    /**
     * Mapeia cada linha da query Eloquent para o formato da planilha.
     * 
     * @param Equipment $row
     * @return array<int, mixed>
     */
    public function map($row): array
    {
        return [
            $row->id,
            $row->name,
            $row->category?->name ?? 'N/A',
            $row->client?->name ?? 'N/A',
            $row->created_at ? Date::dateTimeToExcel($row->created_at) : '', // Serial de data do Excel
            $row->monthly_cost, // Valor numérico a ser formatado pela formatação de coluna
        ];
    }

    /**
     * Formata as colunas explicitamente.
     * 
     * @return array<string, string>
     */
    public function columnFormats(): array
    {
        return [
            'E' => NumberFormat::FORMAT_DATE_DDMMYYYY,
            'F' => '"R$"#,##0.00', // Formato de moeda em Real brasileiro
        ];
    }
}
```

#### Disparando Exportações a partir de Controllers
Sempre retorne a resposta de exportação:

```php
use App\Exports\EquipmentsExport;

public function export(Request $request)
{
    $filters = $request->only(['client_id']);
    return (new EquipmentsExport($filters))->download('equipments.xlsx');
}
```

---

### 2. Importação de Excel (Imports) — Estrutura Obrigatória

Para processar planilhas, sempre use leitura em chunks e importações que podem ser enfileiradas (queueable) para evitar timeouts do PHP e alto uso de memória.

#### Esqueleto Padrão da Classe de Import
Crie classes de import usando `php artisan make:import ModelImport --model=Model`.

```php
<?php

namespace App\Imports;

use App\Models\Measurement;
use Illuminate\Contracts\Queue\ShouldQueue;
use Maatwebsite\Excel\Concerns\ToModel;
use Maatwebsite\Excel\Concerns\Importable;
use Maatwebsite\Excel\Concerns\WithHeadingRow;
use Maatwebsite\Excel\Concerns\WithChunkReading;
use Maatwebsite\Excel\Concerns\WithValidation;
use Maatwebsite\Excel\Concerns\SkipsEmptyRows;
use Maatwebsite\Excel\Concerns\SkipsOnFailure;
use Maatwebsite\Excel\Validators\Failure;
use Illuminate\Support\Facades\Log;

class MeasurementsImport implements 
    ToModel, 
    WithHeadingRow, 
    WithChunkReading, 
    WithValidation, 
    ShouldQueue, 
    SkipsEmptyRows,
    SkipsOnFailure
{
    use Importable;

    public function __construct(
        protected string $importLogId
    ) {}

    /**
     * Converte as chaves da linha de cabeçalho para chaves camelCase/snake_case.
     * 
     * @param array<string, mixed> $row
     * @return \Illuminate\Database\Eloquent\Model|null
     */
    public function model(array $row): ?Measurement
    {
        return new Measurement([
            'equipment_id' => $row['equipment_id'],
            'value'        => $row['measured_value'],
            'measured_at'  => $row['date'] ? \Carbon\Carbon::createFromFormat('d/m/Y', $row['date']) : now(),
        ]);
    }

    /**
     * Define o tamanho de cada chunk a ser processado em um Job de fila.
     */
    public function chunkSize(): int
    {
        return 500; // Tamanho ótimo de chunk para jobs em background
    }

    /**
     * Regras de validação para cada linha.
     * 
     * @return array<string, array<int, string>>
     */
    public function rules(): array
    {
        return [
            'equipment_id'   => ['required', 'exists:equipments,id'],
            'measured_value' => ['required', 'numeric', 'min:0'],
            'date'           => ['required', 'date_format:d/m/Y'],
        ];
    }

    /**
     * Nomes de atributos personalizados para erros de validação.
     * 
     * @return array<string, string>
     */
    public function customValidationAttributes(): array
    {
        return [
            'equipment_id'   => 'Equipment ID',
            'measured_value' => 'Measured Value',
            'date'           => 'Measurement Date',
        ];
    }

    /**
     * Trata as linhas que falharam na validação.
     * 
     * @param Failure ...$failures
     */
    public function onFailure(Failure ...$failures): void
    {
        foreach ($failures as $failure) {
            Log::channel('import_errors')->warning('Row validation failed', [
                'import_log_id' => $this->importLogId,
                'row'           => $failure->row(),
                'attribute'     => $failure->attribute(),
                'errors'        => $failure->errors(),
                'values'        => $failure->values(),
            ]);
        }
    }
}
```

#### Disparando Importações (Assíncrono via Filas)
Não faça o parse do arquivo dentro do ciclo de vida da requisição. Faça o upload dele e dispare um job de fila:

```php
use App\Imports\MeasurementsImport;

public function import(Request $request)
{
    $request->validate([
        'file' => ['required', 'file', 'mimes:xlsx,xls,csv'],
    ]);

    $path = $request->file('file')->store('temp-imports');
    $importLogId = Str::uuid()->toString();

    // A importação rodará em background (fila) em chunks de 500
    (new MeasurementsImport($importLogId))->queue($path)->allOnQueue('default');

    return response()->json([
        'message' => 'Import started in the background.',
        'import_log_id' => $importLogId,
    ]);
}
```

---

### 3. Referência de Helpers de Formatação (Padrões Brasileiros)

Colunas de planilha frequentemente contêm dados com formatação personalizada (ex: CPF, CNPJ, moeda). Mantenha os valores brutos no mapeamento, mas atribua máscaras de formatação de coluna:

* **Moeda em Real brasileiro (R$):**
  Use a máscara de formato: `'"R$"#,##0.00'`
* **CPF / CNPJ:**
  Se você precisar exibi-los como strings formatadas, sanitize-os no `map()`:
  ```php
  // Formatação de CPF
  preg_replace("/(\d{3})(\d{3})(\d{3})(\d{2})/", "$1.$2.$3-$4", $rawCpf);
  // Formatação de CNPJ
  preg_replace("/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/", "$1.$2.$3/$4-$5", $rawCnpj);
  ```
* **Conversão de Data:**
  Sempre use `PhpOffice\PhpSpreadsheet\Shared\Date::dateTimeToExcel($date)` ao escrever campos de data, e registre `NumberFormat::FORMAT_DATE_DDMMYYYY` como o formato da coluna.

---

### 4. Testando Importações e Exportações com Pest

Sempre teste os recursos de Excel usando o dublê da facade `Excel` para mockar o sistema de arquivos.

#### Caso de Teste de Exportação
```php
use App\Exports\EquipmentsExport;
use Maatwebsite\Excel\Facades\Excel;

test('it can download equipments export file', function () {
    Excel::fake();

    $response = $this->get(route('equipments.export'));

    $response->assertStatus(200);
    Excel::assertDownloaded('equipments.xlsx', function (EquipmentsExport $export) {
        return true; // Opcionalmente, verifique filtros ou estado interno aqui
    });
});
```

#### Caso de Teste de Importação
```php
use App\Imports\MeasurementsImport;
use Maatwebsite\Excel\Facades\Excel;
use Illuminate\Http\UploadedFile;

test('it queues measurements import when uploading file', function () {
    Excel::fake();

    $file = UploadedFile::fake()->create('measurements.xlsx');

    $response = $this->post(route('measurements.import'), [
        'file' => $file,
    ]);

    $response->assertStatus(200);
    Excel::assertQueued($file->hashName(), function (MeasurementsImport $import) {
        return true;
    });
});
```

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
1. **NUNCA** use `FromCollection` ou `ToArray` para exportações com mais de 500 linhas. Sempre implemente `FromQuery` para aproveitar a paginação do banco de dados.
2. **NUNCA** chame propriedades de relação Eloquent no método `map()` sem declará-las dentro do eager loading (ex: `with()`) em `query()`. Isso evita queries N+1.
3. **NUNCA** execute importações diretamente dentro da thread da requisição HTTP (`(new Import)->import(...)`). Sempre implemente `ShouldQueue` e use `(new Import)->queue(...)` para planilhas contendo mais de 100 linhas.
4. **NUNCA** esqueça de incluir `SkipsEmptyRows` ao importar. Usuários frequentemente enviam planilhas com linhas em branco no final, o que dispara erros de validação.
5. **SEMPRE** implemente `SkipsOnFailure` ou `SkipsOnError` em importações enfileiráveis para registrar e rastrear erros de importação, evitando falhas silenciosas.
6. **SEMPRE** converta timestamps de data para floats de serialização do Excel (`Date::dateTimeToExcel`) ao exportar datas, associando-os a formatos de célula explícitos.
7. **SEMPRE** teste os controllers de importação e exportação com `Excel::fake()` no Pest.
