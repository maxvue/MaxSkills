# Laravel API Controller Best Practices

## Goal
Establish clean, performant, and standardized API Controllers inside the Laravel backend ecosystem, ensuring thin controllers, isolated validation layers, and predictable structured JSON responses.

## Instructions
1. **Controller Structure:**
   - Extend the base `Controller` class.
   - Use PHP 8 constructor property promotion for service/action dependency injection.
   - Keep actions minimal (Thin Controllers). Complex business logic MUST be delegated to Services or Actions.
   - Use single-action controllers (`__invoke`) when a controller only has one public responsibility.

2. **Validation (Form Requests):**
   - NEVER perform validation inline inside the controller using `$request->validate()`.
   - ALWAYS generate and inject a custom Form Request (e.g., `StoreUserRequest`) for request validation.

3. **Responses (Eloquent API Resources):**
   - ALWAYS return data wrapped in Eloquent API Resources or Resource Collections.
   - Specify HTTP status codes explicitly (e.g., `201` for Created, `200` for OK, `204` for No Content).
   - Use structured response JSON formatting.

4. **Types and Return Declarations:**
   - Define strict parameter types and return type declarations on all controller methods (e.g., `public function show(User $user): UserResource`).
   - Use correct Laravel request parameters mapping and Route Model Binding.

## Constraints
- DO NOT execute database queries directly in the controller; use Eloquent relationships, Query Scopes, or Services.
- DO NOT return raw Eloquent Models or arrays directly as HTTP responses; always wrap them in API Resources.
- DO NOT use inline `try/catch` blocks for global exceptions (like ModelNotFoundException); let the Laravel global Exception Handler capture and format the response.
