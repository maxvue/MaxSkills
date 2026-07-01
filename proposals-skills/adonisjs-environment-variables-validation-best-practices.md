# PROPOSTA DE SKILL: adonisjs-environment-variables-validation-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when configuring, reviewing, or validating environment variables, updating start/env.ts, defining Env.schema schemas, troubleshooting missing or invalid env keys, or configuring environment variable injection across different deployment environments in AdonisJS v6. Triggers on start/env.ts modification, Env.schema validation, and env configuration.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** Garantir que o ecossistema Engeapp (baseado em AdonisJS v6) possua uma validação robusta e estrita de variáveis de ambiente. Isso evita falhas de execução em produção por falta de variáveis obrigatórias e garante tipagem segura (type safety) em toda a aplicação.
* **Recursos:** Validação de tipos (string, number, boolean, enum), tratamento de segredos (Env.schema.secret), tratamento de variáveis opcionais, e boas práticas para estruturar o arquivo `start/env.ts`.
* **Objetivo:** Estabelecer padrões e boas práticas para declaração, validação e injeção de variáveis de ambiente no AdonisJS v6.
* **Casos de uso:** Configurar chaves de APIs externas (ex: Gemini, Meta), conexões de banco de dados e Redis, e gerenciar segredos de forma segura no desenvolvimento e produção.
* **Workflows:**
  - /bug-fix-back-end
* **Skills próprias utilizadas:**
  - `adonisjs-best-practices` — Para alinhar a inicialização e estrutura do projeto com as regras gerais de backend.
* **Skills auxiliares:** Nenhuma no momento.
* **Skills beneficiadas:**
  - `adonisjs-gemini-file-api-media-integration-best-practices`
  - `adonisjs-meta-graph-api-integration-best-practices`
* **Benefícios:** Prevenção de erros em runtime devido a variáveis ausentes ou inválidas, melhor documentação das dependências de ambiente (.env.example), e tipagem estática autocompletada para `process.env` através do Env service.
