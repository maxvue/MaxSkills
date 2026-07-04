---
name: laravel-solar-inverter-telemetry-monitoring-best-practices
description: Use when creating, reviewing, or debugging solar inverter telemetry integration and real-time generation monitoring in Laravel. Triggers on files modifying inverter API clients (Growatt, Fronius, Sungrow), telemetry jobs, telemetry data persistence, or alert triggers for low generation or inverter communication loss.
---

# Solar Inverter Telemetry Monitoring Best Practices in Laravel

## Goal
Establish a resilient, high-performance architecture for integrating third-party solar inverter APIs (Growatt, Fronius, Sungrow), fetching telemetry data, caching real-time metrics using Redis, persisting telemetry history, and triggering alerts for anomalies (e.g., low generation or offline inverters) within the Engeapp ecosystem.

## Instructions
1. **Inverter Client Abstraction**:
   - Define a PHP Interface `App\Services\Telemetry\Contracts\InverterClientInterface` with methods such as `fetchRealTimeMetrics(StationInverter $inverter): InverterTelemetryDto` and `checkConnection(StationInverter $inverter): bool`.
   - Implement concrete clients (`GrowattClient`, `FroniusClient`, `SungrowClient`) extending a base class or injecting a resilient HTTP Client.
   - Use Laravel's HTTP Client (`Http::withHeaders()->retry()->timeout()`) to handle API instability, rate limiting, and network failures.

2. **Telemetry Data Transfer Object (DTO)**:
   - Use strict DTOs to encapsulate inverter state data (active power, daily energy, total energy, status, raw payload) before persistence or caching.

3. **Scheduled Telemetry Collection Jobs**:
   - Create asynchronous jobs (e.g., `FetchInverterTelemetryJob`) implementing `ShouldQueue`.
   - Schedule jobs in `routes/console.php` or `app/Console/Kernel.php` to distribute load. Avoid concurrent mass API requests by spacing out jobs or using queue rate limiters (e.g., `Redis::throttle`).
   - Use queue tags and separate queues (e.g., `telemetry`) to ensure telemetry tasks do not bottleneck transactional user workflows.

4. **Real-Time Cache (Redis)**:
   - Store the latest telemetry read in Redis (`Cache::tags(['inverters'])->put(...)`) with a short TTL (e.g., 5-15 minutes) for instant dashboard retrieval without hitting the database.
   - Provide fallback logic to database queries if the cache is empty.

5. **Telemetry Persistence Pattern**:
   - Save historical telemetry data in a structured database table (e.g., `station_inverter_telemetries` with fields: `station_inverter_id`, `active_power_kw`, `daily_energy_kwh`, `total_energy_kwh`, `recorded_at`, `status`).
   - Ensure indexing on foreign keys and timestamps for fast time-series analytical queries.

6. **Anomaly Alerts and Notifications**:
   - Implement alert triggers using Laravel Notifications.
   - Send alerts (e.g., Slack, Email, or WhatsApp SMS) if:
     - The active generation is below expected thresholds (e.g., < 10% during peak sun hours 09:00 - 15:00).
     - The inverter has been offline/communication loss for more than 4 consecutive hours.
   - Guard alerts using cache flags to prevent spamming the client (e.g., allow only one notification per 24 hours per inverter anomaly).

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- Do NOT make direct raw HTTP calls inside Controllers or Models; always route them through abstract client implementations.
- Do NOT perform intensive data synchronization synchronously within web request cycles.
- Do NOT store large telemetry payloads long-term in the main database without compression or structural normalization.
- Avoid using DB raw queries for time-series queries without appropriate scopes and indexes.
