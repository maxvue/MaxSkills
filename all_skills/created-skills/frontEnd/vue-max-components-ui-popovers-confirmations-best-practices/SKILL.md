---
name: vue-max-components-ui-popovers-confirmations-best-practices
description: "Use when implementing tooltips, popovers, dropdown menus, and confirmation dialogs in Vue 3 SFCs. Covers PrimeVue v-tooltip directive registered via MaxComponentsUi, MaxPopover, MaxPopoverConfirm, MaxIconConfirm, and MaxPopoverMenu components with SCSS styling."
author: Johnattas Conrady Gomes Santana
---
# Melhores Práticas para Popovers & Confirmações do MaxComponentsUi no Vue

## Objetivo
Fornecer diretrizes, padrões de design e exemplos claros para a implementação e estilização de tooltips de texto no hover, popovers contextuais, menus suspensos (dropdowns) e confirmações de ações rápidas utilizando a diretiva `v-tooltip` (do PrimeVue, registrada por `@maxvue/max-components-ui`) e os componentes da biblioteca interna `MaxComponentsUi` (`MaxPopover`, `MaxPopoverConfirm`/`MaxIconConfirm` e `MaxPopoverMenu`) em templates Vue 3 SFC (Single File Component) com TypeScript e SCSS.

> **Verdade-base sobre tooltips:** a diretiva `v-tooltip` NÃO vem do `floating-vue`. Ela é o `primevue/tooltip`, registrado em `@maxvue/max-components-ui` (`app.directive('tooltip', Tooltip)`). O pacote `floating-vue` até consta no `package.json`, mas é uma **dependência morta**: nunca é registrada como plugin nem usada em `resources/`/`src/`. Portanto NÃO existem `VDropdown`, `VMenu`, temas FloatingVue nem o evento `@apply-show`. Não os utilize — esta skill cobre todos os casos de tooltip/popover/menu do projeto.
>
Padronizar a criação e manutenção de dicas visuais flutuantes (tooltips), popovers ricos, painéis deslizantes (drawers), menus de contexto e caixas de diálogo de confirmação rápida no front-end em Vue 3 (Engeapp), utilizando exclusivamente os componentes e diretivas fornecidos pelo `@maxvue/max-components-ui`.

## Instruções

1. **Uso de Tooltips com a Diretiva `v-tooltip`:**
   - Use a diretiva nativa `v-tooltip` do PrimeVue (registrada automaticamente pelo plugin `install` do MaxComponentsUi).
   - Prefira posicionar explicitamente: `v-tooltip.top="'Atualizar últimas mensagens'"`.
   - Mantenha a diretiva e todos os atributos **inline, na mesma linha** do elemento.
   - Aplique a diretiva no componente Max ou no elemento que já existe no template (ex.: `MaxIconButton`, `Icon`), nunca introduzindo `<button>` nativo só por causa da tooltip.
   - Garanta `aria-label` descritivo em gatilhos com ícone.

2. **Uso do MaxPopover:**
   - Utilize `MaxPopover` para diálogos popover genéricos que exigem cabeçalhos personalizados ou templates de conteúdo ricos.
   - Use slots para construir layouts personalizados:
     - Use `#button` para definir o botão de gatilho (recebe as props do componente).
     - Use `#header` para áreas de cabeçalho personalizadas. Por padrão, renderiza um título/subtítulo e um botão de fechar.
     - Use `#content` ou o slot padrão (`default`) para o corpo principal do popover.
   - Use a propriedade `no-picker` para ocultar a seta indicadora em forma de triângulo, se necessário.
   - Exponha os métodos `show()`, `hide()` e `toggle()` via Template Refs se o controle manual for necessário. **Atenção:** `show()` é apenas um alias de `toggle()` — chamar `show()` com o popover já aberto FECHA o popover. Só `hide()` é idempotente/seguro para forçar fechamento.

3. **Prompts de Confirmação Rápida (`MaxButtonConfirm`, `MaxIconConfirm` & `MaxPopoverConfirm`):**
   - NÃO construa popovers de confirmação personalizados usando HTML puro.
   - Em vez disso, coloque o componente global `MaxPopoverConfirm` uma única vez no layout principal do sistema (ou reutilize a instância global existente).
   - Use `MaxButtonConfirm` quando precisar de um botão completo com rótulo textual e confirmação (props `:accept="fn"`, `:reject="fn"`, `message="Deseja continuar?"`).
   - Use `MaxIconConfirm` quando precisar de um botão compacto apenas com ícone (props `message`, `:acceptProps="{ label, icon, action }"`, `:rejectProps="{ label, icon, action }"`). Ambos calculam automaticamente as coordenadas de posicionamento e atualizam a store Pinia `useConfirmStore`.

4. **Uso do MaxPopoverMenu:**
   - Utilize `MaxPopoverMenu` para menus dropdown contextuais (ex: ações de linhas de tabelas, menus de perfil) baseados no componente Menu do PrimeVue.
   - Passe um array de itens para a prop `items` (ou `model`). Cada item deve possuir:
     - `label`: O texto de exibição.
     - `icon` ou `i`: Identificador do ícone.
     - `route`: **NOME** de rota de PÁGINA Vue opcional (ex.: `'new_project'`, `'project'`, `'board'`) usado para navegação via `goToRoute` (de `@maxvue/max-use`). O `goToRoute` resolve exclusivamente por nome (Ziggy/Vue Router) — NUNCA passe path string tipo `/reports/proposals`, pois seria interpretado como nome de rota inexistente e a navegação falharia. **Cuidado:** nomes de rotas HTTP do backend (Ziggy, ex.: `'equipments.list.equipments'`) também existem no Ziggy e passariam pela checagem `hasRoute()`, mas resolvem para URLs de API sem página Vue correspondente — não os use em `route` de itens de menu, apenas nomes gerados pelo glob de `resources/Vue/Pages`. O `data` do item é repassado como params/query.
     - `action`: Função de callback opcional que recebe `{ event, data }`.
     - `data`: Payload de dados associados ao item.
   - Personalize o botão de gatilho com o slot `#button` ou deixe renderizar o `MaxButton` padrão do componente.
   - Personalize itens de lista individuais com o slot `#item="{ data }"`.

5. **Uso do MaxDrawer (Painel Deslizante / Slide-Over):**
   - Utilize `MaxDrawer` para painéis laterais de edição rápida, filtros avançados e detalhes contextuais que deslizam sobre a página.
   - Controle reativamente a abertura com `v-model:visible="exibirDrawer"`.
   - Defina a borda de surgimento com `position`: `'right'` (padrão), `'left'`, `'top'`, `'bottom'` ou `'full'`.
   - O componente ativa internamente bloqueio de rolagem do body (`useScrollLock`), captura acessível de foco (`useFocusTrap`) e fechamento via tecla Escape (`closeOnEscape`) ou clique fora da gaveta (`dismissable`).
   - Use os slots `#header` (cabeçalho), `#footer` (rodapé de ações) e `#default` (corpo).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Estrutura SFC:** Siga sempre a ordem estrita de blocos: `<template>`, depois `<script setup lang="ts">` e, por fim, `<style lang="scss">`.
- **Atributos Inline:** Todos os atributos/props dentro dos templates Vue DEVEM ser declarados em uma única linha (sem quebras de linha entre propriedades na mesma tag).
- **TypeScript:** O bloco de script deve sempre utilizar `lang="ts"`.
- **Estilização SCSS:** Todos os estilos devem utilizar `lang="scss"` (com escopo `scoped` sempre que apropriado).
- **Imports Manuais:** Confie no auto-import do projeto (`unplugin-auto-import` e `unplugin-vue-components`) — não importe componentes nem APIs como `ref`/`computed` manualmente. Se em algum caso o import explícito for necessário, os componentes vêm de `@maxvue/max-components-ui` e helpers como `goToRoute` de `@maxvue/max-use`.
- **Options API:** Nunca utilize a Options API. Use exclusivamente a Composition API com `<script setup>`.
- **Comentários de Código:** Escreva comentários de código dentro dos exemplos estritamente em português do Brasil (pt-BR).
- **floating-vue:** NÃO use `floating-vue`, `VDropdown`, `VMenu`, temas FloatingVue ou o evento `@apply-show` — nada disso está registrado/ativo no projeto (dependência morta).

## Examples

### 1. Tooltip de texto no hover (diretiva PrimeVue v-tooltip)
```vue
<template>
  <!-- Posição pelo modificador; valor é string (não objeto) -->
  <IconButton icon="reload" flex v-tooltip.top="'Atualizar últimas mensagens'" />
  <div class="icon-alert" v-tooltip.right="'Este contato não está no WhatsApp. Verifique o número.'" />
  <!-- Forma objeto do PrimeVue: necessária para HTML na tooltip -->
  <MaxIconButton i="mdi:eye" aria-label="Visualizar tarefa" v-tooltip.top="{ value: '<b>Visualizar</b> detalhes da tarefa', escape: false }" />
</template>

<script setup lang="ts">
</script>
```

### 2. MaxPopover com Conteúdo Personalizado
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
  color: var(--text);
}
</style>
```

### 3. Confirmação de Ação Rápida via MaxIconConfirm
```vue
<template>
  <MaxIconConfirm i="iconoir:trash" size="1.2" message="Tem certeza que deseja excluir esta proposta?" :acceptProps="acceptConfig" :rejectProps="rejectConfig" />
</template>

<script setup lang="ts">
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
```

### 4. MaxPopoverMenu para Ações em Linhas de Tabela
```vue
<template>
  <MaxPopoverMenu i="iconoir:more-vert" size="1.2" :items="menuItems" />
</template>

<script setup lang="ts">
interface MenuItem {
  label: string;
  icon?: string;
  action?: (payload: { event: any, data: any }) => void;
  route?: string; // NOME de rota (Ziggy/Vue Router), não path string
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
    // route é o NOME da rota; goToRoute resolve por nome e repassa data como params/query
    label: 'Visualizar Projeto',
    icon: 'iconoir:reports',
    route: 'project',
    data: { id: 123 }
  }
]);
</script>
```

### 5. Confirmação com MaxButtonConfirm e Painel Deslizante com MaxDrawer
```vue
<template>
  <div class="acoes-container" flex items-center gap-2>
    <!-- Botão de exclusão com popover de confirmação ancorado -->
    <MaxButtonConfirm
      label="Excluir"
      icon="mdi:trash-can"
      severity="danger"
      message="Confirma a exclusão deste item?"
      :accept="excluirItem"
    />

    <!-- Botão que abre gaveta lateral de edição -->
    <MaxButton label="Filtros" icon="mdi:filter" @click="gavetaAberta = true" />

    <!-- Painel deslizante lateral (slide-over) -->
    <MaxDrawer v-model:visible="gavetaAberta" header="Filtros Rápidos" position="right">
      <p>Conteúdo do formulário de filtros contextuais.</p>
      <template #footer>
        <div flex justify-end gap-2>
          <MaxButton label="Fechar" severity="secondary" @click="gavetaAberta = false" />
          <MaxButton label="Aplicar" @click="aplicarFiltros" />
        </div>
      </template>
    </MaxDrawer>
  </div>
</template>

<script setup lang="ts">
const gavetaAberta = ref(false);

function excluirItem(): void {
  console.log('Item excluído!');
}

function aplicarFiltros(): void {
  gavetaAberta.value = false;
}
</script>
```
