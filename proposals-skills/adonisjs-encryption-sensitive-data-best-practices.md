# PROPOSTA DE SKILL: adonisjs-encryption-sensitive-data-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when encrypting, decrypting, or storing sensitive client credentials, access tokens (Meta Graph, Instagram, WhatsApp), and API keys in the database using AdonisJS v6 Encryption service. Triggers on model hooks, custom setters/getters for credential serialization, and environment key rotation.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** Armazenamento seguro de tokens de terceiros (Meta, Instagram, WhatsApp) e credenciais de clientes no banco de dados para evitar exposição de chaves privadas em caso de vazamento de dados ou dumps da base de dados.
* **Recursos:** Criptografia e descriptografia automática com Lucid ORM (decorators, getters, setters), validação de chaves, rotação segura e tratamento de falhas.
* **Objetivo:** Definir padrões e boas práticas para criptografia de informações sensíveis no banco de dados no ecossistema AdonisJS v6 usando o Encryption Service nativo.
* **Casos de uso:** Salvar chaves de API, credenciais do Meta e segredos de clientes de forma criptografada.
* **Workflows:**
  - /bug-fix-back-end
* **Skills próprias utilizadas:**
  - `adonisjs-lucid-orm-best-practices` — Para manipulação segura do ciclo de vida de dados nos models Lucid.
* **Skills auxiliares:** Nenhuma no momento.
* **Skills beneficiadas:**
  - `adonisjs-meta-graph-api-integration-best-practices`
  - `adonisjs-whatsapp-cloud-api-integration-best-practices`
* **Benefícios:** Aumento significativo de segurança da informação, conformidade com a LGPD, e implementação limpa sem poluir regras de negócios dos controllers.
