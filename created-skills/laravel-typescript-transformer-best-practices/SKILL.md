---
name: laravel-typescript-transformer-best-practices
description: Use when configuring, updating, or generating TypeScript types/interfaces from PHP DTOs and Enums in Laravel using Spatie Laravel TypeScript Transformer. Triggers on typescript:transform command execution, custom type writer/transformer adjustments, and TypeScript type checking errors in Vue/TS components.
---

# Goal
Ensure solid, consistent guidelines for configuring, generating, and validating TypeScript definitions from backend PHP DTOs and Enums, maintaining seamless synchronization between Laravel and Vue 3 / TypeScript in the Engeapp ecosystem.

# Instructions
1. **Directory Inspection & Scope:** The Spatie TypeScript Transformer automatically transforms classes in `app/Data` (for Spatie Data Transfer Objects) and `app/Enums` (for Enums). The output is written to [generated.d.ts](file:///home/johnattas/GitHub/engeapp/resources/Types/generated.d.ts).
2. **DTO Mappings (Automatic):** 
   - Backend classes extending `Spatie\LaravelData\Data` do not require the `#[TypeScript]` attribute. They are discovered automatically by `LaravelDataTransformedProvider`.
   - Ensure the file suffix `Data` is kept in the PHP class name (e.g., `BrandData`), which is automatically stripped to `Brand` in TypeScript by the custom `FlatGlobalWriter`.
3. **Enum Mappings (Explicit):**
   - For PHP Enums in `app/Enums`, you MUST explicitly add the `#[TypeScript]` attribute from `Spatie\TypeScriptTransformer\Attributes\TypeScript` on top of the enum declaration to trigger transformation.
4. **Typed Collections using `#[DataCollectionOf]`:**
   - When declaring collections of another DTO, use `Lazy | DataCollection` and decorate the property with the `#[DataCollectionOf(TargetClassData::class)]` attribute.
   - The custom `CustomDataClassTransformer` and `DataCollectionOfPropertyProcessor` will convert this to a TypeScript typed array (e.g., `TargetClass[]`) instead of `undefined`.
5. **Generating Types:**
   - Execute the Artisan command to regenerate TypeScript definitions:
     `php artisan typescript:transform`
6. **Frontend Integration:**
   - Since types are written to [generated.d.ts](file:///home/johnattas/GitHub/engeapp/resources/Types/generated.d.ts) inside `declare global`, they are accessible globally in Vue 3 / TypeScript components without explicit import statements.

# Constraints
- Do NOT add the `#[TypeScript]` attribute to classes inheriting from `Spatie\LaravelData\Data`, as they are auto-mapped.
- Do NOT use plain untyped array properties in DTOs when they represent collections of DTOs; always specify the target type using the `#[DataCollectionOf(ClassData::class)]` attribute.
- Do NOT import generated types manually in Vue components; they are registered globally via `declare global` in `generated.d.ts`.
