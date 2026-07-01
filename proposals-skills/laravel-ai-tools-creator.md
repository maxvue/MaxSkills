# PROPOSTA DE SKILL: laravel-ai-tools-creator

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, reviewing, debugging, or documenting custom AI tools (Function Calling) implemented with the Laravel aiSDK (`Laravel\Ai\Contracts\Tool`) in the Engeapp codebase. Triggers on Tool definition, custom schema design, handle method logic, and AI action registration.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp faz uso de múltiplos Agentes de IA que dependem de chamadas de função (Function Calling) estruturadas para realizar tarefas no sistema. É necessário definir um padrão rígido de código para a definição de propriedades, assinaturas de métodos, formatação de descrição para os LLMs, esquemas JSON de parâmetros (`JsonSchema`) e logs estruturados em caso de falhas de execução.
* **Recursos:** Diretrizes para definição da assinatura do método `name()`, regras de redação de descrições eficazes para LLM em `description()`, mapeamento tipado de parâmetros de entrada no método `schema()`, injeção do objeto `Laravel\Ai\Tools\Request` e tratamento resiliente de erros na lógica do método `handle()`.
* **Objetivo:** Fornecer diretrizes padronizadas e rigorosas de código para a criação e manutenção de ferramentas de IA (AI Tools) integradas aos Agentes de IA do Engeapp baseadas no Laravel aiSDK.
* **Casos de uso:** Criação de ferramentas de consulta a dados de clientes e projetos, gravação e atualização de dados de boletos, acionamento de fluxos corporativos automatizados guiados pelo modelo LLM.
* **Workflows:** []
* **Skills próprias utilizadas:**
  - `laravel-ai-agent-creator` — Utilizará os padrões de integração e mapeamento de dependências de IA para assegurar que as ferramentas registradas sejam consumidas perfeitamente pelos agentes.
  - `laravel-exception-handling-logging` — Utilizará as boas práticas de log estruturado e captura centralizada de exceções para depurar erros na execução interna das ferramentas.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Benefícios:** Melhor consistência sintática e semântica de esquemas, maior precisão nas chamadas de função pelo Gemini, redução de falhas de execução por dados nulos ou inválidos e rastreabilidade robusta de ações executadas por agentes de IA.
