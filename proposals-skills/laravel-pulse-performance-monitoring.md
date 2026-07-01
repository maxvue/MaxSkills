# PROPOSTA DE SKILL: laravel-pulse-performance-monitoring

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when configuring, optimizing, or debugging application performance, slow queries, slow requests, or system resource bottlenecks using Laravel Pulse dashboard and custom recorders.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp processa um grande volume de dados e jobs em background. Sem um monitoramento centralizado de performance, gargalos de rede, queries ineficientes e consumo de memória podem degradar o sistema de forma silenciosa. O Laravel Pulse fornece a visibilidade necessária para atuar preventivamente nessas falhas.
* **Recursos:** Configuração de recorders nativos, criação de recorders customizados para métricas de negócio, políticas de segurança para o dashboard em produção, estratégias de limpeza de dados e integração com o Laravel Horizon.
* **Objetivo:** Fornecer diretrizes para monitorar a saúde do aplicativo Engeapp, identificar gargalos de CPU/memória, rastrear requisições e queries lentas e configurar o dashboard do Pulse com segurança.
* **Casos de uso:** Diagnóstico de lentidão em endpoints específicos, identificação de concorrência excessiva em tabelas do banco, monitoramento do consumo de memória de jobs de IA e análise de uso do cache Redis.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-jobs-queues-horizon-best-practices` — Utilizará as métricas de performance do Horizon integradas ao Pulse para monitorar jobs com falhas frequentes ou execução lenta.
  - `laravel-eloquent-relationships-loader` — Utilizará o mapeamento de queries N+1 sugerido pelo Pulse para otimizar o carregamento de relacionamentos no Eloquent.
  - `laravel-cache-best-practices` — Utilizará as métricas de hit/miss indicadas pelo Pulse para ajustar o TTL e chaves do cache do Redis.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-exception-handling-logging`
* **Benefícios:** Detecção precoce de gargalos de performance, redução no tempo de carregamento de páginas, estabilização do consumo de recursos do servidor e facilitação na triagem de bugs de infraestrutura.
