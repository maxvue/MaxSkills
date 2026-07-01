# Laravel Data DTO Creator Best Practices

## Goal
Establish clean, robust, and consistent standards for creating, updating, and refactoring Spatie Laravel Data DTO classes in the Engeapp codebase. This ensures seamless type generation and data safety between the Laravel backend and Vue/TypeScript frontend.

## Instructions

### 1. File Location and Naming Conventions
- Place all DTOs in the `app/Data/` directory. Use appropriate subdirectories to group related DTOs (e.g., `app/Data/User/`, `app/Data/Client/`).
- Class names must use the `Data` suffix and match the Eloquent model or context (e.g., `UserData`, `ClientData`, `ProjectDetailData`).
- Add a PHPDoc description at the class level indicating what model or context it transfers.

### 2. Class Declaration and Properties
- Extend `Spatie\LaravelData\Data` for all DTO classes.
- Use PHP 8 Constructor Property Promotion for all properties. Do not leave empty constructors.
- Always use explicit types for properties (e.g., `string`, `int`, `bool`, `float`, custom Enum class, `Carbon`).
- Avoid the use of `array` without specific item types. Use `DataCollection` instead.
- Use nullable types (`?type`) or default values (e.g., `= null`, `= ''`) to handle optional values.

### 3. Handling Relationships (Lazy and DataCollectionOf)
- **Single Relationships:** Use `Lazy | OutroData | null` to represent conditional/lazy-loaded relationships.
  ```php
  public Lazy | OutroData | null $group
  ```
- **Has-Many / Collections:** Use `Lazy | DataCollection` and annotate it with the `#[DataCollectionOf]` attribute referencing the target DTO class.
  ```php
  #[DataCollectionOf(UserRecoveryPasswordData::class)]
  public Lazy | DataCollection $user_recovery_token
  ```
- This setup is critical because the custom `DataCollectionOfPropertyProcessor` uses these attributes to generate typed arrays (e.g. `UserRecoveryPassword[]`) in TypeScript.

### 4. Dates and Timezones
- Always use `Illuminate\Support\Carbon` (e.g., `?Carbon $created_at`) for date/time columns.
- Ensure proper imports (`use Illuminate\Support\Carbon;`).

### 5. Enums
- Use project Enums (e.g., `Gender`, `BrowserAction`) directly as property types.
- Ensure the Enum is annotated with `#[TypeScript]` from `Spatie\TypeScriptTransformer\Attributes\TypeScript` so that typescript-transformer exports it.

### 6. TypeScript Integration
- Properties that might not be sent or are completely optional on the frontend should be annotated with `#[TypeScriptOptional]` from `Spatie\TypeScriptTransformer\Attributes\Optional as TypeScriptOptional`.

### 7. Validation Rules
- Spatie Laravel Data infers validation rules from property types (e.g., `string` is required, `?string` is sometimes/nullable).
- If additional custom validation is required, use attributes like `#[Max(255)]`, `#[Email]`, or override the `rules()` method.

## Constraints
- **NEVER** use raw arrays for nested data objects or collections; always use nested DTOs or `DataCollection`.
- **NEVER** declare properties outside the constructor; always use PHP 8 Constructor Property Promotion.
- **NEVER** bypass Spatie's `Lazy` wrapper for relationships; doing so causes N+1 query issues during serialization.
- **NEVER** forget the `#[DataCollectionOf(ClassData::class)]` attribute on `DataCollection` fields. Without it, the TypeScript type will fail to resolve.
- Do not add custom, inline comments inside the DTO file; prefer clean PHPDocs at class/method levels.
