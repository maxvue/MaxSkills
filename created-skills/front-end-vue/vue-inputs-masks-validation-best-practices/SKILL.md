---
name: vue-inputs-masks-validation-best-practices
description: Use when implementing, formatting, or validating user inputs with masks in Vue 3 components using the Maska library (v3), libphonenumber-js, card-validator, and @polvo-labs/card-type. Triggers on setting up phone, CPF, CNPJ, currency, zip code (CEP), vehicle plate, credit card inputs, handling dynamic masks, and validation/unmasking.
---

# Boas Práticas de Inputs, Máscaras e Validação no Vue 3

## Objetivo
Estabelecer padrões claros e de alta qualidade de desenvolvimento para a aplicação de máscaras e validações de input em formulários no front-end Vue 3 do Engeapp. Isso garante uma interface consistente, tratamento dinâmico de máscaras, validação de cartões de crédito e telefones, e a extração automática do valor bruto sem formatação (unmasked) antes da persistência dos dados via store `@maxvue/max-pinia` no backend AdonisJS.

## Instruções

### 1. Registro e Configuração de Componentes (Maska)
- Sempre utilize a Composition API (`<script setup lang="ts">`) e SCSS (`lang="scss"` com escopo `scoped`) para os componentes.
- Importe a diretiva `vMaska` diretamente do pacote `maska/vue`:
  ```typescript
  import { vMaska } from 'maska/vue';
  ```
- Aplique a diretiva nos seus elementos de input.

### 2. Máscaras de Padrões Brasileiros
Garanta que as máscaras usem exatamente estes padrões de caracteres:
- **CPF**: `###.###.###-##`
- **CNPJ**: `##.###.###/####-##`
- **CEP**: `#####-###`
- **Placa de Veículo (Mercosul e Legado)**: Use máscaras dinâmicas ou fallback: `AAA-####` ou o padrão Mercosul `AAA#A##`.

### 3. Seleção de Máscara Dinâmica
O Maska v3 suporta a passagem de um array de máscaras:
- **Input Dinâmico de CPF/CNPJ**:
  ```html
  <input v-maska="['###.###.###-##', '##.###.###/####-##']" />
  ```
- **Input Dinâmico de Telefone** (Fixo de 8 dígitos vs. celular de 9 dígitos brasileiro):
  ```html
  <input v-maska="['(##) ####-####', '(##) #####-####']" />
  ```

### 4. Máscara de Moeda (Dinheiro)
Para formatar inputs monetários, utilize a configuração nativa de número (`number`) do Maska:
- Sempre defina a configuração para o padrão `pt-BR`:
  ```typescript
  const currencyOptions = {
    number: {
      fraction: 2,
      locale: 'pt-BR',
      prefix: 'R$ '
    }
  };
  ```

### 5. Remoção de Máscara e Sanitização de Dados
Nunca envie caracteres de formatação da máscara para a validação do backend AdonisJS. Sempre faça a sanitização:
- **Usando Vinculações Nativas do Maska**: Use o modificador `.unmasked`:
  ```html
  <input v-model="displayValue" v-maska:rawValue.unmasked="maskPattern" />
  ```
- **Usando Funções Utilitárias**: Limpe os caracteres de formatação utilizando a função `onlyNumbers(val)` do `@maxvue/max-use` antes de persistir o dado.
- **Persistência via MaxPinia**: O valor limpo (rawValue/E.164) deve ser atribuído ao campo da store `@maxvue/max-pinia`; o auto-save (debounced) da store envia ao backend. Não faça `axios.post`/submit manual para salvar inputs de página.

### 6. Validação de Input de Telefone
- Sempre prefira utilizar o componente pré-definido `MaxPhoneField` da biblioteca `MaxComponentsUi`, que encapsula a seleção de código de país (DDI) e a máscara de input dinâmica.
- Importe e use a função helper de validação `phone` de `@maxvue/max-use` (que utiliza internamente `libphonenumber-js`).
- Normalize o valor no formato estrito `E.164` antes de atribuí-lo ao campo da store MaxPinia (que persiste via auto-save):
  ```typescript
  const formatToE164 = (rawPhone: string): string => {
      const cleanDigits = rawPhone.replace(/\D/g, '');
      return cleanDigits ? `+${cleanDigits}` : '';
  };
  ```

### 7. Formatação e Validação de Cartões de Crédito
- **Formatação em Tempo Real**: Máscara padrão para número de cartão: `#### #### #### ####`. Máscara de data de validade: `##/##`.
- **Validação de Cartão**: Use o pacote `card-validator`:
  ```typescript
  import cardValidator from 'card-validator';
  const numberValidation = cardValidator.number(form.number);
  const expiryValidation = cardValidator.expirationDate(form.expiry);
  const cvvValidation = cardValidator.cvv(form.cvv, numberValidation.card?.code?.size || 3);
  ```
- **Detecção de Bandeira**: Use `@polvo-labs/card-type`:
  ```typescript
  import { cardType } from '@polvo-labs/card-type';
  const detectedBrand = cardType(form.number);
  ```
- Nunca persista dados brutos de cartão de crédito ou códigos CVV no `localStorage` ou `sessionStorage`.

## Restrições
- **Sem Valores Formatados para o Backend**: Nunca persista valores contendo caracteres de formatação de máscara no backend AdonisJS. Sempre grave strings limpas ou floats, ou formato `E.164` para telefones, nos campos da store `@maxvue/max-pinia`.
- **Sem Save Manual**: Não use `axios`/fetch manual nem submit de formulário para salvar inputs de página. A persistência ocorre pelo auto-save da store MaxPinia.
- **Sem Formatação/Validação Manual via Expressões Regulares**: Não utilize substituição de strings sob demanda (ad-hoc) ou regex complexos personalizados para validação ou formatação de dados padrão brasileiros ou telefones. Confie inteiramente nos arrays de diretivas do Maska, `libphonenumber-js` ou `card-validator`.
- **Sem Options API**: Todos os arquivos SFC do Vue devem utilizar estritamente `<script setup lang="ts">` e a Composition API.
- **Atributos em Linha Única**: Sempre mantenha todas as propriedades dos elementos HTML/Vue em linha única nos templates.
- **Conformidade de Idioma**: Todos os comentários no código de exemplos ou trechos de código do Vue devem estar estritamente escritos em português do Brasil (pt-BR).
