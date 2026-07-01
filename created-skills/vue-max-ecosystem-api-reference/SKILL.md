---
name: vue-max-ecosystem-api-reference
description: >-
  Catálogo de API (referência) das bibliotecas locais do ecossistema Max — @maxvue/max-components-ui
  (MaxComponentsUi), @maxvue/max-use (MaxUse) e @maxvue/max-pinia (MaxPinia). Use SEMPRE que precisar
  saber as props, v-model, emits, slots, expose de um componente Max* (MaxButton, MaxInputText,
  MaxInputSelect, MaxTable, MaxModal, MaxPopover, MaxGrid, etc.), a assinatura de um composable/rota/helper
  do MaxUse (useRefCached, useRefCachedApi, useTimeAgo, apiGetRoute, goToRoute, o objeto `_`, re-export do
  VueUse) ou o contrato de store cacheado do MaxPinia (isCached, options.get/save/key, status, reload,
  clearAll, saveInServer). Dispara quando você for escolher qual componente/composable usar, conferir um
  nome de prop, um payload de evento, um slot disponível, o default de um valor, ou a assinatura exata de
  uma função — mesmo que o usuário não diga "Max". Consulte esta skill antes de inventar props ou importar
  `@vueuse/core`/`lodash` direto. É referência de API; para convenções de código e como montar telas use a
  vue-max-stack-frontend-best-practices.
---

# Catálogo de API do Ecossistema Max (MaxComponentsUi · MaxUse · MaxPinia)

## Objetivo

Ser a **fonte única de consulta de API** das três bibliotecas locais do stack Maxdmin. Quando você
precisar saber *o que existe* e *como chamar* — o nome exato de uma prop, o tipo, o default, o payload de
um `@evento`, os slots, a assinatura de um composable ou o contrato de uma store — a resposta está aqui,
extraída direto do código-fonte das libs (`/home/johnattas/GitHub/MaxComponentsUi`, `.../MaxUse`,
`.../MaxPinia`).

Esta skill é **referência**, não tutorial. Ela responde "qual prop faz X?" e "essa função recebe o quê?".
Para *convenções* de escrita (ordem de blocos do SFC, UnoCSS/SCSS, atributos inline, proibição de
`<section>` e de inputs/botões nativos, como montar formulários e integrar com a API) use a skill
[vue-max-stack-frontend-best-practices](../vue-max-stack-frontend-best-practices/SKILL.md).

## Por que usar o catálogo em vez de adivinhar

O ecossistema Max usa auto-import e auto-resolução de componentes: `Max*`, composables e stores aparecem
sem import manual. Isso torna **fácil inventar uma prop que não existe** ou passar o tipo errado — o
editor não reclama até rodar. Consultar o catálogo evita: props inexistentes, `v-model` no lugar errado,
handler ouvindo um evento que a lib não emite, e reimportar `@vueuse/core`/`lodash` quando o MaxUse já
re-exporta tudo. Cada item abaixo foi lido do fonte real, então o que está aqui é o que a lib de fato
expõe.

## Como navegar

Carregue **apenas o arquivo da biblioteca que você precisa** (progressive disclosure — não leia os três de
uma vez):

| Biblioteca | Pacote | O que consultar | Arquivo |
|-----------|--------|-----------------|---------|
| **MaxComponentsUi** | `@maxvue/max-components-ui` | Todos os 70 componentes `Max*` — props, v-model, emits, slots, expose, exemplo; e as stores/helpers públicos (useConfirmStore, toast, etc.) | [references/maxcomponentsui.md](references/maxcomponentsui.md) |
| **MaxUse** | `@maxvue/max-use` | Composables (useRefCached…), rotas (`apiGetRoute`, `goToRoute`…), helpers de data/browser, o objeto `_` e o re-export do VueUse | [references/maxuse.md](references/maxuse.md) |
| **MaxPinia** | `@maxvue/max-pinia` | Contrato do store cacheado: `isCached`, `options.get/save/key`, `status`, métodos injetados (`reload`, `clearAll`, `saveInServer`), ciclo de vida | [references/maxpinia.md](references/maxpinia.md) |

Fluxo de consulta:

1. **Precisa de um componente de tela** (input, botão, tabela, modal, grid, popover…) → abra
   `references/maxcomponentsui.md` e procure o `Max*` pelo nome. Cada entrada traz Import, Propósito,
   Props, v-model, Emits, Slots, Expose e um Exemplo mínimo.
2. **Precisa de um utilitário/composable/rota** (cache, datas, formatação, chamada de API, navegação) →
   abra `references/maxuse.md`. Se for um helper genérico de coleção/objeto (debounce, cloneDeep, etc.),
   use o objeto `_` — nunca `lodash` direto. Se for um composable do VueUse, ele vem de `@maxvue/max-use`,
   não de `@vueuse/core`.
3. **Precisa buscar/salvar dados do servidor** → abra `references/maxpinia.md`. Todo GET de front-end passa
   por um store MaxPinia (`options.get.route`), e saves usam `options.save` (auto-save debounced) — nunca
   `axios.get`/`watch`+`setTimeout` manuais em componentes.

## Regras rápidas que o catálogo reforça

- **Componentes de UI**: sempre `Max*` da MaxComponentsUi — nunca `<input>`/`<button>`/`<select>`/
  `<textarea>`/checkbox nativos em código de aplicação.
- **Utilitários**: sempre via MaxUse — nunca importar `@vueuse/core` nem `lodash` direto. Nomes de
  composables VueUse são os mesmos, só muda a origem (`@maxvue/max-use`); utilitários lodash-style via `_`.
- **Dados**: todo fetch/persistência via store MaxPinia, não axios manual.

Essas regras vêm da [vue-max-stack-frontend-best-practices](../vue-max-stack-frontend-best-practices/SKILL.md);
o catálogo existe justamente para você achar o item Max certo em vez de cair no equivalente nativo/externo.
