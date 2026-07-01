---
name: adonisjs-database-replicas-connection-pooling-best-practices
description: Use when designing, configuring, profiling, or debugging database connections, read/write replica routing, connection pool tuning, or connection timeouts in AdonisJS v6 using Lucid ORM. Triggers on database.ts connection config, replica setup, query routing to read/write nodes, pool size tuning, and database connection timeouts.
---

## Objetivo
Fornecer diretrizes sólidas e padrões de configuração para replicação de banco de dados e gerenciamento de pools de conexão no AdonisJS v6 (usando Lucid ORM) para garantir alta disponibilidade, escalabilidade e resiliência sob cargas de trabalho concorrentes (como tarefas em segundo plano do BullMQ).

## Instruções
1. **Configuração de Conexão do Lucid ORM**:
   Configure as conexões de banco de dados em `config/database.ts`. Especifique um nó de escrita (principal) e réplicas de leitura (somente leitura).
   Use a chave `replicas` na configuração da conexão para definir múltiplos hosts de leitura.
   Exemplo de estrutura:
   ```typescript
   import env from '#start/env'
   import { defineConfig } from '@adonisjs/lucid'

   const dbConfig = defineConfig({
     connection: 'pg',
     connections: {
       pg: {
         client: 'pg',
         connection: {
           write: {
             host: env.get('DB_WRITE_HOST'),
             port: env.get('DB_PORT'),
             user: env.get('DB_USER'),
             password: env.get('DB_PASSWORD'),
             database: env.get('DB_DATABASE'),
           },
           read: {
             replicas: [
               {
                 host: env.get('DB_READ_HOST_1'),
                 port: env.get('DB_PORT'),
                 user: env.get('DB_USER'),
                 password: env.get('DB_PASSWORD'),
                 database: env.get('DB_DATABASE'),
               },
               // Adicione mais réplicas se disponíveis
             ]
           }
         },
         // Ajuste do Pool de Conexões
         pool: {
           min: env.get('DB_POOL_MIN', 2),
           max: env.get('DB_POOL_MAX', 10),
           idleTimeoutMillis: 30000,
           createTimeoutMillis: 30000,
           acquireTimeoutMillis: 30000,
         },
         healthCheck: true,
         debug: env.get('NODE_ENV') === 'development',
       }
     }
   })
   export default dbConfig
   ```

2. **Roteamento de Consultas**:
   Garanta que as consultas de escrita vão para o nó de escrita, e as de leitura sejam distribuídas automaticamente entre as réplicas de leitura.
   - Para consultas select normais, o Lucid ORM as direciona para as réplicas de leitura por padrão se as réplicas `read` estiverem configuradas.
   - Para inserções, atualizações e exclusões, o Lucid direciona para o nó de escrita.
   - Para transações, elas DEVEM sempre rodar no nó de escrita. Garanta que as transações sejam iniciadas corretamente:
     ```typescript
     import db from '@adonisjs/lucid/services/db'
     
     const trx = await db.transaction()
     try {
       // todas as consultas dentro da trx serão executadas no nó de escrita
       await trx.commit()
     } catch (error) {
       await trx.rollback()
     }
     ```

3. **Ajuste de Pool para Workers Concorrentes (BullMQ)**:
   Em ambientes que executam processadores de tarefas em segundo plano (como BullMQ):
   - Calcule o tamanho máximo do pool para que `(numero_conexoes_web * max_pool) + (numero_workers * max_pool) < max_connections_permitido_pelo_postgres`.
   - Defina tamanhos de pool menores para os workers em segundo plano para evitar o esgotamento de conexões. Você pode condicionalizar o `DB_POOL_MAX` em `config/database.ts` usando variáveis de ambiente específicas para o tipo de processo (ex: `BULLMQ_WORKER=true`).

4. **Depuração e Profiling**:
   - Ative a depuração de consultas do Lucid em ambiente de desenvolvimento para verificar o roteamento:
     ```typescript
     import db from '@adonisjs/lucid/services/db'
     db.on('query', (query) => {
       console.log(query.sql, query.bindings)
     })
     ```
   - Monitore erros de "Too many connections". Use limites de pool de conexões ou poolers de conexão como PgBouncer/Supabase se necessário.

## Restrições
- **NUNCA** execute operações de escrita (INSERT, UPDATE, DELETE) em configurações de somente leitura.
- **NUNCA** execute transações contra réplicas de leitura; as transações devem sempre rodar na conexão de escrita.
- Não defina tamanhos de pool de conexões de forma estática; sempre leia-os de variáveis de ambiente validadas em `start/env.ts`.
- Evite manter conexões abertas por mais tempo que o necessário; garanta que as consultas sejam executadas com eficiência e as conexões retornem ao pool.
