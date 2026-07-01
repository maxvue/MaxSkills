# PROPOSTA DE SKILL: laravel-base-api-integration-patterns

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 3
* **Wake Word (YAML Description):** Use when creating, debugging, or extending external HTTP API integrations that inherit from BaseApi. Triggers on setting up new API connectors, writing Attributes.json or EndPoints.json, configuring OAuth2 caching, or implementing custom call methods for APIs like Whapi or Efi.
* **Estrutura de Diretórios:**
  - `SKILL.md` (Arquivo principal de instruções)
  - `examples/Attributes.json` (Exemplo prático de atributos definidos)
  - `examples/EndPoints.json` (Exemplo prático de mapeamento de endpoints)
  - `examples/Connector.php` (Exemplo prático de classe filha herdando de BaseApi)
* **Necessidade:** O Engeapp utiliza uma arquitetura dinâmica e própria baseada na classe `BaseApi` para comunicação com APIs de terceiros (como pagamentos Efi e mensagens WhapiCloud). Essa arquitetura depende de mapeamentos estritos em arquivos JSON e do método mágico `__call()`. Os desenvolvedores precisam de diretrizes claras sobre como criar os arquivos `Attributes.json`, `EndPoints.json` e a classe PHP para garantir o correto funcionamento de autenticação, cache e validação de atributos.
* **Recursos:** Mapeamento de endpoints aninhados em JSON, configuração de tipos e validações no `Attributes.json`, herança da classe `BaseApi`, cache de chamadas e token, e implementação de fluxo de autenticação (OAuth2/Tokens).
* **Objetivo:** Padronizar a criação e manutenção de integrações HTTP robustas baseadas na classe nativa `BaseApi` no Engeapp.
* **Casos de uso:** Implementar um novo endpoint na integração com a Efí, criar uma nova integração com uma API de envio de SMS/e-mails, e debugar problemas de envio de payloads incorretos ou expiração de cache/tokens.
* **Workflows:** [bug-fix-back-end]
* **Skills próprias utilizadas:** Nenhuma no momento.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** laravel-jobs-queues-horizon-best-practices (pois os Jobs que enviam dados para APIs usam essas integrações).
* **Benefícios:** Aceleração no desenvolvimento de novas integrações de API, prevenção de erros de tempo de execução causados por mapeamentos incorretos em arquivos JSON e uso eficiente de cache/OAuth2.
