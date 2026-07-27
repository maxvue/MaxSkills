---
title: Single Responsibility Principle
impact: CRITICAL
impactDescription: One reason to change, easier testing and maintenance
tags: solid, srp, design-principles, single-responsibility
---

# Single Responsibility Principle (SRP)

A class should have only one reason to change - one responsibility.

## Bad Example

```php
<?php

// This class has multiple responsibilities
class User
{
    public function __construct(
        private int $id,
        private string $name,
        private string $email,
    ) {}

    // Responsibility 1: User data
    public function getName(): string
    {
        return $this->name;
    }

    // Responsibility 2: Database operations
    public function save(): void
    {
        DB::table('users')->insert(['name' => $this->name, 'email' => $this->email]);
    }

    // Responsibility 3: Email sending
    public function sendWelcomeEmail(): void
    {
        mail($this->email, 'Welcome!', "Hello {$this->name}, welcome to our platform!");
    }

    // Responsibility 4: Validation
    public function validate(): array
    {
        $errors = [];
        if (empty($this->name)) {
            $errors[] = 'Name is required';
        }
        if (!filter_var($this->email, FILTER_VALIDATE_EMAIL)) {
            $errors[] = 'Invalid email';
        }
        return $errors;
    }
}
```

## Good Example

```php
<?php

// Responsibility: domain entity, no persistence/validation/email logic
class User extends Model
{
    protected $fillable = ['name', 'email'];
}

// Responsibility: validation (Laravel FormRequest)
class CreateUserRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'name' => ['required', 'string'],
            'email' => ['required', 'email'],
        ];
    }
}

// Responsibility: notification
class UserWelcomeNotifier
{
    public function __construct(private MailerInterface $mailer) {}

    public function send(User $user): void
    {
        $this->mailer->send(to: $user->email, subject: 'Welcome!', body: "Hello {$user->name}!");
    }
}

// Responsibility: orchestration (thin application service)
class UserService
{
    public function __construct(private UserWelcomeNotifier $notifier) {}

    public function create(array $data): User
    {
        $user = User::create($data);
        $this->notifier->send($user);

        return $user;
    }
}
```

## Identifying Violations

- Class name contains "And", "Manager", or "Helper"
- Large number of injected dependencies (5+)
- Fat controllers/models mixing validation, business logic, persistence, email, and formatting

**Refactoring:** Validation -> Form Request; Persistence -> Eloquent model/Repository; Notifications -> dedicated notifier class; Orchestration -> thin service class.

## Why

- **Focused Classes**: Each class does one thing well
- **Easier Testing**: Small, focused classes are easier to unit test
- **Simpler Maintenance**: Changes to one responsibility don't affect others
- **Clear Dependencies**: Easier to understand what a class needs

