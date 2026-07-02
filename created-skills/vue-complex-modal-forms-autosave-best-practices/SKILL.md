---
name: vue-complex-modal-forms-autosave-best-practices
description: Use when designing, building, or refactoring complex modal forms in Vue 3 that integrate auto-saving features, real-time sync state indications (saving, saved, error), or multi-tab layouts using @maxvue/max-components-ui, @maxvue/max-use and @maxvue/max-pinia. Auto-save is delegated to a MaxPinia store (options.save + 300ms debounce, status.server.save), NOT manual watch/setTimeout. Triggers on auto-save modal forms, MaxPinia-backed form state, and complex form validations inside modals.
---

# Boas Práticas para Formulários de Modal Complexos e Salvamento Automático em Vue 3

## Objetivo
Estabelecer diretrizes arquiteturais e padrões de codificação para a implementação de formulários de modal complexos em Vue 3 que requerem navegação por abas múltiplas, debounce de entrada, estados de sincronização em tempo real (idle, pending, saving, saved, error) e integração harmoniosa com o ecossistema de componentes de interface `@maxvue/` e stores.

---

## Instruções

### 1. Estrutura e Configuração do Componente
- Sempre utilize a **Composition API do Vue 3** com `<script setup lang="ts">`. A Options API é estritamente proibida.
- Implemente os estilos dentro de `<style scoped lang="scss">`.
- Mantenha a ordem padrão dos blocos do SFC: `<template>`, `<script setup lang="ts">`, e depois `<style scoped lang="scss">`.
- Dentro do bloco `<template>`, formate os componentes do Vue mantendo todas as propriedades/atributos em uma única linha (estilo inline). Evite quebrar atributos em várias linhas.

### 2. Configuração do Modal e Navegação
- Envolva formulários complexos utilizando o `MaxModal` da biblioteca `@maxvue/max-components-ui`.
- Utilize uma referência (ex: `const modalRef = ref<any>(null)`) e alterne a visibilidade chamando os métodos realmente expostos pelo MaxModal: `.toggle()`, `.show()` e `.hide()` (o estado reativo é `is_show`). O MaxModal **não** expõe `.open()` / `.close()`.
- Para formulários com abas múltiplas, gerencie a navegação das abas usando uma referência reativa (ex: `const activeTab = ref<string>('nomeDaAba')`).
- Vincule classes de estilo dinamicamente para indicar a aba ativa e alterne as abas por meio de eventos de clique simples.

### 3. Reutilização de Componentes de UI
- Utilize os componentes principais da biblioteca `@maxvue/max-components-ui`:
  - `MaxInputText` para entradas de texto padrão.
  - `MaxInputTextArea` para campos de entrada de texto com várias linhas.
  - `MaxTagSelect` para tags suspensas e seleção de formatos.
  - `MaxButton` e `MaxIconButton` para ações, cancelamento, salvamento e operações de fechar.
  - `MaxIcon` para ícones.

### 4. Padrão de Salvamento Automático — delegue ao MaxPinia (NÃO reimplemente)
**Regra central:** o auto-save destes formulários é responsabilidade da store `@maxvue/max-pinia`, não do componente. O MaxPinia já faz GET ao montar, observa mudanças em `store.data` e dispara um **POST com debounce (300ms)** para `options.save`, com deduplicação de requisições concorrentes. Reimplementar isso com `watch` + `setTimeout` no componente duplica o salvamento, cria condições de corrida e diverge do padrão do projeto.

- O formulário deve editar diretamente o `data` de uma store cacheada (a edição reativa já agenda o save):
  ```typescript
  // store: useCharacterStore — isCached + options.get.route + options.save
  const store = useCharacterStore();
  // No template, vincule os inputs a store.data.<campo>; ao alterar, o MaxPinia salva sozinho.
  ```
- Não crie `saveStatus`/`autoSaveTimer` manuais nem chame um `saveData()` próprio. Se precisar forçar um envio imediato (ex: ao fechar o modal), use `store.saveInServer()`.
- Para campos que NÃO pertencem ao `data` cacheado (ações pontuais fora do fluxo de página), aí sim um POST manual via `apiPostRoute` é aceitável — mas isso é a exceção, não o padrão de formulário.

### 5. Indicadores Visuais — derivados do `status` da store
- Use o objeto reativo `store.status.server.save` (exposto pelo MaxPinia) em vez de um enum manual:
  - **Salvando**: `store.status.server.save.is_requesting` → `MaxIcon` `"mdi:loading"` com classe `spin` + texto `"Salvando..."`.
  - **Salvo**: `store.status.server.save.is_success_now` → `MaxIcon` `"mdi:check-circle-outline"` cor `var(--emerald-600)` + texto `"Salvo"` (o `*_now` já é transitório; não precisa de `setTimeout` para limpar).
  - **Erro**: `store.status.server.save.is_error` (e `.error`) → toast de aviso / ícone de erro.
- O status de carregamento inicial vem de `store.status.server.get` (ou dos helpers `is_done_to_show`/`is_blank`) para skeletons.
- Para descartar alterações locais não persistidas, use as APIs da store (ex: `store.reload()` para revalidar do servidor) em vez de gerenciar cópias manuais.

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Não** utilize inputs HTML puros quando houver inputs equivalentes na biblioteca `@maxvue/max-components-ui`.
- **Não** omita a Composition API (`<script setup lang="ts">`) ou os estilos SCSS.
- **Não** quebre os atributos de componentes/elementos HTML em várias linhas dentro do `<template>`. Mantenha as tags em uma única linha.
- **Não** reimplemente o salvamento automático com `watch` + `setTimeout`/`clearTimeout` no componente. O debounce e a deduplicação são do MaxPinia (`options.save`); edite `store.data` e deixe a store salvar. Save manual só para ações fora do `data` cacheado.
- **Não** escreva scripts ou estilos inline fora dos blocos SFC do Vue.
- **Não** utilize CSS puro ou bibliotecas utilitárias inline genéricas (como TailwindCSS) a menos que sejam utilizadas classes utilitárias do UnoCSS ou variáveis SCSS definidas no projeto.
- **Não** escreva comentários de código ou documentação em outros idiomas que não o **Português do Brasil (pt-BR)** dentro do componente.
