# PROPOSTA DE SKILL: adonisjs-database-replicas-connection-pooling-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
  - Nível 2: Requer pasta `resources/` (textos pesados/templates)
  - Nível 3: Requer pasta `examples/` (inputs/outputs de few-shot)
  - Nível 4: Requer pasta `scripts/` (lógicas delegadas Bash/Python/Node)
* **Wake Word (YAML Description):** Use when designing, configuring, profiling, or debugging database connections, read/write replica routing, connection pool tuning, or connection timeouts in AdonisJS v6 using Lucid ORM. Triggers on database.ts connection config, replica setup, query routing to read/write nodes, pool size tuning, and database connection timeouts.
* **Estrutura de Diretórios:** Apenas `SKILL.md` (Nível 1).
* **Necessidade:** O ecossistema `SocialMediaApp` opera com um modelo multitenant complexo e executa tarefas assíncronas concorrentes via BullMQ, o que gera uma alta carga no banco de dados PostgreSQL. Atualmente, o arquivo `config/database.ts` não possui qualquer otimização de connection pooling ou suporte a réplicas de leitura/escrita, o que pode levar a gargalos de performance e esgotamento de conexões sob carga real.
* **Recursos:**
  - Configuração de múltiplos hosts de banco de dados no Lucid ORM do AdonisJS v6 (réplicas de leitura/escrita).
  - Sintonia fina do pool de conexões (tamanhos de pool min/max baseados no ambiente e número de workers BullMQ).
  - Gerenciamento de timeouts de conexão e queries lentas.
  - Padrão de roteamento automático de consultas (leituras para réplicas de leitura, escritas e transações para a réplica principal).
* **Objetivo:** Fornecer diretrizes sólidas e padrões de configuração para replicação de banco de dados e gerenciamento de pools de conexão no AdonisJS v6, visando alta disponibilidade e escalabilidade.
* **Casos de uso:**
  - Configuração de ambiente de alta concorrência em produção.
  - Resolução de gargalos de banco de dados em jobs pesados executados pelo BullMQ.
  - Implementação de failover e escalabilidade horizontal de leitura no PostgreSQL.
* **Workflows:**
  - `/bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `systematic-debugging-best-practices` — Utilizará as técnicas de isolamento de problemas e análise de logs para diagnosticar vazamentos de conexões e queries lentas.
* **Skills auxiliares:** database-connections, database-schema
* **Skills beneficiadas:**
  - `adonisjs-bullmq-multi-tenant-job-isolation-best-practices` — Será beneficiada por garantir que workers paralelos em background não esgotem as conexões de banco de dados.
* **Benefícios:** Otimização do tempo de resposta de leitura, maior resiliência sob concorrência e eliminação do risco de "Too many connections" no PostgreSQL in picos de processamento do BullMQ.
