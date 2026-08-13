---
name: laravel-brazilian-localization-best-practices
description: "Use when validating, formatting, or sanitizing Brazilian documents (CPF, CNPJ, CEP, phone numbers) and currency values (BRL, pt-BR) across Laravel backend and Vue 3 / MaxUse frontend. Covers Brazilian localization best practices and document validation."
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
* O padrão real do backend é `number_format($valor, 2, ',', '.')` com o prefixo `'R$ '` concatenado manualmente na exibição, como em `app/Traits/HasAgentAiRequest.php:137`:
  ```php
  $totalPriceBrl = 'R$ ' . number_format($priceData['total_usd'] * $cotacaoDolar, 2, ',', '.');
  ```
  Outros exemplos reais: `app/Services/Bank/EfiPaymentStatus.php` e `app/Services/Finance/PaymentPricing.php` (`'R$' . number_format(...)`).
* `\NumberFormatter` (extensão `intl`) e `Illuminate\Support\Number::currency` são opcionais, não o padrão do projeto: `ext-intl` NÃO está declarada em `composer.json` (apenas `ext-curl`/`dom`/`iconv`/`pdo`/`redis`/`zip`), então `Number::currency` lança `RuntimeException` e `new NumberFormatter` é fatal error sem a extensão instalada. Se optar por esse caminho, valide antes com `extension_loaded('intl')`.

#### E. Arredondamento de Precisão
* O padrão real do projeto é `round($value, 2, PHP_ROUND_HALF_UP)` — não há uso de `bcmath` em `app/` nem a extensão declarada no `composer.json`:
  ```php
  $rounded = round($value, 2, PHP_ROUND_HALF_UP);
  ```
* `bcmath` (`bcadd`, etc.) é uma alternativa genérica para quem precisar de precisão arbitrária, mas confirme antes com `extension_loaded('bcmath')` — não é dependência do projeto.
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
  Evidência real: `resources/Vue/Sections/supportChat/ChatInputTemplatesPopover.vue` (input de `type_input === 'finance' | 'money'`). NÃO use `v-maska` cru + função manual de `parse` (`parseBrlToFloat` etc.): isso reinventa o `MaxInputNumber` já existente.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* NÃO escreva algoritmos de validação customizados para CPF/CNPJ ou CEP. Reutilize `lacus/br-utils` no backend (padrão do projeto) e `@maxvue/max-use` no frontend. NÃO confie em uma rule `cpf`/`cnpj` do Validator — ela não existe.
* No frontend, sempre use `Intl.NumberFormat` (via `formatCurrency` do MaxUse) para formatação de moeda. No backend, o padrão real é `number_format($valor, 2, ',', '.')` com `'R$ '` concatenado manualmente na exibição — `NumberFormatter`/`Number::currency` são opcionais e dependem de `ext-intl`, não declarada no projeto.
* **NÃO** use adições baseadas em float (`$a + $b`) diretamente para cálculos financeiros sensíveis. Imponha arredondamento de 2 casas decimais com `round($value, 2, PHP_ROUND_HALF_UP)`; `bcmath` é uma alternativa apenas se a extensão estiver disponível.
* **NÃO** duplique a criação da instância de `NumberToWords` desnecessariamente; reutilize os helpers estabelecidos como `nameNumber()` dentro de `StringsHelper.php` quando aplicável.
