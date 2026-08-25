---
name: laravel-concessionaires-connection-regulation-best-practices
description: "Use when managing energy concessionaires, subsidiaries, RPAs, and connection standards (phases, voltage, breaker, cables) in Engeapp, and electrical parameters for PV sizing. Covers concessionaire regulations and electrical connection standards."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Concessionárias e Normas Técnicas de Conexão

## Objetivo
Estabelecer padrões consistentes para o gerenciamento de concessionárias de energia (distribuidoras), suas filiais regionais, canais de atendimento, automações e as normas técnicas de conexão que ditam o padrão de entrada dos projetos solares no backend Laravel do engeapp. O domínio real é a **regulação técnica de conexão** (fases, tensão, disjuntor, bitola de cabos).

> Escopo real (verificado no código): estes models tratam APENAS de estrutura corporativa, canais/automações e parâmetros elétricos de conexão. Não existe domínio tarifário no engeapp — veja a restrição em "Restrições" antes de assumir o contrário.

## Instruções

### 1. Estrutura de Models e Relacionamentos
Todos os models usam `HasUlids` e vivem em `app/Models/Concessionaire/`. Mantenha claro o mapeamento hierárquico:

- **ConcessionaireCompany** (`concessionaires_company`): matriz/holding corporativa (ex.: Energisa, Equatorial). `$guarded = []`, cast `details => object`. Relaciona `subsidiary()`/`subsidiaries()` (`hasMany` por `concessionaire_company_id`) e `automations()` (`morphToMany` via `concessionaires_automations_assignments`). Helpers `addSubsidiary()`/`createSubsidiary()` criam filiais já vinculadas.
- **ConcessionaireSubsidiary** (`concessionaires_subsidiaries`): unidade operacional regional (ex.: Energisa Sul-Sudeste). Guarda áreas de atendimento (`service_locations_array`), URLs (`virtual_agency_url`, `photovoltaic_url`, `regulations_url`, etc.) e templates de placa (`placa1`, `placa2` — cast `array`; `texto_placa1`, `texto_placa2`). Relações: `business()`/`concessionaire()` (matriz), `regulations()` (`hasMany` por `concessionaires_subsidiaries_id`), `channels()` (`hasMany` de ConcessionaireSubsidiaryChannel), `automations_local()` (`morphToMany` de ConcessionaireAutomation via `concessionaires_automations_assignments`), `states()` e `cities()` (`hasMany` por `concessionaires_subsidiaries_id`, área de cobertura) e `projects()` (`hasMany` de Project por `concessionaire_company_id`). Possui ainda o accessor `automations` (com `Cache::remember` de 30 min) e o método `reloadAutomations()`, que mescla automações general/company/subsidiary.
- **ConcessionaireSubsidiaryRegulation** (`concessionaires_subsidiaries_regulations`): agrupa os padrões de conexão de uma filial por classe de tensão e fases. `$attributes = ['class' => 'Conexão']`, `$with = ['data']`. Relaciona `data()` (`hasMany`). Expõe accessors calculados `mono_127`, `mono_220`, `bi_127`, `bi_220`, `tri_127`, `tri_220`, cada um filtrando `data()` por `amount_phases` (1/2/3) e `voltage_phase_neutral` (127/220).
- **ConcessionaireSubsidiaryRegulationData** (`concessionaires_subsidiaries_regulations_data`): parâmetros elétricos granulares de cada norma. Um **global scope** definido em `booted()` ordena sempre por `circuit_breaker` (`addGlobalScope('order', ...)`), para renderização previsível na interface.
- **ConcessionaireAutomation** (`concessionaires_automations`): script/rotina executável por filial. `$appends = ['data_send']` (accessor `getDataSendAttribute()` que faz `json_decode` de `data` com falha segura para `[]`), casts `details => object` e `is_general_automation => boolean`. Relaciona `Concessionaire()` (`belongsTo` ConcessionaireSubsidiary via FK `id_concessionaria`) — **mas a coluna `id_concessionaria` não existe**: a migration cria `concessionaires_subsidiaries_id` (char 26), que é também a coluna da FK real. Mesma armadilha do `regulation_id` abaixo: não confie nessa relação. A coluna `level` assume `general`, `company` ou `subsidiary` e é normalizada por `reloadAutomations()`.
- **ConcessionaireSubsidiaryChannel** (`concessionaires_subsidiaries_channels`): canal de atendimento da filial. Relaciona `subsidiary()` (`belongsTo` via `concessionaires_subsidiaries_id`). Casts para os enums de `app/Enums/Concessionaire/`: `department => ChannelDepartmentEnum` (website, virtual_agency, customer_service, change_ownership, internal_affairs, regulations, photovoltaic, project_submit, others), `type => ChannelTypeEnum` (phone, mail, whatsapp, url), `status => ChannelStatusEnum` (found, confirmed, not_found); `notes => object`. O método estático **`catalog()` fica no model** `ConcessionaireSubsidiaryChannel`, não nos enums — é o checklist canônico de canais esperados por filial e não gera linhas placeholder.

#### Models legados sem tabela (não use)
- **ConcessionaireSubsidiaryRegulationsFile** (declara `$table = 'concessionaires_subsidiaries_regulations_files'`) e **ConcessionaireSubsidiaryRegionals** (declara `$table = 'concessionarias_regionais'`) **não possuem migration** em `database/migrations` nem uso em runtime (nenhum controller, rota, DTO ou observer os referencia). Trate-os como legado morto.
- Consequência: a relação `files()` de `ConcessionaireSubsidiaryRegulation` (`hasMany(ConcessionaireSubsidiaryRegulationsFile::class, 'concessionaires_subsidiaries_regulations_id')`) **quebra se chamada** — não a use nem a documente como caminho válido.
- Se por algum motivo mexer no model de arquivos, note que os métodos reais têm inicial maiúscula: `Regulations()` (`hasMany` ConcessionaireSubsidiaryRegulation via FK `id_file`) e `Concessionaires()` (`belongsTo` ConcessionaireSubsidiary via `id_business`) — não `regulations()`/`business()`.

#### Armadilha: `ConcessionaireSubsidiaryRegulationData::regulation()`
`ConcessionaireSubsidiaryRegulationData::regulation()` declara `belongsTo(ConcessionaireSubsidiaryRegulation::class, 'regulation_id')`, mas a coluna `regulation_id` **não existe**: a migration cria `concessionaires_subsidiaries_regulations_id` (char 26), que é também a FK usada pelo lado inverso (`ConcessionaireSubsidiaryRegulation::data()`). Não confie nessa relação e não a replique; navegue a partir da norma (`regulation->data`) ou corrija a FK para `concessionaires_subsidiaries_regulations_id`.

### 2. DTOs (Spatie Laravel Data)
Os DTOs vivem em `app/Data/Concessionaire/` (`ConcessionaireCompanyData`, `ConcessionaireSubsidiaryData`, `ConcessionaireSubsidiaryRegulationData`, `ConcessionaireSubsidiaryRegulationDataData`, `ConcessionaireAutomationData`) e estendem `Spatie\LaravelData\Data`. Ao validar/transferir os parâmetros de norma, respeite os campos **reais** de `ConcessionaireSubsidiaryRegulationDataData` — todos elétricos:

- `amount_phases` (`?int`): número de fases — 1, 2 ou 3.
- `voltage_phase_neutral` (`int`): tensão fase-neutro — tipicamente 127 ou 220.
- `circuit_breaker` (`?int`): limite de disjuntor (A).
- `wire_phase`, `wire_neutral`, `wire_ground` (`?int`): bitolas dos condutores (mm²).
- `maximum_load` (`?float`): carga máxima suportada.
- `details` (`?object`) e a relação `regulation` (carregada como `Lazy`).

Use `Lazy` para relacionamentos pesados e mantenha os tipos alinhados às colunas da migration (`integer` para fases/tensão/disjuntor/cabos, `double` para `maximum_load`, `json` para `details`).

### 3. Camada HTTP (controllers e rotas)
Os controllers ficam em `app/Http/Controllers/Concessionaire/`: `ConcessionairesDataController` (leituras), `ConcessionairesExecuteController` (escritas) e `ConcessionairesListController`. As rotas são declaradas em `routes/web/Web.Concessionaires.Routes.php`, dentro de `Route::middleware(['auth', 'verified'])`, com 16 rotas **nomeadas** consumidas pelo front via nomes Ziggy pontilhados (`apiGetRoute('concessionaire.subsidiary.regulations', { id })`), nunca por caminhos `/api/...`:

- Leituras: `concessionaires.list`, `concessionaire.list.all.subsidiaries`, `concessionaire.list.all.subsidiaries.select`, `concessionaire.subsidiaries.list`, `concessionaire.subsidiary.data`, `concessionaire.subsidiary.regulations`, `concessionaire.subsidiary.channels`, `concessionaire.subsidiary.automations`, `concessionaire.subsidiary.automation.data`, `concessionaire.subsidiary.location`.
- Escritas (POST): `concessionaire.subsidiary.automations.new`, `concessionaire.subsidiary.automation.save`, `concessionaire.subsidiary.save`, `concessionaire.subsidiary.regulation.data.save`.
- Fora do padrão: `concessionaire.business.create` é **GET** apontando para `ConcessionairesExecuteController::createBusiness` — ou seja, uma escrita exposta como leitura, contrariando a divisão DataController/ExecuteController. Além disso está **quebrada**: `createBusiness` chama `$company->createBusiness([])`, método que não existe em `ConcessionaireCompany` (só `addSubsidiary()`/`createSubsidiary()`). Não a use como referência.
- Atenção: `concessionaire.subsidiary.automations.new` também **estoura em runtime**: `createAutomation` chama `$concessionaire->automations()->create(...)` em `ConcessionaireSubsidiary`, que não tem relação `automations()` — só `automations_local()` (`morphToMany`) e o accessor `getAutomationsAttribute()`.
- Atenção: `concessionaire.subsidiary.data` está declarada **duas vezes** (linhas duplicadas idênticas). Não replique a duplicata; ao mexer no arquivo, remova-a em vez de adicionar mais uma.

`ConcessionairesExecuteController::saveRegulationData` valida e persiste **apenas** `id`, `maximum_load`, `circuit_breaker`, `wire_phase` e `wire_ground` (`findOrFail` + `fill(collect($data)->except('id'))` + `save()`). Campos como `amount_phases`, `voltage_phase_neutral` e `wire_neutral` enviados pelo front são **silenciosamente descartados** — se precisar salvá-los, adicione-os explicitamente às regras de validação.

### 4. Separação de Responsabilidades
- Não crie camadas de lógica novas nos models; siga o padrão já existente (accessors `mono_*`/`tri_*`, `reloadAutomations()`, cache de automações) para qualquer lógica adicional.
- Não há camada `app/Services/Financial` nem `PaybackCalculatorService` — a pasta real para cálculos financeiros é `app/Services/Finance`. Se um cálculo justificar um service de concessionária, crie-o seguindo essa convenção.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Idioma:** Comunique-se com o humano em pt-BR; comentários de código em pt-BR.
- **NÃO invente domínio de tarifas.** Não adicione colunas, DTOs, services ou cálculos de TUSD/TE, Grupo A/B, bandeiras tarifárias, demanda contratada, COSIP/CIP, payback ou compensação de GD — nada disso existe no engeapp e não deve ser apresentado como se existisse. Se for necessário, trate como funcionalidade nova a especificar.
- **Preserve o global scope de ordenação** em `ConcessionaireSubsidiaryRegulationData` (`addGlobalScope('order', orderBy('circuit_breaker'))`); use `withoutGlobalScope('order')` explicitamente se precisar de outra ordenação.
- **Mantenha `HasUlids`** em todos os models de Concessionaire — as PKs são `char(26)`, não auto-incremento.
- **Invalide o cache de automações.** O accessor `getAutomationsAttribute()` guarda a coleção em `Cache::remember("subsidiary:{$this->id}:automations", now()->addMinutes(30), ...)` e **nada no projeto chama `Cache::forget` nessa chave** — nem `reloadAutomations()`, nem `saveSubsidiary`, nem `createAutomation`/`saveAutomation`. Ao alterar automações de uma filial, execute `Cache::forget("subsidiary:{$subsidiary->id}:automations")`, senão a filial serve dados velhos por até 30 minutos.
