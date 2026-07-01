# Laravel Reliese Models Generator Best Practices

## Goal
Establish clean, standardized guidelines for generating and maintaining Laravel Eloquent models from the database schema using the Reliese Laravel Model Generator in the Engeapp ecosystem.

## Instructions

1. **Configuration (`config/models.php`):**
   - **Enable Base Files:** Always set `'base_files' => true` to keep a clean separation. This generates an abstract base class (e.g., `App\Models\Base\User`) which is safe to overwrite, and a child class (`App\Models\User`) where custom business logic, custom attributes, or manual overrides are placed.
   - **Path & Namespaces:** Ensure `'path' => app_path('Models')` and `'namespace' => 'App\\Models'` are properly set.
   - **Timestamps & Soft Deletes:** Set `'timestamps' => true` and `'soft_deletes' => true` to automatically map database columns (`created_at`, `updated_at`, `deleted_at`) to Eloquent's native features.
   - **Casts:** Define mapping patterns under the `'casts'` key (e.g., `'*_json' => 'json'`) to automatically parse column types.

2. **Model Generation Command:**
   - Use the Artisan command to generate models:
     ```bash
     php artisan code:models --no-interaction
     ```
   - **Targeted Generation:** Always filter by specific tables to avoid bulk overwrites or unnecessary file creations:
     ```bash
     php artisan code:models --table=table_name --no-interaction
     ```
   - Verify the generated files in the `app/Models/Base/` directory immediately after execution.

3. **Managing Business Logic (Separation of Concerns):**
   - **Base Models:** All automatic columns, casts, dates, and database-level relationships (`hasMany`, `belongsTo`, etc.) reside in the Base model. Do not modify these files manually.
   - **App Models:** Add custom local scopes, mutators, accessors, business events, custom relationships, and custom traits inside the App model (e.g., `app/Models/Project.php`). These classes inherit the Base model and are never overwritten by Reliese.

4. **IDE & Static Analysis Support (Larastan/IDE Helper):**
   - To keep the models clean and avoid inline PHPDoc pollution in App models, do not write model properties directly in PHPDoc blocks on the App models.
   - Run the IDE helper command to generate model type information in a separate metadata file:
     ```bash
     php artisan ide-helper:models -M --nowrite
     ```

## Constraints
- **Never** edit files inside `app/Models/Base/` manually. Any manual changes there will be destroyed on the next model generation.
- **Do not** run `php artisan code:models` globally without specifying `--table` unless explicitly requested or during a full database synchronization task.
- **Never** add business logic, validation, custom queries, or app-specific traits inside the Base models.
- **Do not** declare PHPDoc properties inside custom App models; run `php artisan ide-helper:models -M --nowrite` to maintain external autocompletion files.
- All comments, logs, and developer documentation within code files must strictly be in **Brazilian Portuguese (pt-BR)**.
