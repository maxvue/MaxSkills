---
name: vue-typescript-best-practices
description: Use when writing, reviewing, or debugging Vue 3 components, composables, Pinia stores, or utility functions written in TypeScript, or when adjusting TypeScript configurations (tsconfig.json, declare module) in the frontend. Triggers on defineProps, defineEmits, ComputedRef, PropType, typed ref, and compiler type-check issues in Vue/TS files.
---

## Objetivo
Garantir a segurança de tipos, estrutura limpa de código e total conformidade com o compilador do TypeScript no desenvolvimento com Vue 3 no ecossistema Engeapp, utilizando componentes tipados, composables, stores do Pinia e DTOs integrados ao backend.

## Instruções

## 1. Estrutura do Componente Single File (SFC)
Sempre estruture os componentes SFC do Vue na seguinte ordem de blocos:
1. `<template>`: Estrutura HTML.
2. `<script setup lang="ts">`: Lógica da Composition API em TypeScript.
3. `<style scoped lang="scss">` ou `<style lang="scss">`: Estilização escrita em SCSS.

*Os atributos nos templates devem ser mantidos **sempre inline**, em uma única linha, por mais atributos que a tag tenha — vale para componentes, `div` e qualquer elemento. **Nunca** quebre atributos em várias linhas.*

❌ Errado:
```vue
<MaxModal
    ref="cardModal"
    no-button
    class="card-modal"
>
```

✅ Certo:
```vue
<MaxModal ref="cardModal" no-button class="card-modal">
```

*Nunca use `<section>`: prefira sempre `<div>` no lugar de `<section>` (e de outras tags seccionais) para agrupar conteúdo.*

*Nunca use inputs/botões nativos em código de aplicação (`<input>`, `<button>`, `<select>`, `<textarea>`): use sempre os componentes **MaxComponentsUi** (`MaxInputText`, `MaxInputNumber`, `MaxInputSelect`, `MaxInputTextArea`, `MaxInputCheckbox`, `MaxButton`, `MaxIconButton`, etc.). O elemento nativo só é permitido ao construir a própria biblioteca MaxComponentsUi.*

*Nunca importe `@vueuse/core` nem `lodash` diretamente: use os composables e o objeto `_` (estilo lodash) do **MaxUse** (`@maxvue/max-use`). Se faltar algo, adicione ao MaxUse encapsulando o VueUse — não importe `@vueuse/core`/`lodash` no código de aplicação.*

*Nunca use headings nativos (`<h1>`/`<h2>`/`<h3>`/`<h4>`) como título: use `<MaxTitle1 h1="Título" h2="Subtítulo" />` (título principal) e `<MaxTitle2 h1="Título da seção" />` (seção).*

*Formulários usam `MaxGrid` (nunca `MaxGridCols`): dimensione os campos internos com atributos UnoCSS — `s-[porcentagem]` (ex.: `s-30` = 30% da largura do formulário) e `[w|h]-[max|min]-[valor]` (px sem unidade, ou `rem`: `w-max-300`, `h-min-50`, `w-min-10rem`).*

## 2. Tipagem de defineProps e defineEmits
- **defineProps:** Use declarações baseadas em tipo (`defineProps<{ ... }>()`) em vez de arrays ou objetos em tempo de execução. Utilize `withDefaults` para definir valores padrão para as propriedades.
  ```typescript
  interface Props {
      clientId: string;
      isActive?: boolean;
      role?: 'admin' | 'user';
  }

  const props = withDefaults(defineProps<Props>(), {
      isActive: true,
      role: 'user',
  });
  ```
- **defineEmits:** Use emissões tipadas para garantir a validação estrita dos eventos.
  ```typescript
  const emit = defineEmits<{
      (e: 'update', id: string): void;
      (e: 'close'): void;
  }>();
  ```

## 3. Estado Reativo e Referências de Template
- **Refs e Propriedades Computadas:** Defina explicitamente o tipo de refs quando o valor inicial for null ou complexo.
  ```typescript
  import { ref, computed, ComputedRef, Ref } from 'vue';

  const clientData: Ref<Client | null> = ref<Client | null>(null);
  const isLoaded = ref<boolean>(false);

  const formattedName: ComputedRef<string> = computed<string>(() => {
      return clientData.value ? `${clientData.value.name}` : '';
  });
  ```
- **Template Refs:** Especifique o elemento DOM ou o tipo do componente alvo.
  ```typescript
  const modalContainer = ref<HTMLDivElement | null>(null);
  ```

## 4. Consumo de Tipos Gerados pelo Backend
- O backend AdonisJS exporta automaticamente modelos Lucid e DTOs como tipos globais (ex: `Brand`, `Client`, `User`, `Projeto`) em um arquivo de definições `.d.ts` gerado.
- Acesse estes tipos globalmente em toda a aplicação frontend. **Não escreva imports manuais** para esses tipos gerados.
- Evite o uso do tipo `any`. Consulte o arquivo de tipos gerado (`.d.ts`) para identificar os tipos corretos das tabelas e relacionamentos. Não há `_ide_helper_models.php` neste stack (era um artefato do Laravel/IDE Helper).
- Trate relacionamentos de forma explícita (ex: `Client & { projects?: Project[] }` ou `Client: { projects?: Project[] }`).

## 5. Stores do Pinia (Setup Stores)
- **Dados de página vindos do backend (GET) e salvamento (save) DEVEM passar por uma store `@maxvue/max-pinia`**, que é a camada padrão de cache + auto-save (debounced) do projeto. Não faça `axios.get`/`axios.post` manuais nem salvamento por submit manual para dados de página; o próprio MaxPinia faz o GET e o save usando a instância axios que ele injeta internamente, contra uma **rota string** configurada nas `options` da store (não usa `apiGetRoute`). Reserve `apiGetRoute`/`apiPostRoute` para chamadas pontuais fora do fluxo da store cacheada. Tipifique explicitamente o estado da store.
  ```typescript
  import { defineStore } from 'pinia';
  import { ref, computed } from 'vue';

  export const useClienteStore = defineStore('cliente', () => {
      // Contrato da store cacheada: `data` guarda o estado do servidor, `isCached` ativa
      // a camada MaxPinia e `options` fornece as rotas string. Com isso o plugin faz o GET
      // (cache-first) e o auto-save (debounce 300ms sobre `data`) automaticamente.
      const data = ref<Client | null>(null);
      const isCached = ref(true);

      const options = computed(() => ({
          get:  { route: '/api/cliente' }, // GET automático + cache
          save: '/api/cliente',            // opcional: POST com auto-save debounced
          id:   'cliente',                 // alimenta a chave de cache do localforage
      }));

      const possuiProjetos = computed<boolean>(() => (data.value?.projects?.length ?? 0) > 0);

      return { data, isCached, options, possuiProjetos };
  });
  ```
- Para estado puramente local de UI (sem origem no backend), uma Setup Store Pinia comum (`defineStore` de `pinia`) é aceitável. Tipifique explicitamente refs de estado, getters e retornos de actions.
  ```typescript
  import { defineStore } from 'pinia';
  import { ref, computed } from 'vue';

  export const useActiveUserStore = defineStore('activeUser', () => {
      const currentUser = ref<User | null>(null);
      const isAuthenticated = computed<boolean>(() => currentUser.value !== null);

      function setCurrentUser(user: User | null): void {
          currentUser.value = user;
      }

      return { currentUser, isAuthenticated, setCurrentUser };
  });
  ```

## 6. Resolução de Rotas com TypeScript
- Não existe Ziggy neste projeto (é nativo do Laravel e foi descontinuado). Use os helpers `apiGetRoute`/`apiPostRoute` do `@maxvue/max-use`, que resolvem para caminhos string `/api/...`.
- Respeite as assinaturas de parâmetros esperadas pelo backend. Evite passar objetos não tipados para endpoints que esperam parâmetros específicos.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Options API é proibida:** Não utilize as opções `data()`, `methods` ou `computed`. Sempre use `<script setup lang="ts">`.
- **SCSS é obrigatório:** Não utilize CSS padrão, Less ou utilitários (como Tailwind) a menos que utilize as classes utilitárias do UnoCSS.
- **Proibido o uso de `any`:** A checagem do compilador do TypeScript deve passar sem erros. Todos os tipos devem ser declarados ou importados.
- **Idioma dos Comentários:** Todos os comentários nos códigos devem ser escritos estritamente no idioma Português do Brasil (pt-BR).
