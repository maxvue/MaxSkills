---
name: laravel-engeapp-project-homologation-best-practices
description: Use when managing solar project homologation flows, tracking concessionaire submittals, managing concessionaire rules/requirements, or tracking protocol statuses for solar integration projects in the Engeapp ecosystem.
---

# Laravel Engeapp Project Homologation Best Practices

## Goal
Establish standard guidelines for managing solar photovoltaic project homologation flows with energy concessionaires within the Engeapp ecosystem, ensuring compliance with local subsidiary technical regulations, correct tracking of protocols, and validation of mandatory documentation.

## Instructions

### 1. Concessionaire Technical Regulations Validation
When dealing with electrical design validations and project approvals:
- Always reference the `ConcessionaireSubsidiaryRegulation` model to fetch the allowed breaker and conductor capacities based on the installation phases (monophase, biphase, triphase) and line voltages (127V, 220V).
- Validate calculations before dispatching submittals to prevent concessionaire rejection. The parameters are stored in `concessionaires_subsidiaries_regulations` and related `data` tables.
- Use explicit checks using the dynamic attributes of the model, such as `$regulation->mono_127`, `$regulation->mono_220`, `$regulation->bi_127`, etc.

### 2. Homologation Protocol Lifecycle & Audit
- All submittals and interactions with the utility company must generate a `Protocol` record.
- Implement the `HasProtocol` trait on models that need direct association with utility protocols (e.g., `Project`, `PlannerCard`).
- Every status transition (e.g., "Submitted", "Under Analysis", "Pending Corrections", "Approved") must be tracked. Updates to a protocol must automatically sync between the project and the planner card via `HasProtocol::setProtocol()`.
- Use queue workers or scheduler tasks to monitor protocol expiration dates (`expires_at`) and generate alerts for impending utility deadlines.

### 3. Homologation Business Logic Decoupling
- Do not place validation or database persistence logic inside controllers.
- Implement all homologation-specific actions inside a dedicated `HomologationService`.
- The service should orchestrate:
  1. Validating technical inputs against the selected `ConcessionaireSubsidiaryRegulation`.
  2. Verifying the presence of required documents (e.g., Power of Attorney via `ProjectPowerOfAttorneyDocument`, Single Line Diagrams, Descriptive Memorials).
  3. Generating and assigning a new `Protocol` to the project and planner card.
  4. Triggering notifications to the client, designer, or solar company based on checkboxes (`notify_client`, `notify_designer`, `notify_solar_company`).

### 4. Vue 3 Frontend Validation and UI
- Utilize components from the `MaxComponentsUi` library for form fields, upload zones, and status indicators.
- Leverage composables and helper functions from `MaxUse` to handle reactive validations, date formatting, and state management.
- Ensure that document upload states are dynamically updated and reflect the utility's requirements.

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **Do not bypass technical regulations:** Never allow a project to proceed to submittal if it violates the limits specified in the active `ConcessionaireSubsidiaryRegulation`.
- **Do not write direct DB queries in controllers:** All query modifications or updates to homologation processes must go through the service layer (`HomologationService`).
- **Do not bypass notifications logic:** Ensure that protocol status changes respect the notification flags (`notify_client`, `notify_designer`, `notify_solar_company`) and delegate the notification delivery to asynchronous Jobs to prevent blocking user requests.
