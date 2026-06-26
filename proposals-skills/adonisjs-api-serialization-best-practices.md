# PROPOSTA DE SKILL: adonisjs-api-serialization-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when designing, configuring, customizing, or debugging JSON serialization payloads, formatting Lucid ORM model serialization, mapping snake_case database columns to camelCase API responses, or preventing N+1 queries during response generation in AdonisJS v6. Triggers on custom namingStrategy, serialize() overrides, omit fields serializing, and formatting paginated responses.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O backend AdonisJS do SocialMediaApp se comunica com o frontend Vue 3. A ausência de um padrão rígido de serialização pode expor chaves confidenciais no payload JSON, causar inconsistências entre chaves snake_case no banco e camelCase no Vue, e acarretar degradação de desempenho devido a consultas N+1 acidentais causadas pela serialização de relacionamentos não pré-carregados.
* **Recursos:**
  - Diretrizes para customizar a serialização de models Lucid ORM usando a propriedade `serializeAs` nos decorators `@column`.
  - Sobrecarga (overrides) do método `serialize` e uso de serializadores customizados para transformar coleções e modelos em payloads limpos.
  - Configuração de um `namingStrategy` global ou local no Lucid para converter chaves em camelCase automaticamente na camada de API.
  - Padrões seguros para serializar relacionamentos condicionalmente apenas se estiverem previamente carregados (preloaded), evitando N+1 queries.
  - Formatação de atributos específicos de data/hora (Luxon DateTime) em formato ISO padronizado ou pt-BR.
  - Padronização de metadados e chaves de payloads de paginação provenientes do Lucid Paginate.
* **Objetivo:** Fornecer práticas consolidadas para a serialização de dados e formatação de respostas de API no AdonisJS v6, garantindo segurança, padronização de chaves e alta performance.
* **Casos de uso:**
  - Serialização de dados de clientes e agências protegendo tokens de acesso do Instagram e credenciais do banco.
  - Transformação de listas paginadas de postagens do calendário editorial mantendo chaves camelCase para compatibilidade direta com a tipagem do Vue 3.
  - Prevenção de queries N+1 durante o retorno de relacionamentos aninhados de eventos com comentários e mídias.
* **Workflows:** [/bug-fix-back-end]
* **Skills próprias utilizadas:**
  - `adonisjs-lucid-orm-best-practices` — Utilizará os conceitos de models, query builders, relacionamentos e hooks para interceptar e estruturar os dados.
  - `adonisjs-multitenancy-data-isolation-best-practices` — Utilizará as regras de isolamento de dados por agência para garantir que nenhum dado de outro tenant seja exposto no payload serializado.
* **Skills auxiliares:** adonisjs-specialist, adonisjs-best-practices
* **Skills beneficiadas:** adonisjs-saas-subscription-quota-enforcement-best-practices, adonisjs-editorial-calendar-event-workflow-best-practices
* **Benefícios:** Prevenção do vazamento de credenciais e campos internos do banco, compatibilidade direta de nomenclatura com o frontend TypeScript/Vue (camelCase), eliminação de queries N+1 na serialização e melhor performance geral da API.
