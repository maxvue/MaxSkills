# PROPOSTA DE SKILL: laravel-api-resources-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, modifying, configuring, or debugging Laravel API Resources or Resource Collections. Triggers on custom resource fields, conditional relationships (whenLoaded, whenCounted), pagination formatting, camelCase/snakeCase transformations, API versioning payloads, or files within app/Http/Resources.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp se comunica extensivamente com o front-end via APIs HTTP. A padronização da serialização de dados (incluindo camelCase/snakeCase, tratamento de relacionamentos condicionais e paginação) é vital para evitar inconsistências nos dados consumidos pelo Vue e reduzir o acoplamento de dados brutos do banco de dados na resposta, evitando o vazamento de chaves privadas e dados não processados.
* **Recursos:**
  - Padrões para herança de `JsonResource` e `ResourceCollection`.
  - Tratamento de relacionamentos carregados condicionalmente (`whenLoaded`, `whenCounted`, `whenPivotLoaded`).
  - Formatação e transformação de atributos (ex: data e hora via Carbon, valores monetários).
  - Padronização de chaves de resposta em camelCase (para compatibilidade com front-end TypeScript/Vue) versus snake_case no banco de dados.
  - Paginação consistente e estruturação de metadados de paginação.
  - Encapsulamento de dados adicionais e versionamento básico na camada de resposta.
* **Objetivo:** Definir diretrizes robustas para a criação, transformação e depuração de respostas JSON utilizando Laravel API Resources, garantindo consistência na API consumida pelo front-end.
* **Casos de uso:**
  - Serialização de listagem e detalhes de entidades (como Mídia, Clientes, Projetos, etc.) com seus relacionamentos.
  - Formatação de respostas paginadas enviadas ao front-end Vue.
  - Sanitização de payloads JSON protegendo campos sensíveis do banco de dados.
* **Workflows:** [/bug-fix-back-end]
* **Skills próprias utilizadas:**
  - `laravel-form-requests-validation-best-practices` — Utilizada para complementar o ciclo de requisição e resposta do Laravel, validando dados de entrada enquanto os API Resources estruturam a saída de forma padronizada.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Padronização das payloads de resposta de API, prevenção de erros de N+1 queries (garantindo o uso de `whenLoaded`), ocultação de campos sensíveis de models, facilidade na tipagem do front-end e melhor manutenibilidade do código.
