---
name: vue-max-components-ui-popovers-confirmations-best-practices
description: "Use when designing, implementing, styling, or reviewing contextual popovers, dropdown menus, and quick-action confirmations with the internal MaxComponentsUi library (MaxPopover, MaxPopoverConfirm/MaxIconConfirm, MaxPopoverMenu, useConfirmStore) in Vue 3 SFCs. Default for rich popovers and row menus. For plain hover tooltips or floating-vue, use vue-floating-vue-tooltips-popovers-best-practices."
---

# Melhores Práticas para Popovers & Confirmações do MaxComponentsUi no Vue

## Objetivo
Fornecer diretrizes, padrões de design e exemplos claros para a implementação e estilização de popovers contextuais, menus suspensos (dropdowns) e confirmações de ações rápidas utilizando os componentes da biblioteca interna `MaxComponentsUi` (`MaxPopover`, `MaxPopoverConfirm`/`MaxIconConfirm` e `MaxPopoverMenu`) em templates Vue 3 SFC (Single File Component) com TypeScript e SCSS.

> **Qual skill usar?** `MaxComponentsUi` é o padrão do ecossistema para popovers ricos, confirmações de ação e menus de ações (ex.: ações de linha de tabela, menus de perfil). Para **tooltips simples de texto no hover** (`v-tooltip`) ou para componentes flutuantes genéricos de terceiros (`VDropdown`/`VMenu` da lib `floating-vue`), use a skill **`vue-floating-vue-tooltips-popovers-best-practices`**.

## Instruções
1. **Uso do MaxPopover:**
   - Utilize `MaxPopover` para diálogos popover genéricos que exigem cabeçalhos personalizados ou templates de conteúdo ricos.
   - Use slots para construir layouts personalizados:
     - Use `#button` para definir o botão de gatilho (recebe as props do componente).
     - Use `#header` para áreas de cabeçalho personalizadas. Por padrão, renderiza um título/subtítulo e um botão de fechar.
     - Use `#content` ou o slot padrão (`default`) para o corpo principal do popover.
   - Use a propriedade `no-picker` para ocultar a seta indicadora em forma de triângulo, se necessário.
   - Exponha os métodos `show()`, `hide()` e `toggle()` via Template Refs se o controle manual for necessário.

2. **Prompts de Confirmação Rápida (`MaxIconConfirm` & `MaxPopoverConfirm`):**
   - NÃO construa popovers de confirmação personalizados usando HTML puro.
   - Em vez disso, coloque o componente global `MaxPopoverConfirm` uma única vez no layout principal do sistema (ou reutilize a instância global existente).
   - Use o componente `MaxIconConfirm` como o botão de gatilho em seu template. Ele calcula automaticamente as coordenadas de posicionamento e atualiza a store do Pinia `useConfirmStore`.
   - Configure as seguintes props no `MaxIconConfirm`:
     - `message`: O texto de confirmação para o usuário (padrão: "Deseja continuar?").
     - `messageIcon`: Ícone exibido ao lado da mensagem (padrão: `null`).
     - `acceptProps`: Objeto contendo `{ label, icon, action }` para o botão de confirmação.
     - `rejectProps`: Objeto contendo `{ label, icon, action }` para o botão de cancelamento.

3. **Uso do MaxPopoverMenu:**
   - Utilize `MaxPopoverMenu` para menus dropdown contextuais (ex: ações de linhas de tabelas, menus de perfil) baseados no componente Menu do PrimeVue.
   - Passe um array de itens para a prop `items` (ou `model`). Cada item deve possuir:
     - `label`: O texto de exibição.
     - `icon` ou `i`: Identificador do ícone.
     - `route`: Caminho string opcional (ex.: `/reports/proposals`) para navegação via `goToRoute` (importado de `@maxvue/max-use`). Não use rotas nomeadas.
     - `action`: Função de callback opcional que recebe `{ event, data }`.
     - `data`: Payload de dados associados ao item.
   - Personalize o botão de gatilho com o slot `#button` ou deixe renderizar o `MaxButton` padrão do componente.
   - Personalize itens de lista individuais com o slot `#item="{ data }"`.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Estrutura SFC:** Siga sempre a ordem estrita de blocos: `<template>`, depois `<script setup lang="ts">` e, por fim, `<style lang="scss">`.
- **Atributos Inline:** Todos os atributos/props dentro dos templates Vue DEVEM ser declarados em uma única linha (sem quebras de linha entre propriedades na mesma tag).
- **TypeScript:** O bloco de script deve sempre utilizar `lang="ts"`.
- **Estilização SCSS:** Todos os estilos devem utilizar `lang="scss"` (com escopo `scoped` sempre que apropriado).
- **Imports Manuais:** Confie no auto-import do projeto (`unplugin-auto-import` e `unplugin-vue-components`) — não importe componentes nem APIs como `ref`/`computed` manualmente. Se em algum caso o import explícito for necessário, os componentes vêm de `@maxvue/max-components-ui` e helpers como `goToRoute` de `@maxvue/max-use`.
- **Options API:** Nunca utilize a Options API. Use exclusivamente a Composition API com `<script setup>`.
- **Comentários de Código:** Escreva comentários de código dentro dos exemplos estritamente em português do Brasil (pt-BR).

## Examples

### 1. MaxPopover com Conteúdo Personalizado
```vue
<template>
  <MaxPopover title="Opções Extras" subTitle="Configurações rápidas" size="1.2" icon="iconoir:settings">
    <template #content>
      <div class="popover-custom-content">
        <p>Conteúdo personalizado do popover.</p>
      </div>
    </template>
  </MaxPopover>
</template>

<script setup lang="ts">
// Auto-import ativo: nenhum import necessário. Se preciso, importar de @maxvue/max-components-ui
</script>

<style scoped lang="scss">
.popover-custom-content {
  padding: 10px;
  color: var(--text-color);
}
</style>
```

### 2. Confirmação de Ação Rápida via MaxIconConfirm
```vue
<template>
  <MaxIconConfirm i="iconoir:trash" size="1.2" message="Tem certeza que deseja excluir esta proposta?" :acceptProps="acceptConfig" :rejectProps="rejectConfig" />
</template>

<script setup lang="ts">
// ref é auto-importado pelo unplugin-auto-import; não importe manualmente.

// Configuração das ações de confirmar e cancelar
const acceptConfig = ref({
  label: 'Excluir',
  icon: 'iconoir:check',
  action: () => {
    // Lógica para excluir o item
    console.log('Item excluído com sucesso');
  }
});

const rejectConfig = ref({
  label: 'Voltar',
  icon: 'iconoir:xmark',
  action: () => {
    // Lógica ao cancelar
    console.log('Ação cancelada');
  }
});
</script>

<style scoped lang="scss">
/* Estilos específicos se necessário */
</style>
```

### 3. MaxPopoverMenu para Ações em Linhas de Tabela
```vue
<template>
  <MaxPopoverMenu i="iconoir:more-vert" size="1.2" :items="menuItems" />
</template>

<script setup lang="ts">
// ref é auto-importado pelo unplugin-auto-import; não importe manualmente.

interface MenuItem {
  label: string;
  icon?: string;
  action?: (payload: { event: any, data: any }) => void;
  route?: string;
  data?: any;
}

// Lista de ações para a proposta específica
const menuItems = ref<MenuItem[]>([
  {
    label: 'Editar Proposta',
    icon: 'iconoir:edit',
    action: ({ data }) => {
      console.log('Editando proposta:', data.id);
    },
    data: { id: 123 }
  },
  {
    label: 'Visualizar Relatórios',
    icon: 'iconoir:reports',
    route: '/reports/proposals'
  }
]);
</script>

<style scoped lang="scss">
/* Estilos do menu contextual */
</style>
```
