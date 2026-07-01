# PROPOSTA DE SKILL: laravel-hashids-obfuscation-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, configuring, or debugging ID obfuscation in Laravel Eloquent models, API routes, or controllers using the vinkla/hashids package. Triggers on route model binding customization, ID masking in API resources, and database ID obfuscation/decoding.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp expõe chaves primárias numéricas sequenciais de banco de dados (IDs autoincrementais) em URLs e retornos de API. O uso de `vinkla/hashids` permite mascarar esses IDs de forma reversível sem alterar o tipo físico do banco de dados, protegendo contra raspagem de dados (scraping) e ataques do tipo IDOR.
* **Recursos:**
  - Configuração centralizada e segura do sal (salt) e comprimento dos hashids.
  - Criação de uma trait reutilizável `HasHashid` para codificar chaves primárias e configurar Route Model Binding customizado de forma transparente.
  - Convenções de nomeação para as rotas e validação de chaves hashid em Form Requests.
  - Padrões para exportar IDs codificados em recursos de API (Eloquent API Resources) e DTOs (laravel-data) mantendo a compatibilidade com a tipagem TypeScript.
  - Regras para tratamento de erros em caso de hashes inválidos ou decodificações falhas (ex: retornar 404 automaticamente).
* **Objetivo:** Estabelecer diretrizes e padrões de implementação consistentes para a ofuscação segura de IDs nas URLs e APIs do ecossistema Engeapp/Laravel utilizando a biblioteca `vinkla/hashids`.
* **Casos de uso:**
  - Exibição segura de rotas públicas (ex: `/clientes/{hashid}`, `/orcamentos/{hashid}`) ocultando o ID real do banco.
  - Retorno de rotas de API que expõem IDs de recursos de forma segura para o front-end Vue 3.
  - Decodificação transparente de parâmetros de rotas usando Model Binding nativo do Laravel.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as diretrizes de criação de Eloquent Models para integrar a trait `HasHashid` de maneira correta aos atributos e casts.
  - `laravel-code-generators-best-practices` — Utilizará os padrões de controle para padronizar a decodificação nos controllers quando o Model Binding implícito não for viável.
  - `laravel-code-generators-best-practices` — Garantirá que os DTOs utilizem strings de hashid em vez de inteiros sequenciais para suas propriedades de identificador exportadas.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Aumento da segurança do sistema impedindo a enumeração de recursos por terceiros, ocultação da escala do negócio (evitando que usuários estimem o volume de dados pelo valor sequencial do ID), e manutenção da alta performance do banco de dados ao continuar utilizando chaves primárias numéricas nativas.
