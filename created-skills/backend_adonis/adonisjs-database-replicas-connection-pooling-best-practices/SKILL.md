---
name: adonisjs-database-replicas-connection-pooling-best-practices
description: Use when designing, configuring, profiling, or debugging database connections, read/write replica routing, connection pool tuning, or connection timeouts in AdonisJS v6 using Lucid ORM. Triggers on database.ts connection config, replica setup, query routing to read/write nodes, pool size tuning, and database connection timeouts.
---

## Goal
Provide solid guidelines and configuration patterns for database replication and connection pool management in AdonisJS v6 (using Lucid ORM) to ensure high availability, scalability, and resilience under concurrent workloads (such as BullMQ background jobs).

## Instructions
1. **Lucid ORM Connection Setup**:
   Configure database connections in `config/database.ts`. Specify a write node (primary) and read replicas (read-only).
   Read/write replica routing is configured via a top-level `replicas` key (sibling to `connection`/`pool`): `replicas.write.connection` is a single connection object and `replicas.read.connection` is an ARRAY of connection objects for the read hosts.
   Example layout:
   ```typescript
   import env from '#start/env'
   import { defineConfig } from '@adonisjs/lucid'

   const dbConfig = defineConfig({
     connection: 'pg',
     connections: {
       pg: {
         client: 'pg',
         // Default node connection
         connection: {
           host: env.get('DB_WRITE_HOST'),
           port: env.get('DB_PORT'),
           user: env.get('DB_USER'),
           password: env.get('DB_PASSWORD'),
           database: env.get('DB_DATABASE'),
         },
         // Read/write replica routing
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
               // Add more replicas if available
             ],
           },
         },
         // Connection Pool Tuning
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
   > **Health checks:** Lucid v6 has no `healthCheck` config boolean. To monitor a connection, register `DbCheck` / `DbConnectionCountCheck` from `@adonisjs/lucid/database` with the app's HealthChecks service (e.g. `import { DbCheck } from '@adonisjs/lucid/database'`), not via a config key.

2. **Query Routing**:
   Ensure write queries go to the write node, and read queries are automatically distributed among read replicas.
   - For standard select queries, Lucid ORM routes them to read replicas by default if `read` replicas are configured.
   - For insertions, updates, and deletions, Lucid routes to the write node.
   - For transactions, they MUST always run on the write node. Ensure transactions are initiated properly:
     ```typescript
     import db from '@adonisjs/lucid/services/db'
     
     const trx = await db.transaction()
     try {
       // all queries within trx will execute on the write node
       await trx.commit()
     } catch (error) {
       await trx.rollback()
     }
     ```

3. **Pool Tuning for Concurrent Workers (BullMQ)**:
   In environments running background job processors (like BullMQ):
   - Calculate the max pool size so that `(number_of_web_conns * max_pool) + (number_of_workers * max_pool) < max_connections_allowed_by_postgres`.
   - Set smaller pool sizes for background workers to prevent connection exhaustion. You can conditionalize `DB_POOL_MAX` in `config/database.ts` using env variables specific to the process type (e.g., `BULLMQ_WORKER=true`).

4. **Debugging and Profiling**:
   - Enable Lucid query debugging in development to verify routing:
     ```typescript
     import emitter from '@adonisjs/core/services/emitter'
     emitter.on('db:query', (query) => {
       console.log(query.sql, query.bindings)
     })
     ```
   - Watch for "Too many connections" errors. Use connection pooling limits or PgBouncer/Supabase connection poolers if necessary.

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **NEVER** run write operations (INSERT, UPDATE, DELETE) inside read-only configurations.
- **NEVER** execute transactions against read replicas; transactions must always run on the write connection.
- Do not hardcode connection pool sizes; always read them from validated environment variables in `start/env.ts`.
- Avoid keeping connections open longer than necessary; ensure queries execute efficiently and connections return to the pool.
