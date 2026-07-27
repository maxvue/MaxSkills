---
name: vue-inputs-masks-validation-best-practices
description: Use ao implementar, formatar ou validar inputs com máscaras em componentes Vue 3 do EngeApp usando Maska v3 e libphonenumber-js, além de card-validator e @polvo-labs/card-type (ambos já instalados no projeto). Acione ao configurar telefone, CPF, CNPJ, moeda, CEP, placa de veículo e cartão de crédito, tratar máscaras dinâmicas e fazer validação/unmask antes de persistir na store @maxvue/max-pinia.
---

# Boas Práticas de Inputs, Máscaras e Validação no Vue 3

## Objetivo
Estabelecer padrões claros e de alta qualidade de desenvolvimento para a aplicação de máscaras e validações de input em formulários no front-end Vue 3 do Engeapp. Isso garante uma interface consistente, tratamento dinâmico de máscaras, validação de cartões de crédito e telefones, e a extração automática do valor bruto sem formatação (unmasked) antes da persistência dos dados via store `@maxvue/max-pinia` no backend Laravel 13.

## Instruções

> **Prefira os componentes MaxComponentsUi já mascarados.** Em código de aplicação, para os casos cobertos use **sempre** os inputs dedicados do MaxComponentsUi em vez de `<input>` nativo + `v-maska`: `MaxInputCpfCnpj` (CPF/CNPJ), `MaxInputCep` (CEP), `MaxInputNumber` (moeda/número) e, para telefone, `MaxInputPhoneMail` **ou** `MaxPhoneField` conforme o caso (ver critério abaixo). A diretiva `v-maska` em elemento nativo, mostrada abaixo, é a camada de baixo nível — use-a apenas para máscaras **ainda não cobertas** por um componente Max (ex.: placa de veículo), de preferência encapsulada num componente próprio, nunca como `<input>` solto numa página.
>
> **Telefone — qual componente escolher:**
> - **`MaxPhoneField`**: use quando precisar de seleção de país/DDI. Encapsula um `Select` de bandeiras (`country_ddi_flags`) + input mascarado dinâmico e emite via `v-model` o valor concatenado `DDI + dígitos, sem '+'` (ex.: `5511999999999`) — não E.164. É o componente indicado para telefone/WhatsApp internacional.
> - **`MaxInputPhoneMail`**: use no campo **combinado** que aceita telefone **ou** e-mail. Sem hints (`attrs.phone`/`whatsapp`/`zap` ou `attrs.email`/`mail`/`e-mail`), detecta automaticamente qual o usuário digitou (letras vs. dígitos); com um hint explícito, o modo é forçado antes da digitação. Valida telefone com `libphonenumber-js` (país `'BR'`) e e-mail por regex, aplicando máscara dinâmica com `v-maska:unmaskedValue.unmasked`. É o indicado quando o mesmo campo deve aceitar os dois formatos (ex.: login por e-mail ou WhatsApp).

### 1. Registro e Configuração de Componentes (Maska)
- Sempre utilize a Composition API (`<script setup lang="ts">`) e SCSS (`lang="scss"` com escopo `scoped`) para os componentes.
- Importe a diretiva `vMaska` diretamente do pacote `maska/vue`:
  ```typescript
  import { vMaska } from 'maska/vue';
  ```
- Aplique a diretiva nos seus elementos de input.

### 2. Máscaras de Padrões Brasileiros
Garanta que as máscaras usem exatamente estes padrões de caracteres:
- **CPF**: `###.###.###-##` (o `MaxInputCpfCnpj` usa internamente `###.###.###-##@`, com um token `@` extra opcional)
- **CNPJ**: `##.###.###/####-##`
- **CEP**: `##.### - ###` (é a máscara real usada pelo `MaxInputCep`, com pontuação/espaçamento diferente de `#####-###`)
- **Placa de Veículo (Mercosul e Legado)**: Use máscaras dinâmicas ou fallback: `AAA-####` ou o padrão Mercosul `AAA#A##`.

### 3. Seleção de Máscara Dinâmica
> Orientação prescritiva sem precedente de uso no engeapp — `v-maska` cru hoje só é usado dentro dos próprios componentes do MaxComponentsUi, nunca solto em código de aplicação.

O Maska v3 suporta a passagem de um array de máscaras:
- **Input Dinâmico de Telefone** (Fixo de 8 dígitos vs. celular de 9 dígitos brasileiro):
  ```html
  <input v-maska="['(##) ####-####', '(##) #####-####']" />
  ```

### 4. Máscara de Moeda (Dinheiro)
Para inputs monetários/numéricos em código de aplicação, use o componente `MaxInputNumber` do MaxComponentsUi. Ele **não** usa o modo `number` do Maska: internamente encapsula `primevue/inputnumber`, expondo props como `prefix`, `suffix` e `minFractionDigits` (padrão `2`). O `v-model` já entrega o valor numérico limpo (não formatado), pronto para persistir na store — não há passo de unmask manual.
- Exemplo de uso para moeda em `pt-BR`:
  ```html
  <MaxInputNumber v-model="form.valor" prefix="R$ " :minFractionDigits="2" />
  ```

### 5. Remoção de Máscara e Sanitização de Dados
Nunca envie caracteres de formatação da máscara para a validação do backend Laravel (FormRequest / `$request->validate()`). Sempre faça a sanitização — o backend rejeita entradas inválidas com resposta `422` no shape `{ message, errors: { campo: ["..."] } }`:
- **Usando Vinculações Nativas do Maska**: Use o modificador `.unmasked`:
  ```html
  <input v-model="displayValue" v-maska:rawValue.unmasked="maskPattern" />
  ```
- **Usando Funções Utilitárias**: Limpe os caracteres de formatação utilizando a função `onlyNumbers(val)` do `@maxvue/max-use` antes de persistir o dado.
- **Helpers de formatação/validação do `@maxvue/max-use`** (auto-importados): para EXIBIÇÃO, prefira `formatCep`, `formatCpf`, `formatCnpj`, `formatCpfCnpj`, `formatPhone` e `maskSensitive`; para validação, `isCpf`, `isCnpj`, `isCpfCnpj`, `cepIsValid`, `isEmail` e `phone` (este último usa `libphonenumber-js` internamente). São a via preferencial antes de recorrer a Maska/libphonenumber-js/card-validator crus.
- **Persistência via MaxPinia**: O valor limpo (rawValue/DDI+dígitos) deve ser atribuído ao campo da store `@maxvue/max-pinia`; o auto-save (debounced) da store envia ao backend.

### 6. Validação de Input de Telefone
- Use o componente pré-definido do `MaxComponentsUi` conforme o critério da seção de Instruções: `MaxPhoneField` quando precisar de seleção de código de país (DDI) — ele encapsula o `Select` de bandeiras e a máscara dinâmica; `MaxInputPhoneMail` no campo combinado telefone/e-mail. Neste último, os atributos `attrs.phone`/`whatsapp`/`zap` e `attrs.email`/`mail`/`e-mail` (lidos em `onMounted`) são hints explícitos que FORÇAM o modo do campo antes de qualquer digitação; se nenhum for passado, a detecção é automática pelo que o usuário digita (letras vs. dígitos, via computed interno), não pelos attrs.
- Importe e use a função helper de validação `phone` de `@maxvue/max-use` (que utiliza internamente `libphonenumber-js`) apenas para VALIDAR — não para reformatar em E.164 antes de persistir.
- **Contrato real de persistência: DDI + dígitos, sem `+`** (ex.: `5511999999999`) — é o que `MaxPhoneField` emite via `v-model` e o que `PhoneClass::getInternationalPhoneNumber` grava no backend. NÃO normalize para E.164 estrito (com `+`) antes de atribuir à store: um valor com `+` seria descartado pelo próprio `MaxPhoneField`/`MaxInputPhoneMail`, que removem tudo que não é dígito antes de compor o valor.

### 7. Formatação e Validação de Cartões de Crédito
> Orientação prescritiva sem precedente de uso no engeapp — `card-validator` e `@polvo-labs/card-type` estão instalados mas sem nenhuma ocorrência real no código.

- **Dependências já instaladas:** `card-validator` (`^10.0.4`) e `@polvo-labs/card-type` (`^0.0.3`) já constam no `package.json` do EngeApp — importe-os direto, sem `npm i`.
- Nunca persista dados brutos de cartão de crédito ou códigos CVV no `localStorage` ou `sessionStorage`.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Sem Valores Formatados para o Backend**: Nunca persista valores contendo caracteres de formatação de máscara no backend Laravel. Sempre grave strings limpas ou floats, ou o formato `DDI + dígitos sem '+'` para telefones (ex.: `5511999999999`), nos campos da store `@maxvue/max-pinia`.
- **Sem Save Manual**: Não use `axios`/fetch manual nem submit de formulário para salvar inputs de página. A persistência ocorre pelo auto-save da store MaxPinia.
- **Sem Formatação/Validação Manual via Expressões Regulares**: Não utilize substituição de strings sob demanda (ad-hoc) ou regex complexos personalizados para validação ou formatação de dados padrão brasileiros ou telefones. Prefira primeiro os helpers de `@maxvue/max-use` (seção 5); use os arrays de diretivas do Maska, `libphonenumber-js` ou `card-validator` como camada de baixo nível.
- **Sem Options API**: Todos os arquivos SFC do Vue devem utilizar estritamente `<script setup lang="ts">` e a Composition API.
- **Atributos em Linha Única**: Sempre mantenha todas as propriedades dos elementos HTML/Vue em linha única nos templates.
- **Conformidade de Idioma**: Todos os comentários no código de exemplos ou trechos de código do Vue devem estar estritamente escritos em português do Brasil (pt-BR).
