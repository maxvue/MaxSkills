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

*Os atributos nos templates devem ser mantidos inline em uma única linha (ex: `<MyComponent prop1="val1" prop2="val2" />`). Não quebre os atributos dos componentes em várias linhas.*

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
- O backend exporta automaticamente modelos e DTOs no arquivo `resources/Types/generated.d.ts` como tipos globais (ex: `Brand`, `Bug`, `Client`, `User`).
- Acesse estes tipos globalmente em toda a aplicação frontend. **Não escreva imports manuais** para esses tipos gerados.
- Evite o uso do tipo `any`. Consulte o arquivo `generated.d.ts` ou `_ide_helper_models.php` para identificar os tipos corretos das tabelas e relacionamentos.
- Trate relacionamentos de forma explícita (ex: `Client & { projects?: Project[] }` ou `Client: { projects?: Project[] }`).

## 5. Stores do Pinia (Setup Stores)
- Use Setup Stores no Pinia. Tipifique explicitamente as referências de estado, getters e retornos de actions.
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
- **Options API é proibida:** Não utilize as opções `data()`, `methods` ou `computed`. Sempre use `<script setup lang="ts">`.
- **SCSS é obrigatório:** Não utilize CSS padrão, Less ou utilitários (como Tailwind) a menos que utilize as classes utilitárias do UnoCSS.
- **Proibido o uso de `any`:** A checagem do compilador do TypeScript deve passar sem erros. Todos os tipos devem ser declarados ou importados.
- **Idioma dos Comentários:** Todos os comentários nos códigos devem ser escritos estritamente no idioma Português do Brasil (pt-BR).
