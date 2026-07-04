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
  component: 'MaxInputText' | 'MaxInputTextArea' | 'MaxInputSelect' | 'MaxInputSwitch';
  gridClass: 's33' | 's50' | 's100';
  props?: Record<string, any>;
  validation?: z.ZodTypeAny;
}
```

## 2. Mapeamento Dinâmico de Componentes
Em vez de duplicar templates com diretivas `v-if` para cada tipo de campo, mapeie os nomes dos componentes dinamicamente usando o mecanismo `<component :is="...">` do Vue.

Os componentes `@maxvue/max-components-ui` são resolvidos por auto-import (`unplugin-vue-components`); **não** os importe manualmente. Como `<component :is="...">` exige uma referência, use `resolveComponent` para obter o componente registrado a partir do nome em string.

> **Atenção:** `resolveComponent()` só funciona dentro de `setup()` ou de uma função de render — nunca no escopo de módulo (top level). O snippet abaixo é ilustrativo; na prática, declare o `componentMap` **dentro do `<script setup>` do SFC** (como na versão de `MaxDynamicForm.vue` mais adiante), não em um módulo isolado.

```typescript
// Dentro de setup()/<script setup> — resolveComponent é auto-importado no SFC.
const componentMap = {
  MaxInputText: resolveComponent('MaxInputText'),
  MaxInputTextArea: resolveComponent('MaxInputTextArea'),
  MaxInputSelect: resolveComponent('MaxInputSelect'),
  MaxInputSwitch: resolveComponent('MaxInputSwitch')
};
```

## 3. Criando o Componente de Formulário Dinâmico
Construa um renderizador de formulário dinâmico SFC reutilizável. Mantenha os atributos na mesma linha no bloco `<template>`.

### Exemplo: `MaxDynamicForm.vue`
```vue
<template>
  <form class="max-dynamic-form" @submit.prevent="handleSubmit">
    <!-- Use sempre <MaxGrid> (nunca <MaxGridCols>) em formulários. O dimensionamento vem de atributos UnoCSS em cada campo:
         largura percentual s-[porcentagem] (ex.: s-30 = 30% da largura do formulário; s33/s50/s100 são atalhos de 33/50/100%)
         e limites [w|h]-[max|min]-[valor] (px sem unidade ou rem: w-max-300, h-min-50, w-min-10rem). Nunca monte grids/larguras manuais. -->
    <MaxGrid>
      <!-- Mapeamento dinâmico dos componentes com atributos em uma única linha -->
      <component :is="componentMap[field.component]" v-for="field in schema" :key="field.key" :class="field.gridClass" v-model="formData[field.key]" v-bind="field.props" :label="field.label" :error="errors[field.key]" @update:model-value="clearError(field.key)" />
    </MaxGrid>

    <div class="form-actions">
      <slot name="actions">
        <MaxButton label="Salvar" type="submit" :loading="submitting" />
      </slot>
    </div>
  </form>
</template>

<script setup lang="ts">
// ref/reactive/watch e os componentes Max sao auto-importados (unplugin-auto-import / unplugin-vue-components). Nao os importe manualmente.
import { z } from 'zod';
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
  MaxInputText: resolveComponent('MaxInputText'),
  MaxInputTextArea: resolveComponent('MaxInputTextArea'),
  MaxInputSelect: resolveComponent('MaxInputSelect'),
  MaxInputSwitch: resolveComponent('MaxInputSwitch')
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
    // Zod 4: use .issues (a antiga .errors foi removida)
    errors.value = result.error.issues.reduce((acc, err) => {
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
  // O grid e o dimensionamento das colunas (s33/s50/s100) sao responsabilidade do <MaxGrid> + UnoCSS (presetMaxUno). Nao reimplemente grid manual aqui.
  display: flex;
  flex-direction: column;
  gap: 1.5rem;

  .form-actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 1rem;
  }
}
</style>
```

## 4. Exemplo de Uso
Defina um componente que consome o renderizador de formulário dinâmico, mostrando como configurar campos com validações e opções específicas. Os dados de página vêm de uma store `@maxvue/max-pinia`: a store faz o GET inicial e persiste as alterações com auto-save (debounced), dispensando requisições/salvamentos manuais.

```vue
<template>
  <div class="inverter-configuration">
    <MaxTitle1>Configuração do Inversor Fotovoltaico</MaxTitle1>
    <MaxDynamicForm :schema="formSchema" v-model="store.inverterConfig" />
  </div>
</template>

<script setup lang="ts">
import { z } from 'zod';
import MaxDynamicForm from './components/MaxDynamicForm.vue';
import type { FormFieldSchema } from './components/types';
import { useInverterStore } from '@/stores/inverter';

// Store @maxvue/max-pinia: o GET inicial e o salvamento sao feitos pela store.
// Ao editar campos do v-model, o MaxPinia salva automaticamente no backend (auto-save debounced).
// Por isso o formulario nao precisa de @submit nem de logica manual de POST.
const store = useInverterStore();

const formSchema: FormFieldSchema[] = [
  {
    key: 'model',
    label: 'Modelo do Inversor',
    component: 'MaxInputText',
    gridClass: 's50',
    validation: z.string().min(3, 'O modelo deve ter pelo menos 3 caracteres').max(50, 'O modelo não deve exceder 50 caracteres'),
    props: { placeholder: 'Ex: Growatt MIN 5000TL-X' }
  },
  {
    key: 'phase',
    label: 'Tipo de Fase',
    component: 'MaxInputSelect',
    gridClass: 's50',
    validation: z.string().min(1, 'O tipo de fase é obrigatório'),
    props: {
      options: [
        { label: 'Monofásico', value: 'single' },
        { label: 'Bifásico', value: 'biphasic' },
        { label: 'Trifásico', value: 'three' }
      ]
    }
  },
  {
    key: 'notes',
    label: 'Observações de Instalação',
    component: 'MaxInputTextArea',
    gridClass: 's100',
    validation: z.string().min(10, 'As observações devem ter pelo menos 10 caracteres'),
    props: { placeholder: 'Descreva detalhes da instalação do inversor...', rows: 4 }
  },
  {
    key: 'active',
    label: 'Ativo',
    component: 'MaxInputSwitch',
    gridClass: 's100',
    props: { label: 'Habilitar monitoramento deste inversor' }
  }
];
</script>
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Apenas Composition API**: Nunca utilize a Options API. Sempre use `<script setup lang="ts">`.
* **TypeScript Obrigatório**: Todos os scripts devem ser totalmente tipados. Use `lang="ts"`.
* **Estilização UnoCSS attributify-first**: Prefira UnoCSS attributify (`presetMaxUno`) com tokens de tema e atributos inline; o dimensionamento de campos vem do `MaxGrid` + atributos (`s33`/`s50`/`s100`, `w-max-300`). Use um bloco `<style scoped lang="scss">` apenas para o resíduo que o UnoCSS não cobre — não é obrigatório e não deve reimplementar grid/layout manual. Não imponha "SCSS-only".
* **Estilo de Parâmetro do Componente em Linha**: Dentro de `<template>`, mantenha todos os atributos/props do componente em uma única linha. Não os divida em várias linhas.
* **Idioma dos Comentários de Código**: Todos os comentários dentro dos componentes Vue/TS devem ser escritos em Português do Brasil (pt-BR).
* **Validação Segura**: Sempre use `.safeParse()` do Zod. Não use `.parse()` para evitar exceções não tratadas em tempo de execução.
