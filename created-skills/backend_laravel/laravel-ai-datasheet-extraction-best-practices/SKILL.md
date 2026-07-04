---
name: laravel-ai-datasheet-extraction-best-practices
description: >-
  Use when creating, modifying, reviewing, or debugging technical data extraction workflows from solar inverter and module datasheets (PDFs) using AgentDatasheetReader, defining output schemas, extracting electrical/dimensional specifications, handling OCR failures, or validating structured JSON results.
---

# Laravel AI Datasheet Extraction Best Practices

## Goal

Provide structured guidelines and consistent patterns for technical data extraction, validation, and normalization from solar inverter and photovoltaic module datasheet PDF files using the `AgentDatasheetReader` in the Laravel backend of Engeapp.

## Instructions

### 1. Data Source and Grounding Rules
- **Grounding**: Extract all specifications exclusively from the provided PDF file (datasheet/manual). Do not look up missing info online or hallucinate values.
- **Fallback to Zero**: If a technical field is not present, identifiable, or applicable to a specific model in the PDF, fallback to `0` (zero) for numeric fields, and `false` for boolean fields. Never leave them null or empty.

### 2. Normalization of Units
- **Strict Numeric Outputs**: All electrical and dimensional fields (voltages, currents, dimensions, weights, efficiency, etc.) must return raw numbers (integers or floats).
- **Remove Text Units**: Strip all text units (e.g., "W", "V", "A", "mm", "kg", "%", "°C", "years", "anos") from the values.
- **Example**:
  - Input: `550W` -> Output: `550`
  - Input: `22.2 A` -> Output: `22.2`
  - Input: `21.5%` -> Output: `21.5`
  - Input: `380mm` -> Output: `380`

### 3. Multi-Model and Shared Data Extraction
- **Model Isolation**: Datasheets often contain tables with multiple models. Ensure that data is mapped carefully to the correct model.
- **Merged Columns/Cells**: If a table has merged columns (e.g., a single value for AC Voltage shared by 4 models), copy/propagate that value to all corresponding models.
- **Unambiguous Mapping**: Pay extra attention to column alignment to prevent values of one model from leaking into another.

### 4. OCR & Parsing Failures
- **Non-Searchable PDFs**: Perform OCR (Optical Character Recognition) on scanned or image-only PDFs before technical extraction.
- **Synonyms Handling**: Treat terminology synonyms correctly:
  - "MPP Trackers", "MPP", and "MPPT" are equivalent.
  - "DADOS FV", "FV", "DADOS CC", "DADOS DE INPUT", "DADOS DE ENTRADA", and "DADOS DE ENTRADA CC" (and English equivalents like "DC Data", "Input Data") are equivalent.
- **Inverter CA Output ranges**: Often voltage limits are bundled with the nominal voltage (e.g., `127/220V (188.6-237.7V)`). Correctly split these into:
  - Nominal: `220` (or `127`)
  - Min: `188.6`
  - Max: `237.7`

### 5. Schema Definition using `JsonSchema`
All schema definitions in `AgentDatasheetReader::schema()` must define strict types with description annotations.

#### Brand Schema (`brand`)
An object containing:
- `name`: Common manufacturer name, typically one word (e.g., "Jinko", "Deye").
- `alternative_name`: Standard/known brand name (e.g., "Jinko Solar").
- `company_name`: Official corporate entity name (e.g., "Jinko Solar Holding Co., Ltd.").
- `address`: Manufacturer's physical address.
- `country`: Country of origin (e.g., "China", "Brasil").
- `about_en`: Description in English.
- `about_br`: Description in Brazilian Portuguese.
- `phone_number`: Phone number.
- `web_site`: Official website.
- `email`: Contact email.

#### Inverter Schema (`inverters`)
An array of objects representing inverter models, containing:
- `brand`: Brand object.
- `model`: Model identifier (e.g., "X1000").
- `grid`: Connection type ("On-Grid", "Off-Grid", "Hybrid").
- `size_type`: "Micro" (microinverters) or "String" (conventional).
- `inmetro`: Inmetro certificate number (e.g., "035820/2025").
- `nominal_power`: Nominal AC power in W.
- `maximum_power`: Max DC input power in W.
- `phases`: Number of phases (e.g., 1, 3).
- `voltage`: Nominal AC voltage in V.
- `ac_current`: Nominal AC current in A.
- `strings`: Array of numbers (inputs per MPPT).
- `max_in_group`: Max inverters per AC trunk cable (Micro only).
- `max_in_line`: Max inverters per AC circuit (Micro only).
- `min_voltage_ca`: Min AC output voltage in V.
- `max_voltage_ca`: Max AC output voltage in V.
- `mppts`: Number of MPPTs.
- `inputs_per_mppt`: Inputs per MPPT.
- `total_inputs`: Total DC inputs.
- `v_start`: Startup voltage in V.
- `max_vcc`: Max DC input voltage in V.
- `min_vcc`: Min DC input voltage in V.
- `efficiency_max`: Maximum efficiency percentage (e.g., 98.3).
- `range_vcc`: Object with `min` and `max` operating DC voltages.
- `max_icc`: Max DC input current per MPPT in A.
- `max_icc_sc`: Max DC short-circuit current per MPPT in A.
- `module_per_mppt`: Modules per MPPT (Micro only).
- `warranty_product`: Product warranty in years.
- `descriptive_summary`: Short plain-language description (up to 200 words).

#### Module Schema (`modules`)
An array of objects representing PV module models, containing:
- `brand`: Brand object.
- `model`: Model name.
- `nominal_power`: Nominal power in W.
- `bifacial`: Boolean.
- `n_type`: Boolean (N-Type technology).
- `half_cell`: Boolean (half-cell technology).
- `voc`: Open circuit voltage in V.
- `isc`: Short-circuit current in A.
- `vmpp`: Voltage at MPP in V.
- `impp`: Current at MPP in A.
- `height`: Height in mm.
- `width`: Width in mm.
- `weight`: Weight in kg.
- `efficiency`: Module efficiency percentage (e.g., 21.5).
- `temperature_coefficient`: Pmax temperature coefficient in %/°C.
- `maximum_system_voltage`: Max system voltage in V (e.g., 1500).
- `fuse_rated_current`: Series fuse rating in A.
- `warranty_linear_power`: Linear power warranty in years.
- `warranty_product`: Product warranty in years.
- `warranty_linear_power_percent`: Power percentage guaranteed at year limit.
- `annual_degradation`: Annual degradation percentage.
- `wire_length`: Cable length in mm.
- `descriptive_summary`: Short plain-language description (up to 200 words).

### 6. Testing Best Practices with Pest
- Always write tests inside `tests/Feature/` or `tests/Unit/` using Pest to validate extraction logic.
- Mock the Gemini LLM API calls using Laravel AI SDK testing capabilities (e.g., `Ai::fake()`).
- Verify:
  - Exact parsing of fields without units.
  - Proper fallback to `0` when fields are missing from the mock raw response.
  - Correct model separation and brand metadata mapping.

## Constraints

- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **NEVER** return units (V, A, W, mm, kg, %, etc.) in numeric schema fields.
- **NEVER** default missing numeric fields to `null` or empty strings; always use `0`.
- **NEVER** search the internet or use external knowledge for missing technical details. Ground all extractions in the provided PDF.
- **NEVER** group distinct models into a single output object; each model must be a separate entry in the output array.
- **NEVER** use double-quoted HereDoc prompts (`<<<INSTRUCTIONS`) in the `AgentDatasheetReader`. Always use single-quoted HereDocs.
