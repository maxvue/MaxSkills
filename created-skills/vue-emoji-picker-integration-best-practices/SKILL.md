---
name: vue-emoji-picker-integration-best-practices
description: Use when implementing, configuring, or debugging emoji picker features in the Vue 3 frontend using the vue3-emoji-picker library. Triggers on emoji selector instantiation, binding emojis to text inputs or textareas, cursor position insertion, dark mode styling integration, and localization of emoji categories.
---

# Boas Práticas de Integração do Seletor de Emojis no Vue 3

## Objetivo
Estabelecer um padrão de alta performance, acessibilidade e consistência visual para integrar a biblioteca `vue3-emoji-picker` em aplicações Vue 3, garantindo importações dinâmicas (lazy loading) adequadas para manter o Core Web Vitals (LCP) e a inserção precisa do texto na posição do cursor (caret position).

---

## Instruções

### 1. Performance e Carregamento Preguiçoso (Lazy Loading)
Devido ao dataset pesado em formato JSON exigido pelos seletores de emojis, não importe o componente `EmojiPicker` de forma síncrona. Use importações dinâmicas (componentes assíncronos) para carregar o seletor apenas quando o usuário disparar sua visibilidade.

```vue
<template>
  <div class="emoji-picker-wrapper">
    <MaxButton label="😀" @click="togglePicker" />
    <div v-if="isOpen" class="picker-container">
      <LazyEmojiPicker :native="true" :theme="theme" :group-names="groupNames" :static-texts="staticTexts" @select="onEmojiSelect" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineAsyncComponent } from 'vue';

const isOpen = ref(false);
const theme = ref<'light' | 'dark'>('light'); // Vincula ao estado do tema da aplicação

// Importação Dinâmica (Lazy Loading)
// defineAsyncComponent já gerencia o estado de carregamento internamente
// (use loadingComponent se quiser um fallback); não precisa de <Suspense>.
const LazyEmojiPicker = defineAsyncComponent(() => import('vue3-emoji-picker'));
import 'vue3-emoji-picker/css'; // Importa estilos normalmente ou dinamicamente se preferir
</script>
```

### 2. Inserção na Posição do Cursor (Caret Position)
Ao inserir um emoji, não o anexe diretamente no final do texto. Implemente um helper ou lógica inline para determinar a posição do cursor (`selectionStart` e `selectionEnd`) dentro do `HTMLInputElement` ou `HTMLTextAreaElement` de destino.

```typescript
/**
 * Insere um emoji na posição atual do cursor do input/textarea de destino.
 * @param target Elemento Input ou TextArea
 * @param emoji O caractere de emoji selecionado
 * @param currentValue Valor atual do model do input
 * @returns O valor da string atualizado
 */
import { nextTick } from 'vue';

export function insertEmojiAtCaret(
  target: HTMLInputElement | HTMLTextAreaElement | null,
  emoji: string,
  currentValue: string
): string {
  if (!target) {
    return currentValue + emoji;
  }

  const startPos = target.selectionStart ?? currentValue.length;
  const endPos = target.selectionEnd ?? currentValue.length;

  const updatedValue = 
    currentValue.substring(0, startPos) + 
    emoji + 
    currentValue.substring(endPos);

  // Restaura o foco e atualiza a posição do cursor na próxima atualização do DOM
  nextTick(() => {
    target.focus();
    const newCursorPos = startPos + emoji.length;
    target.setSelectionRange(newCursorPos, newCursorPos);
  });

  return updatedValue;
}
```

No componente:
```typescript
const textInput = ref<HTMLTextAreaElement | null>(null);
const messageText = ref<string>('');

const onEmojiSelect = (emoji: any) => {
  messageText.value = insertEmojiAtCaret(textInput.value, emoji.i, messageText.value);
};
```

### 3. Localização (pt-BR)
Garanta que as categorias de emoji e o placeholder de busca estejam totalmente localizados em português (pt-BR) utilizando as propriedades padrão `:group-names` e `:static-texts`:

```typescript
const groupNames = {
  recently_used: 'Usados recentemente',
  smileys_people: 'Emoções e Pessoas',
  animals_nature: 'Animais e Natureza',
  food_drink: 'Comida e Bebida',
  activities: 'Atividades',
  travel_places: 'Viagem e Lugares',
  objects: 'Objetos',
  symbols: 'Símbolos',
  flags: 'Bandeiras'
};

const staticTexts = {
  placeholder: 'Procurar emoji...',
  skinTone: 'Tom de pele'
};
```

### 4. Integração Dinâmica de Temas
Determine o tema programaticamente com base na configuração ativa do usuário (ex: estado da store, classe HTML ou consultas de mídia) em vez de fixar estaticamente `theme="light"`.

Passe o atributo de tema dinâmico para o seletor:
```vue
<LazyEmojiPicker :theme="currentAppTheme" />
```

Garanta a consistência visual personalizando as cores do componente utilizando variáveis CSS dentro de blocos SCSS escopados:
```scss
.picker-container {
  .v3-emoji-picker {
    --v3-background: var(--bg-primary);
    --v3-border-color: var(--border-color);
    --v3-search-background: var(--bg-secondary);
    --v3-search-text-color: var(--text-primary);
  }
}
```

### 5. Manipulação de Clique Fora (Click-Outside) e Segurança de Memória
Utilize um mecanismo confiável (como o `onClickOutside` do MaxUse (`@maxvue/max-use`, que reexporta o VueUse) ou popovers nativos) para lidar com o fechamento do seletor em cliques externos. Certifique-se de limpar todos os event listeners personalizados durante a desmontagem (`onUnmounted`) para evitar vazamentos de memória.

---

## Restrições
- **NÃO** importe o `EmojiPicker` de forma síncrona. Sempre envolva-o dentro de `defineAsyncComponent` (que já gerencia o estado de carregamento; `<Suspense>` é desnecessário).
- **NÃO** anexe emojis estritamente no final do texto a menos que as referências da posição do cursor não estejam disponíveis ou estejam vazias.
- **NÃO** fixe de forma estática os temas `"light"` ou `"dark"`; torne-os reativos com base no contexto de tema global da aplicação.
- **NÃO** ignore os parâmetros de localização para o português (`pt-BR`).
- **NÃO** formate atributos do template SFC em múltiplas linhas. Mantenha todos os atributos na mesma linha (ex: `<Componente param1="..." param2="..." />`).
