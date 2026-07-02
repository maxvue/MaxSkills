---
name: laravel-lighthouse-graphql-best-practices
description: Use when creating, updating, or debugging GraphQL schemas, queries, mutations, subscriptions, custom resolvers, or Lighthouse configuration in Laravel. Triggers on changes to GraphQL schema files (*.graphql), Lighthouse directives, and custom GraphQL resolver PHP classes.
---

# Laravel Lighthouse GraphQL Best Practices

## Goal
Provide solid guidelines and best practices for building, optimizing, and debugging GraphQL APIs using the `nuwave/lighthouse` package in Laravel, ensuring consistency, schema readability, proper error handling, and prevention of N+1 query performance issues within the Engeapp ecosystem.

## Instructions

1. **Schema Design & Organization**:
   - Maintain the entry schema file at `graphql/schema.graphql`.
   - For larger applications, decompose the schema using the `#import` directive (e.g., `#import types/*.graphql`) to organize queries, mutations, and types into domains.
   - Follow standard naming conventions: `PascalCase` for Types and Enums, `camelCase` for fields, arguments, and input names, and `UPPERCASE` for Enum values.
   - Group related mutations and queries logically.

2. **Leveraging Built-in Directives**:
   - Prefer built-in Lighthouse directives over writing custom PHP resolvers for standard CRUD operations:
     - **Retrieval**: Use `@all`, `@find`, `@first`, and `@paginate` (always use `@paginate` for lists that might grow to prevent loading too many records in memory).
     - **Relationships**: Use `@belongsTo`, `@hasMany`, `@hasOne`, `@belongsToMany` to let Lighthouse resolve relationships automatically.
     - **Performance**: Always use `@with` directive to eager load relations and prevent N+1 query execution problems.
       ```graphql
       type User {
         id: ID!
         name: String!
         posts: [Post!]! @hasMany @with(relation: "posts")
       }
       ```
     - **Filtering**: Use `@eq`, `@where`, `@like` for basic filtering arguments on fields.
     - **Authorization**: Secure fields, queries, or mutations by applying `@can` (uses Laravel Policies) or `@guard` (uses Laravel Auth middlewares).
       ```graphql
       type Query {
         users: [User!]! @paginate @can(ability: "viewAny", model: "App\\Models\\User")
       }
       ```

3. **Custom Resolvers**:
   - Write custom resolvers only when complex business logic is required that cannot be expressed via schema directives.
   - Place queries in `app/GraphQL/Queries` and mutations in `app/GraphQL/Mutations`.
   - Write type-safe code using PHP 8 type declarations. Use PHPDoc block definitions to specify the shapes of `$args` using array shapes:
     ```php
     namespace App\GraphQL\Queries;

     use GraphQL\Type\Definition\ResolveInfo;
     use Nuwave\Lighthouse\Support\Contracts\GraphQLContext;

     class UserReport
     {
         /**
          * Resolve user report details.
          *
          * @param  null  $rootValue
          * @param  array{start_date: string, end_date: string, user_id: int}  $args
          * @param  GraphQLContext  $context
          * @param  ResolveInfo  $resolveInfo
          * @return array<string, mixed>
          */
         public function __invoke($rootValue, array $args, GraphQLContext $context, ResolveInfo $resolveInfo): array
         {
             // Implement logic using strict types
             return [];
         }
     }
     ```

4. **Error Handling & Validation**:
   - For input validation, use the built-in `@validator` directive to delegate validation to custom validator classes or standard Laravel Form Requests.
   - Custom exceptions meant to display clean, formatted errors to the frontend client must implement the `GraphQL\Error\ClientAware` interface and return `true` for `isClientSafe()`.
   - Never expose raw SQL exceptions or system stack traces to the client in production. Ensure that `lighthouse.debug` is disabled in non-local environments.

5. **Performance & Security Settings**:
   - Monitor the query complexity and depth using the security middleware settings in `config/lighthouse.php` to prevent malicious or excessively heavy nested queries (DoS attacks).
   - Eagerly utilize Laravel's query profiling (using Clockwork or Debugbar) to inspect SQL queries dispatched during GraphQL operations.

6. **Frontend Integration**:
   - Map returned paginate envelopes (`Paginator` or `Connection` types) to matching frontend reactive structures.
   - Ensure the frontend properly reads the GraphQL standard response: data is in `data`, and issues are in the top-level `errors` array.

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
1. **Never perform manual N+1 loops**: Never execute queries inside loops within custom resolvers. Eager load all relations (`$models->load(...)` or use schema `@with`).
2. **Do not modify state in Queries**: Queries must be side-effect-free (read-only). State-modifying actions must strictly be modeled as GraphQL Mutations.
3. **No raw database errors in production**: Ensure all raw database exceptions are caught and sanitized. Do not allow raw DB details to leak in the GraphQL error payload.
4. **Never skip type declarations**: Always use return types and parameter type hints in custom query, mutation, and validator PHP classes.
