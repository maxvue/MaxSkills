---
name: vue-floating-vue-tooltips-popovers-best-practices
description: "Use ao implementar, revisar ou depurar tooltips de texto no hover e popovers/menus flutuantes no front Vue 3 do engeapp. A diretiva v-tooltip é do PrimeVue (registrada por MaxComponentsUi) e usa modificadores de posição: v-tooltip.top/.right/.bottom/.left=\"'texto'\". Popovers e menus de ação usam MaxPopover e MaxPopoverMenu (@maxvue/max-components-ui), nunca componentes crus."
---

# Boas Práticas de Tooltips e Popovers Flutuantes no Vue 3 (engeapp)

## Objetivo
Padronizar tooltips de texto no hover e elementos flutuantes (popovers e menus de ação) no front-end Vue 3 do engeapp, usando exclusivamente os recursos realmente registrados no app: a diretiva `v-tooltip` do PrimeVue (registrada por `@maxvue/max-components-ui`) e os componentes `MaxPopover` / `MaxPopoverMenu`.

> **Verdade-base:** a diretiva `v-tooltip` NÃO vem do FloatingVue. Ela é o `primevue/tooltip`, registrado em `@maxvue/max-components-ui` (`app.directive('tooltip', Tooltip)`). O pacote `floating-vue` até consta no `package.json`, mas é uma dependência morta: nunca é registrada como plugin nem usada em `resources/`. Portanto NÃO existem `VDropdown`, `VMenu`, temas FloatingVue nem o evento `@apply-show`. Não os utilize.

> **Qual skill usar?** Use esta skill para **tooltips simples de texto no hover** (`v-tooltip`) e para **popovers/menus de ação** (`MaxPopover`, `MaxPopoverMenu`). Para **confirmações de ação rápida** (`MaxIconConfirm`/`useConfirmStore`) veja a skill **`vue-max-components-ui-popovers-confirmations-best-practices`**.

## Instruções

1. **Ordenação de Blocos SFC:** estruture o arquivo Vue na ordem:
   1. `<template>`
   2. `<script setup lang="ts">`
   3. `<style scoped lang="scss">`

2. **Diretiva v-tooltip (PrimeVue):**
   - O valor da diretiva é uma **string** com o texto — não um objeto. `v-tooltip="{ content, placement, delay }"` (sintaxe FloatingVue) **não funciona** aqui.
   - Defina a posição por **modificador**: `v-tooltip.top`, `v-tooltip.right`, `v-tooltip.bottom`, `v-tooltip.left`. Sem modificador, o PrimeVue usa `right` como padrão.
   - Prefira posicionar tooltips de forma explícita: `v-tooltip.top="'Atualizar últimas mensagens'"`.
   - Mantenha todos os atributos e a diretiva **inline, na mesma linha** do elemento.
   - Aplique a diretiva no componente Max ou no elemento que já existe no template (ex.: `MaxIconButton`, `Icon`), nunca introduzindo `<button>` nativo só por causa da tooltip.

3. **Popovers ricos com MaxPopover:**
   - Use `MaxPopover` para conteúdo flutuante rico (formulários, detalhes, cards) acionado por clique no botão-gatilho.
   - Props úteis: `title`, `sub-title` (cabeçalho padrão), `icon`/`i` e `size`/`icon-size` (botão-gatilho), `class` (repassada ao `.max-popover-dialog`).
   - Slots: `button` (customiza o gatilho), `header` (substitui o cabeçalho padrão), `content` e slot default (corpo).
   - Controle a abertura pela `ref` do componente, que expõe `toggle()`, `show()` e `hide()`:
     `const popover_ref = useTemplateRef<{ toggle: () => void; show: () => void; hide: () => void }>('popover_ref');`
   - Feche após uma ação com `popover_ref.value?.hide()`.

4. **Menus de ação com MaxPopoverMenu:**
   - Use `MaxPopoverMenu` para menus suspensos de ações (ex.: botão "+" com lista de opções, menu de perfil).
   - Passe as opções por `:items` (ou o alias `:model`). Cada item é `{ label, icon | i, action }`, onde `action` recebe `({ event, data })`.
   - O botão-gatilho é configurado por props (`icon`/`i`, `icon-size`/`size`, `label`) ou pelo slot `button`; o rótulo/ícone de cada linha pode ser customizado pelo slot `item`.

5. **Estilização por variáveis de tema:**
   - Estilize o conteúdo via classe (`class="..."`) e ajuste o `.max-popover-dialog` quando necessário (ex.: `.max-popover-dialog::before { display: none; }`).
   - NÃO use cores/bordas/sombras estáticas: alinhe ao design system com variáveis de tema.

6. **Carregamento de dados dentro de popovers:**
   - Para buscar dados de página, NÃO faça `axios.get`/`fetch` manual: use uma store `@maxvue/max-pinia`, que resolve a rota nomeada (Ziggy) via `apiGetRoute` e cuida de cache/estado.
   - Renderize o conteúdo pesado condicionalmente (`v-if`) e leia o estado reativo da store no corpo do popover, evitando montar/buscar enquanto ele estiver fechado.

7. **Acessibilidade (WAI-ARIA):**
   - Garanta que gatilhos com ícone tenham `aria-label` descritivo.
   - Verifique navegação por teclado (Esc para fechar, foco dentro do menu).

## Restrições
- **Idioma:** comunique-se com o usuário humano sempre em Português (pt-BR), independentemente do idioma do corpo da skill. Comentários de código em pt-BR.
- NÃO use a Options API. Sempre Composition API (`<script setup lang="ts">`).
- NÃO use `floating-vue`, `VDropdown`, `VMenu`, temas FloatingVue ou o evento `@apply-show` — nada disso está registrado/ativo no projeto.
- NÃO passe objeto para `v-tooltip`; o valor é uma string e a posição vem do modificador.
- NÃO quebre atributos de tags em múltiplas linhas no `<template>`: mantenha inline.
- NÃO use `vueuse`/`lodash`/PrimeVue crus diretamente; use `@maxvue/max-use` e os componentes `Max*` de `@maxvue/max-components-ui`.
- NÃO faça chamadas de API nem renderize conteúdo pesado dentro de popovers ocultos: use `v-if` + store MaxPinia.

## Exemplos

### 1. Tooltip de texto no hover (diretiva PrimeVue)
```vue
<template>
    <!-- Posição pelo modificador; valor é string -->
    <IconButton icon="reload" flex v-tooltip.top="'Atualizar últimas mensagens'" />
    <div class="icon-alert" v-tooltip.right="'Este contato não está no WhatsApp. Verifique o número.'" />
    <MaxIconButton i="mdi:eye" aria-label="Visualizar tarefa" v-tooltip.top="'Visualizar detalhes da tarefa'" />
</template>
```

### 2. Menu de ações com MaxPopoverMenu
```vue
<template>
    <MaxPopoverMenu :items="items" icon="ic:twotone-plus" icon-size="1.5" />
</template>

<script setup lang="ts">
    // Cada item: { label, icon|i, action({ event, data }) }
    const items = [
        { label: 'Editar', i: 'mdi:pencil', action: () => editar() },
        { label: 'Excluir', i: 'mdi:trash-can', action: () => excluir() }
    ];

    const editar = (): void => {
        // ...lógica de edição
    };

    const excluir = (): void => {
        // ...lógica de exclusão
    };
</script>
```

### 3. Popover rico com MaxPopover e carregamento via store MaxPinia
```vue
<template>
    <MaxPopover ref="popover_ref" class="detalhes-responsavel-popover" title="Responsável Técnico" sub-title="Detalhes do responsável" icon="mdi:account" icon-size="1.4">
        <div v-if="store.status.server.get.is_requested && !store.status.server.get.is_success" class="popover-loader">Carregando...</div>
        <div v-else-if="store.data" class="popover-details">
            <p><strong>Nome:</strong> {{ store.data.name }}</p>
            <p><strong>E-mail:</strong> {{ store.data.email }}</p>
            <div grid center>
                <Botao label="Fechar" flex @click.stop="popover_ref?.hide()" />
            </div>
        </div>
    </MaxPopover>
</template>

<script setup lang="ts">
    // A store MaxPinia resolve a rota nomeada (Ziggy) via apiGetRoute e faz o GET
    // automático no boot, além de cachear o resultado — nada de axios/fetch manual.
    const store = useResponsavelTecnicoStore();

    const popover_ref = useTemplateRef<{ toggle: () => void; show: () => void; hide: () => void }>('popover_ref');
</script>

<style scoped lang="scss">
    .detalhes-responsavel-popover {
        // Ajuste o container do popover pela classe repassada ao .max-popover-dialog
        .max-popover-dialog::before {
            display: none;
        }

        .popover-loader {
            padding: 0.75rem 1rem;
            color: var(--text-muted);
        }

        .popover-details p {
            margin: 0.25rem 0;
        }
    }
</style>
```
