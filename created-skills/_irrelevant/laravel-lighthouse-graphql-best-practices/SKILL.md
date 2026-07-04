---
name: laravel-lighthouse-graphql-best-practices
description: Use when creating, updating, or debugging GraphQL schemas, queries, mutations, subscriptions, custom resolvers, or Lighthouse configuration in Laravel. Triggers on changes to GraphQL schema files (*.graphql), Lighthouse directives, and custom GraphQL resolver PHP classes.
---

# Boas Práticas de GraphQL com Lighthouse no Laravel

## Objetivo
Fornecer diretrizes sólidas e boas práticas para construir, otimizar e depurar APIs GraphQL usando o pacote `nuwave/lighthouse` no Laravel, garantindo consistência, legibilidade do schema, tratamento adequado de erros e prevenção de problemas de performance com queries N+1 dentro do ecossistema Engeapp.

## Instruções

> **⚠️ Setup necessário no engeapp:** `nuwave/lighthouse ^6.64` já está no vendor, mas **ainda não foi configurado** — não existem `config/lighthouse.php` nem `graphql/schema.graphql`. Antes de aplicar qualquer boa prática abaixo, faça o scaffold da instalação:
> ```bash
> php artisan vendor:publish --provider="Nuwave\Lighthouse\LighthouseServiceProvider" --tag=config   # cria config/lighthouse.php
> php artisan vendor:publish --provider="Nuwave\Lighthouse\LighthouseServiceProvider" --tag=schema   # cria graphql/schema.graphql inicial
> ```
> Só depois de `config/lighthouse.php` e `graphql/schema.graphql` existirem é que as diretivas e resolvers passam a ser resolvidos.

1. **Design & Organização do Schema**:
   - Mantenha o arquivo de schema de entrada em `graphql/schema.graphql`.
   - Para aplicações maiores, decomponha o schema usando a diretiva `#import` (ex: `#import types/*.graphql`) para organizar queries, mutations e types em domínios.
   - Siga as convenções de nomenclatura padrão: `PascalCase` para Types e Enums, `camelCase` para campos, argumentos e nomes de input, e `UPPERCASE` para valores de Enum.
   - Agrupe mutations e queries relacionadas de forma lógica.

2. **Aproveitando as Diretivas Nativas**:
   - Prefira diretivas nativas do Lighthouse em vez de escrever resolvers PHP customizados para operações CRUD padrão:
     - **Recuperação**: Use `@all`, `@find`, `@first` e `@paginate` (sempre use `@paginate` para listas que possam crescer, para evitar carregar registros demais em memória).
     - **Relacionamentos**: Use `@belongsTo`, `@hasMany`, `@hasOne`, `@belongsToMany` para deixar o Lighthouse resolver os relacionamentos automaticamente.
     - **Performance**: A diretiva de relação (`@hasMany`, `@belongsTo`, etc.) já resolve o relacionamento e faz o batching/eager-load correto sozinha — **não empilhe `@with` sobre um campo que já usa `@hasMany`** (é redundante e incorreto). Use `@with` apenas para eager-loading de relações que são consumidas por um resolver que **não** é o resolver de relação (por exemplo, uma relação necessária dentro de um accessor/campo computado que não é exposto diretamente como `@hasMany`).
       ```graphql
       type User {
         id: ID!
         name: String!
         # @hasMany sozinho já resolve e faz batching da relação — sem @with aqui
         posts: [Post!]! @hasMany
       }
       ```
     - **Filtragem**: Use `@eq`, `@where`, `@like` para argumentos básicos de filtragem em campos.
     - **Autorização**: Proteja campos, queries ou mutations aplicando `@can` (usa Policies do Laravel) ou `@guard` (usa middlewares de Auth do Laravel).
       ```graphql
       type Query {
         users: [User!]! @paginate @can(ability: "viewAny", model: "App\\Models\\User")
       }
       ```

3. **Resolvers Customizados**:
   - Escreva resolvers customizados apenas quando for necessária uma lógica de negócio complexa que não possa ser expressa via diretivas de schema.
   - Coloque as queries em `app/GraphQL/Queries` e as mutations em `app/GraphQL/Mutations`.
   - Escreva código type-safe usando declarações de tipo do PHP 8. Use blocos de definição PHPDoc para especificar os formatos de `$args` usando array shapes:
     ```php
     namespace App\GraphQL\Queries;

     use GraphQL\Type\Definition\ResolveInfo;
     use Nuwave\Lighthouse\Support\Contracts\GraphQLContext;

     class UserReport
     {
         /**
          * Resolve os detalhes do relatório de usuário.
          *
          * @param  null  $rootValue
          * @param  array{start_date: string, end_date: string, user_id: int}  $args
          * @param  GraphQLContext  $context
          * @param  ResolveInfo  $resolveInfo
          * @return array<string, mixed>
          */
         public function __invoke($rootValue, array $args, GraphQLContext $context, ResolveInfo $resolveInfo): array
         {
             // Implemente a lógica usando tipos estritos
             return [];
         }
     }
     ```

4. **Tratamento de Erros & Validação**:
   - Para validação de input, use a diretiva nativa `@validator` para delegar a validação a classes validadoras customizadas ou a Form Requests padrão do Laravel.
   - Exceções customizadas destinadas a exibir erros limpos e formatados para o cliente frontend devem implementar a interface `GraphQL\Error\ClientAware` e retornar `true` para `isClientSafe()`.
   - Nunca exponha exceções SQL brutas ou stack traces do sistema para o cliente em produção. Garanta que `lighthouse.debug` esteja desabilitado em ambientes não-locais.

5. **Configurações de Performance & Segurança**:
   - Monitore a complexidade e a profundidade das queries usando as configurações de middleware de segurança em `config/lighthouse.php` para prevenir queries aninhadas maliciosas ou excessivamente pesadas (ataques de DoS).
   - Utilize ativamente o profiling de queries do Laravel (usando Clockwork ou Debugbar) para inspecionar as queries SQL disparadas durante as operações GraphQL.

6. **Integração com o Frontend**:
   - Mapeie os envelopes de paginação retornados (types `Paginator` ou `Connection`) para estruturas reativas correspondentes no frontend.
   - Garanta que o frontend leia corretamente a resposta padrão do GraphQL: os dados ficam em `data` e os problemas ficam no array `errors` de nível superior.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
1. **Nunca faça loops N+1 manuais**: Nunca execute queries dentro de loops em resolvers customizados. Faça eager-load de todas as relações (`$models->load(...)` ou use `@with` no schema).
2. **Não modifique estado em Queries**: Queries devem ser livres de efeitos colaterais (read-only). Ações que modificam estado devem ser modeladas estritamente como Mutations GraphQL.
3. **Sem erros de banco brutos em produção**: Garanta que todas as exceções brutas de banco de dados sejam capturadas e sanitizadas. Não permita que detalhes brutos do DB vazem no payload de erro do GraphQL.
4. **Nunca pule declarações de tipo**: Sempre use tipos de retorno e type hints de parâmetros em classes PHP customizadas de query, mutation e validator.
