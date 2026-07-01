# B2B Health Score (AgentHealthScore)

## Goal
Core rules, parameterization, and calculation modeling adopted by `AgentHealthScore`, the Customer Success agent that determines the commercial health metric of partner photovoltaic integration companies (B2B Health Score) in Engeapp.

## Instructions

### 1. Base Weights and Parameters
An account's overall health always starts from **100**. The total score is the weighted average across the three major partnership areas:
- **Business (40%)**: Reflects sales trends, payments, and defaults.
- **Experience (35%)**: Reflects communication friction, satisfaction, or hostility.
- **Operation (25%)**: Reflects technical friction, scope, or technical maturity.

Final calculation: `(Business * 0.40) + (Experience * 0.35) + (Operation * 0.25)`. Each area's score is controlled by clamping the results between 0 and 100.

### 2. Decay Rule (Recency / Time Decay)
Past problems or wins fade in impact over time. The factor is applied by calculating how many days ago the event occurred:
- Up to `< 10` days: **100%** impact.
- `>= 10` days: **25%** reduction in impact.
- `>= 20` days: **50%** reduction.
- `>= 30` days: **75%** reduction.
*Use the data trend in the text report to justify the reasoning.*

### 3. Mathematical Guidelines (Penalties/Bonuses)
- **Business**: Critical drop (-35); Moderate drop (-15); Active default (-30); Significant growth (+15).
- **Experience**: Cancellation threat / very hostile tone (-30); Excessive effort (-20); Explicit praise (+10).
- **Operation**: Technical crisis under our responsibility (-25); Technical recovery or masterful solution (+15).

### 4. Insufficient Data Condition
If any area lacks billable information during data collection, assign a value of **5** and make clear in the text that this number does not represent a failure, but rather a lack of metrics.

### 5. B2B Status Classes
- Excellent: **81 - 100**
- Good: **61 - 80**
- Regular: **41 - 60**
- Poor: **21 - 40**
- Critical: **0 - 20**

### 6. Markdown Report (Template `health_details`)
The text document model produced by this LLM must contain the H1 header (`# 🩺 Relatório de Saúde Comercial`), the bulleted summaries (`### 1. Diagnóstico de Negócio`, etc.), and end with `🎯 4. Playbook de Ação Recomendado`. (End-user report content is written in pt-BR.)

### 7. Required Tools and Tests
Use the `GetClientData` tool to ingest metadata and billing. At the end, ALWAYS trigger the `SetHealth` tool to persist the JSON of the individual scores. Tests must cover mocking these tools, verifying recalculation of the decay window.
