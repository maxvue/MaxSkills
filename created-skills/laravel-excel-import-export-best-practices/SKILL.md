---
name: laravel-excel-import-export-best-practices
description: >-
  Use when creating, reviewing, or debugging Excel import and export features in Laravel using the Maatwebsite/Laravel-Excel package. Triggers on model imports, exports, chunk reading, queueable imports/exports, validation rules in imports, and custom formatting.
---

# Laravel Excel Import & Export — Best Practices

## Goal

Provide standardized, highly performant, and memory-safe guidelines for implementing spreadsheet import and export features in the Laravel framework using the `maatwebsite/excel` package. This skill ensures imports and exports avoid memory exhaustion (OOM), prevent N+1 query patterns, leverage Laravel queues via Horizon, validate raw data correctly, and format outputs according to Brazilian and international standards.

## Instructions

### 1. Excel Export (Exports) — Required Structure

When exporting data from a database, **NEVER** load the entire dataset into memory using `FromCollection` unless the collection size is guaranteed to be extremely small (under 100 rows). Instead, use `FromQuery` combined with eager loading.

#### Standard Export Class Skeleton
Create export classes using `php artisan make:export ModelExport --model=Model`.

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
     * Define the query for exporting. Eager load relations to prevent N+1 issues.
     */
    public function query(): Builder
    {
        return Equipment::query()
            ->with(['client', 'category']) // ALWAYS eager load relations
            ->when($this->filters['client_id'] ?? null, function ($query, $clientId) {
                $query->where('client_id', $clientId);
            });
    }

    /**
     * Define headings for the export sheet.
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
     * Map each row from the Eloquent query to the sheet format.
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
            $row->created_at ? Date::dateTimeToExcel($row->created_at) : '', // Excel Date Serial
            $row->monthly_cost, // Numeric value to be formatted by column formatting
        ];
    }

    /**
     * Format columns explicitly.
     * 
     * @return array<string, string>
     */
    public function columnFormats(): array
    {
        return [
            'E' => NumberFormat::FORMAT_DATE_DDMMYYYY,
            'F' => '"R$"#,##0.00', // Brazilian Real Currency Format
        ];
    }
}
```

#### Triggering Exports from Controllers
Always return the export response:

```php
use App\Exports\EquipmentsExport;

public function export(Request $request)
{
    $filters = $request->only(['client_id']);
    return (new EquipmentsExport($filters))->download('equipments.xlsx');
}
```

---

### 2. Excel Import (Imports) — Required Structure

For processing spreadsheets, always use chunk reading and queueable imports to avoid PHP timeouts and high memory usage.

#### Standard Import Class Skeleton
Create import classes using `php artisan make:import ModelImport --model=Model`.

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
     * Convert heading row keys to camelCase/snake_case keys.
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
     * Define the size of each chunk to be processed in a queue Job.
     */
    public function chunkSize(): int
    {
        return 500; // Optimal chunk size for background jobs
    }

    /**
     * Validation rules for each row.
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
     * Custom attribute names for validation errors.
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
     * Handle rows that failed validation.
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

#### Dispatching Imports (Async via Queues)
Do not parse the file in the request lifecycle. Upload it and dispatch a queue job:

```php
use App\Imports\MeasurementsImport;

public function import(Request $request)
{
    $request->validate([
        'file' => ['required', 'file', 'mimes:xlsx,xls,csv'],
    ]);

    $path = $request->file('file')->store('temp-imports');
    $importLogId = Str::uuid()->toString();

    // The import will run in the background (queue) in chunks of 500
    (new MeasurementsImport($importLogId))->queue($path)->allOnQueue('default');

    return response()->json([
        'message' => 'Import started in the background.',
        'import_log_id' => $importLogId,
    ]);
}
```

---

### 3. Formatting Helper Reference (Brazilian Standards)

Spreadsheet columns often hold data using custom formatting (e.g. CPF, CNPJ, currency). Keep raw values in mapping, but assign column formatting masks:

* **Brazilian Real Currency (R$):**
  Use format mask: `'"R$"#,##0.00'`
* **CPF / CNPJ:**
  If you must output them as formatted strings, sanitize them in `map()`:
  ```php
  // CPF formatting
  preg_replace("/(\d{3})(\d{3})(\d{3})(\d{2})/", "$1.$2.$3-$4", $rawCpf);
  // CNPJ formatting
  preg_replace("/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/", "$1.$2.$3/$4-$5", $rawCnpj);
  ```
* **Date Conversion:**
  Always use `PhpOffice\PhpSpreadsheet\Shared\Date::dateTimeToExcel($date)` when writing date fields, and register `NumberFormat::FORMAT_DATE_DDMMYYYY` as the column format.

---

### 4. Testing Imports & Exports with Pest

Always test Excel features using the `Excel` facade double to mock the filesystem.

#### Export Test Case
```php
use App\Exports\EquipmentsExport;
use Maatwebsite\Excel\Facades\Excel;

test('it can download equipments export file', function () {
    Excel::fake();

    $response = $this->get(route('equipments.export'));

    $response->assertStatus(200);
    Excel::assertDownloaded('equipments.xlsx', function (EquipmentsExport $export) {
        return true; // Optionally assert filters or internal state here
    });
});
```

#### Import Test Case
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

## Constraints

1. **NEVER** use `FromCollection` or `ToArray` for exports with over 500 rows. Always implement `FromQuery` to leverage database pagination.
2. **NEVER** call Eloquent relation properties in the `map()` method without declaring them inside eager loading (e.g., `with()`) in `query()`. This avoids N+1 queries.
3. **NEVER** run imports directly inside the HTTP Request thread (`(new Import)->import(...)`). Always implement `ShouldQueue` and use `(new Import)->queue(...)` for spreadsheets containing more than 100 rows.
4. **NEVER** forget to include `SkipsEmptyRows` when importing. Users often upload sheets with blank trailing lines, which triggers validation errors.
5. **ALWAYS** implement `SkipsOnFailure` or `SkipsOnError` on queueable imports to log and trace import errors, preventing silent failures.
6. **ALWAYS** convert date timestamps to Excel serialization floats (`Date::dateTimeToExcel`) when exporting dates, matching them with explicit cell formats.
7. **ALWAYS** test import and export controllers with `Excel::fake()` in Pest.
