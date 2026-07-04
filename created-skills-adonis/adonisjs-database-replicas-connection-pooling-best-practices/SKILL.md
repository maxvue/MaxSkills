---
name: adonisjs-database-replicas-connection-pooling-best-practices
description: Use when designing, configuring, profiling, or debugging database connections, read/write replica routing, connection pool tuning, or connection timeouts in AdonisJS v6 using Lucid ORM. Triggers on database.ts connection config, replica setup, query routing to read/write nodes, pool size tuning, and database connection timeouts.
---

## Objetivo
Fornecer diretrizes sólidas e padrões de configuração para replicação de banco de dados e gerenciamento de pool de conexões no AdonisJS v6 (usando o Lucid ORM), garantindo alta disponibilidade, escalabilidade e resiliência sob cargas de trabalho concorrentes (como jobs em background do BullMQ).

## Instruções
1. **Configuração de Conexão do Lucid ORM**:
   Configure as conexões de banco de dados em `config/database.ts`. Especifique um nó de escrita (primário) e réplicas de leitura (read-only).
   O roteamento de réplicas de leitura/escrita é configurado por meio de uma chave de nível superior `replicas` (irmã de `connection`/`pool`): `replicas.write.connection` é um único objeto de conexão e `replicas.read.connection` é um ARRAY de objetos de conexão para os hosts de leitura.
   Exemplo de estrutura:
   ```typescript
   import env from '#start/env'
   import { defineConfig } from '@adonisjs/lucid'

   const dbConfig = defineConfig({
     connection: 'pg',
     connections: {
       pg: {
         client: 'pg',
         // Conexão do nó padrão
         connection: {
           host: env.get('DB_WRITE_HOST'),
           port: env.get('DB_PORT'),
           user: env.get('DB_USER'),
           password: env.get('DB_PASSWORD'),
           database: env.get('DB_DATABASE'),
         },
         // Roteamento de réplicas de leitura/escrita
         replicas: {
           write: {
             connection: {
               host: env.get('DB_WRITE_HOST'),
               port: env.get('DB_PORT'),
               user: env.get('DB_USER'),
               password: env.get('DB_PASSWORD'),
               database: env.get('DB_DATABASE'),
             },
           },
           read: {
             connection: [
               {
                 host: env.get('DB_READ_HOST_1'),
                 port: env.get('DB_PORT'),
                 user: env.get('DB_USER'),
                 password: env.get('DB_PASSWORD'),
                 database: env.get('DB_DATABASE'),
               },
               // Adicione mais réplicas se disponíveis
             ],
           },
         },
         // Ajuste do Pool de Conexões
         pool: {
           min: env.get('DB_POOL_MIN', 2),
           max: env.get('DB_POOL_MAX', 10),
           idleTimeoutMillis: 30000,
           createTimeoutMillis: 30000,
           acquireTimeoutMillis: 30000,
         },
         debug: env.get('NODE_ENV') === 'development',
       }
     }
   })
   export default dbConfig
   ```
   > **Health checks:** O Lucid v6 não possui um booleano de configuração `healthCheck`. Para monitorar uma conexão, registre `DbCheck` / `DbConnectionCountCheck` de `@adonisjs/lucid/database` com o serviço de HealthChecks da aplicação (ex: `import { DbCheck } from '@adonisjs/lucid/database'`), e não via uma chave de configuração.

2. **Roteamento de Queries**:
   Garanta que as queries de escrita vão para o nó de escrita e que as queries de leitura sejam distribuídas automaticamente entre as réplicas de leitura.
   - Para queries `select` padrão, o Lucid ORM as roteia para as réplicas de leitura por padrão, se réplicas de `read` estiverem configuradas.
   - Para inserções, atualizações e exclusões, o Lucid roteia para o nó de escrita.
   - Para transações, elas DEVEM sempre executar no nó de escrita. Garanta que as transações sejam iniciadas corretamente:
     ```typescript
     import db from '@adonisjs/lucid/services/db'
     
     const trx = await db.transaction()
     try {
       // todas as queries dentro de trx serão executadas no nó de escrita
       await trx.commit()
     } catch (error) {
       await trx.rollback()
     }
     ```

3. **Ajuste do Pool para Workers Concorrentes (BullMQ)**:
   Em ambientes que executam processadores de jobs em background (como o BullMQ):
   - Calcule o tamanho máximo do pool de forma que `(number_of_web_conns * max_pool) + (number_of_workers * max_pool) < max_connections_allowed_by_postgres`.
   - Defina tamanhos de pool menores para os workers em background para evitar o esgotamento de conexões. Você pode condicionar `DB_POOL_MAX` em `config/database.ts` usando variáveis de ambiente específicas do tipo de processo (ex: `BULLMQ_WORKER=true`).

4. **Depuração e Profiling**:
   - Habilite a depuração de queries do Lucid em desenvolvimento para verificar o roteamento:
     ```typescript
     import emitter from '@adonisjs/core/services/emitter'
     emitter.on('db:query', (query) => {
       console.log(query.sql, query.bindings)
     })
     ```
   - Fique atento a erros de "Too many connections". Use limites de pool de conexões ou pools de conexão como PgBouncer/Supabase, se necessário.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NUNCA** execute operações de escrita (INSERT, UPDATE, DELETE) dentro de configurações read-only.
- **NUNCA** execute transações contra réplicas de leitura; transações devem sempre executar na conexão de escrita.
- Não deixe tamanhos de pool de conexões fixos no código; sempre leia-os de variáveis de ambiente validadas em `start/env.ts`.
- Evite manter conexões abertas por mais tempo que o necessário; garanta que as queries executem de forma eficiente e que as conexões retornem ao pool.
