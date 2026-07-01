# PROPOSTA DE SKILL: laravel-cache-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, configuring, or debugging caching mechanisms in Laravel. Triggers on Cache facade usage, Cache::remember, Cache::forget, Cache::put, cache configuration, TTL definitions, and cache-aside patterns.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp faz uso extensivo de cacheamento de dados de APIs externas (CEP, CNPJ, Correios, WhatsApp Cloud API), além de informações do banco de dados e templates de suporte para otimizar o desempenho. Padrões claros de TTL, nomenclatura de chaves e invalidação evitam dados desatualizados e problemas de inconsistência de estado.
* **Recursos:** Convenções de nomenclatura de chaves de cache, estratégias de expiração (TTL), uso correto de Cache::remember e Cache::forget, invalidação de caches de models via Observers, boas práticas para evitar race conditions sob concorrência e compatibilidade com o stateless do Octane.
* **Objetivo:** Fornecer diretrizes sólidas e padrões estruturados para o uso eficiente e seguro do cache no Laravel.
* **Casos de uso:** Cache de dados estáticos ou semi-estáticos de APIs externas (Correios, WhatsApp, CEP/CNPJ), cache de consultas Eloquent pesadas em models (Inverter, Module, SupportContact), invalidação dinâmica de cache em eventos de alteração de dados.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as convenções de Eloquent Observers para padronizar onde as ações de invalidação de cache (ex: `Cache::forget`) serão disparadas automaticamente após operações de salvar/deletar nos models.
  - `laravel-services-best-practices` — Utilizará o padrão de serviços para encapsular a lógica de cache-aside ao integrar APIs externas.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-code-generators-best-practices` — Será beneficiada ao adicionar boas práticas de encapsulamento de caches de relacionamento ou atributos dinâmicos nos Eloquent Models.
  - `laravel-services-best-practices` — Será beneficiada com métodos padronizados de cacheamento de requisições de API no nível da camada de serviço.
* **Benefícios:** Melhoria significativa na performance de carregamento de páginas, redução de requisições redundantes a APIs externas, consistência de dados armazenados e facilidade de manutenção de chaves de cache.
