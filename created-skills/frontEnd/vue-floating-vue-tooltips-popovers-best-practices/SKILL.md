---
name: vue-floating-vue-tooltips-popovers-best-practices
description: "Use when implementing, updating, or debugging plain-text hover tooltips and generic floating elements in Vue 3 SFCs with the FloatingVue (floating-vue) library. Triggers on v-tooltip directives, VDropdown/VMenu config, placements, trigger behaviors, and floating positioning/cleanup. For rich popovers, confirmations or row menus, use vue-max-components-ui-popovers-confirmations-best-practices."
---

# Boas Práticas de FloatingVue Tooltips & Popovers no Vue 3

## Objetivo
Estabelecer diretrizes sólidas e padrões consistentes para a utilização da biblioteca de terceiros FloatingVue (`floating-vue`) no frontend Vue 3 do Engeapp, garantindo interfaces flutuantes performáticas, acessíveis e visualmente integradas.

> **Qual skill usar?** Use `floating-vue` para **tooltips simples de texto no hover** (`v-tooltip`) e para casos de componentes flutuantes genéricos (`VDropdown`/`VMenu`) que não são cobertos pela biblioteca interna. Para popovers ricos, **confirmações de ação rápida** (`MaxIconConfirm`/`useConfirmStore`) e **menus de ações** (ex.: ações de linha de tabela, menus de perfil) — que são o padrão do ecossistema — use a skill **`vue-max-components-ui-popovers-confirmations-best-practices`**.

## Instruções
1. **Ordenação de Blocos SFC:** Sempre estruture os arquivos Vue que contêm componentes flutuantes na seguinte ordem:
   1. `<template>`
   2. `<script setup lang="ts">`
   3. `<style scoped lang="scss">`

2. **Uso da Diretiva v-tooltip:**
   - Use a diretiva `v-tooltip` para tooltips simples de texto.
   - Mantenha a declaração limpa aplicando a diretiva no componente Max: `<MaxButton v-tooltip="'Texto da tooltip'" label="Ação" />` (nunca `<button>` nativo).
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
   - Para buscar dados de página dentro de um popover, NÃO faça `axios.get` manual: use uma store `@maxvue/max-pinia` (que resolve a rota via `apiGetRoute` e cuida de cache). Dispare o carregamento da store no `@apply-show` e leia o estado reativo no slot `#popper`.

6. **Acessibilidade (WAI-ARIA):**
   - Certifique-se de que os elementos gatilho possuam textos descritivos ou um `aria-label` ao usar ícones.
   - O FloatingVue lida automaticamente com atributos ARIA essenciais (ex: `aria-describedby` e `aria-haspopup`), mas verifique se a navegação por teclado (Esc para fechar, tab-index dentro dos menus) funciona perfeitamente.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
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
    <MaxIconButton v-tooltip="'Visualizar detalhes da tarefa'" icon="eye" class="btn-action" aria-label="Visualizar tarefa" />

    <!-- Exemplo 2: Menu suspenso de ações usando VDropdown -->
    <VDropdown :triggers="['click']" placement="bottom-start" theme="max-dropdown">
      <MaxButton class="btn-trigger" label="Ações do Card" />
      <template #popper="{ hide }">
        <ul class="actions-list">
          <li><MaxButton class="action-item" label="Editar" @click="handleAction('edit', hide)" /></li>
          <li><MaxButton class="action-item text-danger" label="Excluir" @click="handleAction('delete', hide)" /></li>
        </ul>
      </template>
    </VDropdown>

    <!-- Exemplo 3: Popover complexo usando VMenu com carregamento condicional -->
    <VMenu :triggers="['hover']" placement="top" theme="max-popover" @apply-show="loadDetails">
      <MaxButton class="btn-info" label="Detalhes do Usuário" />
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

// Carregamento assíncrono ao abrir o menu.
// Em caso real de dados de página, use uma store @maxvue/max-pinia
// (apiGetRoute resolve para /api/...), NÃO um fetch/axios manual.
const loadDetails = async (): Promise<void> => {
  if (userData.value) return; // Evita requisições repetidas se os dados já existirem
  isLoading.value = true;
  try {
    // Exemplo com store MaxPinia (cache + GET automático):
    // const store = useResponsavelTecnicoStore();
    // await store.reload(); // GET automático no boot; reload() apenas para refetch manual
    // userData.value = store.data;
    // (placeholder de simulação abaixo apenas para o exemplo isolado)
    await new Promise((resolve) => setTimeout(resolve, 600));
    userData.value = {
      name: 'Engenheiro Responsável',
      email: 'responsavel@engeapp.com.br'
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
    border: 1px solid var(--border-base);
    border-radius: 6px;
    background-color: var(--surface-0);
    color: var(--text-default);
    cursor: pointer;
    transition: background-color 0.2s ease;

    &:hover {
      background-color: var(--surface-100);
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
        background-color: var(--surface-100);
      }

      &.text-danger {
        color: var(--danger-500);
      }
    }
  }

  .popover-loader {
    padding: 0.75rem 1rem;
    font-size: 0.875rem;
    color: var(--text-muted);
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
