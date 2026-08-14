---
name: vue-max-ecosystem-api-reference
description: "Use when referencing APIs of Engeapp local Vue libraries: MaxComponentsUi, MaxUse, and MaxPinia. Covers component props/events/slots, composables, and cached store configurations. Covers objectives, component props, composables, and API navigation."
---
# Catálogo de API do Ecossistema Max (MaxComponentsUi · MaxUse · MaxPinia)

## Objetivo

Ser a **fonte única de consulta de API** das três bibliotecas locais usadas no projeto Vue EngeApp
(Laravel 13 + Vue 3 SPA). Quando você precisar saber *o que existe* e *como chamar* — o nome exato de uma prop, o tipo, o default, o payload de
um `@evento`, os slots, a assinatura de um composable ou o contrato de uma store — a resposta está aqui,
extraída direto do código-fonte das libs (`/home/johnattas/GitHub/MaxComponentsUi`, `.../MaxUse`,
`.../MaxPinia`).

Esta skill é **referência**, não tutorial. Ela responde "qual prop faz X?" e "essa função recebe o quê?".
Para *convenções* de escrita (ordem de blocos do SFC, UnoCSS/SCSS, atributos inline, proibição de
`<section>` e de inputs/botões nativos, como montar formulários e integrar com a API) use a skill
[vue-max-stack-frontend-best-practices](../vue-max-stack-frontend-best-practices/SKILL.md).

## Instruções

### Como navegar

`Max*`, composables e stores aparecem sem import manual (auto-import/auto-resolução) — consulte o
catálogo antes de assumir uma prop ou reimportar `@vueuse/core`/`lodash`, já que o MaxUse já re-exporta
tudo.

Carregue **apenas o arquivo da biblioteca que você precisa** (progressive disclosure — não leia os três de
uma vez):

| Biblioteca | Pacote | O que consultar | Arquivo |
|-----------|--------|-----------------|---------|
| **MaxComponentsUi** | `@maxvue/max-components-ui` | Todos os 68 componentes `Max*` — props, v-model, emits, slots, expose, exemplo; e as stores/helpers públicos (useConfirmStore, toast, etc.) | [references/maxcomponentsui.md](references/maxcomponentsui.md) |
| **MaxUse** | `@maxvue/max-use` | Composables (useRefCached…), rotas (`apiGetRoute`, `goToRoute`…), helpers de data/browser, o objeto `_` e o re-export do VueUse | [references/maxuse.md](references/maxuse.md) |
| **MaxPinia** | `@maxvue/max-pinia` | Contrato do store cacheado: `isCached`, `options.get/save/key`, `status`, métodos injetados (`reload`, `clearAll`, `saveInServer`), ciclo de vida | [references/maxpinia.md](references/maxpinia.md) |

Notas adicionais além da tabela acima:

- Em `references/maxuse.md`: se for um helper genérico de coleção/objeto (debounce, cloneDeep, etc.), use
  o objeto `_` — nunca `lodash` direto. Se for um composable do VueUse, ele vem de `@maxvue/max-use`, não
  de `@vueuse/core`.
- Em `references/maxpinia.md`: todo GET de front-end passa por um store MaxPinia (`options.get.route`), e
  saves usam `options.save` (auto-save debounced) — nunca `axios.get`/`watch`+`setTimeout` manuais em
  componentes.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
