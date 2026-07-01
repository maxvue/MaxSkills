---
name: laravel-concessionaires-tariffs-regulation-best-practices
description: Use when creating, modifying, or querying energy concessionaires (concessionárias), subsidiaries, regional units, electrical regulations (ANEEL rules), or tariff data (group A/B, green/blue tax flags, TUSD/TE distribution tariffs) in Laravel. Triggers on calculations involving power distribution costs, energy concessionaire CRUDs, and regulation data validations.
---

# Energy Concessionaires, Tariffs, and Regulation Best Practices

## Goal
Establish clean, consistent, and architecturally sound standards for managing energy concessionaires (distribuidoras), their subsidiaries, local tariffs, and ANEEL (Agência Nacional de Energia Elétrica) regulations in the Laravel backend of Engeapp. This ensures precise financial viability calculations (payback, savings) for solar projects and prevents tax or logic discrepancies.

## Instructions

### 1. Model Structure & Relationships
Keep the hierarchical mapping of energy concessionaires clear:
- **ConcessionaireCompany**: Represents the corporate holding company (e.g., Energisa, Equatorial). Uses ULIDs (`HasUlids`), maps to `concessionaires_company`.
- **ConcessionaireSubsidiary**: Represents regional operating units (e.g., Energisa Sul-Sudeste). Inherits ULIDs, maps to `concessionaires_subsidiaries`. Houses service locations (cities, states), urls, and configuration templates (like signage templates: `placa1`, `placa2`).
- **ConcessionaireSubsidiaryRegulation**: Defines technical standards, connection classes, voltage and phases. Maps to `concessionaires_subsidiaries_regulations`. Includes relationships to files and data limits.
- **ConcessionaireSubsidiaryRegulationData**: Granular parameters (breaker limit, conductor cross-sections, phase-neutral voltage). Order results globally by `circuit_breaker` using boot hooks.

### 2. DTO & Validation Patterns (Spatie Laravel Data)
When validating or transferring tariff configuration payloads, use Spatie Laravel Data DTOs:
- Group tariff structures into distinct categories:
  - **Group A (High Voltage)**: High-voltage consumers. Require fields for peak tariff (ponta), off-peak tariff (fora de ponta), and demand charges (demanda contratada). Ensure TUSD and TE components are separately validated.
  - **Group B (Low Voltage)**: Conventional low-voltage consumers (residential, commercial, rural). Require fields for single rate TUSD, TE, and public lighting taxes (COSIP/CIP).
- Validate Brazilian regulatory fields using strict rules:
  - Phase configurations (`amount_phases`: 1, 2, or 3).
  - Volts values (`voltage_phase_neutral`: typically 127V or 220V).

### 3. Tariff Calculations & Monetary Representation
- **No Float for Money**: All tariff calculations (TUSD, TE, demand costs, tax flags) must avoid raw floating-point operations. Use integer values representing cents (R$ 0.01 = 1) or high-precision decimals (e.g., `BCMath` wrapper) up to 4 or 6 decimal places (tariffs in Brazil are defined with 4-6 decimals, e.g., R$ 0,654321 / kWh).
- **Separate TUSD and TE**: Distribution (TUSD - Tarifa de Uso do Sistema de Distribuição) and Energy (TE - Tarifa de Energia) must be treated as independent components. They have different tax treatments (ICMS, PIS, COFINS) and regulatory compensation rates.
- **Tax Flags (Bandeiras Tarifárias)**: Implement a service to retrieve or apply active ANEEL tax flags (Verde, Amarela, Vermelha Patamar 1, Vermelha Patamar 2) onto the TE component.
- **GD Compensation Rules**: Calculations for Distributed Generation (Geração Distribuída) payback must respect active ANEEL regulations (e.g., Lei 14.300 transition rules, TUSD Fio B charge-backs).

### 4. Separation of Concerns
- **No Calculation Logic in Models**: Eloquent models should only represent the database structure and relationships.
- **Actions / Service Classes**: Place payback calculations, tariff applications, and ANEEL compensation models inside specific service classes (e.g., `App\Services\Financial\PaybackCalculatorService`).

## Constraints
- **NEVER** use raw floats for database columns storing tariffs or monetary totals. Use `decimal(12, 6)` or `integer` representing cents.
- **DO NOT** hardcode TUSD/TE rates inside controllers or services. Always fetch them from the database or DTO config arrays associated with the client's `ConcessionaireSubsidiary`.
- **DO NOT** duplicate calculation logic across controllers. Centralize in Service/Action classes.
- **NEVER** perform raw database operations without transactions when updating multiple concessionaire tariff settings at once.
