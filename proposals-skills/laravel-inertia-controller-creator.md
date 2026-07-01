# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
* **Wake Word (YAML Description):** Use when creating, reviewing, or modifying Laravel Inertia controllers inside App/Http/Controllers/InertiaPages. Triggers on Inertia::render or Inertia::renderData invocations, handling page props, subpages, vuex state binding, active menu state, and redirects.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp utiliza um padrão customizado de renderização com Inertia.js (através do wrapper Inertia e InertiaVue) para passar dados estruturados, subpáginas (abas), namespaces do Vuex e status do menu ativo. A falta de padronização na escrita desses controllers pode quebrar a reatividade no front-end ou o comportamento do painel de navegação.
* **Recursos:**
  - Estruturação de retornos utilizando os métodos `Inertia::render()` e `Inertia::renderData()`.
  - Passagem correta de parâmetros para carregar subpáginas/abas (`$subpage`, `$section_file`).
  - Sincronização do estado global definindo o namespace correto para o Vuex/Pinia (`$vuex`).
  - Indicação do item de menu ativo (`$menuActive`) para controle visual no layout do front-end.
  - Padrões de redirecionamento (`Inertia::location`) e tratamento de dados ausentes com fallback.
* **Objetivo:** Fornecer diretrizes e convenções estritas para a criação, refatoração e manutenção de controladores baseados no Inertia.js no ecossistema Engeapp.
* **Casos de uso:**
  - Criação de novos controladores de páginas de painel (Dashboard), Kanban (Board) ou formulários complexos no Engeapp.
  - Refatoração de rotas e controllers para carregar dados de forma lazy no front-end.
  - Proteção de fluxos com tratamento de erros de carregamento e redirecionamento correto.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as regras de carregamento de relacionamentos Eloquent (eager loading) para buscar dados consistentes que serão injetados no renderizador do Inertia.
  - `laravel-code-generators-best-practices` — Integrará o uso de Data Transfer Objects (Spatie Data) para tipagem e transporte seguro de dados do controller para as propriedades do Inertia no Vue.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices, php-best-practices
* **Skills beneficiadas:** vue-code-generators-best-practices, vue-code-generators-best-practices
* **Benefícios:** Uniformidade nas respostas de página do Inertia, prevenção de bugs na interface ao alternar abas, garantia de sincronização do estado global do Vuex/Pinia e menu lateral integrado, facilitando a navegação e a manutenibilidade do código do Engeapp.
