---
name: laravel-whatsapp-cloud-api-integration
description: Use when creating, reviewing, or debugging WhatsApp Cloud API integrations, handling WhatsApp webhooks, sending templates or interactive messages, processing incoming messages, and managing conversation states.
---

# Goal
Provide strict guidelines, architectural patterns, and code conventions for implementing, refactoring, and debugging WhatsApp Cloud API integrations within the Laravel ecosystem of Engeapp. This ensures secure webhook validation, non-blocking asynchronous message processing, robust API rate-limit management, error resilience, and standardized database storage.

# Instructions

## 1. Webhook Verification & Processing
* **Security Validation:** Verify the incoming request signature using the `X-Hub-Signature-256` header and the App Secret. Validate the Hub Verification Token during subscription confirmation.
* **Immediate Response:** The controller receiving webhook requests MUST return an immediate HTTP 200 OK response. Avoid performing heavy database operations or external API calls synchronously inside this controller to prevent Meta webhook timeout flags.
* **Asynchronous Offloading:** Dispatch the raw webhook payload directly to an asynchronous job (e.g., `WebhookWhatsappJobExecuteJob`) on the `whatsapp` queue:
  ```php
  WebhookWhatsappJobExecuteJob::dispatch($data)->onQueue('whatsapp');
  ```

## 2. Asynchronous Job & Queue Configurations
* **Dedicated Queue:** Always execute WhatsApp jobs on the `whatsapp` queue.
* **Retry Strategy & Backoff:** Setup retries and backoff limits to handle temporary API errors and rate limiting:
  ```php
  public int $tries = 5;
  public array $backoff = [30, 60, 120, 180, 300];
  ```
* **Idempotency Check:** Prevent duplicate message delivery and processing by checking if a message with the given `message_meta_id` already exists at the start of the job handler:
  ```php
  if ($message->message_meta_id) {
      Log::channel('whatsapp')->info('Message already sent, ignoring retry', ['message_id' => $id]);
      return;
  }
  ```
* **Permanent Failures:** Catch specific exceptions representing unrecoverable states (e.g., a phone number that is not WhatsApp-enabled). In such cases, fail the job immediately to avoid consuming unnecessary attempts:
  ```php
  catch (\RuntimeException $e) {
      Log::channel('whatsapp')->error('Permanent failure sending message: ' . $e->getMessage());
      $this->fail($e);
      return;
  }
  ```
* **Retry Middleware:** Apply the `NotifyRetryingWhatsappMiddleware` to jobs so that real-time notifications can be sent to the front-end via WebSockets when attempts fail but retries are scheduled.

## 3. Data Modeling & Helper Standards
* **Contact & Message Association:** Store incoming and outgoing chat messages in the `SupportMessage` model, and link them to a `SupportContact` instance.
* **Parsing Structure:** Recursively loop through `entry` -> `changes` -> `value` -> `messages`/`statuses` arrays from the Meta webhook payload to parse message contents or delivery status.
* **Phone Standardization:** Always utilize the `PhoneClass` helpers to normalize phone numbers and resolve Meta-compatible IDs:
  ```php
  $phone_number = PhoneClass::getInternationalPhoneNumber($raw_phone);
  $whatsapp_id = PhoneClass::getWhatsappMetaId($phone_number);
  ```
* **Message Schema Fields:** Ensure messages persist key metadata:
  - `message_meta_id`: The ID returned by Meta or incoming from the webhook.
  - `message_type`: E.g., `text`, `template`, `image`, `document`, `audio`, `payment`.
  - `direction`: E.g., `receive` or `send`.
  - `status`: E.g., `sent`, `delivered`, `read`, `failed`, `received`.
  - `meta_payload`: The full JSON payload for tracking and debugging.

## 4. Resilience, Logging & HTTP Client Usage
* **Dedicated Log Channel:** Direct all integration logs (info, warn, error) to the `whatsapp` channel:
  ```php
  Log::channel('whatsapp')->error('Integration error detail', ['context' => $data]);
  ```
* **HTTP Client Conventions:** Utilize Laravel's `Http` client wrapper. Manage authorization tokens through configuration files rather than hardcoded variables:
  ```php
  Http::withHeaders([
      'Authorization' => 'Bearer ' . config('api.whatsapp_token'),
  ])->post($url, $data);
  ```

# Constraints
* **DO NOT** perform long-running business logic, notifications, or database transactions directly inside the webhook HTTP request context. Always push to the queue.
* **DO NOT** try to resend messages that already contain a valid `message_meta_id` to avoid sending duplicates to users.
* **DO NOT** log raw auth tokens or client secrets. Ensure they are read from `config()` files and securely stored in `.env`.
* **DO NOT** use default application log files (`laravel.log`) for WhatsApp integrations. Always use the `whatsapp` log channel.
