---
name: laravel-brazilian-localization-best-practices
description: Use when validating, formatting, sanitizing, or processing Brazilian documents (CPF, CNPJ, CEP, phone numbers) and when formatting, parsing, or rounding currency (BRL), percentages, decimal numbers, or converting numbers and monetary values into words in Portuguese (pt-BR) on both backend (Laravel) and frontend (Vue 3/MaxUse).
---

# Brazilian Localization Best Practices

## Goal
Establish standard, precise, and consistent patterns for:
1. Validating, formatting, and sanitizing Brazilian documents (CPF, CNPJ, CEP, and phone numbers).
2. Formatting Brazilian currency (BRL), handling precise rounding, and converting numbers/monetary values to words (por extenso) in Portuguese (pt-BR) across backend (Laravel) and frontend (Vue 3).

## Instructions

### 1. Backend (Laravel / PHP)

#### A. Document Data Sanitization (Database level)
* Always store only numbers for documents (CPF, CNPJ, CEP) in the database.
* Use the global helper function `onlyNumbers($value)` to strip formatting and masks before saving.
* Implement this sanitization in Eloquent Model observers, saving events, or mutators.

#### B. Document Validation Rules in Requests
* For Form Requests and controller validations, use the global Laravel Validator rules provided by the `phillarmonic/cpf-cnpj` package:
  * `cpf` — Validates CPF digit algorithm.
  * `cnpj` — Validates CNPJ digit algorithm.
* Example validation signature:
  ```php
  $request->validate([
      'cpf_cnpj' => 'required|string|cpf', // Use 'cnpj' for CNPJ validation
  ]);
  ```

#### C. Programmatic Document Validation
* If you need to programmatically validate a document, use the `Lacus\BrUtils\BrUtils` package:
  ```php
  use Lacus\BrUtils\BrUtils;

  $brUtils = new BrUtils();
  $isValid = $brUtils->cpf->isValid(onlyNumbers($value)) || $brUtils->cnpj->isValid(onlyNumbers($value));
  ```

#### D. String Formatting Helpers (PHP)
* Use the global helper functions defined in `StringsHelper.php`:
  * `onlyNumbers($value)`: Returns only digits.
  * `formatCPFCNPJ($value)`: Formats string as CPF or CNPJ depending on length.
  * `formatCPF($value)` / `formatCNPJ($value)`: Formats CPF/CNPJ.
  * `formatCep($value, $format = '#####-###')`: Formats CEP.

#### E. Number and Currency Formatting (BRL)
* Always use `NumberFormatter` from the PHP `intl` extension for formatting values to BRL:
  ```php
  $formatter = new \NumberFormatter('pt_BR', \NumberFormatter::CURRENCY);
  $formatted = $formatter->formatCurrency(1250.50, 'BRL'); // Output: R$ 1.250,50
  ```
* Alternatively, if using Laravel's `Number` helper utility (Laravel 10+):
  ```php
  use Illuminate\Support\Number;
  
  $formatted = Number::currency(1250.50, in: 'BRL', locale: 'pt_BR'); // Output: R$ 1.250,50
  ```

#### F. Precision Rounding
* To prevent cent calculation mismatches (e.g., floating-point inaccuracies), use PHP's `bcmath` extension for mathematical operations or `round()` with explicit precision:
  ```php
  // Math operation using bcmath
  $sum = bcadd('10.25', '20.35', 2); // '30.60'
  
  // Safe rounding
  $rounded = round($value, 2, PHP_ROUND_HALF_UP);
  ```
* Avoid casting float values directly to integer without proper rounding.

#### G. Converting Numbers and Currency to Words (por extenso)
* Use the `kwn/number-to-words` package integrated into `StringsHelper.php` or instantiate `NumberToWords` for custom conversions:
  ```php
  use NumberToWords\NumberToWords;

  $numberToWords = new NumberToWords();
  $numberTransformer = $numberToWords->getNumberTransformer('pt_BR');
  
  // Convert number to words
  $words = $numberTransformer->toWords(1250); // "mil duzentos e cinquenta"
  ```
* Use the global helper function `nameNumber($number, $gender = 'm')` from `StringsHelper.php` where available to handle masculine/feminine genders (e.g., "um" vs. "uma", "dois" vs. "duas").

---

### 2. Frontend (Vue 3 / TypeScript)

#### A. Input UI Components
Always use the specialized components from `@maxvue/max-components-ui` inside templates. When using them, keep all attributes/parameters inline in a single line (no multi-line attribute break):
* **MaxInputCpfCnpj**: Híbrido com máscara e validação automáticas para CPF/CNPJ.
  ```vue
  <MaxInputCpfCnpj v-model="form.cpf_cnpj" label="CPF/CNPJ" required />
  ```
* **MaxInputCep**: Máscara automática e evento `@complete`.
  ```vue
  <MaxInputCep v-model="form.cep" label="CEP" required />
  ```
* **MaxInputPhoneMail**: Híbrido para telefone ou email com detecção dinâmica.
  ```vue
  <MaxInputPhoneMail v-model="form.phone" label="Telefone" required />
  ```

#### B. Document Validation and Formatting helpers (TypeScript)
Use the `@maxvue/max-use` library helpers for logic and validation:
* **Validations**:
  ```ts
  import { isCpf, isCnpj, isCpfCnpj, cepIsValid } from '@maxvue/max-use/validations';

  if (isCpfCnpj(form.cpf_cnpj)) {
      // Documento válido
  }
  ```
* **Formatters**:
  ```ts
  import { formatCpfCnpj, formatCep, formatPhone } from '@maxvue/max-use/format';

  const docFormatted = formatCpfCnpj(rawDoc);
  ```

#### C. Formatting Currency (BRL)
* Reuse the official `formatCurrency` helper from the `MaxUse` library:
  ```typescript
  import { formatCurrency } from '@maxvue/max-use'; // Or relative import from helpers
  
  const price = formatCurrency(1250.50); // Output: "R$ 1.250,50"
  ```
* Under the hood, this uses:
  ```typescript
  new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
  }).format(value);
  ```

#### D. Currency Inputs and Parsing (Maska)
* When capturing currency inputs, use `v-maska` to mask the input, and ensure you parse the formatted string back to a numeric float before sending it to the backend:
  ```typescript
  // Convert "R$ 1.250,50" or "1.250,50" to float 1250.5
  function parseBrlToFloat(value: string): number {
      if (!value) return 0;
      const cleanValue = value
          .replace(/[^\d,.-]/g, '') // remove "R$" and spaces
          .replace(/\./g, '')       // remove thousands separator
          .replace(',', '.');       // replace decimal separator
      return parseFloat(cleanValue) || 0;
  }
  ```

## Constraints
* NEVER store formatted documents (e.g., with dots, slashes, or dashes) in the database. Always use `onlyNumbers()`.
* DO NOT write custom validation algorithms for CPF/CNPJ or CEP. Always reuse `lacus/br-utils`, `phillarmonic/cpf-cnpj` or `@maxvue/max-use`.
* NEVER break HTML/Vue component attributes into multiple lines inside templates. Maintain single-line tags (inline style).
* **Do NOT** perform manual string replacements for currency formatting (e.g., `str_replace` or manually concatenating `"R$ "`). Always use `Intl.NumberFormat` on the frontend and `NumberFormatter` or Laravel `Number` helper on the backend.
* **Do NOT** use float-based additions (`$a + $b`) directly for sensitive financial calculations. Prefer `bcmath` or enforce 2-decimal rounding.
* **Do NOT** duplicate the `NumberToWords` instance creation unnecessarily; reuse established helpers like `nameNumber()` inside `StringsHelper.php` where applicable.
