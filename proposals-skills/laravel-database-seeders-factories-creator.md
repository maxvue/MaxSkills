# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 3
  - Nível 3: Requer pasta `examples/` (inputs/outputs de few-shot)
* **Wake Word (YAML Description):** Use when creating, reviewing, or debugging Laravel database seeders and model factories, defining factory states, or generating mock data for tests. Triggers on factory definition, seeder setup, and mock data generation.
* **Estrutura de Diretórios:** SKILL.md, `examples/` (Nível 3).
* **Necessidade:** O ecossistema Engeapp requer testes automatizados robustos e um setup fácil do ambiente local de desenvolvimento. Para isso, são fundamentais factories e seeders padronizados que gerem dados realistas e previsíveis sem duplicar código.
* **Recursos:** Convenções de uso do Faker (com localização pt_BR onde aplicável), definição de estados específicos nas factories (ex: `active`, `pending`), tratamento de relacionamentos (hasMany, belongsTo) em cascata e estruturação de DatabaseSeeder.
* **Objetivo:** Fornecer diretrizes consistentes para a criação e manutenção de Factories e Seeders no Laravel, servindo como base sólida para testes automatizados e seeding local.
* **Casos de uso:** Criação de factories com estados para testes no Pest, criação de seeders de tabelas de domínio (ex: permissões, configurações padrão) e seeding de dados de teste realistas.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as definições de relacionamentos, casts e atributos do model para mapear os campos na factory correspondente.
  - `laravel-pest-testing-best-practices` — Integrará o uso dessas factories nos cenários de testes unitários e de feature escritos com Pest.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-pest-testing-best-practices` — Será beneficiada por dispor de factories consistentes e fáceis de instanciar nos testes.
* **Benefícios:** Melhoria na qualidade e cobertura dos testes automatizados, redução no tempo de setup de novos ambientes de desenvolvimento e prevenção de inconsistências nos dados de mock.
