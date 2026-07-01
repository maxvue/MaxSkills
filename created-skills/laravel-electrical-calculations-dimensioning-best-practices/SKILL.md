---
name: laravel-electrical-calculations-dimensioning-best-practices
description: Use when performing or validating electrical sizing, calculating circuit breakers, sizing cables, verifying voltage drop, or resolving inverter and solar module specifications. Triggers on calls to getWireSize, getCircuitBrake, getInverter, or when handling NBR 5410 electrical standards.
---

# Goal
Ensure standard and accurate execution of electrical sizing, circuit breaker selection, cable dimensioning, and inverter lookup within Engeapp by leveraging global helpers and database tables instead of manual math or hardcoded values.

# Instructions
1. **Sizing Cables (Wire Sizing):**
   - Always use the `getWireSize($currents, $options)` global helper.
   - Do NOT implement custom copper/aluminum resistance formula or voltage drop math.
   - Properly map the `$options` parameter:
     - `material`: Pass `'copper'` or `'aluminum'`.
     - `length`: Cable distance in meters.
     - `voltage`: Operating voltage (e.g., 220, 380, 127).
     - `phases`: Phase count (1, 2, or 3).
     - `type_line`: Installation method from NBR 5410 (e.g., `'B1'`, `'B2'`).
     - `cables`: Number of loaded conductors.
     - `max_percent`: Acceptable voltage drop percentage (default: 2% for 1-phase, 3% for 3-phase).
   - If validating a pre-selected cable, supply the `wire` or `wire_target` option to simulate its power loss and check compliance via `$result->permitido`.

2. **Selecting Circuit Breakers:**
   - Always use the `getCircuitBrake($currents, $limit_percent = 80)` global helper (or its alias `getCircuitBraker`).
   - The first parameter `$currents` can be a float, string, or array (if array, it selects the maximum current).
   - The `$limit_percent` specifies the maximum load capacity (default is 80%).
   - Rely on this function to match the next available standard commercial breaker rating (e.g., 10A, 13A, 16A, 20A, 25A, 32A, 40A, 50A, 63A, 80A, 100A, 125A).

3. **Inverter Sizing and Lookup:**
   - Use the `getInverter($brand_name, $model, $power)` helper to search and return an `App\Models\Equipment\Inverter` model from the database.
   - Avoid direct database query builders for matching inverter power or model name unless standard helper matching is insufficient.
   - Use `defaultAmountCircuitsMicroInverters($amount_micro_inverters, $max_inverter_group)` to distribute micro-inverters evenly among circuits.

4. **Voltage and Phase conversions:**
   - Use `toPhasePhase($voltage)` and `toPhaseNeutral($voltage)` when converting between line-to-line and line-to-neutral voltages.
   - Use `voltageBetweenPhases($phase1, $phase2, $lag = 120)` to compute the line voltage under a specific phase lag.
   - Map phase strings to numbers using `getPhaseNumberByName($name)` and vice versa using `getPhaseName($number, $abbrev)`.
   - Use `getPoleName($numberPhases)` to determine the matching poles description (e.g. Bipolar, Tripolar).

# Examples
### Cable sizing calculation:
```php
$result = getWireSize(25.4, [
    'material' => 'copper',
    'length' => 30,
    'voltage' => 220,
    'phases' => 3,
    'type_line' => 'B1',
    'cables' => 3
]);

// $result will contain:
// - wire_size (e.g., 6.0)
// - drop_voltage
// - efficiency
// - loss
```

### Cable compliance simulation:
```php
$result = getWireSize(40, [
    'material' => 'aluminum',
    'length' => 15,
    'voltage' => 220,
    'wire_target' => 10
]);
```

### Finding a commercial breaker:
```php
$breaker = getCircuitBrake([15.5, 24.2, 19.8], 80); // Returns 32
```

# Constraints
- **No Manual Math:** Never hardcode voltage drop constants (0.0172 or 0.0283) or write custom formula loops to find cable section sizes. Always delegate to `getWireSize`.
- **Database Caching:** Do not clear or bypass the `db_abnt_wire` caching mechanisms. The helper handles caching automatically.
- **Strict Typing:** Ensure input currents are converted or cast appropriately before passing them to the helpers. If array or null are possible, let the helper normalize it or handle empty values gracefully (e.g., returning 0 or null).
- **Standards:** All calculations must align with NBR 5410. Do not invent custom rating values for standard commercial breakers.
