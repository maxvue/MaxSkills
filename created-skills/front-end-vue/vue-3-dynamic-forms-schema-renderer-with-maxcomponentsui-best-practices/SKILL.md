---
name: vue-3-dynamic-forms-schema-renderer-with-maxcomponentsui-best-practices
description: Use when designing, building, or refactoring dynamic form renderers, schema-based inputs, automatic fields generation, and validation layouts in Vue 3 using the MaxComponentsUi library and Zod. Triggers on schema-driven forms, custom dynamic inputs maps, reactive forms generation from JSON metadata, and fields layout binding (e.g. s50, s100 grids).
---

## Objetivo
Estabelecer padrões e arquiteturas comuns para a criação de renderizadores de formulários dinâmicos orientados por metadados no Vue 3. Esta skill integra componentes da biblioteca `@maxvue/max-components-ui` e utiliza o Zod para validação reativa baseada em esquemas.

## Instruções

## 1. Arquitetura de Definição de Esquema
Os campos do formulário devem ser representados por um esquema declarativo (objetos JSON ou TypeScript) que dita as características do campo, mapeamento do componente, configurações de layout e regras de validação.

### Definição da Interface do Campo em TypeScript
Sempre defina uma interface TypeScript estrita para modelar os esquemas dos seus campos.
```typescript
import { z } from 'zod';

export interface FormFieldSchema {
  key: string;
  label: string;
  component: 'MaxInputText' | 'MaxInputTextArea' | 'MaxSelect' | 'MaxSwitch';
  gridClass: 's33' | 's50' | 's100';
  props?: Record<string, any>;
  validation?: z.ZodTypeAny;
}
```

## 2. Mapeamento Dinâmico de Componentes
Em vez de duplicar templates com diretivas `v-if` para cada tipo de campo, mapeie os nomes dos componentes dinamicamente usando o mecanismo `<component :is="...">` do Vue.

```typescript
import { MaxInputText, MaxInputTextArea, MaxSelect, MaxSwitch } from '@maxvue/max-components-ui';

const componentMap = {
  MaxInputText,
  MaxInputTextArea,
  MaxSelect,
  MaxSwitch
};
```

## 3. Criando o Componente de Formulário Dinâmico
Construa um renderizador de formulário dinâmico SFC reutilizável. Mantenha os atributos na mesma linha no bloco `<template>`.

### Exemplo: `MaxDynamicForm.vue`
```vue
<template>
  <form class="max-dynamic-form" @submit.prevent="handleSubmit">
    <div class="form-grid">
      <!-- Mapeamento dinâmico dos componentes com atributos em uma única linha -->
      <div v-for="field in schema" :key="field.key" :class="['form-field', field.gridClass]">
        <component :is="componentMap[field.component]" v-model="formData[field.key]" v-bind="field.props" :label="field.label" :error="errors[field.key]" @update:model-value="clearError(field.key)" />
      </div>
    </div>
    
    <div class="form-actions">
      <slot name="actions">
        <MaxButton label="Salvar" type="submit" :loading="submitting" />
      </slot>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue';
import { z } from 'zod';
import { MaxButton, MaxInputText, MaxInputTextArea, MaxSelect, MaxSwitch } from '@maxvue/max-components-ui';
import type { FormFieldSchema } from './types';

const props = defineProps<{
  schema: FormFieldSchema[];
  modelValue: Record<string, any>;
  submitting?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', value: Record<string, any>): void;
  (e: 'submit', value: Record<string, any>): void;
}>();

// Estado reativo do formulário herdado do modelValue
const formData = ref<Record<string, any>>({ ...props.modelValue });
const errors = ref<Record<string, string>>({});

// Sincroniza estado de entrada com o formData interno
watch(() => props.modelValue, (newVal) => {
  formData.value = { ...newVal };
}, { deep: true });

// Sincroniza alterações locais com o pai
watch(formData, (newVal) => {
  emit('update:modelValue', newVal);
}, { deep: true });

const componentMap = {
  MaxInputText,
  MaxInputTextArea,
  MaxSelect,
  MaxSwitch
};

// Constrói o schema Zod dinamicamente a partir das regras de validação do formulário
const buildZodSchema = () => {
  const shape: Record<string, z.ZodTypeAny> = {};
  props.schema.forEach((field) => {
    if (field.validation) {
      shape[field.key] = field.validation;
    } else {
      shape[field.key] = z.any().optional();
    }
  });
  return z.object(shape);
};

const validate = (): boolean => {
  const validationSchema = buildZodSchema();
  const result = validationSchema.safeParse(formData.value);
  
  if (!result.success) {
    errors.value = result.error.errors.reduce((acc, err) => {
      const path = err.path.join('.');
      acc[path] = err.message;
      return acc;
    }, {} as Record<string, string>);
    return false;
  }
  
  errors.value = {};
  return true;
};

const clearError = (fieldKey: string) => {
  if (errors.value[fieldKey]) {
    delete errors.value[fieldKey];
  }
};

const handleSubmit = () => {
  if (validate()) {
    emit('submit', formData.value);
  }
};
</script>

<style scoped lang="scss">
.max-dynamic-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  .form-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;

    .form-field {
      display: flex;
      flex-direction: column;

      &.s33 {
        flex: 1 1 calc(33.333% - 1rem);
        min-width: 250px;
      }

      &.s50 {
        flex: 1 1 calc(50% - 1rem);
        min-width: 300px;
      }

      &.s100 {
        flex: 1 1 100%;
      }
    }
  }

  .form-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 1rem;
  }
}
</style>
```

## 4. Exemplo de Uso
Defina um componente que consome o renderizador de formulário dinâmico, mostrando como configurar campos com validações e opções específicas.

```vue
<template>
  <div class="agent-configuration">
    <h2>Configurações do Agente de IA</h2>
    <MaxDynamicForm :schema="formSchema" v-model="agentData" :submitting="saving" @submit="saveConfig" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { z } from 'zod';
import MaxDynamicForm from './components/MaxDynamicForm.vue';
import type { FormFieldSchema } from './components/types';
import { Toast } from '@maxvue/max-components-ui';

const saving = ref(false);

const agentData = ref({
  name: '',
  description: '',
  tone: 'professional',
  active: true
});

const formSchema: FormFieldSchema[] = [
  {
    key: 'name',
    label: 'Nome do Agente',
    component: 'MaxInputText',
    gridClass: 's50',
    validation: z.string().min(3, 'O nome deve ter pelo menos 3 caracteres').max(50, 'O nome não deve exceder 50 caracteres'),
    props: { placeholder: 'Ex: Assistente de Vendas' }
  },
  {
    key: 'tone',
    label: 'Tom de Voz',
    component: 'MaxSelect',
    gridClass: 's50',
    validation: z.string().min(1, 'O tom de voz é obrigatório'),
    props: {
      options: [
        { label: 'Profissional', value: 'professional' },
        { label: 'Amigável', value: 'friendly' },
        { label: 'Criativo', value: 'creative' }
      ]
    }
  },
  {
    key: 'description',
    label: 'Instruções de Comportamento',
    component: 'MaxInputTextArea',
    gridClass: 's100',
    validation: z.string().min(10, 'A descrição deve ter pelo menos 10 caracteres'),
    props: { placeholder: 'Descreva as instruções que o agente deve seguir...', rows: 4 }
  },
  {
    key: 'active',
    label: 'Ativo',
    component: 'MaxSwitch',
    gridClass: 's100',
    props: { label: 'Habilitar agente de IA nas redes sociais' }
  }
];

const saveConfig = async (data: Record<string, any>) => {
  saving.value = true;
  try {
    // Lógica para enviar dados à API
    Toast.show({ severity: 'success', title: 'Sucesso', message: 'Configurações do agente salvas!' });
  } catch (error) {
    Toast.show({ severity: 'error', title: 'Erro', message: 'Falha ao salvar as configurações.' });
  } finally {
    saving.value = false;
  }
};
</script>
```

## Restrições
* **Apenas Composition API**: Nunca utilize a Options API. Sempre use `<script setup lang="ts">`.
* **TypeScript Obrigatório**: Todos os scripts devem ser totalmente tipados. Use `lang="ts"`.
* **SCSS Obrigatório**: Todas as estilizações devem ser escritas em SCSS e com escopo local (`scoped`).
* **Estilo de Parâmetro do Componente em Linha**: Dentro de `<template>`, mantenha todos os atributos/props do componente em uma única linha. Não os divida em várias linhas.
* **Idioma dos Comentários de Código**: Todos os comentários dentro dos componentes Vue/TS devem ser escritos em Português do Brasil (pt-BR).
* **Validação Segura**: Sempre use `.safeParse()` do Zod. Não use `.parse()` para evitar exceções não tratadas em tempo de execução.
