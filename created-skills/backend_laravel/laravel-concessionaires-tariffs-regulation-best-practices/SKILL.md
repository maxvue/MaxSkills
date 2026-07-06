---
name: laravel-concessionaires-tariffs-regulation-best-practices
description: Use ao criar, alterar ou consultar concessionárias de energia, filiais regionais, regionais, automações e normas técnicas de conexão (padrão de entrada, fases, tensão, disjuntor e bitola de cabos) no backend Laravel do Engeapp. Acione em models/DTOs de Concessionaire e nos parâmetros elétricos usados para dimensionar projetos fotovoltaicos.
---

# Boas Práticas de Concessionárias e Normas Técnicas de Conexão

## Objetivo
Estabelecer padrões consistentes para o gerenciamento de concessionárias de energia (distribuidoras), suas filiais regionais e as normas técnicas de conexão que ditam o padrão de entrada dos projetos solares no backend Laravel do Engeapp. O domínio real é a **regulação técnica de conexão** (fases, tensão, disjuntor, bitola de cabos) — não há subsistema de tarifas/faturamento no projeto.

> Escopo real (verificado no código): estes models tratam APENAS de estrutura corporativa e parâmetros elétricos de conexão. Não existem no Engeapp colunas, DTOs, services ou lógica de tarifas (TUSD/TE, Grupo A/B, bandeiras tarifárias, demanda contratada, COSIP/CIP, payback de GD). Não fabrique esse domínio; se precisar dele, trate como funcionalidade nova a ser especificada, nunca como algo já existente.

## Instruções

### 1. Estrutura de Models e Relacionamentos
Todos os models usam `HasUlids` e vivem em `app/Models/Concessionaire/`. Mantenha claro o mapeamento hierárquico:

- **ConcessionaireCompany** (`concessionaires_company`): matriz/holding corporativa (ex.: Energisa, Equatorial). `$guarded = []`, cast `details => object`. Relaciona `subsidiary()`/`subsidiaries()` (`hasMany` por `concessionaire_company_id`) e `automations()` (`morphToMany` via `concessionaires_automations_assignments`). Helpers `addSubsidiary()`/`createSubsidiary()` criam filiais já vinculadas.
- **ConcessionaireSubsidiary** (`concessionaires_subsidiaries`): unidade operacional regional (ex.: Energisa Sul-Sudeste). Guarda áreas de atendimento (`service_locations_array`, `states()`, `cities()`), URLs (`virtual_agency_url`, `photovoltaic_url`, `regulations_url`, etc.) e templates de placa (`placa1`, `placa2` — cast `array`; `texto_placa1`, `texto_placa2`). `business()`/`concessionaire()` apontam para a matriz; `regulations()` lista as normas. Possui accessor `automations` (com cache `Cache::remember` de 30 min) e o método `reloadAutomations()` que mescla automações general/company/subsidiary.
- **ConcessionaireSubsidiaryRegulation** (`concessionaires_subsidiaries_regulations`): agrupa os padrões de conexão de uma filial por classe de tensão e fases. `$attributes = ['class' => 'Conexão']`, `$with = ['data']`. Relaciona `data()` (`hasMany`) e `files()`. Expõe accessors calculados `mono_127`, `mono_220`, `bi_127`, `bi_220`, `tri_127`, `tri_220`, cada um filtrando `data()` por `amount_phases` (1/2/3) e `voltage_phase_neutral` (127/220).
- **ConcessionaireSubsidiaryRegulationData** (`concessionaires_subsidiaries_regulations_data`): parâmetros elétricos granulares de cada norma. Um **global scope** definido em `booted()` ordena sempre por `circuit_breaker` (`addGlobalScope('order', ...)`), para renderização previsível na interface. Relaciona `regulation()` (`belongsTo`).

### 2. DTOs (Spatie Laravel Data)
Os DTOs vivem em `app/Data/Concessionaire/` (`ConcessionaireCompanyData`, `ConcessionaireSubsidiaryData`, `ConcessionaireSubsidiaryRegulationData`, `ConcessionaireSubsidiaryRegulationDataData`, `ConcessionaireAutomationData`) e estendem `Spatie\LaravelData\Data`. Ao validar/transferir os parâmetros de norma, respeite os campos **reais** de `ConcessionaireSubsidiaryRegulationDataData` — todos elétricos, nenhum tarifário:

- `amount_phases` (`?int`): número de fases — 1, 2 ou 3.
- `voltage_phase_neutral` (`int`): tensão fase-neutro — tipicamente 127 ou 220.
- `circuit_breaker` (`?int`): limite de disjuntor (A).
- `wire_phase`, `wire_neutral`, `wire_ground` (`?int`): bitolas dos condutores (mm²).
- `maximum_load` (`?float`): carga máxima suportada.
- `details` (`?object`) e a relação `regulation` (carregada como `Lazy`).

Use `Lazy` para relacionamentos pesados e mantenha os tipos alinhados às colunas da migration (`integer` para fases/tensão/disjuntor/cabos, `double` para `maximum_load`, `json` para `details`).

### 3. Separação de Responsabilidades
- **Sem lógica de negócio nos models além do necessário**: os models Eloquent representam estrutura e relacionamentos. A lógica que já existe embutida (accessors `mono_*`/`tri_*`, `reloadAutomations()`, cache de automações) é a exceção real do projeto — siga esse padrão em vez de inventar camadas novas.
- **Não há camada `app/Services/Financial` nem `PaybackCalculatorService`**. As pastas reais em `app/Services/` são temáticas (`Ai`, `Bank`, `Browser`, `Calendar`, `Signature`, `SocialMedia`, `Whatsapp`, `Project`, etc.). Se um cálculo justificar um service, crie-o na pasta temática apropriada seguindo a convenção existente — não referencie namespaces inexistentes.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo desta skill está escrito. Comentários de código em pt-BR.
- **NÃO invente domínio de tarifas.** Não adicione colunas, DTOs, services ou cálculos de TUSD/TE, Grupo A/B, bandeiras tarifárias, demanda contratada, COSIP/CIP, payback ou compensação de GD — nada disso existe no Engeapp e não deve ser apresentado como se existisse.
- **Preserve o global scope de ordenação** em `ConcessionaireSubsidiaryRegulationData` (`addGlobalScope('order', orderBy('circuit_breaker'))`); use `withoutGlobalScope('order')` explicitamente se precisar de outra ordenação.
- **Mantenha `HasUlids`** em todos os models de Concessionaire — as PKs são `char(26)`, não auto-incremento.
- **NUNCA** realize operações em massa que atualizem várias normas/parâmetros de conexão sem envolvê-las em uma transação, para não deixar a hierarquia de conexão em estado inconsistente.
