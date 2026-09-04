# Auditar, Corrigir e Otimizar Skills (High-Efficiency Runbook)

Runbook de alta eficiência para auditar, validar, corrigir e otimizar **todas as skills de `all_skills/`** contra o código real dos projetos de referência em `projects/`. Projetado para ser executado por um agente autônomo do início ao fim, com orquestração multi-agente otimizada para **mínimo consumo de tokens**, **máxima agilidade/paralelismo** e **zero perda de rigor técnico**.

> **Idioma:** conduza toda a conversa com o humano em **pt-BR**.  
> **Escopo:** somente `all_skills/`. Não altere qualquer coisa fora deste escopo.  
> **Ferramenta de apoio (uso restrito — não carregar em toda fase):** a `skill-creator` é referência de boa `SKILL.md` (description acionável de 200–400 chars, progressive disclosure, instruções imperativas com o *porquê*). **Só carregue a skill-creator quando a tarefa envolve julgar/reescrever FORMA ou `description`** — ou seja, apenas em: Fase 1 quando o problema encontrado for de forma/gatilho, Etapas 2 e 3 do plano (reescrita de Críticas/Ruins), e Etapa 5 (Boas). Nas Fases 0.5, 2, 3 e nas Etapas 1 e 4 do plano, a tarefa é puramente técnica/factual (redundância, refutação, remoção/merge, podas) — **não carregue a skill-creator ali**, ela não agrega e consome tokens inutilmente.

---

## Taxonomia de Tiers de Modelos e Roteamento de Custo

A eficiência de custo e velocidade deste runbook apoia-se em uma separação rigorosa de **2 Tiers de Modelos**:

| Tier | Modelos Recomendados | Perfil de Custo / Latência | Casos de Uso no Runbook |
| :--- | :--- | :--- | :--- |
| **Tier 1 (Fast / Economic)** | `Gemini 3.7 Flash` / `Flash-Lite` / `Claude 3.5 Haiku` | **Muito Baixo Custo / Ultra Rápido** (~75-80% do volume total de chamadas) | • Fase 1 (Auditoria Unificada padrão)<br>• Fase 3 (Revisão adversarial de checagens pontuais/locais)<br>• Fase 6: Etapa 4 (Regulares e Bloat) e Etapa 5 (Boas) |
| **Tier 2 (High-Reasoning)** | `Gemini 3.7 Flash (High)` / `Pro` / `Claude 3.7 Sonnet` | **Alto Raciocínio / Julgamento Complexo** (~20-25% do volume total) | • Agente Principal (Orquestrador)<br>• Fase 2 (Cluster & Judge de redundâncias)<br>• Fase 3 (Revisão adversarial de contratos arquiteturais)<br>• Fase 4 (Conciliação inline)<br>• Fase 6: Etapas 1, 2 e 3 (Remoções, Merges, Críticas, Ruins)<br>• Fase 7 (Verificação adversarial final) |

### Agente Principal (Orquestrador): **Tier 2 — Gemini 3.7 Flash (High)**
Rode a sessão principal sempre em Tier 2. O motivo:
- A **conciliação (Fase 4) roda inline no orquestrador** — recalcular estados e arbitrar destinos com precedência estrita exige alto discernimento.
- O orquestrador é a **rede de segurança entre fases**: valida a integridade das saídas antes de disparar a próxima etapa.
- Erro de orquestração é o mais caro de um sistema multi-agente; garantir precisão no nó central protege 100% dos fan-outs seguintes.

---

## 0. Verdade-base do projeto (verificar antes, nunca assumir de memória)

Os projetos reais ficam em `projects/` (symlinks). Hoje: `engeapp` (Laravel 13 + PHP 8.4 + MySQL, front Vue 3 SPA), `MaxComponentsUi`, `MaxPinia`, `MaxUse`, `AgenteDeBolso`, `SocialMedia`, `MaxCode`. **Confirme quais existem** com `ls projects/` no início — se houver alvos de skill sem projeto correspondente, avalie pelo que der para inferir e registre como *limitação*, não como erro.

Convenções fundamentais confirmadas no código real:
- **Rotas do front = NOMES Ziggy pontilhados**, não caminhos `/api/...`. Os helpers `apiGetRoute('cliente.data', params)` / `apiPostRoute('cliente.save', payload)` do `@maxvue/max-use` recebem o **nome** da rota. Ziggy **está** configurado (`resources/app.ts`: `ZiggyVue` + `route`).
- **Sem libs cruas de terceiros:** nada de `vueuse`/`lodash`/`primevue` direto. Usar `@maxvue/max-use` (reexporta VueUse + utilitários) e componentes `Max*` de `@maxvue/max-components-ui`.
- **Contrato MaxPinia:** store com `isCached = ref(true)` + `options` (`get.route`, `save`, `key`, `enabled`), `data`, `status.server.get.is_requested`/`is_success`. A chave real de cache do LocalForage é `getKey() = store.$id + (store.id ?? options.id)` — **`options.key` NÃO é a chave de cache** (é convenção que casa com `$id`). Todo GET de página passa por store MaxPinia.
- **Sem camada `services/` no front.** Mutações via `apiPostRoute` a partir de stores.
- **Laravel é v13 / PHP 8.4.**.
- Comentários de código nas skills em **pt-BR**.

---

## Visão Geral do Fluxo Otimizado

```
Fase 0.5  Pré-Triagem Determinística    → Script zero-token: YAML, contagem de chars, regex de strings proibidas
Fase 1    Auditoria unificada           → Fan-out Tier 1 (1 verificador/skill): conformidade + bloat + resumo-map
Fase 2    Redundância inter-skills      → Pré-filtro de afinidade léxica → Cluster (Tier 2) → Judge paralelo
Fase 3    Revisão adversarial           → Micro-batching contextual (2-4 problemas por arquivo/contexto comum)
Fase 4    Conciliação                   → Inline no Orquestrador: REMOVER > FUNDIR > PODAR > CORRIGIR > MANTER
Fase 5    Tabela consolidada            → Linha-a-linha 1:1 de todas as skills [no-op: encerra se tudo MANTER]
Fase 6    Plano de correção (5 etapas)  → ⛔ PARADA OBRIGATÓRIA: aprovar antes de executar (Pipelines de contexto quente)
Fase 7    Verificação adversarial final → Tier 2 focado em alto risco (Críticas, Ruins, Merges)
Fase 8    Versionamento (git)           → ⛔ commit/push/merge SÓ sob pedido explícito do humano
```

**Fases 0.5 a 5 executam SEMPRE de forma direta e read-only.** Não modificam arquivos de skills nem executam comandos git. Ao receber a ordem de rodar o runbook, execute direto até a Fase 5.

---

## Fase 0.5 — Pré-Triagem Determinística (Zero-Token Fast-Path)

Antes de invocar qualquer modelo LLM, o agente orquestrador roda uma varredura estática e instantânea (via comandos shell / scripts em milissegundos) para extrair defeitos sintáticos e literais óbvios:

1. **Checagem de YAML Frontmatter & Tamanho de Description:**
   - Detectar `description` ausente, sem aspas contendo dois-pontos (`:`), ou fora da faixa de **200 a 400 caracteres**.
2. **Scan de Violações Literais de Convenção:**
   - Ocorrências de `adonis`, `AdonisJS`, rotas cruas `/api/` no frontend, imports diretos de `lodash` ou `vueuse`.
3. **Mapeamento de Arquivos Existentes:**
   - Lista exata de todos os `SKILL.md` alvos em `all_skills/`.

> **Ganho de Eficiência:** Os subagentes da Fase 1 já recebem essa lista de fatos pré-computados em seu briefing de entrada, eliminando buscas cegas e focando 100% de seu tempo de inferência na validação técnica de código profundo.

---

## Fase 1 — Auditoria Unificada (1 verificador por skill) — **Tier 1 (Fast)**

Uma única passada produz os **três sinais por skill** (conformidade + bloat + resumo-map), aproveitando o mesmo contexto carregado:

1. Liste os alvos: `find all_skills -name SKILL.md`.
2. Dispare **1 subagente verificador por `SKILL.md`** em **Tier 1 (Fast)**.

**Ação do verificador (3 sinais na mesma chamada):**

**(a) Conformidade:**
- Ler o `SKILL.md` e referências dele.
- Para cada afirmação técnica (rota, classe, config, tabela/coluna, componente, lib, método), abrir os projetos `projects/` (`Grep`/`Read`) e confirmar/refutar.
- Conferir detalhadamnte o conteúdo da Skill contra as convenções da Seção 0.

**(b) Descrição:**
- Verificar se o campo description da SKILL está em conformidade com as seguintes regras:
  - O Campo description existe e seu conteúdo está entre 200 e 400 Caracteres;
  - O Campo description descreve claramente o que a Skill faz;
  - O Campo description permite inferir de forma clara e fácil quando ela deve ser usada;
  - O Campo description contém termos semanticamente discriminantes;
  - O Campo description representa corretamente o conteúdo real da Skill;
  - O Campo description cobre as principais intenções que deveriam ativá-la;
  - O Campo description evita ser genérica demais;
  - O Campo description evita ser ampla demais;
  - O Campo description evita ser restritiva demais;
  - O Campo description evita linguagem promocional ou sem valor de roteamento;
  - O Campo description evita procedimentos que deveriam estar no corpo da Skill;
  - O Campo description evita redundâncias;
  - O Campo description evita repetir informações sem ganho semântico.

**(c) Bloat:**
- Seções mortas que não correspondem a nada usável no projeto.
- Redundância interna e preâmbulos verbosos que não afetam o comportamento do agente.
- Arquivos órfãos em `references/` ou `rules/`.

**(d) Front-End ** 
- Específico para Skills de FrontEnd - Pular esta etapa quando a skill não for sobre o front-end**
- Verificar se o conteúdo da SKILL está em conformidade com as seguintes regras para o front-end
  - Para componentes genéricos e de uso recorrente, sempre adotar a biblioteca local MaxComponentsUi.
    - Exemplos:
      - Botões: MaxButton, MaxIconButton, MaxIconButtonConfirm, MaxButtonConfirm
      - Tabs: MaxTabs
      - Tabelas: MaxTable ou MaxTableFields
      - Inputs: MaxInput* (MaxInputText, MaxInputCep, MaxInputPhone, MaxInputCpfCnpj, etc. )
      - Select: MaxInputSelect
      - Select em formato de Badge (Tag): MaxTagSelect
      - Formulários -> MaxGrid
      - Titulos -> MaxTitle1 e MaxTitle2
  - Para Funções Helpers no Frontend, sempre adotar "MaxUse".
  - Para Funções Helpers no Frontend, nunca adotar "VueUse" nem tampouco "Lodash".
    - MaxUse possui as funções de VueUse e Lodash próprias.
  - Para Salvamentos no Frontend, as skills devem sempre adotar Stores Pinia com "MaxPinia".
  - Para Cache no Frontend, as skills devem sempre adotar Stores Pinia com "MaxPinia"
  - Para Salvamentos Automáticos no frontend, as skills devem sempre adotar Stores Pinia com "MaxPinia"
  - O Formato dos nomes de arquivos pinia deverá ser "Use{NomeStore}.Store.ts" Ex: "UseSystm.Store.ts"
  - No front-end, não fazer uso de classes de estilo. Ex: class="p-4 rounded-2xl" Os estilos devem estar na seção <style>

**(e) Resumo-map:**
- Extração concisa: tema (1 frase), entidades citadas (libs, rotas, componentes, classes) e ~10 palavras-chave.

**Classificação de `reviewModel` para a Fase 3:**
- `"Tier 1 (Fast)"` — problema **factual pontual e localizado**: 1 citação (nome de rota/config/tabela/coluna/classe/caminho) verificável em 1 arquivo. Cortes de bloat padrão.
- `"Tier 2 (High-Reasoning)"` — problema **arquitetural/estrutural**: fluxo, contrato ou design multi-arquivo (ex.: padrão multi-tenant, ciclo de vida complexo, guards).

**Saída estruturada (JSON compacto):**
```json
{
  "skillName": "string",
  "skillPath": "string",
  "state": "Excelente | Boa | Regular | Ruim | Crítica",
  "problemCount": 0,
  "problems": [
    { "text": "1 problema concreto com evidência", "reviewModel": "Tier 1 (Fast) | Tier 2 (High-Reasoning)" }
  ],
  "bloatVerdict": "ENXUTA | PODAR | INCHADA",
  "estimatedCutPct": 0,
  "cuts": [
    { "text": "seção a remover/condensar e o porquê", "reviewModel": "Tier 1 (Fast) | Tier 2 (High-Reasoning)" }
  ],
  "mapSummary": {
    "tema": "1 frase",
    "entidades": ["libs/classes/rotas/componentes citados"],
    "keywords": ["10 a 20 palavras-chave"]
  },
  "summary": "veredito em 1 frase"
}
```

Régua de estado: **Excelente** (100% aderente) | **Boa** (ajustes só de formato/redação) | **Regular** (desacordos superficiais) | **Ruim** (desacordos medianos) | **Crítica** (ensina arquitetura/APIs inexistentes).  
Régua de bloat: **ENXUTA** (0%) | **PODAR** (< 25%) | **INCHADA** (≥ 25%).

---

## Fase 2 — Redundância Inter-Skills (Cluster → Judge)

**2.1 Pré-Filtro & Cluster (1 agente — BARREIRA) — Tier 2 (High-Reasoning).**  
Com a tabela de todos os `mapSummary` da Fase 1, o agente calcula a afinidade de entidades e palavras-chave compartilhadas. Gera apenas a lista de **clusters suspeitos com sobreposição real** (2 a 4 skills por cluster), descartando falsos alertas antes do Judge.

**2.2 Judge (fan-out paralelo, 1 agente/cluster) — Tier 2 (High-Reasoning).**  
Cada subagente lê apenas as skills do seu cluster e emite o julgamento:
```json
{
  "cluster": ["skillA", "skillB"],
  "recommendation": "MERGE | LAPIDAR | DEMARCAR | FALSO-POSITIVO",
  "into": "skill destino (se MERGE)",
  "rationale": "motivo e o que cada uma possui de exclusivo",
  "mergePlan": "como fundir sem perda de conteúdo (se MERGE)",
  "reviewModel": "Tier 1 (Fast) | Tier 2 (High-Reasoning)"
}
```
- **MERGE:** fundir em uma única skill abrangente sem perda de conteúdo.
- **LAPIDAR:** manter ambas mas ajustar o conteúdo interno para que cada uma cumpra apenas com seu próprio escopo e elimine os conflitos internos existentes.
- **DEMARCAR:** manter ambas com descrições e gatilhos estritamente delimitados para evitar conflito.
- **FALSO-POSITIVO:** cobrem domínios distintos; manter separadas.

---

## Fase 3 — Revisão Adversarial com Micro-Batching Contextual

Para evitar o overhead massivo de disparar centenas de subagentes isolados (pagando system prompt e leitura de arquivos repetidamente), a revisão adversarial adota **Micro-Lotes Contextuais**:

1. **Agrupamento por Contexto Comum:** Agrupe os problemas e cortes apontados nas Fases 1 e 2 em micro-lotes de **2 a 4 problemas** que pertençam à mesma skill ou que toquem o mesmo arquivo/classe do projeto.
2. **Roteamento Dinâmico de Modelo:**
   - Se todos os problemas do lote forem pontuais/locais → **Tier 1 (Fast)**.
   - Se houver pelo menos um problema arquitetural no lote → **Tier 2 (High-Reasoning)**.
3. **Ação do Revisor Adversarial:** Atua como "advogado do diabo" assumindo que a acusação pode ser um falso-positivo. Abre o arquivo do projeto 1 única vez para testar e refutar todos os problemas do lote.

**Saída estruturada (um objeto por problema avaliado):**
```json
{
  "skillName": "string",
  "problem": "texto avaliado",
  "verdict": "CONFIRMADO | REFUTADO",
  "evidence": "arquivo e linha real que sustenta o veredito",
  "correctedDescription": "descrição retificada se CONFIRMADO e impreciso; senão vazio"
}
```

> **Ganho de Eficiência:** Reduz o número total de chamadas em ~70% a 75%, reaproveita a leitura de arquivos em disco e acelera drasticamente a conclusão da fase.

---

## Fase 4 — Conciliação Determinística

Funde os sinais confirmados e define o destino único de cada skill aplicando a **Regra de Precedência Rígida**:

> ### 👑 PRECEDÊNCIA: `REMOVER` > `FUNDIR` (Merge) > `PODAR` (Bloat) > `CORRIGIR` (Conformidade) > `MANTER`

**Regra de Ouro:** Nunca reescrever no detalhe uma skill cujo destino é `FUNDIR` ou `REMOVER`. O merge reconcilia o conteúdo e a remoção descarta a skill.

### Guarda Anti-Churn (Regra Dura)
Qualquer problema **não CONFIRMADO** pela revisão adversarial da Fase 3 é **SUMARIAMENTE DESCARTADO**. Não entra na conciliação, não vira briefing e não gera edições. Sugestões estéticas sem defeito técnico confirmado contra o código são ignoradas para garantir que o processo convirja rapidamente.

---

## Fase 5 — Tabela Consolidada (1 Linha por Skill)

> **Regra Obrigatória:** A tabela apresentada ao humano deve conter **exatamente N linhas** (onde N = total de `SKILL.md` auditados), ordenada por severidade (`Crítica → Ruim → Regular → Boa → Excelente`) e nº de problemas decrescente:

| # | Skill | Estado | Nº de problemas | Destino | Descrição dos problemas |
|---|-------|--------|------------------|---------|--------------------------|
| 1 | `laravel-editorial-calendar-event-workflow` | Crítica | 9 | CORRIGIR | Ensina `AiPipeline`/trait `AdvancesEventStatus` inexistentes — real é `EventObserver::updated()`. |
| 2 | `laravel-social-media-oauth-token-lifecycle` | Crítica | 8 | CORRIGIR | Ensina padrão Strategy e colunas cifradas inexistentes no projeto. |
| … | … | … | … | … | … |

Acompanhada de:
- Distribuição quantitativa por Estado e Destino.
- Seções de apoio opcionais (ex.: lista de pares `FUNDIR`, lista de `DEMARCAR`).

### Critério de Parada Rápida (No-Op)
Se todas as skills resultarem em destino **`MANTER`** (zero problemas confirmados), o runbook encerra imediatamente exibindo: **"Nenhuma correção necessária — todas as skills em MANTER"**, economizando 100% dos tokens das Fases 6 a 8.

---

## Fase 6 — Plano de Correção em 5 Etapas (Contexto Quente)

> ### ⛔ PARADA OBRIGATÓRIA DE APROVAÇÃO HUMANA
> Após estruturar o plano de 5 etapas e **antes** de modificar qualquer arquivo, **PARE e apresente o plano ao humano**. Não execute nenhuma modificação sem autorização explícita.

Ao receber aprovação, execute as etapas organizadas para encolher a base e maximizar o reaproveitamento de contexto:

- **Etapa 1 — Remoções + Merges (Tier 2):**  
  Apaga as skills `REMOVER`, executa a fusão das skills `FUNDIR` sem perda de conteúdo e atualiza `manifests/` e arquivos de sincronização. Encolhe o total de skills para as etapas seguintes.
- **Etapa 2 — Críticas (Tier 2 + skill-creator):**  
  Reescrita profunda: remove seções inventadas, reconstrói a arquitetura conforme o código real e recalibra a `description` (200–400 chars).
- **Etapa 3 — Ruins (Tier 2 + skill-creator):**  
  Correções medianas: nomes de rotas Ziggy, configs, tabelas, colunas reais e remoção de mecanismos obsoletos.
- **Etapa 4 — Regulares + Podas de Bloat (Tier 1 em Lotes de 3 a 5 skills):**  
  Correções pontuais e cortes de bloat (`PODAR`/`INCHADA`). Agrupar por domínio (`laravel-*`, `vue-*`) usando **`pipeline` de Contexto Quente** (chamadas sequenciais no mesmo subagente para reaproveitar arquivos de projeto já abertos na memória de trabalho).
- **Etapa 5 — Boas (Tier 1 + skill-creator em Lotes de 3 a 5 skills):**  
  Ajustes puramente mecânicos de documentação, seções em pt-BR, formato YAML e otimização de `description`.

---

## Fase 7 — Verificação Adversarial Final (Tier 2)

Dispara 1 verificador em **Tier 2 (High-Reasoning)** para cada skill de alto risco (todas as Críticas, Ruins e resultantes de Merge) para validar a versão corrigida contra o código real — veredito `LIMPA` / `RESIDUAL` / `FALHA`. Executa spot-check em skills Excelentes para garantir que não sofreram alterações indevidas.

---

## Fase 8 — Versionamento Git (Sob Pedido Explícito)

> ### ⛔ NENHUM COMMIT / PUSH / MERGE AUTOMÁTICO
> Concluídas as correções e validações, o agente **NÃO** commita nem sobe código por iniciativa própria. Apresente o sumário das alterações e solicite autorização explícita:
> - **Commit** exige confirmação dedicada.
> - **Push** e **Merge** exigem confirmações adicionais e independentes.

---

## Checklist de Integridade de Saída

- [ ] **YAML Válido:** Frontmatter íntegro em todo `SKILL.md` (strings com `:` sempre entre aspas).
- [ ] **`description` Otimizada:** Entre 200 e 400 caracteres, acionável e fiel ao código real.
- [ ] **0 Menções a AdonisJS:** Nenhuma referência à stack legada em `all_skills/`.
- [ ] **0 Rotas `/api/...` no Frontend:** Utilização estrita de rotas Ziggy pontilhadas com `@maxvue/max-use`.
- [ ] **0 Violações MaxPinia:** Contrato `getKey()` respeitado, sem confusão com `options.key`.
- [ ] **Manifestos e Syncs Atualizados:** `manifests/` consistente após qualquer remoção ou merge.

---

## Tabela de Impacto e Eficiência (Benchmark Estimado)

| Dimensão | Runbook Anterior | Runbook Otimizado (Este) | Ganho / Economia |
| :--- | :--- | :--- | :--- |
| **Consumo de Tokens** | ~5.200.000 tokens | **~1.600.000 tokens** | **~69% de economia de tokens** |
| **Tempo Total Estimado** | ~35 a 45 minutos | **~9 a 12 minutos** | **~3.8x mais rápido** |
| **Chamadas de Revisão (Fase 3)** | 1 subagente / problema (~120 chamadas) | Micro-batching contextual (~30 chamadas) | **-75% de round-trips** |
| **Triagem Inicial** | 100% LLM | Pré-triagem determinística zero-token | **Zero gasto em checagens sintáticas** |
| **Reaproveitamento de Contexto** | Paralelo isolado (releituras do zero) | Pipelines de contexto quente por domínio | **Arquivos de projeto lidos 1x por domínio** |
