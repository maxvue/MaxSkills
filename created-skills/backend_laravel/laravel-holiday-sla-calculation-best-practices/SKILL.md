---
name: laravel-holiday-sla-calculation-best-practices
description: Use when designing, implementing, or debugging SLA tracking, business days calculation, holiday management, or date-based deadline services in the Laravel backend of the Engeapp ecosystem.
---

# Laravel Holiday & SLA Calculation Best Practices

## Goal
Establish solid guidelines and consistent code patterns for calculating business days, SLA deadlines, and managing national, state, and local holidays in the Laravel backend of the Engeapp ecosystem, especially for solar project homologations.

## Instructions

### 1. Using Global Date Helpers (DatesHelper)
Always prefer using the global helper functions defined in `DatesHelper.php` instead of reimplementing date calculation logic:
- **`addBusinessDays($data, $dias) : DateTime`**: Adds a specific number of business days to a starting date, automatically skipping weekends and holidays.
- **`isHoliday($date) : bool`**: Checks if a given date is a holiday (national or state-specific).
- **`isBusinessHours($date, $after = 8, $before = 17, $interval = ['start' => 12, 'end' => 14]) : bool`**: Checks if the given date and time falls within business hours (Monday to Friday, excluding lunch interval and holidays).
- **`businessMinutesBetween($start, $end, $dayStart = '08:30', $dayEnd = '17:30', ...)`**: Calculates the exact number of business minutes between two timestamps, applying the timezone `America/Sao_Paulo`, skipping weekends, holidays, and lunch breaks. Useful for auditing exact API and process response times.

### 2. Holiday Verification & Synchronization (`HolidayService`)
Understand how holidays are fetched, cached, and synchronized:
- `HolidayService::isHoliday(Carbon $date)` checks if the date exists in the database table mapped by `App\Models\Address\Holiday`.
- If no records exist for the year of the query, it triggers an external API call to Invertexto (`https://api.invertexto.com/v1/holidays/{year}`) filtered by the configured default state (default: `'go'` for Goiás).
- The API response is permanently cached using `Cache::rememberForever` and persisted via `upsert` in the DB.
- Any manual validation or seeding should delegate to `HolidayService`.

### 3. Implementing SLA Rules for Homologation
Solar project homologations with electricity concessionaires require precise SLA tracking:
- When calculating legal response deadlines (e.g., Access Opinion / *Parecer de Acesso* which usually takes 15 business days), calculate the deadline using:
  ```php
  $deadline = addBusinessDays($submittalDate, 15);
  ```
- To identify late tasks in database queries, calculate the boundary date in business days using Carbon in PHP and compare it to the current time, rather than attempting complex raw SQL holiday logic.

### 4. Testing SLA Calculations
- Write unit and feature tests using Pest.
- Always freeze/mock the current system time in tests using `Carbon::setTestNow('2026-06-20 10:00:00')` to verify boundary conditions (e.g., submissions on Friday evenings, weekends, holidays, or year-end transitions).
- Verify that `addBusinessDays` shifts the date correctly across multiple consecutive holidays (e.g., Carnival or Christmas/New Year).

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **DO NOT** write custom loops (`while`) to skip weekends or calculate business days directly in Controllers or Services. Use `addBusinessDays`.
- **DO NOT** query the Invertexto API directly from custom services or commands. All holiday fetches must go through `HolidayService`.
- **DO NOT** write holidays directly to the database without updating the cache or bypassing `HolidayService::isHoliday()` logic.
- **DO NOT** use timezones other than `'America/Sao_Paulo'` when calculating business minutes or business hours.
- **DO NOT** use corrido days (calendar days) for deadlines legally defined as business days (*dias úteis*).
