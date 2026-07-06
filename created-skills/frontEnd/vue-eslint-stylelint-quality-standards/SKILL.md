---
name: vue-eslint-stylelint-quality-standards
description: Use ao rodar ou corrigir ESLint (flat config, v10) e Stylelint (v17, .stylelintrc.json) em SFCs Vue 3 e SCSS do frontend engeapp, ou ao investigar falhas de lint/formatação no CI. Cobre block-order template/script/style, indent 4, aspas simples, semi always, comma-dangle never, arrow-parens always, script-indent baseIndent 1 e ignorePseudoElements v-deep/v-global/v-slotted.
---

# Vue ESLint e Stylelint - Padrões de Qualidade

## Objetivo
Depurar e corrigir problemas de estilo e qualidade do código frontend do engeapp de acordo com as regras REAIS configuradas: ESLint 10 em `eslint.config.js` (flat config) e Stylelint 17 em `.stylelintrc.json`. Só cite como "regra do linter" o que estiver de fato nesses arquivos — o restante são convenções do projeto (ver `CLAUDE.md`) que o linter não valida.

## Regras do ESLint (`eslint.config.js`)
Aplicam-se a `**/*.{ts,js,mts,vue}`; use os nomes reais das regras ao explicar cada erro:

- **`vue/block-order`**: ordem obrigatória dos blocos do SFC: `template`, depois `script`, por fim `style`.
- **`@stylistic/indent: 4`** (TS/JS/mts): indentação de 4 espaços. Em `.vue` essa regra é desligada e substituída por `vue/html-indent: 4` (template) e `vue/script-indent: [4, { baseIndent: 1, switchCase: 1 }]` — o corpo do `<script>` é indentado 1 nível base (a tag `<script>` em si não é indentada).
- **`@stylistic/quotes: single`**: aspas simples em strings JS/TS.
- **`@stylistic/semi: always`**: ponto e vírgula obrigatório ao fim das declarações.
- **`@stylistic/comma-dangle: never`**: sem vírgula pendente em objetos/arrays.
- **`@stylistic/arrow-parens: always`**: sempre parênteses nos parâmetros de arrow functions.
- **`@stylistic/object-curly-spacing: always`**: espaço interno em `{ ... }`.
- **`@stylistic/member-delimiter-style`**: `;` como delimitador de membros de interfaces/types (obrigatório em multiline).
- **`@stylistic/no-trailing-spaces`** e **`@stylistic/no-multi-spaces`**: `warn` (não bloqueiam).
- **`@stylistic/no-multiple-empty-lines: { max: 2 }}`**.
- **`curly: [multi]`** + **`@stylistic/nonblock-statement-body-position: beside`**.
- **`@stylistic/padding-line-between-statements`** (só `.vue`): linha em branco depois do bloco de imports, mas nunca entre imports consecutivos.
- **`vue/multi-word-component-names: off`**; **`vue/no-unused-vars`** e **`@typescript-eslint/no-unused-vars`**: `warn`.

Prefira Composition API com `<script setup lang="ts">` (convenção do projeto; não há regra ESLint que a force).

## Regras do Stylelint (`.stylelintrc.json`)
Estende `stylelint-config-standard-scss` + `stylelint-config-standard-vue`, com overrides:

- **`@stylistic/indentation: 4`**: 4 espaços em SCSS.
- **`@stylistic/string-quotes: single`**: aspas simples em CSS/SCSS.
- **`@stylistic/declaration-block-trailing-semicolon: always`**: `;` ao fim de cada declaração.
- **`scss/at-rule-no-unknown: true`**: sinaliza at-rules desconhecidas.
- **`selector-pseudo-element-no-unknown`** com `ignorePseudoElements: [v-deep, v-global, v-slotted]`: esses pseudo-elementos do Vue NÃO geram erro.
- Desligados: `selector-class-pattern`, `no-descending-specificity`, `no-empty-source`, `declaration-block-single-line-max-declarations`.

## Comandos de correção automática
- **ESLint (via script npm):** `npm run lint` ou `npm run format` — ambos executam `eslint resources/ --fix`. Para um arquivo isolado: `npx eslint --fix <caminho>`.
- **Stylelint:** NÃO há script npm para stylelint (nem no `lint`/`format` nem no CI). Rode avulso via CLI: `npx stylelint --fix <caminho>` (ex.: `npx stylelint "resources/**/*.{scss,vue}" --fix`).
- Há também `npm run typecheck:tsgo` (`tsgo --noEmit`) para checagem de tipos — separado do lint.

## Convenções do projeto (NÃO validadas por linter)
Estas vêm do `CLAUDE.md`, não do ESLint/Stylelint — trate-as como preferência de estilo, não como erro de lint:
- `div` com `v-for` **preferencialmente** em uma única linha, evitando quebras excessivas (`CLAUDE.md`); não é regra absoluta e não existe `vue/max-attributes-per-line` configurada.
- Evite `<section>` como container: um `<MaxGrid>` acompanhado de `<MaxTitle*>` já atua estruturalmente como section.
- Convenções de componentes/composables (usar `MaxInputText`/`MaxButton` no lugar de nativos, `@maxvue/max-use` no lugar de `@vueuse/core`/`lodash`, `MaxTitle1`/`MaxTitle2` no lugar de headings nativos, `MaxGrid` para formulários) são cobertas pelas skills `vue-max-stack-frontend` e afins — fora do escopo de linting.

## Restrições
- **Idioma:** Comunique-se com o usuário humano sempre em Português (pt-BR), independentemente do idioma do corpo desta skill.
- NÃO utilize Options API; use Composition API com `<script setup lang="ts">`.
- Ao relatar um erro de lint, cite o nome real da regra (ex.: `@stylistic/comma-dangle`) e o arquivo (`eslint.config.js` ou `.stylelintrc.json`); não atribua ao linter convenções que só existem no `CLAUDE.md`.
