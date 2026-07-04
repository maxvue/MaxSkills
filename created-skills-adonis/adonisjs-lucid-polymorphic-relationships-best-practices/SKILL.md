---
name: adonisjs-lucid-polymorphic-relationships-best-practices
description: Use when implementing, reviewing, or debugging polymorphic-like relationships (one-to-many or many-to-many morphs) in AdonisJS v6 using Lucid ORM. Triggers on custom morphTo/morphMany resolver getters, storing polymorphic columns (xxxable_type and xxxable_id), resolving dynamic model types using Union Types in TypeScript, or preventing N+1 queries during polymorphic dynamic preloads.
---

## Objetivo
Implementar, refatorar e manter relacionamentos polimórficos (polymorphic-like) no AdonisJS v6 com o Lucid ORM usando um padrão robusto de resolver personalizado que previne problemas de performance de queries N+1 e mantém a type-safety do TypeScript com Union Types.

## Instruções
Como o Lucid ORM não suporta relacionamentos polimórficos nativos (como o `morphTo`/`morphMany` do Eloquent), você deve implementá-los manualmente usando o padrão de resolver personalizado. Siga estes padrões:

1. **Schema do Banco de Dados e Migrações:**
   - Defina as colunas polimórficas usando convenções de nomenclatura padrão: `{name}_type` (string) e `{name}_id` (correspondendo ao tipo das chaves primárias do alvo, ex: UUID, ULID ou string).
   - Adicione índices apropriados a essas colunas para performance de lookup.

2. **Contratos de Model e DTOs:**
   - Mapeie as colunas `{name}Type` e `{name}Id` dentro do model usando `@column()`.
   - Forneça um Union Type do TypeScript representando os models concretos que podem ser resolvidos.

3. **Padrão de Resolver Personalizado (Prevenindo Queries N+1):**
   - Crie um service de resolver dedicado (ex: `app/services/{name}_resolver.ts`) para lidar com a busca dos models concretos.
   - Implemente `resolve(type, id)` para buscar uma única instância concreta.
   - Implemente `loadForMany(rows)` para carregar relacionamentos em lote. Agrupe os IDs de destino por tipo, execute uma única query `whereIn` por tipo de model e mapeie-os de volta para evitar loops de query N+1.

4. **Serialização da Resposta:**
   - Intercepte a serialização (seja por métodos serialize personalizados ou em uma camada de service) para injetar a instância concreta resolvida no payload JSON final.

Consulte a pasta de exemplos para uma implementação concreta:
- Configuração de Model e Migração: [examples/transaction_accountable.ts](examples/transaction_accountable.ts)
- Resolver em lote personalizado: [examples/accountable_resolver.ts](examples/accountable_resolver.ts)
- Consumo pelo service e serialização: [examples/transaction_service.ts](examples/transaction_service.ts)

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- Não tente usar decorators nativos inexistentes `morphTo` ou `morphMany` no Lucid ORM.
- Sempre implemente o método de carregamento em lote (`loadForMany`) nos seus resolvers ao buscar listas de itens para prevenir queries N+1.
- Não perca a type-safety do TypeScript; sempre defina Union Types explícitos (ex: `export type Accountable = UserAccount | UserCard`) para as relações resolvidas.
