# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, modifying, or testing custom Eloquent casts in Laravel. Triggers on custom cast creation, CastsAttributes implementation, and model cast configurations.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp manipula metadados complexos, configurações personalizadas e dados especializados (como coordenadas geográficas e payloads de IA) que exigem conversão robusta e tipagem forte entre o banco de dados e a aplicação.
* **Recursos:** Padrões para implementação da interface `CastsAttributes`, tratamento de valores nulos, conversão bidirecional (get/set), suporte a classes que implementam `Castable` e integração fluida com DTOs (Spatie Data).
* **Objetivo:** Fornecer diretrizes sólidas e padrões estruturados para a criação, registro e teste de Custom Casts Eloquent no ecossistema Engeapp/Laravel.
* **Casos de uso:** Conversão de JSONs complexos para DTOs tipados, formatação e tratamento de coordenadas geográficas (UTM/DMS), e mascaramento/criptografia customizada de campos sensíveis de banco de dados.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as convenções de Models Eloquent para guiar a correta declaração e uso dos casts na propriedade `$casts`.
  - `laravel-code-generators-best-practices` — Utilizará as definições de DTOs para apoiar na conversão de colunas JSON em objetos fortemente tipados baseados no Spatie Data.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-code-generators-best-practices` — Facilitará a limpeza dos models ao extrair lógica de mutação/acesso para classes de cast dedicadas.
* **Benefícios:** Melhor legibilidade e tipagem do código de backend, isolamento da lógica de conversão de dados, e eliminação de mutators/accessors repetitivos nos models.
