# PROPOSTA DE SKILL: laravel-exception-handling-logging

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when defining, refactoring, or debugging exception handlers, custom Exceptions, logging structures, and monolog configurations in Laravel. Triggers on custom exception creation, try-catch blocks for API integrations, logging errors or warnings, and error reporting configurations.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp realiza diversas integrações com serviços e APIs externas (como Gemini, Trello, WhatsApp e gateways de pagamento) que podem apresentar instabilidades temporárias. Sem um tratamento de exceções padronizado e um logging contextualizado, os erros de produção tornam-se difíceis de rastrear, resultando em falhas silenciosas ou na poluição do log de erros padrão do Laravel.
* **Recursos:**
  - Criação de exceções customizadas (Custom Exceptions) herdando o comportamento correto do Laravel.
  - Customização dos métodos `report()` e `render()` em exceções específicas.
  - Padrões de logging estruturado contendo contexto detalhado (ex: ID do usuário, payload relevante de forma segura).
  - Configuração de múltiplos canais de log de acordo com a gravidade do erro.
  - Boas práticas para blocos try-catch em requisições HTTP externas para evitar travamento da aplicação.
* **Objetivo:** Estabelecer diretrizes e padrões consistentes para o tratamento centralizado de erros e logging contextualizado no backend Laravel do Engeapp.
* **Casos de uso:**
  - Criação de uma `AiIntegrationException` para capturar falhas específicas de cotas ou timeouts das LLMs.
  - Registro estruturado de logs ao falhar o envio de notificações de WhatsApp.
  - Formatação e resposta HTTP adequada para exceções que chegam às APIs públicas do sistema.
* **Workflows:**
  - `bug-fix-back-end` — Auxiliará na identificação da raiz de falhas e análise de logs estruturados de erros.
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará os padrões de retorno HTTP para exceções renderizadas nos Controllers de API.
* **Skills auxiliares:** laravel-best-practices, laravel-specialist, php-best-practices
* **Skills beneficiadas:**
  - `laravel-base-api-integration-patterns` — Fornecerá um modelo robusto de tratamento de falhas nas requisições HTTP baseadas na classe BaseApi.
* **Benefícios:** Aumento significativo na rastreabilidade de bugs em produção, isolamento de logs críticos por canal de serviço e eliminação de falhas silenciosas em integrações complexas.
