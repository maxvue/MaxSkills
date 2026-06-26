---
name: vue-max-components-ui-wizard-stepper-forms-best-practices
description: Use when designing, implementing, styling, or validating multi-step form wizard/stepper flows in Vue 3 (EngeApp/Maxdmin) using the @maxvue/max-components-ui library and @maxvue/max-use's useStepper. Triggers on files managing Wizard forms, step navigation logic, steps status (active, completed, error), state persistence between steps using useRefCached, persisting data through @maxvue/max-pinia stores, and partial step-by-step Zod schema validations.
---

# Boas Práticas para Formulários Assistentes (Wizard/Stepper) com MaxComponentsUi no Vue

## Objetivo
Estabelecer um padrão de implementação claro, consistente e robusto para formulários multi-etapas (assistentes/wizards/steppers) no Vue 3 utilizando a biblioteca local `@maxvue/max-components-ui`, `@maxvue/max-use` (especificamente `useStepper` e `useRefCached` para gerenciamento de progresso e persistência entre abas), persistência final via store `@maxvue/max-pinia` e validação parcial de etapas com Zod.

## Instruções

1. **Importações e Configuração do Stepper:**
   - Os componentes de stepper e os componentes de formulário/botões do Max UI são auto-importados pelo projeto (unplugin-vue-components). Quando precisar de import explícito, use sempre o pacote `@maxvue/max-components-ui`:
     ```typescript
     import { Stepper, StepList, Step, StepPanels, StepPanel } from '@maxvue/max-components-ui';
     import { MaxInputText, MaxButton } from '@maxvue/max-components-ui';
     ```
   - Gerencie a navegação de etapas do wizard utilizando um índice reativo (`ref(0)`) ou o `useStepper` do `@maxvue/max-use`.

2. **Estado Persistente do Assistente:**
   - Inicialize e persista as entradas do wizard entre recarregamentos de página ou abas duplicadas utilizando `useRefCached` do `@maxvue/max-use` (auto-importado; não manipule `localStorage` diretamente):
     ```typescript
     const formData = useRefCached('wizard-cache-key', {
       name: '',
       website: '',
       // outros campos...
     });
     ```

3. **Validação Passo a Passo:**
   - Defina esquemas do Zod dedicados para cada etapa do formulário para permitir validações granulares:
     ```typescript
     import { z } from 'zod';
     
     const stepOneSchema = z.object({
       name: z.string().min(3, 'O nome deve conter pelo menos 3 caracteres'),
     });
     ```
   - No clique do botão "Avançar", valide apenas os campos pertinentes à etapa ativa antes de prosseguir.
   - Vincule os erros de validação a campos reativos específicos, passando-os para a propriedade `:error` dos componentes Max para exibir os problemas imediatamente.
   - Limpe o cache (`useRefCached`) somente após o envio final do formulário com sucesso.

4. **Persistência dos Dados (via MaxPinia):**
   - O envio final NÃO deve ser feito com `axios`/`fetch` manual. Persista os dados gravando-os em uma store `@maxvue/max-pinia`, que cuida do auto-save (debounced) contra `/api/...`:
     ```typescript
     import { useWizardStore } from '@/stores/wizard';

     const store = useWizardStore();
     // ao alterar/atribuir os dados na store, o MaxPinia persiste automaticamente no backend
     store.data = { ...formData.value };
     ```

5. **Estilização de Atributos do Template (Restrição Crítica):**
   - Certifique-se de que todos os parâmetros e atributos nos componentes Vue dentro do template sejam escritos inline em uma única linha. Não quebre as tags dos componentes em atributos multilinha.

## Examples

### Componente de Formulário Multi-etapas Completo

```vue
<template>
  <div class="wizard-container">
    <Stepper :value="activeStep">
      <StepList>
        <Step :value="0" class="step-header">Passo 1: Onboarding</Step>
        <Step :value="1" class="step-header">Passo 2: Configuração</Step>
        <Step :value="2" class="step-header">Passo 3: Confirmação</Step>
      </StepList>
      
      <StepPanels>
        <StepPanel :value="0">
          <div class="step-content">
            <MaxInputText v-model="formData.name" :error="errors.name" label="Nome da Usina" placeholder="Digite o nome" />
            <MaxButton @click="validateAndNext(0)" label="Avançar" />
          </div>
        </StepPanel>
        
        <StepPanel :value="1">
          <div class="step-content">
            <MaxInputText v-model="formData.website" :error="errors.website" label="Website" placeholder="https://..." />
            <div class="button-group">
              <MaxButton @click="back" label="Voltar" severity="secondary" />
              <MaxButton @click="validateAndNext(1)" label="Avançar" />
            </div>
          </div>
        </StepPanel>
        
        <StepPanel :value="2">
          <div class="step-content">
            <p>Confirme os dados da usina {{ formData.name }} ({{ formData.website }}).</p>
            <div class="button-group">
              <MaxButton @click="back" label="Voltar" severity="secondary" />
              <MaxButton :loading="submitting" @click="submit" label="Finalizar" />
            </div>
          </div>
        </StepPanel>
      </StepPanels>
    </Stepper>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
// Stepper, MaxInputText e MaxButton são auto-importados de @maxvue/max-components-ui;
// useRefCached é auto-importado de @maxvue/max-use. Imports explícitos, quando necessários:
// import { Stepper, StepList, Step, StepPanels, StepPanel, MaxInputText, MaxButton } from '@maxvue/max-components-ui';
import { z } from 'zod';
import { useUsinaWizardStore } from '@/stores/usinaWizard';

// Definição da interface do formulário
interface WizardData {
  name: string;
  website: string;
}

// Chave para cache de progresso (persistência entre abas/recargas)
const cacheKey = 'usina-onboarding-data';
const formData = useRefCached<WizardData>(cacheKey, { name: '', website: '' });

// Store MaxPinia (auto-save/debounced contra /api/...)
const wizardStore = useUsinaWizardStore();

// Erros de validação
const errors = ref<Record<keyof WizardData, string>>({ name: '', website: '' });
const submitting = ref(false);

// Estado da etapa ativa do stepper
const activeStep = ref(0);

// Esquemas de validação do Zod por etapa
const stepOneSchema = z.object({
  name: z.string().min(3, 'O nome deve conter pelo menos 3 caracteres')
});

const stepTwoSchema = z.object({
  website: z.string().url('Insira uma URL válida')
});

// Função para validar a etapa atual e ir para a próxima
const validateAndNext = (step: number) => {
  // Limpar erros anteriores
  errors.value = { name: '', website: '' };
  
  try {
    if (step === 0) {
      stepOneSchema.parse({ name: formData.value.name });
      activeStep.value = 1;
    } else if (step === 1) {
      stepTwoSchema.parse({ website: formData.value.website });
      activeStep.value = 2;
    }
  } catch (err) {
    if (err instanceof z.ZodError) {
      err.issues.forEach(e => {
        const field = e.path[0] as keyof WizardData;
        errors.value[field] = e.message;
      });
    }
  }
};

// Voltar etapa
const back = () => {
  if (activeStep.value > 0) {
    activeStep.value--;
  }
};

// Submissão final
const submit = async () => {
  submitting.value = true;
  try {
    // Validar esquema completo
    const fullSchema = stepOneSchema.merge(stepTwoSchema);
    fullSchema.parse(formData.value);
    
    // Persistir via store MaxPinia: ao atribuir os dados, o auto-save (debounced)
    // grava no backend em /api/... — sem axios/fetch manual.
    wizardStore.data = { ...formData.value };
    await wizardStore.flush?.();
    
    // Limpar o cache de progresso após sucesso
    formData.value = { name: '', website: '' };
    // Redirecionar ou concluir fluxo
  } catch (err) {
    if (err instanceof z.ZodError) {
      err.issues.forEach(e => {
        const field = e.path[0] as keyof WizardData;
        errors.value[field] = e.message;
      });
    }
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped lang="scss">
.wizard-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
  
  .step-header {
    font-weight: 600;
  }
  
  .step-content {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin-top: 2rem;
  }
  
  .button-group {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
  }
}
</style>
```

## Restrições
- **NÃO use Options API:** Sempre implemente utilizando `<script setup lang="ts">` (Composition API e TypeScript).
- **NÃO use Estilização Tailwind:** Mantenha os estilos estruturados dentro de `<style scoped lang="scss">`. Não use classes utilitárias do Tailwind a menos que explicitamente solicitado.
- **NÃO use Atributos HTML Multilinha:** Todas as propriedades/atributos dentro de componentes customizados Max Vue no `<template>` devem ser formatados inline em uma única linha.
- **NÃO faça Transições de Etapa Sem Validação:** Nunca incremente o índice de etapas ou invoque funções de avanço sem rodar validações Zod nos campos da etapa ativa.
