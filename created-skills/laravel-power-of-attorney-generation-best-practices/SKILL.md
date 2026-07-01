---
name: laravel-power-of-attorney-generation-best-practices
description: Use when creating, reviewing, or debugging Power of Attorney (procurações) generation logic, formatting client or partner addresses for legal documents, or generating PDFs for solar energy project concessionaires in the backend.
---

# laravel-power-of-attorney-generation-best-practices

## Goal
Provide solid guidelines and structured patterns for creating, formatting, and validating Power of Attorney (procurações) generation logic and formatting client or partner addresses for legal documents in the Laravel backend.

## Instructions
1. **Client Type Mapping (PF vs PJ)**:
   - Always check the client entity type (`entity` field: `PF` or `PJ`).
   - For `PJ` (Pessoa Jurídica), include company details (CNPJ, address), legal representative name (`partner_name`), representative document (`partner_document`), and representative residence address (`partner_location`).
   - For `PF` (Pessoa Física), include individual details (CPF, gender-aware pronouns, residence address).

2. **Address Formatting**:
   - Use the `Location` and `Address` relations to compile clean address strings.
   - Format standard addresses as: `[Street], [Number], [Complement (if exists)], [Neighborhood], município de [City], CEP: [CEP]`.
   - Implement safe fallbacks (e.g., using a content helper or 'S/N' for missing house/building numbers).

3. **Status Management**:
   - Set the initial status of the `ProjectPowerOfAttorneyDocument` to `editing` on creation.
   - Support standard status transitions in the signature workflow: `editing`, `sent`, `delivered`, `opened`, `viewed`, `signed`.

4. **PDF Generation and Signature Integration**:
   - Use `Barryvdh\DomPDF\Facade\Pdf` to render HTML templates.
   - Support two PDF templates: `blank` (for physical/manual signature) and `digital` (with digital signature blocks using legal frameworks like Law 14.063/2020 and validation links).
   - Format dates dynamically using localized, translated datetime format (e.g. `now()->translatedFormat(...)` in Portuguese).

## Constraints
- Do NOT hardcode regional concessionaire details or designer data; always resolve them through relations (e.g., `$project->concessionaire`, `$project->designer`).
- Do NOT generate HTML with raw, unformatted CPFs or CNPJs; always apply formatting/sanitization helper functions (e.g., `formatCpfCnpj`).
- Do NOT proceed with PDF generation if crucial client/location fields are null; use validation checks to ensure clean data beforehand.
