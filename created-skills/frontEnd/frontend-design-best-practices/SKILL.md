---
name: frontend-design-best-practices
description: "Use when building new UI or remodeling Engeapp screens (Vue 3 + UnoCSS attributify presetMaxUno + @maxvue/max-components-ui). Covers core design mandate, aesthetics, typography, colors, layout, motion, and accessible production code."
---
# Design de Frontend (Distinto, de Nível de Produção)

Você é um **designer-engenheiro de frontend**, não um gerador de layouts.

## Objetivo

Criar **interfaces memoráveis e de alto acabamento** que:

* Evitem padrões genéricos de "UI de IA"
* Expressem um ponto de vista estético claro
* Sejam totalmente funcionais e prontas para produção
* Traduzam a intenção de design diretamente em código

Esta skill prioriza **sistemas de design intencionais**, não frameworks padrão.

## Instruções

### 1. Honre o Mandato Central de Design

Toda saída deve satisfazer **os quatro**, porque juntos separam design intencional de template:

1. **Direção Estética Intencional** — Uma postura de design explícita e nomeada (ex.: *brutalismo editorial*, *minimalismo de luxo*, *retrofuturista*, *utilitarismo industrial*).
2. **Correção Técnica** — Código de framework real e funcional, não mockups.
3. **Memorabilidade Visual** — Pelo menos um elemento que o usuário lembrará 24 horas depois.
4. **Contenção Coesa** — Nenhuma decoração aleatória. Cada floreio deve servir à tese estética.

### 2. Execute a Fase Obrigatória de Pensamento de Design

Antes de escrever código, defina explicitamente — isso evita que a estética seja escolhida por acaso:

**Propósito**

* Qual ação esta interface deve habilitar?
* É persuasiva, funcional, exploratória ou expressiva?

**Tom (escolha uma direção dominante)** — exemplos (não exaustivos):

* Brutalista / Cru
* Editorial / Revista
* Luxo / Refinado
* Retrofuturista
* Industrial / Utilitário
* Orgânico / Natural
* Lúdico / Brinquedo
* Maximalista / Caótico
* Minimalista / Severo

Não misture mais que **dois** tons, para não diluir a identidade.

**Âncora de Diferenciação** — responda:

> "Se isto fosse capturado em tela com o logo removido, como alguém o reconheceria?"

Essa âncora deve estar visível na UI final.

**Antes de construir, faça um sanity check da direção** (mentalmente, sem pontuação cerimonial):

* É visualmente distinta e adequada ao produto, ao público e ao propósito?
* Dá para construir de forma limpa com a stack disponível (Vue 3 + UnoCSS + Max*)?
* Permanece rápida e acessível, e se mantém consistente entre telas/componentes?

Se qualquer resposta for "não", reduza o escopo dos efeitos ou repense a direção antes de codar.

### 3. Aplique as Regras de Execução Estética

**Tipografia**

* A fonte base do app **já é fixada pelo sistema**: o preflight do `presetMaxUno` compila `themes/all.scss` (que faz `@use './font.scss'`) e aplica `font-family: Quicksand, sans-serif` em `body`/`html`/`#app`. As tabelas Max (`MaxTable`, `MaxTableColumn`, `MaxTableFields`) fixam `font-family: Jost, sans-serif`, e `resources/Views/app.blade.php` ainda carrega `instrument-sans`.
* Portanto, a expressividade tipográfica acontece **dentro dessas fontes**: hierarquia, escala, ritmo, contraste de peso (`font-weight-*`) e caixa/tracking — não trocando a família por padrão.
* Se uma fonte de display autoral for realmente necessária, adicione-a em **escopo local** (classe/atributo da própria tela ou bloco), nunca sobrescrevendo o preflight de `body`/`html`/`#app`.
* Evite fontes de sistema e padrões de IA (Inter, Roboto, Arial, etc.) nesses usos locais de display.

**Cor & Tema**

* Comprometa-se com uma **história de cor dominante**
* Use variáveis CSS e tokens do sistema de design Max
* Prefira um tom dominante, um destaque, um sistema neutro
* Evite paletas equilibradas de forma uniforme

**Composição Espacial**

* Quebre o grid intencionalmente
* Use assimetria, sobreposição, espaço negativo OU densidade controlada
* O espaço em branco é um elemento de design, não ausência

**Movimento**

* O movimento deve ser proposital, escasso e de alto impacto
* Prefira uma sequência de entrada forte mais alguns estados de hover significativos
* Evite spam de micromovimento decorativo

**Textura & Profundidade** — use quando apropriado:

* Sobreposições de ruído / grão
* Malhas de gradiente
* Translucidez em camadas
* Bordas ou divisórias personalizadas
* Sombras com intenção narrativa (não padrões)

### 4. Atenda aos Padrões de Implementação

> **Reconciliação com as Restrições:** "sem design-por-componentes" e "sem layouts padrão de bibliotecas de UI" se referem a montar telas com presets genéricos e sem ponto de vista — **não** dispensam o uso obrigatório dos componentes Max. A expressividade acontece em composição, ritmo, densidade, cor e tokens/atributos UnoCSS aplicados aos componentes Max, nunca substituindo-os por elementos nativos.

**Requisitos de Código**

* Limpo, legível e modular
* Sem estilos mortos nem animações não utilizadas
* HTML semântico e acessível por padrão (contraste, foco, teclado)
* **Convenção de novo código: prefira `<div>` a `<section>`** para agrupar conteúdo. Observação: o codebase atual ainda tem `<section>` em telas antigas (ex.: `resources/Vue/Site/Pages/SiteHome.vue`); não é preciso migrá-las, mas siga a convenção `<div>` ao escrever/reformar código.
* **Atributos sempre inline**: mantenha todos os atributos de uma tag (componente, `div` ou qualquer elemento) em uma única linha, por mais atributos que tenha — nunca quebre atributos em múltiplas linhas.

**Orientação de Framework — Max stack (engeapp: Laravel 13 no backend + frontend Vue 3 com tooling Node/Vite)**

* Construa UI em **Vue 3** com **`<script setup>`**, estilos via **UnoCSS attributify** (`presetMaxUno`) e componentes **`@maxvue/max-components-ui`**. Sem o framework Tailwind como dependência standalone e sem React. Classes utilitárias no estilo Tailwind **são aceitas e usadas** via `presetWind3` + `presetAttributify` (ambos registrados em `uno.config.ts` junto com `presetMaxUno`), inclusive dentro dos próprios componentes Max (ex.: `MaxTitle1.vue` usa `text-lg font-medium uppercase`); o que se evita é adicionar o pacote `tailwindcss` como dependência extra. `shadcn-vue`/`radix-vue` estão declarados no `package.json` do engeapp mas não têm uso em `resources/` — não construa UI nova com eles.
* **Nunca use inputs/botões nativos** (`<input>`/`<button>`/`<select>`/`<textarea>`) em código de app — use sempre os componentes MaxComponentsUi (`MaxInputText`, `MaxButton`, `MaxIconButton`, etc.).
* **Nunca use headings nativos** (`<h1>`…`<h4>`) — use `MaxTitle1`/`MaxTitle2`.
* **Formulários usam `MaxGrid`** (nunca `MaxGridCols`), com campos dimensionados por atributos (`s-30`, `w-max-300`, `h-min-50`, `w-min-160`). Essas regras do `presetMaxUno` concatenam `px` cegamente, então aceitam **apenas número puro** — `w-min-10rem` geraria `min-width: 10rempx` e seria descartado pelo browser.
* **Não importe `@vueuse/core` nem `lodash`** — use os composables/utilitários do MaxUse (`@maxvue/max-use`).
* **Animação**: CSS/transições nativas primeiro; bibliotecas de motion apenas quando justificado.

**Correspondência de Complexidade**

* Design maximalista → código complexo (animações, camadas).
* Design minimalista → espaçamento e tipografia extremamente precisos.
* Incompatibilidade entre ambição e código = falha.

### 5. Entregue a Estrutura de Saída Exigida

Ao gerar trabalho de frontend, apresente nesta ordem:

1. **Resumo da Direção de Design** — nome da estética + inspiração-chave (conceitual, não plágio visual). Reforce aqui a Âncora de Diferenciação definida na fase de pensamento de design (seção 2).
2. **Snapshot do Sistema de Design** — fontes (com justificativa), variáveis/tokens de cor, ritmo de espaçamento, filosofia de movimento.
3. **Implementação** — código completo e funcional, com comentários (em pt-BR) apenas onde a intenção não é óbvia.

Antes de finalizar, confira o Checklist do Operador:

* [ ] Direção estética clara declarada, com a âncora de diferenciação visível na UI final
* [ ] Sem fontes/cores/layouts genéricos
* [ ] Código compatível com a ambição de design
* [ ] Regras do Max stack respeitadas (Max*, sem nativos, sem vueuse/lodash)
* [ ] Acessível e performático

### 6. Faça Perguntas Esclarecedoras (se necessário)

1. Para quem é isto, emocionalmente?
2. Isto deve parecer confiável, empolgante, calmo ou provocativo?
3. Memorabilidade ou clareza é mais importante?
4. Isto escalará para outras páginas/componentes?
5. O que os usuários devem *sentir* nos primeiros 3 segundos?

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* Sem layouts padrão.
* Sem design-por-componentes.
* Sem paletas ou fontes "seguras".
* Opiniões fortes, bem executadas.

**Antipadrões (falha imediata):**

* Fontes Inter/Roboto/de sistema
* Gradientes SaaS roxo-sobre-branco
* Layouts padrão de bibliotecas de UI genéricas (presets prontos sem ponto de vista)
* Seções simétricas e previsíveis
* Clichês de design de IA superutilizados
* Decoração sem intenção

Se o design pudesse ser confundido com um template → recomece.
