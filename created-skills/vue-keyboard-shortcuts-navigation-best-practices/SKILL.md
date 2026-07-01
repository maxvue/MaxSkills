---
name: vue-keyboard-shortcuts-navigation-best-practices
description: Use when implementing, designing, or debugging global or component-specific keyboard shortcuts, keyboard navigation, hotkeys, or managing focus and active elements in Vue 3. Triggers on custom keyboard event listeners, useMagicKeys, useActiveElement, and keydown/keyup event modifiers.
---

## Objetivo
Fornecer diretrizes e convenções claras para implementar atalhos de teclado globais e específicos de componentes, navegação por teclado, hotkeys e gerenciamento de foco no Vue 3, garantindo reatividade, acessibilidade (WAI-ARIA) e prevenindo colisões com os atalhos padrões do navegador ou durante a edição de campos de texto.

## Instruções
1. **Prevenção de Colisão com Entradas de Texto**:
   - Sempre verifique se o usuário está digitando em um campo de texto antes de executar atalhos globais.
   - Use o `useActiveElement` (auto-importado via `@maxvue/max-use`, sem import manual) para verificar o nome da tag do elemento ativo.
   - Previna a execução de atalhos se o `activeElement` for um `INPUT`, `TEXTAREA`, `SELECT` ou possuir `contenteditable="true"`.
   - Exemplo de verificação:
     ```typescript
     // useActiveElement e computed sao auto-importados (unplugin-auto-import + @maxvue/max-use)
     const activeElement = useActiveElement();
     const isTyping = computed(() => {
       if (!activeElement.value) return false;
       const { tagName, contentEditable } = activeElement.value;
       return ['INPUT', 'TEXTAREA', 'SELECT'].includes(tagName) || contentEditable === 'true';
     });

     // dentro do callback do atalho:
     if (isTyping.value) return;
     ```

2. **Utilizando Hotkeys Reativas com VueUse `useMagicKeys`**:
   - Aproveite o `useMagicKeys` (auto-importado via `@maxvue/max-use`) para combinações de teclas complexas.
   - Crie watchers reativos personalizados para teclas e combine-os usando o helper `whenever` (também auto-importado) ou watchers padrão do Vue.
   - Exemplo:
     ```typescript
     // useMagicKeys e whenever sao auto-importados (unplugin-auto-import + @maxvue/max-use)
     const { ctrl_s, escape } = useMagicKeys();

     whenever(ctrl_s, () => {
       if (isTyping.value) return;
       // ação de salvar rascunho
     });
     ```

3. **Modificadores de Eventos de Teclado do Vue 3**:
   - Para ouvintes de teclado locais, específicos de componentes, use modificadores de tecla do Vue 3 como `@keydown.enter` ou `@keyup.escape`.
   - Sempre utilize o modificador `.exact` para garantir que o atalho seja disparado apenas com a combinação exata de teclas, evitando falsos positivos (ex: evitar que `@keydown.enter.exact` seja disparado ao segurar Shift ou Ctrl).
   - Use `.prevent` para parar ações padrões do navegador (como a janela de salvar padrão do navegador ao pressionar Ctrl+S).
   - Exemplo:
     ```html
     <!-- Dispara apenas quando Enter é pressionado sozinho -->
     <MaxInputText @keydown.enter.exact="confirmAction" />

     <!-- Dispara apenas quando Ctrl e S são pressionados juntos, prevenindo a ação do navegador -->
     <div @keydown.ctrl.s.prevent.exact="saveChanges"></div>
     ```

4. **Gerenciamento de Foco e Focus Traps**:
   - Quando modais, painéis laterais (slide-overs) ou popups são abertos, o foco deve ser retido (trap) dentro da sobreposição.
   - Integre com bibliotecas de interface (como os componentes PrimeVue em `MaxComponentsUi` ou modais personalizados) que possuem opções nativas de acessibilidade/focus trap.
   - Garanta que a tecla `Esc` feche modais de forma segura, verificando se o modal está atualmente visível.
   - Restaure o foco para o elemento de ativação assim que a sobreposição for fechada.

5. **Padrões de Acessibilidade WAI-ARIA**:
   - Garanta que componentes interativos (ex: navegação em listas, dropdowns personalizados) suportem os modelos padrão de interação por teclado (teclas direcionais para navegar, Space/Enter to select).
   - Adicione `tabindex="0"` para tornar elementos não interativos personalizados focáveis quando necessário.

## Restrições
- NÃO dispare atalhos globais (como `S`, `N` ou `Ctrl+S`) quando o foco estiver dentro de um controle de formulário (`INPUT`, `TEXTAREA`, `SELECT`, `contenteditable`).
- NÃO defina ouvintes de `keydown` globais usando `window.addEventListener('keydown', ...)` nativo sem removê-los na destruição do componente (`onUnmounted`). Dê preferência aos utilitários reativos reutilizáveis do VueUse ou realize a limpeza correta.
- NÃO defina atalhos de teclado genéricos que colidam com atalhos comuns do navegador (ex: Ctrl+T, Ctrl+W, F5), a menos que explicitamente solicitado e totalmente controlado.
- NÃO use `@keydown` sem `.exact` se você precisar de combinações estritas de teclas.
