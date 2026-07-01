---
name: laravel-slack-notifications-integration
description: Use when creating, reviewing, or debugging Laravel Slack notifications, configuring Slack Webhook channels, handling Slack notification routing, or custom slack block formatting. Triggers on Slack notification setup, webhooks configuration, or message layout changes.
---

# Slack Notifications Integration in Laravel

## Goal
Establish clear guidelines, configuration patterns, and best practices for creating, sending, formatting, and testing Slack notifications within the Laravel backend of the Engeapp ecosystem.

## Instructions

### 1. Configuration Setup
Always store Slack credentials and default channels securely within the `config/services.php` file. Do not access environment variables directly in application code.

- **Standard Slack Notification Config:**
  Configure the services array in `config/services.php`:
  ```php
  'slack' => [
      'notifications' => [
          'bot_user_oauth_token' => env('SLACK_BOT_USER_OAUTH_TOKEN'),
          'channel'              => env('SLACK_BOT_USER_DEFAULT_CHANNEL'),
      ],
  ],
  ```

- **Alternative Incoming Webhook Config:**
  If the application uses a single incoming webhook URL:
  ```php
  'slack' => [
      'webhook' => env('SLACK_WEBHOOK_URL'),
  ],
  ```

### 2. Creating a Notification Class
Generate the notification class using the Artisan CLI:
```bash
php artisan make:notification CriticalErrorSlackAlert
```

Implement the notification structure:
- Implement the `via($notifiable)` method to route through `['slack']`.
- Implement `toSlack($notifiable)` returning an instance of `Illuminate\Notifications\Messages\SlackMessage`.
- Implement the `ShouldQueue` interface to ensure notification API calls are executed in background queues.

### 3. Rich Formatting with Slack Message / Block Kit
Format Slack notifications to look highly professional by using titles, attachments, fields, and custom colors:

```php
<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Slack\BlockKit\Blocks\SectionBlock;
use Illuminate\Notifications\Slack\SlackMessage;
use Illuminate\Notifications\Notification;

class CriticalErrorSlackAlert extends Notification implements ShouldQueue
{
    use Queueable;

    public int $tries = 3;
    public int $backoff = 60;

    public function __construct(
        protected string $message,
        protected string $fileName,
        protected int $line
    ) {}

    public function via(mixed $notifiable): array
    {
        return ['slack'];
    }

    public function toSlack(mixed $notifiable): SlackMessage
    {
        return (new SlackMessage)
            ->headerBlock('🚨 Critical AI Process Failure Detected!')
            ->sectionBlock(function (SectionBlock $block) {
                $block->text("*Error Message:* {$this->message}");
            })
            ->sectionBlock(function (SectionBlock $block) {
                $block->field("*File Location:*\n{$this->fileName} (Line {$this->line})")->markdown();
                $block->field('*Environment:*\n' . config('app.env'))->markdown();
            });
    }
}
```

### 4. Handling Failures and Resiliency
- Always queue Slack notifications. Third-party Slack API requests can add latency or temporarily fail due to rate limits or downtime.
- Set class properties for rate limiting and connection retry policies:
  - `public int $tries = 3;` — Maximum execution attempts.
  - `public int $backoff = 60;` — Time in seconds to wait before retrying a failed attempt.

### 5. Testing and Mocking (Pest v3)
Use Laravel's native `Notification` facade fakes in test suites to assert that Slack notifications are routed correctly without making actual HTTP requests.

```php
<?php

use App\Notifications\CriticalErrorSlackAlert;
use Illuminate\Support\Facades\Notification;
use Illuminate\Notifications\AnonymousNotifiable;
use Illuminate\Notifications\Slack\SlackMessage;

it('sends a critical slack notification on process failure', function () {
    Notification::fake();

    // Trigger logic that throws/dispatches error notification
    $errorMessage = 'API key expired';
    $file = 'AiAgent.php';
    $line = 42;

    // Simulate sending notification to a custom routing channel
    Notification::route('slack', config('services.slack.notifications.channel'))
        ->notify(new CriticalErrorSlackAlert($errorMessage, $file, $line));

    Notification::assertSentTo(
        new AnonymousNotifiable,
        CriticalErrorSlackAlert::class,
        function ($notification, $channels) use ($errorMessage) {
            return in_array('slack', $channels) && $notification->toSlack(null) instanceof SlackMessage;
        }
    );
});
```

## Constraints
- **No Hardcoded Values:** Never write webhook URLs, slack tokens, or default channel names directly inside notification classes. Always load them via `config('services.slack...')`.
- **Always Queue:** Never send Slack notifications synchronously on customer-facing controller requests. Always implement `ShouldQueue`.
- **Keep Payloads Clean:** Do not dump massive raw trace exception arrays directly into the Slack message text. Format only key error summaries into structured attachment fields.
- **Use Native Testing Fakes:** Do not use Guzzle or custom HTTP clients to send slack messages directly, and do not write custom HTTP mock hooks in tests when `Notification::fake()` exists.
