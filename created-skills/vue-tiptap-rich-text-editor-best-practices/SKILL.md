---
name: vue-tiptap-rich-text-editor-best-practices
description: Use when designing, implementing, styling, or debugging a rich text editor component based on Tiptap in Vue 3 (EngeApp, domínio fotovoltaico/solar). Triggers on editor configuration, custom extensions for mentions (@) of usuários/equipamentos or hashtags (#) for categorias, character count integration for limit constraints, HTML sanitization, and dynamic variable replacements.
---

## Objetivo
Fornecer diretrizes e padrões de alta qualidade para projetar, implementar, estilizar e depurar editores de texto rico baseados no Tiptap em Vue 3 (Composition API e TypeScript) dentro do ecossistema Engeapp.

## Instruções

## 1. Configuração Básica do Editor
Ao configurar o Tiptap no Vue 3, utilize sempre o helper `useEditor` de `@tiptap/vue-3` combinado com os hooks de ciclo de vida do Vue para montar e destruir corretamente a instância.

```typescript
import { useEditor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';

const editor = useEditor({
  content: props.modelValue,
  extensions: [
    StarterKit.configure({
      // Configurar opções do Starter Kit
    }),
  ],
  onUpdate: ({ editor }) => {
    // Retorna HTML ou Markdown dependendo do caso de uso
    emit('update:modelValue', editor.getHTML());
  },
});
```

* Certifique-se de que o `editor` seja destruído adequadamente em `onBeforeUnmount` (resolvido automaticamente pelo `useEditor`, mas wrappers customizados precisam garantir essa limpeza).
* Sempre coloque o elemento `<EditorContent :editor="editor" />` no template.

## 2. Sincronização de Formato (Markdown & HTML)
* Se Markdown for necessário (padrão no componente `MaxInputMarkdown` de `@maxvue/max-components-ui`), integre o pacote `tiptap-markdown` e configure-o adequadamente para evitar salvar tags HTML não escapadas.
* Sincronize atualizações de forma bidirecional monitorando a propriedade `modelValue` e comparando-a com o estado atual armazenado no editor antes de definir o novo conteúdo, para evitar loops infinitos que reposicionam o cursor.

## 3. Extensões de Menções (@) e Hashtags (#)
Para configurar menções (usuários, equipamentos/inversores) e hashtags (categorias/projetos):
* Importe e instale `@tiptap/extension-mention`.
* Configure a extensão de menção com gatilhos customizados (ex: `@` para usuários/equipamentos, `#` para categorias).
* Use uma configuração customizada de Suggestion utilizando um componente de popup (como dropdown list ou float popover) para listar sugestões filtradas por query.
* Defina a configuração da extensão da seguinte forma:

```typescript
import Mention from '@tiptap/extension-mention';
import suggestion from './suggestion';

const MentionExtension = Mention.extend({
  name: 'mention',
}).configure({
  HTMLAttributes: { class: 'editor-mention' },
  suggestion: suggestion('@'),
});

const HashtagExtension = Mention.extend({
  name: 'hashtag',
}).configure({
  HTMLAttributes: { class: 'editor-hashtag' },
  suggestion: suggestion('#'),
});
```

## 4. Integração de Limite de Caracteres
Para limitar campos de texto com tamanho máximo (ex: descrição de projeto, observações de proposta):
* Use a extensão `@tiptap/extension-character-count`.
* Configure o `limit` dinamicamente com base no campo/contexto.
* Exiba feedbacks visuais reativos para o usuário (ex: alteração de cor do contador de verde para vermelho ao se aproximar ou exceder os limites) e impeça inserções adicionais ou valide o estado utilizando schemas do Zod.

## 5. Sanitização de HTML
* Sempre sanitize a entrada e saída de HTML ao interagir com o backend utilizando uma biblioteca confiável (ex: DOMPurify) para prevenir vulnerabilidades de Cross-Site Scripting (XSS).
* Mantenha o schema do Tiptap estrito, permitindo apenas tags e atributos explicitamente suportados pela barra de ferramentas do editor.

## 6. Substituição Dinâmica de Variáveis
* Implemente um nó customizado do ProseMirror ou marca inline para tags de substituição dinâmicas (ex: `{{nome_cliente}}`, `{{potencia_kwp}}`).
* Use chips/badges visuais interativos no editor em vez de colchetes de texto puro para que os usuários possam facilmente identificá-los e apagá-los.

## Restrições
* **NUNCA** utilize a Options API. Sempre utilize `<script setup lang="ts">`.
* **NUNCA** utilize TailwindCSS. Para a UI ao redor do editor use UnoCSS attributify (`presetMaxUno` de `@maxvue/max-components-ui`) e componentes Max. Para estilizar os nós internos do ProseMirror (`.ProseMirror`), use classes SCSS escopadas com variáveis CSS/tokens do design system, já que essas regras alcançam markup gerado pelo Tiptap.
* **NUNCA** atualize o conteúdo do editor diretamente a cada alteração de propriedade (`prop`) sem comparar primeiro (utilizando `editor.getHTML()` ou `getMarkdown()`). Isso causaria perda da posição atual do cursor do usuário.
* **NÃO** utilize estilos CSS inline para elementos do Tiptap. Estilizações da classe `.ProseMirror` e auxiliares devem estar dentro de blocos `<style scoped lang="scss">`.
* Todos os itens interativos (popovers, list items) nos menus de sugestão customizados **DEVEM** ter IDs únicos e descritivos para fins de testes automatizados do navegador.
