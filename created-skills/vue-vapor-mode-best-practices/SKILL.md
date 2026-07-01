---
name: vue-vapor-mode-best-practices
description: Use when developing, reviewing, or debugging Vue 3 components using the experimental Vapor Mode, configuring the vaporInteropPlugin, managing reactive state without Virtual DOM, or integrating Vapor components with traditional VDOM components. Triggers on Vapor compilation, .vapor.vue files, vapor import, and VDOM interop.
---

# Boas Práticas do Vapor Mode (experimental) no Vue

## Objetivo
Estabelecer diretrizes sólidas, padrões de desenvolvimento e padrões de performance para criar e otimizar componentes do Vue utilizando o Vapor Mode (experimental, ainda sem release estável — não presuma uma versão específica) no ecossistema Engeapp.

## Instruções
1. **Configuração e Declaração de Componentes**:
   - O Vapor é ativado pelo tooling de build, não por uma sintaxe canônica no SFC. Marque componentes Vapor pela convenção de arquivo `.vapor.vue` e registre o `vaporInteropPlugin` (ver seção de Interop) para habilitar a compilação.
   - O atributo `<script setup lang="ts" vapor>` existe mas ainda **não é estável/canônico** — não o trate como a API oficial; prefira o mecanismo de build (`.vapor.vue` + `vaporInteropPlugin`) enquanto o Vapor for experimental.
   - Certifique-se de que a ordem dos blocos SFC segue o padrão do projeto: `<template>` primeiro, depois `<script setup>` e, por fim, `<style lang="scss" scoped>`.

2. **Reatividade e Gerenciamento de Estado Puro**:
   - Aproveite a reatividade direta e granular. O Vapor Mode ignora o Virtual DOM, compilando refs e computeds diretamente em operações de atualização de DOM refinadas.
   - Prefira o uso de `ref`, `computed` e `shallowRef` padrão para minimizar o overhead de reatividade.
   - Garanta que os composables (do MaxUse — `@maxvue/max-use`, que reexporta o VueUse) retornem estados reativos limpos e não envelopados que possam ser vinculados diretamente ao template.

3. **Interoperabilidade com Virtual DOM (VDOM Interop)**:
   - Ao importar componentes tradicionais de VDOM para dentro de um componente Vapor (ou vice-versa), certifique-se de que o `vaporInteropPlugin` esteja registrado corretamente na aplicação principal do Vue (`app.ts`).
   - Para Vapor dentro de VDOM: Componentes VDOM tradicionais podem importar e renderizar componentes Vapor perfeitamente, já que o Vapor gera definições de componentes padrão.
   - Para VDOM dentro de Vapor: Ao renderizar componentes VDOM (como elementos do `MaxComponentsUi`) dentro de um pai Vapor, envolva-os adequadamente e gerencie suas entradas/saídas de forma estrita, lembrando que atualizações do VDOM podem disparar ciclos completos de diff virtual para esses filhos.

4. **Diretrizes de Template e Diretivas**:
   - Mantenha os templates limpos e inline. Para componentes Vue, mantenha todos os atributos/parâmetros na mesma linha: `<MyComponent attr1="..." attr2="..." />`.
   - Fique atento às limitações de diretivas sob o modo experimental Vapor (ex: modificações de `v-model`, templates dinâmicos complexos). Certifique-se de que o `v-for` utilize sempre uma chave `:key` estrita e única para permitir a atualização granular ideal do DOM.

## Restrições
- **NÃO** utilize a Options API. Sempre utilize a Composition API com `<script setup lang="ts">` em componentes Vapor (habilitados via `.vapor.vue` + `vaporInteropPlugin`).
- **NÃO** utilize estilos CSS puros; use SCSS (`lang="scss" scoped`).
- **NÃO** ignore a segurança de tipos; toda a lógica deve ser tipada em TypeScript.
- **NÃO** aninhe componentes VDOM complexos dentro de loops de renderização Vapor de alta frequência sem validar o uso de memória e os custos de repintura (repaint).
