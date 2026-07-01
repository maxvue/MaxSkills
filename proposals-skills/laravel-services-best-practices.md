# PROPOSTA DE SKILL: laravel-services-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, refactoring, or reviewing Laravel Service classes, applying Single Responsibility Principle, dependency injection, and standardized error handling. Triggers on Service class creation, business logic encapsulation, and external API integrations.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp possui lógicas de negócios complexas e integrações com diversas APIs (Trello, WhatsApp, Correios). É fundamental padronizar a criação de Services para evitar "fat controllers", garantir o uso de injeção de dependências e padronizar o tratamento de erros e logs.
* **Recursos:** Padrões para injeção de dependências, tratamento de exceções customizadas, logging padronizado, uso de DTOs nas assinaturas dos métodos e single responsibility principle (SRP).
* **Objetivo:** Estabelecer diretrizes consistentes para a arquitetura, criação e manutenção de classes de Serviço (Services) no Laravel.
* **Casos de uso:** Criação de integrações com APIs externas, isolamento de regras de negócios que operam sobre múltiplos models, e refatoração de controllers pesados.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará DTOs nas assinaturas de métodos para passagem estruturada de dados.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Código mais testável (mocking de dependências facilitado), separação clara de responsabilidades, e maior reaproveitamento de código entre controllers, jobs e comandos artisan.
