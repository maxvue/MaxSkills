---
name: frontend-design-best-practices
description: Use ao construir nova UI ou remodelar telas do engeapp (Vue 3 + UnoCSS attributify presetMaxUno + componentes @maxvue/max-components-ui) buscando design intencional e distinto em vez de padrões genéricos. Cobre direção estética, tipografia, cor, composição espacial, movimento e a tradução da intenção de design em código acessível de produção.
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

* Evite fontes de sistema e padrões de IA (Inter, Roboto, Arial, etc.)
* Escolha 1 fonte de display expressiva e 1 fonte de corpo contida
* Use a tipografia estruturalmente (escala, ritmo, contraste)

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

**Requisitos de Código**

* Limpo, legível e modular
* Sem estilos mortos nem animações não utilizadas
* HTML semântico e acessível por padrão (contraste, foco, teclado)
* **Convenção de novo código: prefira `<div>` a `<section>`** para agrupar conteúdo. Observação: o codebase atual ainda tem `<section>` em telas antigas (ex.: `resources/Vue/Site/Pages/SiteHome.vue`); não é preciso migrá-las, mas siga a convenção `<div>` ao escrever/reformar código.
* **Atributos sempre inline**: mantenha todos os atributos de uma tag (componente, `div` ou qualquer elemento) em uma única linha, por mais atributos que tenha — nunca quebre atributos em múltiplas linhas.

**Orientação de Framework — Max stack (engeapp: Laravel 13 no backend + frontend Vue 3 com tooling Node/Vite)**

* Construa UI em **Vue 3** com **`<script setup>`**, estilos via **UnoCSS attributify** (`presetMaxUno`) e componentes **`@maxvue/max-components-ui`**. Sem Tailwind, sem ShadCN, sem React.
* **Nunca use inputs/botões nativos** (`<input>`/`<button>`/`<select>`/`<textarea>`) em código de app — use sempre os componentes MaxComponentsUi (`MaxInputText`, `MaxButton`, `MaxIconButton`, etc.).
* **Nunca use headings nativos** (`<h1>`…`<h4>`) — use `MaxTitle1`/`MaxTitle2`.
* **Formulários usam `MaxGrid`** (nunca `MaxGridCols`), com campos dimensionados por atributos (`s-30`, `w-max-300`, `h-min-50`, `w-min-10rem`).
* **Não importe `@vueuse/core` nem `lodash`** — use os composables/utilitários do MaxUse (`@maxvue/max-use`).
* **Animação**: CSS/transições nativas primeiro; bibliotecas de motion apenas quando justificado.

**Correspondência de Complexidade**

* Design maximalista → código complexo (animações, camadas).
* Design minimalista → espaçamento e tipografia extremamente precisos.
* Incompatibilidade entre ambição e código = falha.

### 5. Entregue a Estrutura de Saída Exigida

Ao gerar trabalho de frontend:

**Resumo da Direção de Design**

* Nome da estética
* Inspiração-chave (conceitual, não plágio visual)

**Snapshot do Sistema de Design**

* Fontes (com justificativa)
* Variáveis/tokens de cor
* Ritmo de espaçamento
* Filosofia de movimento

**Implementação**

* Código completo e funcional
* Comentários apenas onde a intenção não é óbvia (em pt-BR)

**Destaque de Diferenciação** — declare explicitamente:

> "Isto evita UI genérica fazendo X em vez de Y."

### 6. Execute o Checklist do Operador

Antes de finalizar a saída:

* [ ] Direção estética clara declarada
* [ ] Uma âncora de design memorável e visível
* [ ] Sem fontes/cores/layouts genéricos
* [ ] Código compatível com a ambição de design
* [ ] Regras do Max stack respeitadas (Max*, sem nativos, sem vueuse/lodash)
* [ ] Acessível e performático

### 7. Faça Perguntas Esclarecedoras (se necessário)

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
