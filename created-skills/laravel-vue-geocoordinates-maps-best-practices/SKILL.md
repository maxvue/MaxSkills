---
name: laravel-vue-geocoordinates-maps-best-practices
description: Use when working with geographical coordinates (latitude, longitude, UTM, DMS), integrating maps in Vue using vue3-google-map, converting coordinate systems (proj4, utm-latlng), validating coordinate DTOs (CoordinateUTMData, LocationCoordinateData) in Laravel, or troubleshooting mapping/location services.
---

# Laravel and Vue Geographical Coordinates & Maps Best Practices

## Goal
Provide guidelines, code patterns, and validation rules for handling geographical coordinates (Decimal, UTM, DMS) in the Laravel backend and integrating them with interactive maps using `vue3-google-map` and coordinate transformations via `proj4` in the Vue 3 frontend of the Engeapp ecosystem.

## Instructions

### 1. Laravel Backend: Models & DTOs
When storing and validating coordinates:
- **Database Storage**: Coordinates are stored as JSON structures mapped to Eloquent attributes in `LocationCoordinate`. Use Custom Attributes (Mutators/Accessors) via `Illuminate\Database\Eloquent\Casts\Attribute` to marshal JSON fields to PHP objects.
- **DTO validation**: Use Spatie Laravel Data objects for payload validation:
  - [CoordinateDecimalData](file:///home/johnattas/GitHub/engeapp/app/Data/Location/CoordinateDecimalData.php) contains `latitude` (float) and `longitude` (float).
  - [CoordinateUTMData](file:///home/johnattas/GitHub/engeapp/app/Data/Location/CoordinateUTMData.php) contains `zone` (int), `letter_zone` (string), `easting` (float), and `northing` (float).
  - [CoordinateDMSData](file:///home/johnattas/GitHub/engeapp/app/Data/Location/CoordinateDMSData.php) contains `latitude` and `longitude` mapped to [DmsValueData](file:///home/johnattas/GitHub/engeapp/app/Data/Location/DmsValueData.php).
- **DMS Orientations (Brazilian Standard)**:
  - Latitude: `N` (North) or `S` (South).
  - Longitude: `L` (East - Leste) or `O` (West - Oeste). **Note that `L` and `O` are used instead of `E` and `W`** to align with Brazilian standard terminology defined in [CoordinateOrientationEnum](file:///home/johnattas/GitHub/engeapp/app/Enums/CoordinateOrientationEnum.php).

#### Backend Conversion Rules
To convert DMS (Degrees, Minutes, Seconds) to Decimal Degrees:
```php
public static function dmsToDecimal(int $degrees, int $minutes, float $seconds, string $orientation): float
{
    $decimal = $degrees + ($minutes / 60.0) + ($seconds / 3600.0);
    if ($orientation === 'S' || $orientation === 'O') {
        $decimal = -$decimal;
    }
    return $decimal;
}
```

### 2. Vue 3 Frontend: Map Integration & Reactivity
When building/editing map components:
- **Component Standard**: Always use Composition API (`<script setup lang="ts">`), SCSS (`<style lang="scss">`), and order blocks: `<template>`, `<script>`, `<style>`.
- **Map Library**: Use `vue3-google-map`. Load it asynchronously or conditionally render using a mount flag (`isMounted`) to prevent SSR or initialization errors.
- **GoogleMap component**: Reference [MaxMaps.vue](file:///home/johnattas/GitHub/MaxComponentsUi/src/components/MaxMaps.vue). All attributes in the template should be on a single line.
- **Reactivity and Marker Dragging**:
  - Keep coordinates reactive in the component. Watch coordinate changes and update the map center and marker position.
  - Bind `@dragend` event on `AdvancedMarker` to capture the new coordinates and update the reactive state:
    ```ts
    function onDrag(event: any) {
        coordinates.value.latitude = Number(event.latLng.lat().toFixed(7));
        coordinates.value.longitude = Number(event.latLng.lng().toFixed(7));
    }
    ```

### 3. Coordinate Conversions in Vue 3 via Proj4
To convert UTM coordinates (highly used in Brazilian solar plant designs) to Decimal (Latitude/Longitude) on the frontend:
- **Proj4 Setup**: Define coordinate reference systems (CRS) using `proj4.defs`.
- **Common Brazilian Projections**:
  - **SIRGAS 2000 / UTM Zone 23S** (EPSG:31983): `+proj=utm +zone=23 +south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs`
  - **WGS 84 / UTM Zone 23S** (EPSG:32723): `+proj=utm +zone=23 +south +datum=WGS84 +units=m +no_defs`
- **Conversion Example**:
  ```typescript
  import proj4 from 'proj4';

  // Define SIRGAS 2000 / UTM Zone 23S and WGS84 (default lat/long)
  proj4.defs("EPSG:31983", "+proj=utm +zone=23 +south +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs");

  // Convert UTM (Easting, Northing) to Decimal (Longitude, Latitude)
  // Note: proj4 returns [longitude, latitude]
  const [lng, lat] = proj4("EPSG:31983", "WGS84", [easting, northing]);
  ```

## Constraints
- **Do NOT** use `E` (East) or `W` (West) orientations in Brazilian DMS formatting. Use `L` (Leste) and `O` (Oeste).
- **Do NOT** duplicate coordinate validation rules in controllers. Always delegate coordinate validation to the Spatie Data classes (`CoordinateUTMData`, `CoordinateDecimalData`, `CoordinateDMSData`).
- **Do NOT** break Vue component template attributes into multiple lines. Keep them in a single line.
- **Do NOT** use Options API in any map/coordinate components. Always use Composition API with TypeScript.
- **Do NOT** write inline styles for Map heights or widths. Use SCSS styles or tailwind classes (if requested).
