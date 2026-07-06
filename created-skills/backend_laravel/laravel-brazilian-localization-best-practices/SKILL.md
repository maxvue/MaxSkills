---
name: laravel-brazilian-localization-best-practices
description: Use when validating, formatting, sanitizing, or processing Brazilian documents (CPF, CNPJ, CEP, phone numbers) and when formatting, parsing, or rounding currency (BRL), percentages, decimal numbers, or converting numbers and monetary values into words in Portuguese (pt-BR) on both backend (Laravel) and frontend (Vue 3/MaxUse).
---

# Boas Práticas de Localização Brasileira

## Objetivo
Estabelecer padrões precisos, consistentes e padronizados para:
1. Validar, formatar e sanitizar documentos brasileiros (CPF, CNPJ, CEP e números de telefone).
2. Formatar moeda brasileira (BRL), lidar com arredondamento preciso e converter números/valores monetários por extenso em português (pt-BR) tanto no backend (Laravel) quanto no frontend (Vue 3).

## Instruções

### 1. Backend (Laravel / PHP)

#### A. Sanitização dos Dados de Documentos (nível de Banco de Dados)
* Sempre armazene apenas números para documentos (CPF, CNPJ, CEP) no banco de dados.
* Use a função helper global `onlyNumbers($value)` para remover formatação e máscaras antes de salvar.
* Implemente essa sanitização em observers de Model do Eloquent, eventos de saving ou mutators.

#### B. Validação Programática de Documentos (CPF/CNPJ)
* NÃO existe rule global de Validator chamada `cpf` ou `cnpj`. O pacote `phillarmonic/cpf-cnpj` NÃO registra ServiceProvider nem auto-discovery (sem `extra.laravel`) e não chama `Validator::extend` — ele expõe apenas as classes puras `Phillarmonic\CpfCnpj\CPF` e `CNPJ` (`isValid()`/`format()`). Usar `'required|string|cpf'` num Form Request quebra em runtime (rule inexistente).
* O padrão real do projeto é validar programaticamente com o pacote `Lacus\BrUtils\BrUtils` sobre os dígitos sanitizados (`onlyNumbers()`), como em `app/Models/Client/Client.php`:
  ```php
  use Lacus\BrUtils\BrUtils;

  $brUtils = new BrUtils;
  $isValid = $brUtils->cnpj->isValid(onlyNumbers($value)) || $brUtils->cpf->isValid(onlyNumbers($value));
  ```
* Para validar dentro de um Form Request, envolva essa checagem em uma closure/Rule customizada (nunca dependa de uma rule string `cpf`/`cnpj`):
  ```php
  'cpf_cnpj' => ['required', 'string', function ($attribute, $value, $fail) {
      $brUtils = new BrUtils;
      $digits = onlyNumbers($value);
      if (! $brUtils->cnpj->isValid($digits) && ! $brUtils->cpf->isValid($digits)) {
          $fail('CPF/CNPJ inválido.');
      }
  }],
  ```

#### C. Helpers de Formatação de String (PHP)
* Use as funções helper globais definidas em `StringsHelper.php`:
  * `onlyNumbers($value)`: Retorna apenas os dígitos.
  * `formatCPFCNPJ($value)`: Formata a string como CPF ou CNPJ dependendo do comprimento.
  * `formatCPF($value)` / `formatCNPJ($value)`: Formata CPF/CNPJ.
  * `formatCep($value, $format = '#####-###')`: Formata CEP.

#### D. Formatação de Números e Moeda (BRL)
* Sempre use o `NumberFormatter` da extensão `intl` do PHP para formatar valores em BRL:
  ```php
  $formatter = new \NumberFormatter('pt_BR', \NumberFormatter::CURRENCY);
  $formatted = $formatter->formatCurrency(1250.50, 'BRL'); // Saída: R$ 1.250,50
  ```
* Alternativamente, se usar o helper `Number` do Laravel (Laravel 10+):
  ```php
  use Illuminate\Support\Number;
  
  $formatted = Number::currency(1250.50, in: 'BRL', locale: 'pt_BR'); // Saída: R$ 1.250,50
  ```

#### E. Arredondamento de Precisão
* Para evitar divergências no cálculo de centavos (ex: imprecisões de ponto flutuante), use a extensão `bcmath` do PHP para operações matemáticas ou `round()` com precisão explícita:
  ```php
  // Operação matemática usando bcmath
  $sum = bcadd('10.25', '20.35', 2); // '30.60'
  
  // Arredondamento seguro
  $rounded = round($value, 2, PHP_ROUND_HALF_UP);
  ```
* Evite converter valores float diretamente para inteiro sem o arredondamento adequado.

#### F. Convertendo Números e Moeda por Extenso
* Use o pacote `kwn/number-to-words` integrado ao `StringsHelper.php` ou instancie `NumberToWords` para conversões customizadas:
  ```php
  use NumberToWords\NumberToWords;

  $numberToWords = new NumberToWords();
  $numberTransformer = $numberToWords->getNumberTransformer('pt_BR');
  
  // Converte número por extenso
  $words = $numberTransformer->toWords(1250); // "mil duzentos e cinquenta"
  ```
* Use a função helper global `nameNumber($number, $gender = 'm')` do `StringsHelper.php` onde disponível para tratar os gêneros masculino/feminino (ex: "um" vs. "uma", "dois" vs. "duas").

---

### 2. Frontend (Vue 3 / TypeScript)

#### A. Componentes de UI de Input
Sempre use os componentes especializados de `@maxvue/max-components-ui` dentro dos templates. Ao usá-los, mantenha todos os atributos/parâmetros inline em uma única linha (sem quebra de atributos em múltiplas linhas):
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

#### B. Helpers de Validação e Formatação de Documentos (TypeScript)
Use os helpers da biblioteca `@maxvue/max-use` para lógica e validação:
* **Validações**:
  ```ts
  import { isCpf, isCnpj, isCpfCnpj, cepIsValid } from '@maxvue/max-use/validations';

  if (isCpfCnpj(form.cpf_cnpj)) {
      // Documento válido
  }
  ```
* **Formatadores**:
  ```ts
  import { formatCpfCnpj, formatCep, formatPhone } from '@maxvue/max-use/format';

  const docFormatted = formatCpfCnpj(rawDoc);
  ```

#### C. Formatação de Moeda (BRL)
* Reutilize o helper oficial `formatCurrency` da biblioteca `MaxUse`:
  ```typescript
  import { formatCurrency } from '@maxvue/max-use'; // Ou import relativo dos helpers
  
  const price = formatCurrency(1250.50); // Saída: "R$ 1.250,50"
  ```
* Por baixo dos panos, isso usa:
  ```typescript
  new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
  }).format(value);
  ```

#### D. Inputs de Moeda (BRL)
* Para capturar valores monetários, use o componente numérico Max (`MaxInputNumber`, resolvido no template como `InputNumber`), que embrulha o `InputNumber` do PrimeVue. Ele já vincula um `v-model` **numérico** direto (float), sem máscara nem parsing manual de string. Passe `prefix="R$ "` e `:minFractionDigits="2"`/`:maxFractionDigits="2"` para o formato brasileiro:
  ```vue
  <InputNumber v-model="form.value" prefix="R$ " :minFractionDigits="2" :maxFractionDigits="2" label="Valor (R$)" />
  ```
  Evidência real: `resources/Vue/Sections/supportChat/ChatInputTemplatesPopover.vue` (input de `type_input === 'finance' | 'money'`).
* NÃO use `v-maska` cru + função manual de `parse` (`parseBrlToFloat` etc.) para moeda: isso reinventa o `MaxInputNumber` já existente e viola a regra de preferir componentes `Max*`. O `v-model` do `InputNumber` já entrega o `number` pronto para enviar ao backend.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* NUNCA armazene documentos formatados (ex: com pontos, barras ou traços) no banco de dados. Sempre use `onlyNumbers()`.
* NÃO escreva algoritmos de validação customizados para CPF/CNPJ ou CEP. Reutilize `lacus/br-utils` no backend (padrão do projeto) e `@maxvue/max-use` no frontend. NÃO confie em uma rule `cpf`/`cnpj` do Validator — ela não existe.
* NÃO use `v-maska` cru + parsing manual para inputs de moeda; use o componente numérico Max (`MaxInputNumber`/`InputNumber`) com `prefix` e `minFractionDigits`.
* NUNCA quebre atributos de componentes HTML/Vue em múltiplas linhas dentro dos templates. Mantenha as tags em linha única (estilo inline).
* **NÃO** faça substituições manuais de string para formatação de moeda (ex: `str_replace` ou concatenar manualmente `"R$ "`). Sempre use `Intl.NumberFormat` no frontend e `NumberFormatter` ou o helper `Number` do Laravel no backend.
* **NÃO** use adições baseadas em float (`$a + $b`) diretamente para cálculos financeiros sensíveis. Prefira `bcmath` ou imponha arredondamento de 2 casas decimais.
* **NÃO** duplique a criação da instância de `NumberToWords` desnecessariamente; reutilize os helpers estabelecidos como `nameNumber()` dentro de `StringsHelper.php` quando aplicável.
