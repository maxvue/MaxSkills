---
name: vue-eslint-stylelint-quality-standards
description: Use when linting, formatting, or resolving ESLint and Stylelint issues in Vue 3 Single-File Components (SFC) or SCSS styles within the Engeapp frontend. Triggers on ESLint configuration, stylelint configuration, formatting errors, and frontend CI/CD linting check failures.
---

# Vue ESLint e Stylelint - Padrões de Qualidade

## Objetivo
Estabelecer diretrizes unificadas para a depuração, formatação e resolução de inconsistências de estilo e qualidade do código frontend utilizando ESLint 10 e Stylelint 17.

## Instruções
1. **Resolução de ESLint**:
   - Mantenha a ordem oficial de blocos do Single-File Component (SFC): `<template>`, depois `<script>`, e por fim `<style>`.
   - Sempre utilize a Composition API com `<script setup lang="ts">`.
   - Dentro de `<script>`, aplique uma indentação base de 1 nível (4 espaços) conforme configurado em `vue/script-indent`. Não indente a tag `<script>` em si, mas indente todas as declarações dentro dela.
   - Para arquivos TypeScript/JavaScript e scripts, aplique indentação de 4 espaços, aspas simples (`'`), ponto e vírgula obrigatório ao final (`;`), sem espaços extras no final das linhas, sem vírgulas pendentes (comma-dangle) para arrays/objetos, e sempre envolva os parâmetros de arrow functions com parênteses.
   - Mantenha **sempre** os atributos de componentes/elementos em templates Vue em uma única linha (sem quebrar atributos em múltiplas linhas), por mais atributos que a tag tenha. Vale para componentes, `div` e qualquer elemento.
   - Nunca use `<section>`: prefira sempre `<div>` no lugar de `<section>` (e de outras tags seccionais) para agrupar conteúdo.

2. **Resolução de Stylelint**:
   - Indente as regras SCSS com 4 espaços.
   - Envolva strings em aspas simples (`'`).
   - Sempre finalize os blocos de declaração com ponto e vírgula (`;`).
   - Garanta que regras at-rule desconhecidas sejam sinalizadas a menos que ignoradas, e não gere erros em pseudo-elementos como `v-deep`, `v-global`, `v-slotted` (eles estão registrados como ignorados).

3. **Comandos de Correção Automática**:
   - Execute as ferramentas de lint locais ou comandos CLI com as flags de correção:
     - ESLint: `npx eslint --fix <caminho_do_arquivo>`
     - Stylelint: `npx stylelint --fix <caminho_do_arquivo>`

## Restrições
- NÃO utilize Options API sob nenhuma circunstância.
- NÃO quebre atributos de componentes/elementos SFC em múltiplas linhas dentro dos templates; mantenha-os todos na mesma linha (regra absoluta, independente da quantidade de atributos).
- NÃO use `<section>` (nem `<article>`/`<aside>` como container genérico); use sempre `<div>` no lugar.
- NÃO use inputs/botões nativos (`<input>`, `<button>`, `<select>`, `<textarea>`) em código de aplicação; use os componentes MaxComponentsUi (`MaxInputText`, `MaxButton`, etc.).
- NÃO importe `@vueuse/core` nem `lodash` diretamente; use os composables/utilitários do MaxUse (`@maxvue/max-use`).
- NÃO use headings nativos (`<h1>`, `<h2>`, `<h3>`, `<h4>`) como título; use `MaxTitle1`/`MaxTitle2`.
- NÃO use `MaxGridCols` em formulários; use `MaxGrid` e dimensione os campos com atributos (`s-30`, `w-max-300`, `h-min-50`, `w-min-10rem`).
- NÃO utilize aspas duplas para strings JS/TS ou CSS/SCSS a menos que estejam aninhadas.
- NÃO adicione vírgulas pendentes em objetos ou arrays (`comma-dangle` é desativado/sinalizado como erro `never`).
- NÃO remova pontos e vírgulas obrigatórios no fim de declarações (`semi` está definido como `always`).
