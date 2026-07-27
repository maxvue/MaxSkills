---
name: vue-brand-positioning-character-management-best-practices
description: "Use quando criar, modificar, estilizar ou depurar componentes, páginas ou stores Vue 3 do módulo de posicionamento de marca e personagens (SocialMedia): TabBrandPositioning, TabCharacters, TabThemes. Cobre a store MaxPinia com salvamento automático (useBrandPositioning) e a store Pinia manual com axios + route Ziggy (useSocialMediaCharacters), uploads de imagens de referência facial e temas."
---

# Boas Práticas de Gerenciamento de Posicionamento de Marca e Personagens em Vue

## Objetivo
Estabelecer diretrizes claras, padrões e convenções de fluxo reativo para gerenciar formulários de posicionamento de marca, personas de personagens e uploads de imagens de referência no front-end do aplicativo em Vue 3, utilizando componentes do design system e gerenciamento de estado do Pinia.

## Instruções

> Para convenções gerais de SFC (Composition API, ordem de blocos, formatação, comentários pt-BR), ver `vue-max-stack-frontend-best-practices` e `vue-eslint-stylelint-quality-standards`. A convenção de estilo real destes componentes específicos (`<style>` não-scoped) está nas Restrições, abaixo.

### 2. Formulários de Posicionamento de Marca
* Implemente formulários reativos com salvamento automático para as diretrizes da marca (ex: tom de voz, público-alvo, configurações de logotipo) para evitar perda de dados.
* Use `<MaxInputTextArea>` para campos de texto multilinha (como guias de estilo ou perfis de público) com um layout de grade padrão (`MaxGrid`).
* Vincule o estado a uma store dedicada do `@maxvue/max-pinia` (ex: `useBrandPositioningStore`). O carregamento inicial dos dados (GET) e o salvamento automático devem vir da própria store: configure `options.get.route` e `options.save` na definição da store como **nomes de rota (Ziggy)** pontilhados (ex.: `route: 'brand_positioning.data'`, `save: 'brand_positioning.save'`) — a store chama `apiGetRoute`/`apiPostRoute` internamente, que resolvem o nome para a URL `/api/...` via Ziggy; NÃO passe caminhos string `/api/...` nem envolva os valores de config com esses helpers, e NÃO implemente auto-save manual com `watch` + `setTimeout`/`axios.post`. O MaxPinia já faz o debounce e o auto-save ao mutar o estado.

### 3. Perfil de Personagem e Gerenciamento de Porta-Vozes
* **Store manual, NÃO MaxPinia:** A store de personagens (`useSocialMediaCharacters.Store.ts`, `defineStore('social.media.characters.store', ...)`) é uma store Pinia **manual** — não usa o contrato MaxPinia. Ela expõe ações explícitas (`load`, `create`, `update`, `remove`, `uploadImage`, `removeImage`) que chamam `axios.get/post/put/delete(route(...))` diretamente, com um `ref` `loading` para o estado de carregamento. Os nomes de rota são Ziggy pontilhados passados a `route()` (ex.: `route('characters.index')`, `route('characters.store')`, `route('characters.update', { character: id })`, `route('characters.image.upload', { character: id })`). **NÃO** aplique aqui `isCached`/`options.get.route`/`save` nem o auto-save com debounce da seção 2 — o padrão MaxPinia vale apenas para `useBrandPositioningStore`. Persista as alterações de personagens chamando explicitamente as ações da store.
* Use o sistema de grade padrão (`MaxGrid`) com espaçamento adequado de linhas/colunas para os detalhes do perfil do personagem (ex: nome, descrição física detalhada, traços).
* **Upload de Rostos de Personagens:** Utilize o componente de upload grande personalizado (`MaxInputFileUploadBig`) para permitir o envio de imagens de referência facial de alta qualidade para geração de imagens por IA.
* Gerencie os estados de carregamento e salvamento de upload com loaders reativos (`uploadingFor` ou `saving`) para desabilitar o envio do formulário enquanto um upload estiver em andamento.
* Forneça um layout de listagem interativa mostrando avatares de personagens, status ativo e opções simples de edição/exclusão.
* **Upload de brandbook (`TabBrandPositioning.vue`):** os assets de referência de marca são enviados via `axios.post(route('brand_positioning.asset.upload'), formData)` e removidos via `axios.post(route('brand_positioning.asset.remove'), { id })`, chamados diretamente no componente (não pela store `useBrandPositioningStore`).
* **Temas (`TabThemes.vue`, store `useSocialMediaThemes.Store.ts`):** os temas têm `ThemeStatus` (`'elaborating' | 'extracting' | 'waiting'`), conteúdo tipado por `ThemeContentType` (`'image' | 'pdf' | 'audio' | 'text' | 'url'`) e agendamento por `ThemeScheduleRule` (variantes `specific_dates`, `weekly`, `monthly_days`, `monthly_nth_weekday`). A tela é composta pelos componentes `ThemeCard.vue`, `ThemeContentList.vue` e `ThemeScheduleBuilder.vue`, seguindo o mesmo padrão de exclusão via `<MaxModal>` dedicado descrito na Seção 4.

### 4. Modais, Confirmações e Toasts
* Envolva formulários de criação/edição em `<MaxModal>`. Para confirmar exclusões (personagens, temas, imagens), o padrão real do módulo é um **segundo `<MaxModal noButton noHeader>` dedicado** como diálogo de confirmação (ex.: `ref="delete_dialog_ref"`, com `MaxTitle2` de aviso e botões "Cancelar"/"Remover") — não os componentes `MaxIconConfirm`/`MaxPopoverConfirm` de `vue-max-components-ui-popovers-confirmations-best-practices` (essa skill documenta uma API diferente, não usada neste módulo). Nunca use `confirm()`/`alert()` nativos.
* Para feedback de API (sucesso/erro/validação), dispare `Toast` do `@maxvue/max-components-ui` e destaque campos inválidos via `error`/`done` do `<InputBase>`. Detalhes em `vue-toast-notifications-toastify-best-practices`.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Estilização (House Rule vs. padrão real):** A house rule do projeto é fazer layout, espaçamento e cores via atributos do UnoCSS attributify (`presetMaxUno`) e tokens do tema (ex.: `p0`, `s50`, `s100`, `s33`, `s25`, `w-flex`); prefira attributify para código novo no módulo. `TabBrandPositioning.vue`, `TabCharacters.vue` e `TabThemes.vue` usam de fato um bloco `<style lang="scss">` **não** `scoped` com CSS baseado em classes (ex.: `.characters-page`) e variáveis de tema (`var(--background-200)`); ao editar esses três arquivos específicos, siga esse padrão já existente em vez de reescrevê-lo para attributify puro. **NÃO** use Tailwind CSS.
* **NÃO** use diálogos nativos do navegador (ex: `confirm()`, `alert()`) para avisos de exclusão. Use o padrão de `<MaxModal>` de confirmação descrito na Seção 4.
