---
name: laravel-typescript-transformer-best-practices
description: "Use when configuring, updating, or generating TypeScript types/interfaces from PHP DTOs and Enums in Laravel using Spatie Laravel TypeScript Transformer (php artisan typescript:transform). Covers objectives, TypeScript DTO transformation, and language rules."
---
## Objetivo
Garantir diretrizes sólidas e consistentes para configurar, gerar e validar definições TypeScript a partir de DTOs e Enums PHP do backend, mantendo a sincronização perfeita entre Laravel e Vue 3 / TypeScript no ecossistema do Engeapp.

## Instruções
1. **Inspeção de Diretórios e Escopo:** O Spatie TypeScript Transformer transforma automaticamente as classes em `app/Data` (para Data Transfer Objects do Spatie) e `app/Enums` (para Enums). A saída é escrita em `resources/Types/generated.d.ts`. Toda essa configuração é **programática**, não via `config/typescript-transformer.php` (esse arquivo não existe no projeto): está em `app/Providers/TypeScriptTransformerServiceProvider.php::configure()`, que usa a API v3 do `spatie/typescript-transformer` (`extension()`, `prependTransformer()`, `provider()`, `transformer()`, `transformDirectories()`, `outputDirectory()`, `writer()`, `formatter()`). É lá que `FlatGlobalWriter`, `CustomDataClassTransformer` e `LaravelDataTransformedProvider` são registrados, e onde `transformer()` registra o `EnumTransformer` (pipeline de Enums) — consulte esse provider para ajustar o pipeline.
2. **Mapeamentos de DTO (Automático):**
   - Classes de backend que estendem `Spatie\LaravelData\Data` não exigem o atributo `#[TypeScript]`. Elas são descobertas automaticamente pelo `LaravelDataTransformedProvider`.
   - Garanta que o sufixo `Data` do arquivo seja mantido no nome da classe PHP (ex: `BrandData`), que é automaticamente removido para `Brand` no TypeScript pelo `FlatGlobalWriter` customizado.
3. **Mapeamentos de Enum (Automático, com convenção de anotar):**
   - Todos os Enums PHP dentro de `app/Enums` são transformados automaticamente pelo `EnumTransformer` registrado no provider (a descoberta é por diretório, não por atributo) — não é preciso anotar para disparar a transformação.
   - Ainda assim, a convenção do projeto é anotar o enum com `#[TypeScript]` de `Spatie\TypeScriptTransformer\Attributes\TypeScript` no topo da declaração (100% dos enums de `app/Enums` seguem essa convenção), pois o atributo permite sobrescrever nome/namespace no `TransformationContext`. Quem de fato controla exclusão é o atributo `#[Hidden]`.
4. **Coleções Tipadas usando `#[DataCollectionOf]`:**
   - Ao declarar coleções de outro DTO, use `Lazy | DataCollection` e decore a propriedade com o atributo `#[DataCollectionOf(TargetClassData::class)]`.
   - O `CustomDataClassTransformer` e o `DataCollectionOfPropertyProcessor` customizados converterão isso em um array tipado do TypeScript (ex: `TargetClass[]`) em vez de `undefined`.
5. **Gerando os Tipos:**
   - Execute o comando Artisan para regenerar as definições TypeScript:
     `php artisan typescript:transform`
6. **Integração com o Frontend:**
   - Como os tipos são escritos em `resources/Types/generated.d.ts` dentro de `declare global`, eles são acessíveis globalmente em componentes Vue 3 / TypeScript sem instruções de import explícitas.

## Idioma
- Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
