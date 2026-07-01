---
name: vue-boleto-utils-best-practices
description: Use when validating, formatting, parsing, or handling bank slip data (boletos) in the frontend Vue 3 application using the @mrmgomes/boleto-utils library. Triggers on validation of digit lines (linha digitável) or barcodes, extraction of expiration dates, calculating slip values, and formatting inputs for boleto payments.
---

# Boas Práticas para Vue Boleto Utils

## Objetivo
Estabelecer diretrizes consistentes e padrões práticos de código para validar, formatar e manipular dados de boletos bancários no frontend Vue 3 utilizando a biblioteca `@mrmgomes/boleto-utils`.

## Instruções

### 1. Visão Geral da Biblioteca e Integração da API
A biblioteca `@mrmgomes/boleto-utils` fornece funções utilitárias limpas para validação de boletos brasileiros. A função principal a ser utilizada é `validarBoleto`.

APIs chaves a serem importadas e utilizadas:
```typescript
import { validarBoleto } from '@mrmgomes/boleto-utils';
```

`validarBoleto(codigo: string)` retorna um objeto de resposta estruturado:
```typescript
interface Boleto {
    sucesso: boolean;
    mensagem: string;
    tipoCodigoInput: 'CODIGO_DE_BARRAS' | 'LINHA_DIGITAVEL';
    tipoBoleto: 'ARRECADACAO_PREFEITURA' | 'CONVENIO_SANEAMENTO' | 'CONVENIO_ENERGIA_ELETRICA_E_GAS' | 'CONVENIO_TELECOMUNICACOES' | 'ARRECADACAO_ORGAOS_GOVERNAMENTAIS' | 'OUTROS' | 'ARRECADACAO_TAXAS_DE_TRANSITO' | 'BANCO';
    codigoBarras: string;
    linhaDigitavel: string;
    vencimento: string; // ISO date string
    vencimentoApos22022025: string; // ISO date string (suporta atualização do fator de 2025)
    valor: number;
}
```

### 2. Fluxo de Validação de Input de Formulário
Ao construir campos de formulário para capturar informações de boleto:
1. **Sanitizar Entrada:** Sempre remova caracteres não numéricos antes de enviar o código para `validarBoleto` (ex: `code.replace(/\D/g, '')`).
2. **Tratar Entrada Incompleta:** Não execute a validação em entradas muito curtas. Aguarde até que o comprimento limpo seja de pelo menos 40 caracteres (códigos de barras padrão possuem 44 dígitos, linhas digitáveis possuem 47 ou 48).
3. **Tratar Erros de Tempo de Execução:** Envolva a chamada de `validarBoleto` em um bloco `try/catch`, pois a biblioteca pode lançar erros internos para entradas muito malformadas.
4. **Preferir Composition API & TypeScript:** Encapsule a lógica de validação dentro de composables Vue reutilizáveis (`useBoleto`) para permitir que vários componentes compartilhem a lógica.

### 3. Ordem dos Blocos SFC
Sempre estruture componentes nesta ordem exata:
1. `<template>`
2. `<script lang="ts">` ou `<script setup lang="ts">`
3. `<style lang="scss">` ou `<style scoped lang="scss">`

Mantenha os atributos dos elementos do template em linha única para evitar poluição visual de múltiplas linhas.

---

## Examples

### Composable Reutilizável (`useBoleto.ts`)
```typescript
import { ref, computed } from 'vue';
import { validarBoleto, type Boleto } from '@mrmgomes/boleto-utils';

// Estado interno da validação: ou um Boleto válido da lib, ou apenas
// sucesso/mensagem. Nunca fabricamos campos que violem a union de Boleto
// (ex: tipoCodigoInput precisa ser 'CODIGO_DE_BARRAS' | 'LINHA_DIGITAVEL').
type ResultadoValidacao =
  | Boleto
  | { sucesso: false; mensagem: string };

export function useBoleto() {
  const boletoCode = ref<string>('');

  const validation = computed<ResultadoValidacao>(() => {
    const cleanCode = boletoCode.value.replace(/\D/g, '');

    if (cleanCode.length < 40) {
      return { sucesso: false, mensagem: 'Código incompleto' };
    }

    try {
      return validarBoleto(cleanCode);
    } catch (error) {
      return {
        sucesso: false,
        mensagem: error instanceof Error ? error.message : 'Código de boleto inválido'
      };
    }
  });

  const isValid = computed(() => validation.value.sucesso);
  const errorMessage = computed(() => !isValid.value ? validation.value.mensagem : '');
  // Só expõe os dados completos quando a validação foi bem-sucedida.
  const boletoData = computed<Boleto | null>(() =>
    validation.value.sucesso ? (validation.value as Boleto) : null
  );

  return {
    boletoCode,
    isValid,
    errorMessage,
    boletoData
  };
}
```

### Componente Vue 3 Integrado (`BoletoField.vue`)
```vue
<template>
  <div class="boleto-field">
    <MaxInputText v-model="boletoCode" label="Linha Digitável / Código de Barras" placeholder="00000.00000 00000.000000..." :error="error" mono @update:model-value="validate" />

    <div v-if="isValid && details" class="boleto-field__details">
      <div class="detail-row"><span>Valor:</span> <strong>R$ {{ details.valor.toFixed(2) }}</strong></div>
      <div class="detail-row"><span>Vencimento:</span> <strong>{{ formatDate(details.vencimentoApos22022025 || details.vencimento) }}</strong></div>
      <div class="detail-row"><span>Tipo:</span> <strong>{{ details.tipoBoleto }}</strong></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { validarBoleto, type Boleto } from '@mrmgomes/boleto-utils';
// MaxInputText é auto-importado via unplugin-vue-components (presetMaxUno / @maxvue/max-components-ui).

// Definição das propriedades e eventos
const emit = defineEmits<{
  (e: 'valid', payload: { code: string; value: number; vencimento: string }): void;
  (e: 'invalid', message: string): void;
}>();

const boletoCode = ref<string>('');
const error = ref<string>('');
const isValid = ref<boolean>(false);
const details = ref<Boleto | null>(null);

// Formata a data ISO para exibição local em pt-BR
const formatDate = (dateStr: string): string => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('pt-BR', { timeZone: 'UTC' });
};

// Executa a validação e atualiza os estados reativos
const validate = () => {
  const cleanCode = boletoCode.value.replace(/\D/g, '');
  
  if (cleanCode.length === 0) {
    error.value = '';
    isValid.value = false;
    details.value = null;
    return;
  }

  if (cleanCode.length < 40) {
    error.value = 'Código incompleto. Continue digitando...';
    isValid.value = false;
    details.value = null;
    emit('invalid', error.value);
    return;
  }

  try {
    const result = validarBoleto(cleanCode);
    if (result.sucesso) {
      error.value = '';
      isValid.value = true;
      details.value = result;
      emit('valid', {
        code: cleanCode,
        value: result.valor,
        vencimento: result.vencimentoApos22022025 || result.vencimento
      });
    } else {
      error.value = result.mensagem || 'Código de boleto inválido';
      isValid.value = false;
      details.value = null;
      emit('invalid', error.value);
    }
  } catch (err: any) {
    error.value = err.message || 'Erro de validação';
    isValid.value = false;
    details.value = null;
    emit('invalid', error.value);
  }
};
</script>

<style scoped lang="scss">
// O input em si é o MaxInputText (label, foco e estado de erro já vêm do
// componente de tema). Aqui estilizamos apenas o bloco de detalhes,
// usando variáveis do tema — sem cores hexadecimais estáticas.
.boleto-field {
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-bottom: 1rem;

  &__details {
    margin-top: 0.75rem;
    padding: 0.75rem;
    background-color: var(--max-surface-2);
    border: 1px solid var(--max-border);
    border-radius: var(--max-radius);
    font-size: 0.875rem;
    color: var(--max-text);

    .detail-row {
      display: flex;
      justify-content: space-between;
      margin-bottom: 0.25rem;

      &:last-child {
        margin-bottom: 0;
      }
    }
  }
}
</style>
```

---

## Restrições
* **Sempre sanitizar entradas:** Nunca envie espaços de formatação, pontos ou traços diretamente para `@mrmgomes/boleto-utils`.
* **Envolver a validação em try/catch:** A biblioteca pode lançar exceções não tratadas em tempo de execução para números extremamente malformados.
* **Ordenação de componentes:** Componentes Vue devem seguir a ordem `<template>`, `<script setup lang="ts">` e `<style lang="scss">` sem exceções.
* **Atributos de template em linha única:** Dentro de templates, formate elementos Vue mantendo todos os parâmetros/atributos em linha única.
* **Comentários em Português Brasileiro:** Dentro de arquivos de código do projeto (ex: componentes Vue ou Composables criados para o Engeapp), escreva os comentários de código no idioma **Português do Brasil (pt-BR)**.
