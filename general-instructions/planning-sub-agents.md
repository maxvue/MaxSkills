## ANÁLISE DE SUBAGENTES: Simule e coordene uma análise completa e colaborativa utilizando **7 subagentes especializados**.

> **NOTA SOBRE CAMINHOS:** As pastas em `projects/` são referências (symlinks) aos projetos reais. Se a leitura de um caminho falhar, solicite ao usuário o caminho absoluto correto do projeto.

* **Subagente 1 — Front-end SocialMediaApp:**
    - **Pasta:** `projects/SocialMediaApp/resources`
    - **Critérios de análise:** Padrões de componentes Vue existentes, convenções de nomenclatura de arquivos, estrutura de pastas de views/components, uso de composables e dependências front-end.

* **Subagente 2 — Biblioteca MaxComponentsUi (Componentes Vue):**
    - **Pasta:** `projects/MaxComponentsUi`
    - **Critérios de análise:** API pública dos componentes, padrões de props/emits/slots, convenções de estilização, componentes reutilizáveis disponíveis.

* **Subagente 3 — Biblioteca MaxUse (Helpers, Composables e funções):**
    - **Pasta:** `projects/MaxUse`
    - **Critérios de análise:** Composables disponíveis, funções utilitárias, padrões de reatividade, integração com @vueuse/core.

* **Subagente 4 — Banco de Dados e Lucid ORM do AdonisJS:**
    - **Pasta:** `projects/SocialMediaApp/app/models`
    - **Critérios de análise:** Relacionamentos entre models, scopes, hooks, convenções de nomenclatura de tabelas/colunas, decorators e decorators de associação.

* **Subagente 5 — Controllers e Rotas do AdonisJS:**
    - **Pastas:**
        - `projects/SocialMediaApp/app/controllers`
        - `projects/SocialMediaApp/start`
    - **Critérios de análise:** Padrões de responsabilidade dos controllers, middleware utilizado, agrupamento de rotas, validações de requisição (VineJS).

* **Subagente 6 — Agentes de IA e Comandos Ace do AdonisJS:**
    - **Pastas:**
        - `projects/SocialMediaApp/app/ai`
        - `projects/SocialMediaApp/commands`
        - `projects/SocialMediaApp/app/services`
    - **Critérios de análise:** Estrutura dos agentes de IA (atributos, tools, providers), padrões de comandos Ace (assinatura, flags, tratamento de erros), integração com Jobs e serviços.

* **Subagente 7 — Arquitetura da Skill para o Antigravity:**
    - **Objetivo:** Identificar se a tarefa demanda automação determinística (scripts), isolamento de textos grandes (resources) ou se é altamente padronizada necessitando demonstração de entrada e saída (examples), determinando o Nível da Skill (1 a 4).
    - **Critérios de análise:** Complexidade da tarefa, volume de texto estático envolvido, necessidade de validação externa, existência de padrões input/output repetíveis.

---

### REGRAS DE EXECUÇÃO
* **SAÍDA EXIGIDA:** Após a análise dos subagentes, você DEVE sintetizar e apresentar um relatório consolidado com os principais achados, padrões e dependências identificadas antes de iniciar a criação da skill.
* **SOMENTE LEITURA:** Os subagentes NÃO podem alterar o conteúdo das pastas observadas.
* **BLOQUEIO:** Os subagentes estão proibidos de modificar os arquivos da pasta `projects/` e suas respectivas subpastas.
