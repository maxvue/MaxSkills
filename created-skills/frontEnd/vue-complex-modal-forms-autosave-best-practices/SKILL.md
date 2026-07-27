---
name: vue-complex-modal-forms-autosave-best-practices
description: "Use when designing, building, or refactoring complex modal forms in Vue 3 with auto-save, real-time sync indicators (saving, saved, error), or multi-tab layouts using @maxvue/max-components-ui, max-use and max-pinia. Auto-save is delegated to a MaxPinia store (options.save + 300ms debounce, status.server.save), not manual watch/setTimeout. Triggers on auto-save modal forms and validation."
---

# Boas Práticas para Formulários de Modal Complexos e Salvamento Automático em Vue 3

## Objetivo
Padronizar formulários de modal complexos em Vue 3 (abas múltiplas, debounce, estados de sincronização em tempo real) integrados ao ecossistema `@maxvue/`.

---

## Instruções

### 1. Configuração do Modal e Navegação
- Envolva formulários complexos utilizando o `MaxModal` da biblioteca `@maxvue/max-components-ui`.
- Utilize uma referência (ex: `const modalRef = ref<any>(null)`) e alterne a visibilidade chamando os métodos realmente expostos pelo MaxModal: `.toggle()` para abrir/alternar e `.hide()` para fechar explicitamente (o mesmo handler usado internamente pelo botão de fechar e pelo clique no backdrop, mas sem a transição de opacity feita pelo `.toggle()`); o estado reativo é `is_show`. **Não** prescreva `.show()`: é a action crua `show(id: string)` da `useModalStore` e, chamada sem o `id` interno do modal (gerado internamente via `Random()`), não abre nada. O MaxModal **não** expõe `.open()` / `.close()`.
- Quando o MaxModal for controlado por ref (sem usar o gatilho embutido), passe a prop `no-button`/`noButton`; caso contrário o componente renderiza um `MaxButton` gatilho embutido por padrão.
- Para formulários com abas múltiplas, gerencie a navegação das abas usando uma referência reativa (ex: `const activeTab = ref<string>('nomeDaAba')`).
- Vincule classes de estilo dinamicamente para indicar a aba ativa e alterne as abas por meio de eventos de clique simples.

### 2. Reutilização de Componentes de UI
- Utilize os componentes principais da biblioteca `@maxvue/max-components-ui`:
  - `MaxInputText` para entradas de texto padrão.
  - `MaxInputTextArea` para campos de entrada de texto com várias linhas.
  - `MaxTagSelect` para tags suspensas e seleção de formatos.
  - `MaxButton` e `MaxIconButton` para ações, cancelamento, salvamento e operações de fechar.
  - `MaxIcon` para ícones.

### 3. Padrão de Salvamento Automático — delegue ao MaxPinia (NÃO reimplemente)
**Regra central:** o auto-save destes formulários é responsabilidade da store `@maxvue/max-pinia`, não do componente. O MaxPinia já faz GET ao montar, observa mudanças em `store.data` e dispara um **POST com debounce (300ms)** para `options.save`, com deduplicação de requisições concorrentes. Reimplementar isso com `watch` + `setTimeout` no componente duplica o salvamento, cria condições de corrida e diverge do padrão do projeto.

- O formulário deve editar diretamente o `data` de uma store cacheada (a edição reativa já agenda o save):
  ```typescript
  // store: useCharacterStore — isCached + options.get.route + options.save
  const store = useCharacterStore();
  // No template, vincule os inputs a store.data.<campo>; ao alterar, o MaxPinia salva sozinho.
  ```
- Não crie `saveStatus`/`autoSaveTimer` manuais nem chame um `saveData()` próprio. Se precisar forçar um envio imediato (ex: ao fechar o modal), use `store.saveInServer()`.
- Para campos que NÃO pertencem ao `data` cacheado (ações pontuais fora do fluxo de página), aí sim um POST manual via `apiPostRoute` é aceitável — mas isso é a exceção, não o padrão de formulário.

### 4. Indicadores Visuais — derivados do `status` da store
- Use o objeto reativo `store.status.server.save` (exposto pelo MaxPinia) em vez de um enum manual:
  - **Salvando**: `store.status.server.save.is_requesting` → `MaxIcon` `"mdi:loading"` com classe `spin` + texto `"Salvando..."`.
  - **Salvo**: `store.status.server.save.is_success_now` → `MaxIcon` `"mdi:check-circle-outline"` cor `var(--emerald-600)` + texto `"Salvo"` (o `*_now` já é transitório; não precisa de `setTimeout` para limpar).
  - **Erro**: `store.status.server.save.is_error` (e `.error`) → toast de aviso / ícone de erro.
- O status de carregamento inicial vem de `store.status.server.get` (ou o helper `is_done_to_show`; para blank state use `store.status.server.get.is_blank` / `store.status.cache.get.is_blank`, não `store.is_blank`) para skeletons.
- Para descartar alterações locais não persistidas, use as APIs da store (ex: `store.reload()` para revalidar do servidor) em vez de gerenciar cópias manuais.

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Não** utilize inputs HTML puros quando houver inputs equivalentes na biblioteca `@maxvue/max-components-ui`.
- **Não** escreva comentários de código ou documentação em outros idiomas que não o **Português do Brasil (pt-BR)** dentro do componente.
