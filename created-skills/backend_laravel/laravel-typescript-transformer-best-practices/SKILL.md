---
name: laravel-typescript-transformer-best-practices
description: Use when configuring, updating, or generating TypeScript types/interfaces from PHP DTOs and Enums in Laravel using Spatie Laravel TypeScript Transformer. Triggers on typescript:transform command execution, custom type writer/transformer adjustments, and TypeScript type checking errors in Vue/TS components.
---

# Objetivo
Garantir diretrizes sólidas e consistentes para configurar, gerar e validar definições TypeScript a partir de DTOs e Enums PHP do backend, mantendo a sincronização perfeita entre Laravel e Vue 3 / TypeScript no ecossistema do Engeapp.

# Instruções
1. **Inspeção de Diretórios e Escopo:** O Spatie TypeScript Transformer transforma automaticamente as classes em `app/Data` (para Data Transfer Objects do Spatie) e `app/Enums` (para Enums). A saída é escrita em [generated.d.ts](file:///home/johnattas/GitHub/engeapp/resources/Types/generated.d.ts).
2. **Mapeamentos de DTO (Automático):**
   - Classes de backend que estendem `Spatie\LaravelData\Data` não exigem o atributo `#[TypeScript]`. Elas são descobertas automaticamente pelo `LaravelDataTransformedProvider`.
   - Garanta que o sufixo `Data` do arquivo seja mantido no nome da classe PHP (ex: `BrandData`), que é automaticamente removido para `Brand` no TypeScript pelo `FlatGlobalWriter` customizado.
3. **Mapeamentos de Enum (Explícito):**
   - Para Enums PHP em `app/Enums`, você DEVE adicionar explicitamente o atributo `#[TypeScript]` de `Spatie\TypeScriptTransformer\Attributes\TypeScript` no topo da declaração do enum para disparar a transformação.
4. **Coleções Tipadas usando `#[DataCollectionOf]`:**
   - Ao declarar coleções de outro DTO, use `Lazy | DataCollection` e decore a propriedade com o atributo `#[DataCollectionOf(TargetClassData::class)]`.
   - O `CustomDataClassTransformer` e o `DataCollectionOfPropertyProcessor` customizados converterão isso em um array tipado do TypeScript (ex: `TargetClass[]`) em vez de `undefined`.
5. **Gerando os Tipos:**
   - Execute o comando Artisan para regenerar as definições TypeScript:
     `php artisan typescript:transform`
6. **Integração com o Frontend:**
   - Como os tipos são escritos em [generated.d.ts](file:///home/johnattas/GitHub/engeapp/resources/Types/generated.d.ts) dentro de `declare global`, eles são acessíveis globalmente em componentes Vue 3 / TypeScript sem instruções de import explícitas.

# Restrições
- NÃO adicione o atributo `#[TypeScript]` a classes que herdam de `Spatie\LaravelData\Data`, pois elas são mapeadas automaticamente.
- NÃO use propriedades de array simples e sem tipo em DTOs quando elas representam coleções de DTOs; sempre especifique o tipo-alvo usando o atributo `#[DataCollectionOf(ClassData::class)]`.
- NÃO importe tipos gerados manualmente em componentes Vue; eles são registrados globalmente via `declare global` em `generated.d.ts`.

## Restrições
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
