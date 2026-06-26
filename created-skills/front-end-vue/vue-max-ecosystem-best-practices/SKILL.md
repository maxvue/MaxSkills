---
name: vue-max-ecosystem-best-practices
description: >-
  Use when working with @maxvue/max-components-ui or @maxvue/max-use — the custom UI and utility
  libraries of the Maxdmin project. Covers MaxButton, MaxModal, MaxTable, MaxGrid, MaxGridCols,
  MaxInput* form components, InputBase validation wrapper, MaxIcon (Iconify), Brazilian formatters
  and validators (_), cached composables (useRefCached, useRefCachedApi), and MaxUse route helpers
  (apiGetRoute, apiPostRoute) that resolve to /api string paths. Triggers on any Max* component, @maxvue import, or reference to the
  MaxComponentsUi/MaxUse libraries. For general SFC structure and Pinia store patterns, use
  vue-maxvue-frontend-best-practices instead.
---

# Melhores Práticas do Ecossistema Vue Max

## Objetivo

Fornecer diretrizes claras para o uso consistente e otimizado da biblioteca de componentes `@maxvue/max-components-ui` (baseada no PrimeVue 4) e da biblioteca de utilitários `@maxvue/max-use` no frontend do Engeapp.

## Instruções

### Parte 1: UI e Componentes (@maxvue/max-components-ui)

#### 1. Prefira Componentes do Catálogo

Antes de construir elementos customizados, verifique o `resources/components-catalog.md`. Dê preferência a componentes como `MaxButton`, `MaxInputText`, `MaxModal`, `MaxTable`, `MaxGrid` e `MaxGridCols`.

#### 2. Layout & Grids

- Organize layouts usando `MaxGrid` (wrapper flexbox) ou `MaxGridCols` (grid de 24 colunas).
- Use atalhos de tamanho UnoCSS em elementos filhos: `s100` (100%), `s50` (50%), `s33` (33%) e `s25` (25%).

#### 3. Formulários e Validação

- Utilize wrappers de input (`MaxInputText`, `MaxInputCep`, `MaxInputCpfCnpj`) para herdar o layout e erros baseados no componente `InputBase`.
- Controle os estados de formulário: `:done="isValid"`, `:error="errorMessage"`, `:caution="warningMessage"`.

#### 4. Tabelas e Listagens

- **`MaxTable`**: Para tabelas de leitura padrão com cabeçalhos fixos.
- **`MaxTableFields`**: Para tabelas editáveis com campos interativos (configurado via `MaxTableColumn`).

#### 5. Modais

- Implemente popups através de `MaxModal`. Interaja com o modal utilizando métodos expostos (`toggle()`, `show()`, `hide()`) ou pela store global `useModalStore`.

### Parte 2: Utilitários e Reatividade (@maxvue/max-use)

#### 1. Importação Modular (Recomendado)

Para melhorar o tree-shaking do bundle, faça importações modulares sempre que possível:

```ts
import { isCpf, cepIsValid } from '@maxvue/max-use/validations'
import { formatCurrency } from '@maxvue/max-use/format'
import { useTimeAgo } from '@maxvue/max-use/composables'
import { apiGetRoute, goToRoute } from '@maxvue/max-use/routes'
```

*(Também é possível acessar a interface fundida via `import { _ } from '@maxvue/max-use'` se houver múltiplos utilitários.)*

#### 2. Reatividade e Ref

Todos os métodos são criados para serem nativamente reativos, aceitando `Refs` ou getters `() => T`. Eles usam `toValue()` para atualizar seus retornos se os parâmetros mudarem.

#### 3. Utilitários Locais Brasileiros

Jamais escreva Regex customizado para dados do Brasil.

- **Validações**: `isCpf()`, `isCnpj()`, `isCpfCnpj()`, `cepIsValid()`, `phone()`.
- **Formatações**: `formatCurrency()`, `formatCpf()`, `formatCnpj()`, `formatPhone()`, e máscara de segurança `maskSensitive()`.

#### 4. Composables Customizados

- `useRefCached(key, initial)`: Sincroniza uma Ref com `localStorage`.
- `useDefaultReset(initial)`: Ref que pode ser zerada (com auto-ULID e data de criação automática).
- `useTimeAgo()`: Fornece tempo relativo em pt-BR ("Mês passado", "Em 3 dias"). Formatos úteis: `br`, `abbrev`, `action`, `limit`.

#### 5. Integração com a API do AdonisJS

Gerencie as requisições API e URLs usando os helpers do `@maxvue/max-use` (resolvem para caminhos string `/api/...`; **não existe Ziggy** — é nativo do Laravel e foi descontinuado):

- `apiGetRoute`, `apiPostRoute`, `apiPutRoute`, `apiDeleteRoute`, `apiUploadRoute`.
- Para buscar dados, prefira uma store `@maxvue/max-pinia` (todo GET deve passar por store — cache + auto-save).
- Navegação SPA via Vue Router com `goToRoute`. **Nunca use Inertia.js.**

## Restrições

- **NÃO** escreva SCSS customizado (como width, height, padding, margin) que possa ser solucionado pelo preset UnoCSS.
- Mantenha os blocos em arquivos Single File Component estritamente nesta ordem: `<template>`, `<script setup lang="ts">`, `<style scoped lang="scss">`.
- Os atributos em tags dentro de `<template>` devem ficar *inline* (em uma única linha), não devendo ser quebrados em múltiplas linhas.
- **NÃO** utilize funções cruas (`unref()`) do Vue dentro dos wrappers. Use apenas a biblioteca.
