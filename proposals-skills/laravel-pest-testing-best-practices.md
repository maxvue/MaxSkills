# PROPOSTA DE SKILL: laravel-pest-testing-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when writing, debugging, or reviewing Unit or Feature tests using Pest PHP. Triggers on test creation, assertions, mocking dependencies, factory usage, or database testing setup.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp possui uma suíte de testes baseada em Pest PHP. Há a necessidade de padronizar a escrita de testes unitários e de feature, definindo melhores práticas para o uso de factories (estados personalizados), isolamento de testes com mocks, testes de endpoints HTTP e controle transacional de banco de dados (`DatabaseTransactions`).
* **Recursos:** Estruturação de testes de Feature e Unitários, asserções idiomáticas do Pest, uso correto de Datasets, mocking de facades/services e regras para isolamento de dados de teste.
* **Objetivo:** Fornecer diretrizes sólidas e padronizadas para criação e manutenção de testes no ecossistema Engeapp com Pest PHP.
* **Casos de uso:** Escrita de testes de Feature para novas APIs de controladores, simulação de fluxo de processamento de Jobs/Events em background, teste de classes utilitárias/Helpers e validação de lógica de negócios complexa.
* **Workflows:** [bug-fix-back-end]
* **Skills auxiliares:**
  - `laravel-specialist`
* **Skills beneficiadas:**
  - `laravel-jobs-queues-horizon-best-practices`
* **Benefícios:** Aumento da cobertura e confiabilidade de código, redução da carga cognitiva na criação de novos testes, execução mais rápida da suíte e prevenção de regressões em produção.
