---
name: laravel-solar-irradiance-cresesb-nasa-integration
description: Use when integrating with solar irradiance APIs (NASA POWER, CRESESB), fetching solar radiation indices by coordinates or ZIP code, or implementing photovoltaic energy generation estimation algorithms in Laravel. Triggers on requests involving solar radiation data, solar generation forecasting, or climatological data integrations.
---

# Laravel Solar Irradiance CRESESB & NASA Integration

## Goal
Standardize the integration of solar irradiance APIs (NASA POWER and CRESESB) and the implementation of solar energy generation calculations in Laravel, ensuring precise calculations, clean service architecture, and optimized Redis caching.

## Instructions

1. **Connector Setup (NASA POWER & CRESESB)**:
   - Implement HTTP integration connectors under `app/Http/Integrations/SolarIrradiance/` (e.g., `NasaPowerConnector.php`, `CresesbConnector.php`).
   - Extend the native `BaseApi` connector class, specifying endpoint mapping in `EndPoints.json` and inputs validation in `Attributes.json` according to `laravel-base-api-integration-patterns`.
   - NASA POWER endpoint configuration should query climatology data using latitude and longitude parameters.
   - CRESESB integration should parse/fetch solar radiation data using the coordinates or postal code.

2. **Data Modeling (Spatie Laravel Data)**:
   - Define a DTO class `App\Data\SolarIrradianceData` extending `Spatie\LaravelData\Data` to represent monthly daily average solar irradiation values ($kWh/m²/day$) from January to December:
     ```php
     namespace App\Data;

     use Spatie\LaravelData\Data;

     class SolarIrradianceData extends Data
     {
         public function __construct(
             public float $january,
             public float $february,
             public float $march,
             public float $april,
             public float $may,
             public float $june,
             public float $july,
             public float $august,
             public float $september,
             public float $october,
             public float $november,
             public float $december,
         ) {}
     }
     ```

3. **Geographic Cache Strategy (Redis)**:
   - To avoid redundant external API calls and rate-limiting issues, implement caching on top of coordinate searches.
   - Round latitude and longitude to 2 decimal places before generating the cache key:
     ```php
     $roundedLat = round($latitude, 2);
     $roundedLon = round($longitude, 2);
     $cacheKey = "solar_irradiance:{$roundedLat}:{$roundedLon}";
     ```
   - Store responses in Redis using Laravel's Cache facade with a long TTL (e.g., 30 days), since monthly average solar climatology changes very slowly.

4. **Solar Calculation Service**:
   - Centralize calculations in `App\Services\SolarCalculationService` using dependency injection:
     ```php
     namespace App\Services;

     use App\Data\SolarIrradianceData;

     class SolarCalculationService
     {
         /**
          * Calculates estimated energy generation for a specific month.
          *
          * Formula: E = Pwp * Hday * days * PR
          */
         public function calculateMonthlyGeneration(
             float $installedCapacityKw,
             float $monthlyDailyAverageIrradiance,
             int $daysInMonth,
             float $performanceRatio = 0.80
         ): float {
             return $installedCapacityKw * $monthlyDailyAverageIrradiance * $daysInMonth * $performanceRatio;
         }
     }
     ```
   - Standardize the `performanceRatio` ($PR$) default value to $0.80$ (representing $20\%$ system losses, including inverter efficiency, temperature coefficients, wiring, and dirt/soiling).

## Constraints
- **Do NOT** make direct HTTP calls using raw `Illuminate\Support\Facades\Http` clients. All integrations must inherit from `BaseApi`.
- **Do NOT** use unrounded coordinates in cache keys. Raw coordinates lead to cache misses and resource exhaustion.
- **Do NOT** hardcode calculation variables such as Performance Ratio ($PR$) globally without letting the user or system configuration override them dynamically.
- **Do NOT** put database transactions or persistence logic inside integration connectors.
