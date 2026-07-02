---
name: adonisjs-environment-variables-validation-best-practices
description: Use when configuring, reviewing, or validating environment variables, updating start/env.ts, defining Env.schema schemas, troubleshooting missing or invalid env keys, or configuring environment variable injection across different deployment environments in AdonisJS v6. Triggers on start/env.ts modification, Env.schema validation, and env configuration.
---

## Goal
Provide a comprehensive set of guidelines and best practices for defining, validating, and using environment variables in AdonisJS v6 applications using `@adonisjs/core/env`.

## Instructions
1. **Define Schema in `start/env.ts`**:
   - Every environment variable used in the project must be declared and validated in `start/env.ts` using `Env.create`.
   - Use `Env.schema` to define constraints for each variable to ensure types are correctly cast at runtime (e.g. `Env.schema.number()`, `Env.schema.boolean()`).
2. **Accessing Env Variables**:
   - Import the validated `env` service via the path alias `#start/env`:
     ```typescript
     import env from '#start/env'
     ```
   - Always access variables using the `env.get('KEY_NAME')` method to benefit from strict static typing and avoid raw `process.env` calls.
3. **Use the Right Schema Validators**:
   - `Env.schema.string()` for text, with optional formatting: `Env.schema.string({ format: 'url' })`, `Env.schema.string({ format: 'host' })`.
   - `Env.schema.number()` to automatically cast string values (like `PORT` or `DB_PORT`) to JavaScript numbers.
   - `Env.schema.boolean()` to cast values like `"true"`, `"false"`, `"1"`, or `"0"` to boolean.
   - `Env.schema.enum(['val1', 'val2'] as const)` for strict set of values.
   - Use `.optional()` at the end of validators for variables that are not mandatory (e.g., `Env.schema.string.optional()`).
   - Declare sensitive information (e.g. `APP_KEY`, API tokens) with `Env.schema.string()` — the same way the project's own `start/env.ts` validates `APP_KEY`. The installed validator schema (`@poppinss/validator-lite`) exposes only `number`, `string`, `boolean`, and `enum`; there is no `Env.schema.secret()` validator, so do not call it (it throws `Env.schema.secret is not a function`) and do not assume any log-masking feature from the schema.
4. **Maintenance of `.env.example`**:
   - Ensure every variable added to `start/env.ts` is documented in the root `.env.example` file with placeholder values, keeping local credentials blank.

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **Never** read environment variables directly using `process.env.KEY_NAME`. Always use `env.get('KEY_NAME')`.
- **Do not** add sensitive credentials, production passwords, or real API keys to version-controlled files like `start/env.ts` or `.env.example`.
- **Never** bypass environment variable validation in production. The application must crash during bootstrap if a required variable is missing or invalid.
- **Do not** write custom parser functions for basic types. Rely entirely on `Env.schema` type casting.
