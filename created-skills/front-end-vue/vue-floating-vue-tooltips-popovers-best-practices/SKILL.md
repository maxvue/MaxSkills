---
name: vue-floating-vue-tooltips-popovers-best-practices
description: Use when implementing, updating, or debugging tooltips, popovers, dropdowns, or contextual floating menus in Vue 3 SFCs using FloatingVue (floating-vue). Triggers on v-tooltip directives, VDropdown/VMenu component configuration, placements, trigger behaviors, and floating interface positioning or lifecycle cleanup.
---

# Boas Práticas de FloatingVue Tooltips & Popovers no Vue 3

## Objetivo
Estabelecer diretrizes sólidas e padrões consistentes para a utilização da biblioteca FloatingVue no frontend Vue 3 do Engeapp, garantindo interfaces flutuantes performáticas, acessíveis e visualmente integradas.

## Instruções
1. **Ordenação de Blocos SFC:** Sempre estruture os arquivos Vue que contêm componentes flutuantes na seguinte ordem:
   1. `<template>`
   2. `<script setup lang="ts">`
   3. `<style scoped lang="scss">`

2. **Uso da Diretiva v-tooltip:**
   - Use a diretiva `v-tooltip` para tooltips simples de texto.
   - Mantenha a declaração limpa: `<button v-tooltip="'Texto da tooltip'">Ação</button>`.
   - Use a sintaxe de objeto para opções personalizadas (ex: posicionamento, atraso ou gatilhos): `v-tooltip="{ content: 'Texto da tooltip', placement: 'top', delay: { show: 300, hide: 100 } }"`.
   - Mantenha todos os atributos do elemento e a diretiva `v-tooltip` em uma única linha dentro do bloco de template.

3. **Componentes VDropdown e VMenu:**
   - Use `<VDropdown>` para menus suspensos interativos (ex: listas de ações, seletores suspensos).
   - Use `<VMenu>` para popovers contextuais complexos (ex: cards que aparecem no hover/click com formulários, conteúdos ricos, detalhes dinâmicos).
   - Use o slot `#default` (ou slot padrão implícito) para o elemento gatilho (trigger).
   - Use o slot `#popper` para o conteúdo flutuante.
   - Configure os gatilhos explicitamente (`:triggers="['click']"` ou `:triggers="['hover']"`).

4. **Posicionamentos (Placements) e Gatilhos (Triggers):**
   - Defina posicionamentos padrões adequados (ex: `bottom-start` para dropdowns, `top` ou `bottom` para tooltips).
   - Evite cortes de popovers configurando limites (boundaries) ou definindo a opção de container caso estejam aninhados em elementos pais roláveis.

5. **Gerenciamento do Ciclo de Vida e Vazamentos de Memória (Memory Leaks):**
   - Envolva componentes pesados ou componentes que fazem requisições de API dentro do slot `#popper` com `v-if` para que eles só sejam montados e carregados quando o container flutuante for de fato exibido.
   - Garanta que eventuais listeners de eventos ou gatilhos manuais se vinculem e limpem os recursos corretamente.

6. **Acessibilidade (WAI-ARIA):**
   - Certifique-se de que os elementos gatilho possuam textos descritivos ou um `aria-label` ao usar ícones.
   - O FloatingVue lida automaticamente com atributos ARIA essenciais (ex: `aria-describedby` e `aria-haspopup`), mas verifique se a navegação por teclado (Esc para fechar, tab-index dentro dos menus) funciona perfeitamente.

## Restrições
- NÃO use a Options API. Sempre utilize a Composition API (`<script setup lang="ts">`).
- NÃO quebre os atributos das tags HTML/SFC em várias linhas no bloco `<template>`. Todos os atributos devem ser mantidos inline na mesma linha.
- NÃO utilize cores, bordas ou sombras estáticas. Alinhe a estilização ao sistema de design da aplicação utilizando variáveis de tema.
- NÃO execute chamadas de API ou renderize componentes pesados dentro de menus ocultos. Sempre use renderização condicional (`v-if`) dentro do slot popper.

## Examples
### Componentes do FloatingVue Seguros e Responsivos

```vue
<template>
  <div class="floating-container">
    <!-- Exemplo 1: Botão de ação com tooltip simples inline -->
    <button v-tooltip="'Visualizar detalhes da tarefa'" class="btn-action" aria-label="Visualizar tarefa">
      <i class="icon-eye" />
    </button>

    <!-- Exemplo 2: Menu suspenso de ações usando VDropdown -->
    <VDropdown :triggers="['click']" placement="bottom-start" theme="max-dropdown">
      <button class="btn-trigger">Ações do Card</button>
      <template #popper="{ hide }">
        <ul class="actions-list">
          <li><button @click="handleAction('edit', hide)" class="action-item">Editar</button></li>
          <li><button @click="handleAction('delete', hide)" class="action-item text-danger">Excluir</button></li>
        </ul>
      </template>
    </VDropdown>

    <!-- Exemplo 3: Popover complexo usando VMenu com carregamento condicional -->
    <VMenu :triggers="['hover']" placement="top" theme="max-popover" @apply-show="loadDetails">
      <button class="btn-info">Detalhes do Usuário</button>
      <template #popper>
        <div v-if="isLoading" class="popover-loader">Carregando...</div>
        <div v-else-if="userData" class="popover-details">
          <p><strong>Nome:</strong> {{ userData.name }}</p>
          <p><strong>Email:</strong> {{ userData.email }}</p>
        </div>
      </template>
    </VMenu>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// Definição de interface para dados do usuário
interface UserData {
  name: string;
  email: string;
}

// Estados reativos
const isLoading = ref<boolean>(false);
const userData = ref<UserData | null>(null);

// Simulação de carregamento assíncrono de dados ao abrir o menu
const loadDetails = async (): Promise<void> => {
  if (userData.value) return; // Evita requisições repetidas se os dados já existirem
  isLoading.value = true;
  try {
    // Simula chamada de API
    await new Promise((resolve) => setTimeout(resolve, 600));
    userData.value = {
      name: 'John Doe',
      email: 'john.doe@engeapp.com.br'
    };
  } catch (error) {
    console.error('Erro ao carregar detalhes:', error);
  } finally {
    isLoading.value = false;
  }
};

// Executa uma ação e fecha o menu
const handleAction = (actionType: string, hideCallback: () => void): void => {
  console.log(`Ação executada: ${actionType}`);
  hideCallback(); // Fecha o dropdown manualmente
};
</script>

<style scoped lang="scss">
.floating-container {
  display: flex;
  gap: 1rem;
  align-items: center;

  .btn-action, .btn-trigger, .btn-info {
    padding: 0.5rem 1rem;
    border: 1px solid var(--border-color, #d1d5db);
    border-radius: 6px;
    background-color: var(--bg-primary, #ffffff);
    color: var(--text-primary, #1f2937);
    cursor: pointer;
    transition: background-color 0.2s ease;

    &:hover {
      background-color: var(--bg-hover, #f3f4f6);
    }
  }

  .actions-list {
    list-style: none;
    padding: 0.25rem 0;
    margin: 0;
    min-width: 150px;

    .action-item {
      width: 100%;
      padding: 0.5rem 1rem;
      border: none;
      background: none;
      text-align: left;
      cursor: pointer;
      font-size: 0.875rem;

      &:hover {
        background-color: var(--bg-hover, #f3f4f6);
      }

      &.text-danger {
        color: var(--color-danger, #ef4444);
      }
    }
  }

  .popover-loader {
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    color: var(--text-secondary, #6b7280);
  }

  .popover-details {
    padding: 0.75rem 1rem;
    font-size: 0.875rem;

    p {
      margin: 0.25rem 0;
    }
  }
}
</style>
```
