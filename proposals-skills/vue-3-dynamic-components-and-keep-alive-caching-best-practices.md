# PROPOSTA DE SKILL: vue-3-dynamic-components-and-keep-alive-caching-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when designing, implementing, or optimizing dynamic component loading using Vue 3 `<component :is="...">`, rendering asynchronous components with `defineAsyncComponent`, or managing component caching and lifecycle hooks with `<KeepAlive>` (e.g., handling onActivated/onDeactivated, cache invalidation, and custom cache keys). Triggers when creating dynamic tab interfaces, multi-step wizards, or dashboard layouts with state retention.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp (especialmente o SocialMediaApp) possui painéis de planejamento, calendários e wizards complexos. A alternância constante de abas exige uma estratégia de renderização dinâmica eficiente para evitar a destruição do estado local de formulários e reduzir o overhead de novas montagens de componentes pesados.
* **Recursos:** Padrões para uso de `<component :is="...">` com tipagem forte, uso de `defineAsyncComponent` para code-splitting, configuração fina do `<KeepAlive>` (include, exclude, max) e ciclo de vida (`onActivated` / `onDeactivated`).
* **Objetivo:** Fornecer diretrizes e boas práticas para implementação de componentes dinâmicos e cache de telas no Vue 3 com foco em performance e preservação de estado.
* **Casos de uso:** Tabs do calendário editorial, etapas do wizard de criação de campanha de posts, carregamento dinâmico de simuladores de prévia de redes sociais.
* **Workflows:** []
* **Skills próprias utilizadas:**
  - `vue-typescript-best-practices` — Utilizará as regras de tipagem para garantir a passagem correta de props genéricas em componentes dinâmicos.
  - `vue-max-components-ui-development-best-practices` — Integração de transições nativas e slots dos componentes Max com o KeepAlive.
* **Skills auxiliares:** Nenhuma no momento.
* **Skills beneficiadas:**
  - `vue-max-components-ui-wizard-stepper-forms-best-practices` — Otimização de navegação entre passos mantendo o estado de cada etapa.
* **Benefícios:** Melhoria de performance de re-renderização, preservação da experiência do usuário ao navegar entre abas, e otimização do uso de memória com limites de cache.
