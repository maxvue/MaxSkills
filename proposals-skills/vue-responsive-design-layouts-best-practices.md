# PROPOSTA DE SKILL: vue-responsive-design-layouts-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when designing, building, styling, or debugging responsive layouts, grids, forms, and media simulators in Vue 3 using UnoCSS (Attributify mode) and the MaxComponentsUi library (MaxGrid, MaxGridCols). Triggers on layout files, component resizing, media queries, flexbox/grid adjustments, and mobile-first implementations in SocialMediaApp.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O frontend do SocialMediaApp e demais aplicações do ecossistema precisam de layouts responsivos consistentes, utilizando a biblioteca local MaxComponentsUi e UnoCSS no modo Attributify, a fim de garantir a correta renderização em dispositivos móveis e desktop, sem duplicar estilos ou causar bugs visuais.
* **Recursos:** 
  - Uso responsivo de shortcuts de tamanho (`s50`, `s100`) em componentes filhos dentro do `MaxGrid`.
  - Configuração de colunas no `MaxGridCols` com CSS Grid de 24 colunas de forma dinâmica e responsiva (`style="grid-column: span N"`).
  - Utilização de breakpoints responsivos do UnoCSS no modo Attributify (ex: `sm:flex-row`, `md:gap-4`).
  - Adaptação responsiva para os simuladores de mídias (Instagram, TikTok, YouTube Shorts) e formulários complexos.
* **Objetivo:** Fornecer diretrizes e padrões para implementar layouts fluidos, responsivos e adaptáveis no Vue 3 no ecossistema Engeapp/SocialMediaApp.
* **Casos de uso:** Formulários de cadastro de agência/cliente com grids responsivos, exibição de simuladores de redes sociais que se ajustam à tela do dispositivo móvel/desktop, e barras de navegação ou layouts principais flexíveis.
* **Workflows:** 
  - `/bug-fix-front-end`
* **Skills próprias utilizadas:**
  - `vue-max-components-ui-development-best-practices` — Utilizará as convenções de uso dos componentes locais MaxGrid e MaxGridCols.
  - `vue-unocss-styling-best-practices` — Utilizará as regras de estilização utilitária do UnoCSS com modo Attributify.
* **Skills auxiliares:** Nenhuma no momento.
* **Skills beneficiadas:**
  - `vue-3-dynamic-forms-schema-renderer-with-maxcomponentsui-best-practices` — Facilitará a renderização de formulários gerados dinamicamente de forma responsiva.
  - `vue-complex-modal-forms-autosave-best-practices` — Ajudará a organizar campos dentro de modais de forma responsiva.
* **Benefícios:** Layouts 100% responsivos e consistentes, facilidade na manutenção dos formulários do sistema, melhor experiência do usuário final nos simuladores de redes sociais em mobile.
