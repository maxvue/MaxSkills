# PROPOSTA DE SKILL: laravel-redis-integration-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
* **Wake Word (YAML Description):** Use when configuring, optimizing, or debugging Redis database connections, queues, sessions, cache stores, pub/sub channels, or distributed locks in Laravel. Triggers on Redis facade usage, phpredis/predis config, cache tags, connection exceptions, and Horizon queue backend configurations.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp utiliza o Redis como infraestrutura central de cache, filas (Horizon), gerenciamento de sessões e pub/sub. Há necessidade de diretrizes consistentes para gerenciar conexões persistentes, estruturar chaves do Redis com prefixos semânticos, implementar locks distribuídos resilientes para evitar condições de corrida (race conditions) em transações financeiras, configurar cache tags de forma segura e implementar mecanismos de fallback robustos caso o servidor Redis fique temporariamente indisponível.
* **Recursos:**
  - Padrões de configuração no `config/database.php` usando Phpredis (conexões persistentes).
  - Convenções de nomenclatura e estruturação de chaves do Redis (`app_name:domain:resource:id`).
  - Uso correto de locks distribuídos com a Facade Cache (`Cache::lock()`) ou Redis nativo para processos críticos.
  - Implementação de pipelines para operações em lote, reduzindo o round-trip time (RTT).
  - Tratamento de exceções e fallback de conexão (`RedisException`, `ConnectionException`).
  - Padrões para monitoramento de concorrência de filas do Horizon baseadas em Redis.
  - Boas práticas para o uso de Cache Tags e sua invalidação controlada.
* **Objetivo:** Fornecer diretrizes sólidas e padrões consistentes para a configuração, otimização, segurança e desenvolvimento resiliente de rotinas baseadas em Redis no backend Laravel do Engeapp.
* **Casos de uso:**
  - Locks distribuídos em APIs de pagamento (`laravel-asaas-payments-integration`, `laravel-efi-payments-integration`) para evitar duplicidade de transações.
  - Armazenamento em cache de respostas de APIs externas de alta latência (NASA POWER, CRESESB) de forma taggeada.
  - Otimização do processamento em massa de dados climatológicos e geográficos através de pipelines do Redis.
  - Configuração do Redis como backend de alto desempenho para o processamento de filas do Horizon.
* **Workflows:**
  - `bug-fix-back-end`
  - `deploy`
* **Skills próprias utilizadas:**
  - `laravel-services-best-practices` — Conexões e interações com o Redis devem ser encapsuladas em classes de serviço para separação de responsabilidades.
  - `laravel-exception-handling-logging` — Para capturar e logar falhas de conexão de Redis de forma resiliente, permitindo alertas imediatos.
* **Skills auxiliares:** laravel-cache-best-practices, laravel-jobs-queues-horizon-best-practices
* **Skills beneficiadas:**
  - `laravel-asaas-payments-integration` — Permitirá transações financeiras seguras utilizando locks distribuídos no Redis.
  - `laravel-efi-payments-integration` — Controlará a concorrência na homologação de boletos bancários.
  - `laravel-solar-irradiance-cresesb-nasa-integration` — Fornecerá cache taggeado e otimizado para os dados climatológicos buscados.
* **Benefícios:**
  - Alta performance e latência minimizada ao consultar dados temporários ou processar jobs em background.
  - Prevenção ativa de condições de corrida (race conditions) em rotinas críticas de negócios e faturamento.
  - Resiliência robusta da aplicação contra quedas temporárias do serviço Redis com fallback gracioso.
  - Governança clara das chaves do Redis, simplificando diagnósticos e evitando colisões entre microsserviços.
