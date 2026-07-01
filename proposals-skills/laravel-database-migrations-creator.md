# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, modifying, reviewing, or running database migrations in Laravel within the database/migrations directory. Triggers on creating migration files, defining table schemas, foreign key constraints, indexes, unique constraints, setting soft deletes, or writing rollback routines.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp possui um banco de dados complexo e de grande escala, exigindo que as novas migrations sigam convenções rígidas, evitem deadlocks, definam chaves estrangeiras com segurança e garantam rollbacks consistentes sem perda de integridade dos dados.
* **Recursos:** Padrões para nomes de tabelas, chaves primárias (BigIncrements, UUID ou ULID), definição de tipos de dados adequados, criação separada de chaves estrangeiras (para evitar problemas de dependência circular na criação das tabelas), indexes para otimização de busca, timestamps, softDeletes e rollback robusto.
* **Objetivo:** Fornecer um guia conciso e diretrizes rígidas para criação de migrations eficientes, seguras e padronizadas no Laravel.
* **Casos de uso:** Criação de novas tabelas de entidade, tabelas pivot para relacionamentos muitos-para-muitos, alteração de tabelas existentes (adição/remoção de colunas) e definição de chaves estrangeiras.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-pest-testing-best-practices` — Utilizada para garantir que as novas migrations sejam validadas por meio de testes automatizados com o Pest, utilizando as factories para testar a persistência no banco.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-code-generators-best-practices` — A padronização das migrations facilitará a definição correta dos relacionamentos, scopes e casts nos Eloquent Models.
* **Benefícios:** Integridade referencial do banco de dados assegurada, rollbacks sem falhas, redução do risco de deadlocks e inconsistências em ambientes de produção, e melhor performance de consultas via indexação padronizada.
