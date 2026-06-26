# INSTRUÇÕES GERAIS PARA A CRIAÇÃO OU ATUALIZAÇÃO DE ARQUIVOS .VUE #
Use esta skill como um conjunto de instruções **obrigatórias** sempre que for criar ou editar um componente Vue (arquivos `.vue`).

## Regras Absolutas de Arquitetura
- **Composition API**: É estritamente obrigatório utilizar a Composition API (`<script setup>` ou `setup()`). 
- **Options API Banida**: Jamais, sob nenhuma circunstância, utilize a Options API (ex: `data()`, `methods`, `computed` dentro do objeto de opções padrão).
- **TypeScript Obrigatório**: Todo código lógico no componente deve ser em TypeScript (`lang="ts"`).
- **SCSS Obrigatório**: Todo o estilo deve ser em SCSS (`lang="scss"`).

## Ordem de Blocos SFC (Single-File Component)
Ao construir ou refatorar o componente, você deve SEMPRE estruturar os blocos na seguinte ordem, **sem exceções**:
1. `<template></template>`
2. `<script lang="ts"></script>` ou `<script setup lang="ts"></script>`
3. `<style lang="scss"></style>` ou `<style scoped lang="scss"></style>`

### Exemplo de Estrutura Esperada

```vue
<template>
  <div class="my-component">
    <h1>{{ title }}</h1>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const title = ref<string>('Hello World');
</script>

<style scoped lang="scss">
.my-component {
  h1 {
    color: blue;
  }
}
</style>
```

## Boas Práticas Adicionais
- **Props e Emits**: Utilize `defineProps` e `defineEmits` da Composition API para tipagem explícita com TS.
- **Evitar re-renderizações desnecessárias**: Utilize propriedades computadas (`computed`) em vez de métodos para valores derivados que não precisam ser recalculados a cada ciclo de renderização.
- **Idioma**: Os comentários do código devem sempre ser escritos no idioma Português do Brasil (pt-BR).
- **Template**: Dentro da seção Template, formate os componentes Vue mantendo todos os atributos/parâmetros na mesma linha (estilo inline). Não quebre os atributos em várias linhas, mesmo que a linha fique longa. Mantenha a abertura da tag em uma linha só. Exemplo: <Componente param1="..." param2="..." />
