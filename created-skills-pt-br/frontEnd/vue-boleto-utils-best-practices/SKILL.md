---
name: vue-boleto-utils-best-practices
description: "Use when validating, formatting, parsing, or handling bank slip data (boletos) in Vue 3 using @mrmgomes/boleto-utils: digit lines, barcodes, expiration dates, values, and payment input formatting. Covers objectives and core workflows."
author: Johnattas Conrady Gomes Santana
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
    tipoCodigoInput: string; // o .d.ts real tipa como string solto; a union 'CODIGO_DE_BARRAS' | 'LINHA_DIGITAVEL' (TipoCodigoInput) só é usada como retorno de identificarTipoCodigo, não neste campo
    tipoBoleto: 'ARRECADACAO_PREFEITURA' | 'CONVENIO_SANEAMENTO' | 'CONVENIO_ENERGIA_ELETRICA_E_GAS' | 'CONVENIO_TELECOMUNICACOES' | 'ARRECADACAO_ORGAOS_GOVERNAMENTAIS' | 'OUTROS' | 'ARRECADACAO_TAXAS_DE_TRANSITO' | 'BANCO';
    codigoBarras: string;
    linhaDigitavel: string;
    vencimento: Date; // objeto Date do JS (não string)
    vencimentoComNovoFator2025: Date; // objeto Date do JS (suporta atualização do fator de 2025)
    valor: number;
}
```

> **Atenção aos tipos:** o `boleto-utils.d.ts` que a lib publica está incorreto — declara `vencimentoApos22022025: string` (e não inclui `vencimentoComNovoFator2025`), mas o runtime (`boleto-utils.js`) na verdade atribui `vencimentoComNovoFator2025` e ambos os campos de vencimento são objetos `Date` do JS (as funções internas fazem `return dataBoleto.toDate()`), não strings. Como o `.d.ts` publicado não bate com o runtime, o `vue-tsc` do projeto rejeita o uso direto desses campos — resolva isso com uma augmentation local de módulo no projeto, por exemplo em um `.d.ts` próprio:
> ```typescript
> declare module '@mrmgomes/boleto-utils' {
>   interface Boleto {
>     vencimento: Date;
>     vencimentoComNovoFator2025: Date;
>   }
> }
> ```
> Confie no runtime, não no `.d.ts` publicado pela lib.

### 2. Fluxo de Validação de Input de Formulário
Ao construir campos de formulário para capturar informações de boleto:
1. **Sanitizar Entrada:** Sempre remova caracteres não numéricos antes de enviar o código para `validarBoleto` (ex: `code.replace(/\D/g, '')`).
2. **Tratar Entrada Incompleta:** Não execute a validação em entradas muito curtas. A lib normaliza internamente 36 dígitos (linha digitável de cartão de crédito Itaú, +11 zeros) e 46 dígitos (+1 zero) para 47 antes de validar; depois disso ela só aceita os comprimentos 36, 44, 46, 47 ou 48 e retorna `sucesso: false` para qualquer outro comprimento — inclusive 45 (código de barras = 44; linha digitável = 36/46 [cartão de crédito], 47 [bancário/cobrança] ou 48 [convênio/arrecadação]). O guard `cleanCode.length < 36` é apenas um heurístico de "ainda digitando" para não disparar erro cedo demais; ele NÃO garante validade — comprimentos como 45 continuam inválidos e serão rejeitados pela própria lib, que reporta a mensagem correspondente em `retorno.mensagem`.
3. **Tratar Erros de Tempo de Execução:** Envolva a chamada de `validarBoleto` em um bloco `try/catch`, pois a biblioteca pode lançar erros internos para entradas muito malformadas.
4. **Preferir Composition API & TypeScript:** Encapsule a lógica de validação dentro de composables Vue reutilizáveis (`useBoleto`) para permitir que vários componentes compartilhem a lógica.

> Para ordem dos blocos SFC, Composition API e demais convenções gerais de estilo, ver a skill `vue-eslint-stylelint-quality-standards`.

---

## Exemplos

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

    // Heurístico de "ainda digitando" (ver Seção 2, item 2, para os comprimentos aceitos).
    if (!([36, 44, 46, 47, 48].includes(cleanCode.length))) {
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
    <MaxInputText v-model="boletoCode" label="Linha Digitável / Código de Barras" placeholder="00000.00000 00000.000000..." :error="errorMessage" />

    <div v-if="isValid && boletoData" class="boleto-field__details">
      <div class="detail-row"><span>Valor:</span> <strong>R$ {{ boletoData.valor.toFixed(2) }}</strong></div>
      <div class="detail-row"><span>Vencimento:</span> <strong>{{ formatDate(boletoData.vencimentoComNovoFator2025 || boletoData.vencimento) }}</strong></div>
      <div class="detail-row"><span>Tipo:</span> <strong>{{ boletoData.tipoBoleto }}</strong></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { watch } from 'vue';
import { useBoleto } from '@/composables/useBoleto';
// MaxInputText é auto-importado via unplugin-vue-components (presetMaxUno / @maxvue/max-components-ui).

// O componente consome o composable useBoleto — toda a lógica de sanitização,
// guard de comprimento e try/catch vive lá (fonte única de verdade), evitando
// reimplementar a validação aqui.
const emit = defineEmits<{
  (e: 'valid', payload: { code: string; value: number; vencimento: Date }): void;
  (e: 'invalid', message: string): void;
}>();

const { boletoCode, isValid, errorMessage, boletoData } = useBoleto();

// Formata o objeto Date (retornado pela lib) para exibição local em pt-BR
const formatDate = (date: Date | null | undefined): string => {
  if (!date) return '';
  return date.toLocaleDateString('pt-BR', { timeZone: 'UTC' });
};

// Reage às mudanças do estado derivado do composable para emitir os eventos.
watch([isValid, boletoData, errorMessage], () => {
  if (isValid.value && boletoData.value) {
    emit('valid', {
      code: boletoCode.value.replace(/\D/g, ''),
      value: boletoData.value.valor,
      vencimento: boletoData.value.vencimentoComNovoFator2025 || boletoData.value.vencimento
    });
  } else if (errorMessage.value) {
    emit('invalid', errorMessage.value);
  }
});
</script>
```

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Comentários em Português Brasileiro:** Dentro de arquivos de código do projeto (ex: componentes Vue ou Composables criados para o Engeapp), escreva os comentários de código no idioma **Português do Brasil (pt-BR)**.
