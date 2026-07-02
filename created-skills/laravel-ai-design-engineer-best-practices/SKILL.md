---
name: laravel-ai-design-engineer-best-practices
description: >-
  Use when implementing, testing, or refining the AgentDesignEngineer or when working with AI-based solar inverter and module allocation, MPPT configuration, sizing calculations, or validating solar system designs. Triggers on modifications to AgentDesignEngineer, design engineering tools, or sizing validation rules.
---

# Laravel AI Design Engineer Best Practices

## Goal

Provide standardized, rigorous guidelines for designing, implementing, and debugging the `AgentDesignEngineer` and its electrical validation/allocation rules within the Engeapp Laravel backend. This skill ensures that AI agents performing electrical sizing and module-to-inverter allocations comply with physical and electrical constraints.

## Instructions

### 1. Agent Mission and Identity

The `AgentDesignEngineer` acts as a Senior Photovoltaic Project Engineer. Its goal is to analyze station data, perform accurate mathematical calculations, and allocate solar modules to inverters safely, efficiently, and in strict compliance with electrical engineering constraints.

### 2. Mandatory Step-by-Step Workflow

All allocation and validation tasks must strictly follow this workflow:

1.  **Coleta (Data Collection):**
    *   Call the `GetStationData` tool to fetch complete specifications for the station, including all inverters, modules, and current connections.
2.  **Planejamento (Planning - CRITICAL):**
    *   Before calling any connection tools, you **must** open a `<planejamento>` XML-like tag.
    *   Write the sizing mathematical calculations inside this tag:
        *   Calculate the Minimum and Maximum Voltage limits (number of modules per string) for each inverter model and module combination.
        *   Calculate the Maximum DC Power capacity (overload limit) of each inverter.
        *   Outline the distribution strategy (which module groups go to which inverters/MPPTs/Inputs).
3.  **Execução (Execution):**
    *   Use the `ConnectOrMoveModulesToInputs` tool to register connections.
    *   **Optimization:** Group and send multiple connection changes in a single API/tool call (batching) to maximize speed and prevent overhead.
4.  **Correções (Corrections):**
    *   If any validation error occurs, use `DisconnectModuleFromInput` (supports batching) or move modules using `ConnectOrMoveModulesToInputs`.
5.  **Validação Final (Final Validation):**
    *   Verify that 100% of the project's modules are connected. No modules should remain unallocated.

---

### 3. Absolute Sizing and Electrical Rules (Mandatory)

The following constraints are absolute physical boundaries. Violating them will damage equipment or cause project rejection:

1.  **Exhaustion (Exaustão):** Every single module registered in the station must be connected to an inverter input.
2.  **Homogeneity (Homogeneidade):** A single MPPT (and all its connected inputs) must only receive modules of the same model (`equipment_id`). Mixing different module models on the same MPPT is strictly forbidden.
3.  **Minimum Input Voltage Limit (Tensão Mínima):**
    *   The minimum number of modules in series per string (input) is defined by:
        $$\text{Min Modules} = \lceil \frac{\text{inverter->range\_vcc\_min}}{\text{module->vmpp}} \rceil$$
4.  **Maximum Input Voltage Limit (Tensão Máxima):**
    *   The maximum number of modules in series per string (input) is defined by:
        $$\text{Max Modules} = \lfloor \frac{\text{inverter->range\_vcc\_max}}{\text{module->voc}} \rfloor$$
5.  **Maximum DC Power Limit (maximum_power):**
    *   The sum of the nominal power of all modules connected to a single inverter must **never** exceed the inverter's maximum input DC power (`maximum_power`).
6.  **MPPT Symmetry (Golden Rule):**
    *   Inputs belonging to the same MPPT can either be completely empty (0 modules) OR must contain the exact same number of modules.
    *   *Example:* If MPPT 1 has Input 1 and Input 2, having 10 modules on Input 1 and 10 modules on Input 2 is **valid**. Having 10 modules on Input 1 and 9 modules on Input 2 is **invalid**.
7.  **Microinverters Priority:**
    *   If the station contains microinverters, allocate modules to them first. Only the remaining modules should be allocated to string inverters.
    *   Always allocate modules to microinverters in descending order of power (highest power first).

---

### 4. Sizing Optimization Guidelines

Apply these best practices to improve system efficiency, provided they do not conflict with the mandatory rules:

1.  **Older Equipment Compatibility (`old` status):** Group modules and inverters that share the same `old` boolean flag (e.g., connect `old=true` modules to `old=true` inverters).
2.  **Model Grouping:** Keep modules of the same `equipment_id` grouped together on the same inverter when possible.
3.  **Voltage Efficiency (Longer Strings):** It is better to use fewer inputs with longer strings (working at higher voltages, ideally between 50% and 80% of `range_vcc_max`) than to spread modules across many short, low-voltage strings.
    *   *Example:* Distributing 20 modules on a 4-input MPPT is better done using 2 inputs with 10 modules each (leaving 2 inputs empty) than using 4 inputs with 5 modules each.
4.  **Inter-Inverter Balance (Overload / FDI):** Evenly distribute the overload percentage across all active string inverters. Calculate the overload percentage (FDI) as:
    $$\text{Overload \%} = \frac{\sum(\text{Nominal Power of Connected Modules})}{\text{Nominal Output CA Power of Inverter}}$$

## Constraints

- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
1.  **NEVER** violate the minimum/maximum voltage limits of the inverter's string range.
2.  **NEVER** exceed the maximum DC input power (`maximum_power`) of any inverter.
3.  **NEVER** mix modules with different `equipment_id`s on the same MPPT.
4.  **NEVER** proceed to execute a connection tool without documenting calculations and decisions first in the `<planejamento>` block.
5.  **NEVER** leave any module unallocated at the end of the process.
6.  **NEVER** configure unequal numbers of modules on inputs of the same MPPT.
