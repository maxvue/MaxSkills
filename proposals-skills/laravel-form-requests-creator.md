# PROPOSTA DE SKILL: laravel-code-generators-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, updating, or reviewing Laravel Form Request classes, configuring input validation rules, customizing validation messages, or handling request authorization. Triggers on form request creation, validation rule definitions, and input sanitization.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp possui formulários complexos no frontend Vue. A validação centralizada e robusta no backend através de Form Requests é essencial para garantir a segurança, sanitização dos dados, prevenção de erros do banco de dados e manutenção de controllers limpos e focados.
* **Recursos:**
  - Padrão moderno de estrutura de Form Request (PHP 8.5+ e Laravel 13).
  - Regras de validação comuns e avançadas (como `Rule::unique`, `Rule::exists`, `Rule::when`).
  - Lógica de autorização no método `authorize()`.
  - Tratamento de parâmetros de rota dinâmicos para regras de unicidade/ignorância (ex: `$this->route('user')`).
  - Preparação e sanitização de dados pré-validação (`prepareForValidation`) e pós-validação (`passedValidation`).
  - Mensagens de erro personalizadas e localizadas em pt-BR.
* **Objetivo:** Estabelecer diretrizes consistentes e padrões rigorosos para a criação e manutenção de Form Requests no ecossistema Laravel do Engeapp.
* **Casos de uso:** Validação de payloads de criação e atualização de entidades (ex: perfis de usuário, upload de arquivos, configurações de tenant).
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as definições de models e colunas do banco para derivar e alinhar regras de validação adequadas (limites de caracteres, nulos, unicidade).
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-code-generators-best-practices` — Proverá requisições validadas prontas para consumo direto nos controllers de API.
  - `laravel-code-generators-best-practices` — Garantirá controllers Inertia mais concisos delegando a validação para o Form Request.
* **Benefícios:** Aumento da segurança, redução de validações duplicadas nos controllers, simplificação do tratamento de erros no frontend, maior legibilidade e consistência na validação de dados da aplicação.
