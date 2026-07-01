---
name: vue-zod-schema-validation-best-practices
description: Use when designing front-end forms in Vue 3, defining validation schemas with Zod, parsing API request payloads, or displaying reactive input validation errors using TypeScript. Triggers on z.object, schema.safeParse, ZodError mapping, and dynamic form validation feedback.
---

# Boas Práticas de Validação com Esquema Zod no Vue 3

## Objetivo
Estabelecer padrões de validação de formulários reativos, análise de payload de requisições e mapeamento de erros de API no Vue 3 usando esquemas Zod e TypeScript.

## Instruções

### 1. Definição de Esquemas e Inferência de Tipos
- Defina todos os esquemas Zod em arquivos dedicados sob um diretório de esquemas (ex: `resources/Vue/Schemas/`). Nomeie-os utilizando o sufixo `.schema.ts`.
- Sempre infira e exporte os tipos do TypeScript diretamente dos esquemas Zod usando `z.infer`. Não duplique definições de interfaces manualmente.
- Exemplo (`resources/Vue/Schemas/gerador.schema.ts`):
  ```typescript
  import { z } from 'zod';

  export const GeradorSchema = z.object({
      nome: z.string()
          .min(3, 'O nome deve ter pelo menos 3 caracteres')
          .max(100, 'O nome não pode exceder 100 caracteres'),
      potencia_kwp: z.number()
          .positive('A potência (kWp) deve ser maior que zero'),
      inversores: z.array(z.string())
          .min(1, 'Selecione pelo menos um inversor'),
      observacoes: z.string()
          .max(2200, 'As observações não podem exceder 2200 caracteres')
          .optional()
          .nullable(),
  });

  export type GeradorInput = z.infer<typeof GeradorSchema>;
  ```

### 2. Validação Reativa de Formulários no Vue 3
- Sempre utilize a Composition API (`<script setup lang="ts">`).
- Utilize `safeParse` para a análise e validação para evitar o lançamento de exceções de runtime não tratadas.
- Implemente um helper de validação de formulário reativo ou um composable personalizado (como `useFormValidation`) para gerenciar os erros de validação dos campos, estados dinâmicos de modificação (dirty states) e limpar os erros à medida que o usuário modifica os inputs.
- Todos os comentários de código dentro dos arquivos Vue/TS devem ser escritos em português brasileiro (pt-BR).
- Exemplo de Composable:
  ```typescript
  import { ref, watch } from 'vue';
  import { ZodSchema } from 'zod';

  export function useFormValidation<T>(schema: ZodSchema<T>, formData: any) {
      const errors = ref<Record<string, string>>({});
      const isValid = ref(true);

      const validate = (): boolean => {
          const result = schema.safeParse(formData);
          if (!result.success) {
              // API atual do Zod: use result.error.issues (errors é alias legado)
              errors.value = result.error.issues.reduce((acc, err) => {
                  const path = err.path.join('.');
                  acc[path] = err.message;
                  return acc;
              }, {} as Record<string, string>);
              isValid.value = false;
              return false;
          }
          errors.value = {};
          isValid.value = true;
          return true;
      };

      // Limpa os erros de um campo específico quando modificado
      const clearError = (field: string) => {
          if (errors.value[field]) {
              delete errors.value[field];
          }
      };

      return { errors, isValid, validate, clearError };
  }
  ```

### 3. Associação (Binding) com Componentes Vue
- Associe o estado de validação diretamente aos inputs do componente (ex: usando propriedades como `error` ou `errorMessage` nos inputs do `@maxvue/max-components-ui`).
- Formate os elementos do componente dentro do bloco `<template>` mantendo todos os atributos/parâmetros na mesma linha. Não quebre os atributos em várias linhas.
- Exemplo de Componente:
  ```vue
  <template>
    <form @submit.prevent="handleSubmit">
      <!-- Mantenha os atributos na mesma linha -->
      <MaxInputText label="Nome" v-model="form.nome" :error="errors.nome" @update:model-value="clearError('nome')" />
      <MaxInputNumber label="Potência (kWp)" v-model="form.potencia_kwp" :error="errors.potencia_kwp" @update:model-value="clearError('potencia_kwp')" />
      <MaxButton label="Salvar" type="submit" :loading="saving" />
    </form>
  </template>

  <script setup lang="ts">
  import { ref, reactive } from 'vue';
  import { GeradorSchema } from '../Schemas/gerador.schema';
  import { useFormValidation } from '../Composables/useFormValidation';
  import { Toast } from '@maxvue/max-components-ui';
  // O salvamento de dados de página passa pela store MaxPinia (auto-save/debounced),
  // não por axios manual. Aqui usamos a store de geradores fotovoltaicos.
  import { useGeradorStore } from '../Stores/gerador';

  const geradorStore = useGeradorStore();

  const form = reactive({
      nome: '',
      potencia_kwp: 0,
      inversores: [],
      observacoes: ''
  });

  const saving = ref(false);
  const { errors, validate, clearError } = useFormValidation(GeradorSchema, form);

  const handleSubmit = async () => {
      // Validação local antes de enviar
      if (!validate()) {
          Toast.show({ severity: 'warn', title: 'Validação', message: 'Por favor, corrija os erros do formulário.' });
          return;
      }

      saving.value = true;
      try {
          // Persiste via store @maxvue/max-pinia: joga o form validado no data da store e
          // o auto-save (debounce) dispara sozinho; force o POST imediato com saveInServer().
          Object.assign(geradorStore.data, form);
          await geradorStore.saveInServer();
          Toast.show({ severity: 'success', title: 'Sucesso', message: 'Gerador cadastrado com sucesso!' });
      } catch (err: any) {
          // Trata erro de validação retornado pelo backend Adonis/VineJS (HTTP 422)
          if (err.response?.status === 422 && err.response?.data?.errors) {
              // Mapeia erros 422 de validação vindos do backend Adonis/VineJS
              err.response.data.errors.forEach((e: any) => {
                  errors.value[e.field] = e.message;
              });
          } else {
              Toast.show({ severity: 'error', title: 'Erro', message: 'Falha ao salvar gerador.' });
          }
      } finally {
          saving.value = false;
      }
  };
  </script>
  ```

### 4. Tratamento de Erros de Validação da API (Integração com VineJS/AdonisJS)
- Converta dinamicamente as respostas de erro de validação do backend (HTTP 422) para o estado local de erros do frontend.
- Os erros do backend geralmente vêm em um formato estruturado:
  ```json
  {
    "errors": [
      { "field": "nome", "message": "O nome é obrigatório" }
  ]
  }
  ```
- Mapeie estes erros diretamente para o objeto reativo de erros dentro do bloco `catch` das requisições de API, conforme demonstrado no exemplo acima.

## Restrições
- NÃO utilize a Options API. Sempre utilize a Composition API (`<script setup lang="ts">`).
- NÃO utilize `.parse()` para validação de formulários; use `.safeParse()` em vez disso para evitar erros de execução não tratados.
- NÃO escreva comentários de código em outro idioma que não seja o português do Brasil (pt-BR).
- NÃO quebre atributos ou propriedades de componentes no bloco `<template>` em várias linhas. Mantenha todos os atributos de uma tag na mesma linha.
- NÃO escreva manualmente estruturas de interfaces que dupliquem definições do Zod; sempre use `z.infer`.
