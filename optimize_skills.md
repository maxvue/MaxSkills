# Auditar, Corrigir e Otimizar Skills (High-Efficiency Runbook)

Runbook de alta eficiência para auditar, validar, corrigir e otimizar **todas as skills de `all_skills/`** aplicando **Regras Adaptativas por Domínio** contra o código real dos projetos de referência em `projects/`. Projetado para ser executado por um agente autônomo do início ao fim, com orquestração multi-agente focada em **auditoria semântica real de IA**, **paralelismo seguro por lotes** e **máximo rigor qualitativo**.

> **Idioma:** conduza toda a conversa com o humano em **pt-BR**.  
> **Escopo:** somente `all_skills/`. Não altere qualquer coisa fora deste escopo.  
> **Regras Adaptativas por Domínio:**  
> - **Skills Proprietárias (`created-skills/`):** auditadas com rigor máximo contra os projetos locais em `projects/` (Engeapp, MaxComponentsUi, MaxPinia, MaxUse, Ziggy, PHP 8.4/Laravel 13).  
> - **Skills Externas e Terceiros (`Agentic Awesome Skills/` e `curated-youtube/`):** auditadas contra qualidade intrínseca (sintaxe YAML íntegra, `description` entre 200–400 chars com alta densidade semântica, ausência de comandos perigosos e eliminação de bloat/redundância). **Nunca force convenções do Engeapp (ex: MaxPinia, MaxComponentsUi) sobre ferramentas externas (ex: AWS, Docker, React, Django)**.  
> **Ferramenta de apoio (uso restrito — não carregar em toda fase):** a `skill-creator` é referência de boa `SKILL.md` (description acionável de 200–400 chars, progressive disclosure, instruções imperativas com o *porquê*). **Só carregue a skill-creator quando a tarefa envolve julgar/reescrever FORMA ou `description`** — ou seja, apenas em: Fase 1 quando o problema encontrado for de forma/gatilho, Etapas 2 e 3 do plano (reescrita de Críticas/Ruins), e Etapa 5 (Boas). Nas Fases 0.5, 2, 3 e nas Etapas 1 e 4 do plano, a tarefa é puramente técnica/factual (redundância, refutação, remoção/merge, podas) — **não carregue a skill-creator ali**, ela não agrega e consome tokens inutilmente.

---

> ### 🛑 CLÁUSULA PÉTREA ANTI-BYPASS: AUDITORIA SEMÂNTICA OBRIGATÓRIA POR IA (LLM)
> **NUNCA CRIE OU EXECUTE SCRIPTS PARA SIMULAR, ATALHAR OU SUBSTITUIR O JULGAMENTO DA IA.**  
> O valor e a exigência central deste processo estão no **discernimento qualitativo, raciocínio contextual e cognição semântica** que somente Modelos de Linguagem (LLMs) atuando como agente orquestrador e subagentes são capazes de fornecer.
> 
> 1. **Proibição Absoluta de Scripts de Auditoria:** É TERMINANTEMENTE PROIBIDO criar, gerar ou executar scripts em Python, Bash, Node.js ou qualquer outra linguagem (como `audit_engine.py` ou similares) para analisar o texto das skills, julgar a qualidade de descrições, verificar regras de negócio/projeto, classificar estados (`Excelente`, `Boa`, `Regular`, `Ruim`, `Crítica`) ou gerar tabelas de consolidação por heurística mecânica.
> 2. **Por que heurísticas mecânicas são estritamente vedadas:** Um script Python apenas mede tamanho (`len(description)`) e busca strings cruas com regex; ele é **completamente incapaz** de entender se uma descrição é clara, se representa o conteúdo real, se possui termos discriminantes, se é genérica, se é promocional ou se ensina padrões arquiteturais errados.
> 3. **Consequência de Violação:** Qualquer tentativa do agente executor de criar scripts de auditoria, classificadores regex ou automações locais para "agilizar" ou "economizar chamadas" é considerada uma **falha grave de execução e invalida 100% da auditoria**.
> 4. **Divisão Rígida de Responsabilidades:**
>    - **Scripts Locais (Fase 0.5 apenas):** Restritos unicamente a catalogar os caminhos dos arquivos (`SKILL.md`) e validar parsing sintático do YAML básico. Eles **NUNCA** emitem vereditos semânticos.
>    - **Subagentes de IA (Fases 1, 2, 3, 6, 7):** Toda e qualquer auditoria qualitativa, avaliação dos 13 critérios de description, conformidade com o código real e detecção de bloat **DEVE OBRIGATORIAMENTE** ser feita por inferência real de LLM via `invoke_subagent`.
>    - **Orquestrador de IA (Fases 4 e 5):** A conciliação e a síntese final são calculadas inline pelo modelo orquestrador com base exclusiva nos relatórios qualitativos retornados pelos subagentes de IA.

---

## Taxonomia de Tiers de Modelos e Mapeamento de Ferramentas

A eficiência de custo e velocidade deste runbook apoia-se em uma separação rigorosa de **2 Tiers de Modelos**, mapeados diretamente para a ferramenta `invoke_subagent`:

| Tier | Modelos Conceituais | Parâmetro invoke_subagent | Perfil de Custo / Latência | Casos de Uso no Runbook |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1 (Fast / Economic)** | `Gemini Flash` / `Claude Haiku` | `Model: 'flash'` (ou `'flash_lite'`) | **Muito Baixo Custo / Ultra Rápido** (~75-80% do volume total de chamadas) | • Fase 1 (Auditoria Unificada em lotes)<br>• Fase 3 (Revisão adversarial pontual)<br>• Fase 6: Etapa 4 e Etapa 5 |
| **Tier 2 (High-Reasoning)** | `Gemini Flash (High)` / `Pro` / `Claude Sonnet` | `Model: 'pro'` (ou `'inherit'`) | **Alto Raciocínio / Julgamento Complexo** (~20-25% do volume total) | • Agente Principal (Orquestrador)<br>• Fase 2 (Cluster & Judge)<br>• Fase 3 (Revisão adversarial arquitetural)<br>• Fase 4 (Conciliação inline)<br>• Fase 6: Etapas 1, 2 e 3<br>• Fase 7 (Verificação final) |

> ⚠️ **Restrição Crítica de Ferramenta:** A ferramenta `invoke_subagent` aceita estritamente o enum `['inherit', 'flash_lite', 'flash', 'pro']`. Nunca passe nomes comerciais livres (ex: `"Claude 3.5 Haiku"` ou `"Gemini 3.7 Flash"`) no parâmetro `Model`, pois isso causa erro fatal de validação de schema.

### Agente Principal (Orquestrador): **Tier 2 — 'pro' ou 'inherit'**
Rode a sessão principal sempre em Tier 2. O motivo:
- A **conciliação (Fase 4) roda inline no orquestrador** — recalcular estados e arbitrar destinos com precedência estrita exige alto discernimento.
- O orquestrador é a **rede de segurança entre fases**: valida a integridade das saídas antes de disparar a próxima etapa.
- Erro de orquestração é o mais caro de um sistema multi-agente; garantir precisão no nó central protege 100% dos fan-outs seguintes.

---

## 0. Verdade-base do projeto (verificar antes, nunca assumir de memória)

Os projetos reais disponíveis ficam em `projects/` (symlinks). Hoje:
- `projects/engeapp` (Laravel 13 + PHP 8.4 + MySQL, front Vue 3 SPA)
- `projects/MaxComponentsUi` (Biblioteca de componentes Vue 3 locais)
- `projects/MaxPinia` (Camada de cache e persistência de stores)
- `projects/MaxUse` (Utilitários e integração de rotas Ziggy no front)
- `projects/MaxCode` (Sidecar e ferramentas do agente)

**Confirme quais existem** com `ls -l projects/` no início — repositórios citados em skills sem correspondente em `projects/` (ex.: legados como `SocialMedia` ou `AgenteDeBolso`) devem ser avaliados pelo que der para inferir e registrados como *limitação contextual*, nunca como erro da skill.

Convenções fundamentais confirmadas no código real:
- **Rotas do front = NOMES Ziggy pontilhados**, não caminhos `/api/...`. Os helpers `apiGetRoute('cliente.data', params)` / `apiPostRoute('cliente.save', payload)` do `@maxvue/max-use` recebem o **nome** da rota. Ziggy **está** configurado (`resources/app.ts`: `ZiggyVue` + `route`).
- **Sem libs cruas de terceiros no ecossistema Engeapp:** nada de `vueuse`/`lodash`/`primevue` direto. Usar `@maxvue/max-use` (reexporta VueUse + utilitários) e componentes `Max*` de `@maxvue/max-components-ui`.
- **Contrato MaxPinia:** store com `isCached = ref(true)` + `options` (`get.route`, `save`, `key`, `enabled`), `data`, `status.server.get.is_requested`/`is_success`. A chave real de cache do LocalForage é `getKey() = store.$id + (store.id ?? options.id)` — **`options.key` NÃO é a chave de cache** (é convenção que casa com `$id`). Todo GET de página passa por store MaxPinia.
- **Sem camada `services/` no front.** Mutações via `apiPostRoute` a partir de stores.
- **Laravel é v13 / PHP 8.4.** Nenhuma menção a AdonisJS em `created-skills/`.
- Comentários de código nas skills em **pt-BR**.

---

## Visão Geral do Fluxo Otimizado

```
Fase 0.5  Pré-Triagem Cadastral          → Script estático zero-token: inventário de arquivos e integridade de parsing YAML
Fase 1    Auditoria Semântica de IA      → Subagentes Tier 1 em Lotes (5-10 skills/subagente): 13 critérios semânticos + conformidade real + bloat
Fase 2    Redundância Inter-Skills       → Agrupamento semântico → Cluster (Tier 2) → Judge de IA paralelo
Fase 3    Revisão Adversarial de IA      → Micro-batching contextual via LLM conferindo código real em projects/
Fase 4    Conciliação de IA              → Raciocínio inline no Orquestrador: REMOVER > FUNDIR > PODAR > CORRIGIR > MANTER
Fase 5    Tabela Consolidada             → Linha-a-linha 1:1 de todas as skills auditadas pelos subagentes [no-op se tudo MANTER]
Fase 6    Plano de Correção (5 etapas)   → ⛔ PARADA OBRIGATÓRIA: aprovar antes de executar (Pipelines de contexto quente)
Fase 7    Verificação Adversarial Final  → Tier 2 focado em alto risco (Críticas, Ruins, Merges)
Fase 8    Versionamento (git)            → ⛔ commit/push/merge SÓ sob pedido explícito do humano
```

**Fases 0.5 a 5 executam SEMPRE de forma direta e read-only.** Não modificam arquivos de skills nem executam comandos git. Ao receber a ordem de rodar o runbook, execute direto até a Fase 5.

---

## Fase 0.5 — Pré-Triagem Cadastral e Sintática (Zero-Token Fast-Path)

Antes de invocar os modelos LLM, o agente orquestrador roda um inventário puramente estático e mecânico através do script em `docs/scripts/pre_triage.py`:

```bash
python3 docs/scripts/pre_triage.py --target all_skills --output docs/reports/pre_triage.json
```

**Delimitação Estrita de Papel da Fase 0.5:**
- ✅ **O que o script FAZ (restrito à mecânica de arquivos):**
  1. Mapeia a lista completa de caminhos dos arquivos `SKILL.md` existentes.
  2. Valida se o frontmatter YAML possui sintaxe íntegra (não quebra parsers).
  3. Contabiliza o número bruto de caracteres do campo `description` para servir como dado cadastral inicial.
  4. Agrupa a lista por domínios (`created-skills`, `curated-youtube`, `awesome-skills`) para permitir o fatiamento dos lotes de subagentes.
- ❌ **O que o script NUNCA FAZ (estritamente vedado):**
  1. **NÃO avalia a semântica da `description`:** Não julga clareza, intenção, gatilhos, termos discriminantes nem qualidade.
  2. **NÃO classifica estados:** Não define se uma skill é `Excelente`, `Boa`, `Regular`, `Ruim` ou `Crítica`.
  3. **NÃO decide destinos:** Não define `MANTER`, `CORRIGIR`, `PODAR`, `FUNDIR` ou `REMOVER`.
  4. **NÃO substitui a leitura de IA:** O arquivo `pre_triage.json` gerado é apenas o mapa de entrada para que o Orquestrador divida o trabalho entre os subagentes cognitivos de IA.

---

## Fase 1 — Auditoria Semântica Unificada por Subagentes de IA — **Tier 1 (Fast)**

> ### 🛑 AVISO DE EXECUÇÃO: PROIBIDO CRIAR SCRIPTS DE AUDITORIA
> O agente orquestrador **NUNCA deve criar scripts Python (como `audit_engine.py`) para substituir os subagentes**. Toda a análise da Fase 1 deve ser executada por subagentes reais de IA via `invoke_subagent`.

Para auditar as skills com máxima profundidade cognitiva, sem risco de timeout, sem esgotamento de contexto e sem violar limites de taxa (HTTP 429), a orquestração adota **Lotes Semânticos Controlados (5 a 10 skills por subagente)**:

1. Carregue a lista de alvos a partir de `docs/reports/pre_triage.json`.
2. Fatie as skills em lotes de **5 a 10 skills por subagente**.
3. Dispare ondas concorrentes de **5 a 10 subagentes por rodada** em **Tier 1** (`invoke_subagent` com `Model: 'flash'` ou `'flash_lite'`).
4. Conduza a auditoria modularmente por domínio:
   - **Lote A (Prioridade Máxima):** `created-skills/` (88 skills proprietárias) → ~9 a 12 subagentes. Auditoria semântica profunda contra os repositórios reais em `projects/`.
   - **Lote B:** `curated-youtube/` (30 skills) → ~3 a 4 subagentes. Auditoria de escopo, relevância e integridade.
   - **Lote C:** `Agentic Awesome Skills/` (763 skills) → Processado em blocos temáticos/categorias (ex: devops, frontend, backend, test, etc.), 5 a 10 skills por subagente.

---

### Ações Cognitivas Obrigatórias do Subagente de IA

Cada subagente lê o conteúdo de cada `SKILL.md` de seu lote e avalia 5 dimensões semânticas fundamentais:

#### (a) Conformidade Adaptativa com o Código Real
- Ler o `SKILL.md` e referências dele.
- **Se a skill pertencer a `created-skills/`:** para cada afirmação técnica (rota, classe, config, tabela/coluna, componente, lib, método), verificar nos projetos em `projects/` (`grep_search`/`view_file`) e confirmar/refutar contra as convenções da Seção 0.
- **Se a skill for externa (`Awesome Skills` ou `curated-youtube`):** verificar a coerência e exatidão técnica da ferramenta ensinada (ex.: Docker, Git, AWS), sem forçar padrões do Engeapp sobre ela.

#### (b) Avaliação Semântica Aprofundada da Description (Os 13 Critérios Obrigatórios)
A análise da `description` é **essencialmente cognitiva** e NUNCA mecânica. O subagente de IA deve inspecionar semanticamente o texto contra cada uma das 13 regras:
1. **Existência e Extensão (200 a 400 caracteres):** Métrica quantitativa de suporte. Se tiver < 200 caracteres, é curta demais para guiar a seleção; se tiver > 400 caracteres, é longa demais e polui o contexto. *Atenção:* Ter entre 200 e 400 caracteres é apenas um pré-requisito mínimo, NÃO garante aprovação!
2. **Clareza de Ação:** O texto deve expressar com clareza imediata e inequívoca *o que* a skill faz e quais tarefas ela executa.
3. **Inferência Clara de Condição de Uso (Gatilho):** O texto deve deixar óbvio para qualquer outro agente LLM *quando* a skill deve ser acionada (ex.: padrões explícitos como "Use when...", "Ative quando o usuário solicitar...", "Guia para quando for necessário...").
4. **Termos Semanticamente Discriminantes:** Deve conter substantivos técnicos, nomes exatos de bibliotecas, componentes, métodos, entidades ou padrões que funcionem como chaves discriminatórias frente a outras skills similares (ex: `MaxComponentsUi`, `apiGetRoute`, `LocalForage`, `getKey()`, `Pinia`).
5. **Fidelidade Estrita ao Conteúdo Real:** A description deve representar com 100% de precisão o conteúdo real encontrado no corpo do `SKILL.md`. Não pode prometer recursos inexistentes nem omitir o escopo real do documento.
6. **Cobertura de Intenções Reais:** Deve antecipar e cobrir as reais intenções, dúvidas e solicitações típicas de um desenvolvedor ou agente que busca aquela funcionalidade.
7. **Ausência de Generalismo:** Não pode usar termos vagos e genéricos (ex: "ajuda a codificar melhor", "conjunto de boas práticas de programação", "dicas úteis").
8. **Equilíbrio de Amplitude (Não Ampla Demais):** A description não pode reivindicar áreas amplas demais que invadam ou roubem gatilhos de outras skills especializadas do ecossistema.
9. **Equilíbrio de Especificidade (Não Restritiva Demais):** A description não pode ser afunilada a ponto de impedir o acionamento em casos de uso legítimos e diretamente cobertos pela skill.
10. **Linguagem Anti-Promocional (Sem Marketing):** Terminantemente proibido adjetivos vazios ou jargões promocionais (ex: "poderosa", "incrível", "mágica", "melhores práticas mundiais", "código perfeito"). O espaço é puramente utilitário de roteamento técnico.
11. **Ausência de Procedimentos Operacionais:** A description orienta O QUÊ e QUANDO usar. Ela NÃO deve listar comandos passo a passo, tutoriais ou regras de implementação interna que pertencem ao corpo do markdown.
12. **Ausência de Redundâncias:** Não repetir o mesmo conceito com palavras ligeiramente diferentes apenas para preencher espaço.
13. **Densidade de Ganho Semântico:** Cada frase e oração deve agregar uma nova dimensão de valor informativo, restrição de uso ou capacidade técnica.

> ⚠️ **Regra de Julgamento Semântico:** Se a description falhar em qualquer um dos critérios 2 a 13 (mesmo tendo entre 200 e 400 caracteres), o subagente DEVE apontar como problema, classificar a severidade e propor a reformulação textual completa nos padrões ideais.

#### (c) Bloat e Ruído Estrutural
- Detectar seções mortas ou obsoletas que não correspondem a nada usável no projeto.
- Detectar redundância interna e preâmbulos verbosos que não afetam o comportamento do agente.
- Mapear arquivos órfãos em `references/` ou `rules/`.

#### (d) Front-End (Específico para Skills de FrontEnd do ecossistema Engeapp/MaxVue)
- Pular esta etapa quando a skill não for sobre o front-end do projeto:
  - Para componentes genéricos e de uso recorrente, sempre adotar a biblioteca local MaxComponentsUi (`MaxButton`, `MaxIconButton`, `MaxTabs`, `MaxTable`, `MaxTableFields`, `MaxInput*`, `MaxInputSelect`, `MaxTagSelect`, `MaxGrid`, `MaxTitle1`, `MaxTitle2`).
  - Para Funções Helpers no Frontend, sempre adotar "MaxUse".
  - Para Funções Helpers no Frontend, nunca adotar "VueUse" nem "Lodash" diretamente.
  - Para Salvamentos, Cache e Salvamentos Automáticos no Frontend, adotar Stores Pinia com "MaxPinia".
  - O Formato dos nomes de arquivos pinia deverá ser `Use{NomeStore}.Store.ts` (ex: `UseSystm.Store.ts`).
  - **Classes no front-end:** não fazer uso de **classes utilitárias inline** no template (ex.: Tailwind/UnoCSS inline como `class="p-4 rounded-2xl"`). Adotar classes semânticas (ex.: `class="contact-info"`) com estilização isolada na seção `<style lang="scss">`.

#### (e) Resumo-map e Roteamento de Revisão
- Extração concisa: tema (1 frase), entidades citadas (libs, rotas, componentes, classes) e ~10 a 20 palavras-chave discriminantes.
- Classificação de `reviewModel` para a Fase 3:
  - `"Tier 1 (Fast)"` — problema factual pontual e localizado (1 citação verificável em 1 arquivo). Cortes de bloat padrão.
  - `"Tier 2 (High-Reasoning)"` — problema arquitetural/estrutural: fluxo, contrato ou design multi-arquivo (ex.: padrão multi-tenant, ciclo de vida complexo, guards).

---

### Template de Prompt Padronizado para Invocação dos Subagentes da Fase 1

O Orquestrador dispara cada subagente com um prompt estruturado contendo a lista das 5 a 10 skills do lote:

```text
Você é um Auditor Semântico Especialista em Skills de IA.
Sua missão é realizar a auditoria semântica profunda e cognitiva do seguinte lote de skills:
[LISTA COM CAMINHOS DAS 5 A 10 SKILLS DO LOTE]

Para CADA skill:
1. Leia o arquivo SKILL.md completo.
2. Avalie rigorosamente a DESCRIPTION contra os 13 Critérios Semânticos (extensão 200-400 chars, clareza, gatilhos de ativação, termos discriminantes, fidelidade ao corpo da skill, intenções cobertas, não-genérica, não ampla, não restritiva, zero marketing/adjetivos promocionais, zero procedimentos passo a passo, zero redundância, densidade semântica real).
3. Se for do ecossistema Engeapp (created-skills/), valide as afirmações técnicas contra os projetos reais em projects/ (MaxComponentsUi, MaxPinia, MaxUse, Laravel 13).
4. Avalie Bloat (seções mortas, preâmbulos vazios, redundâncias).
5. Extraia o mapSummary (tema, entidades, keywords).

Retorne OBRIGATORIAMENTE um array JSON contendo um objeto para cada skill no seguinte formato:
[
  {
    "skillName": "string",
    "skillPath": "string",
    "state": "Excelente | Boa | Regular | Ruim | Crítica",
    "problemCount": 0,
    "problems": [
      { "text": "descrição qualitativa do problema com evidência", "reviewModel": "Tier 1 (Fast) | Tier 2 (High-Reasoning)" }
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
]
```

**Régua de Estado:**
- **Excelente:** 100% aderente sem pendências conceituais nem de descrição.
- **Boa:** Conteúdo correto, ajustes estritamente semânticos de redação/gatilhos na `description` ou formato.
- **Regular:** Desacordos superficiais ou pontuais (ex.: 1 convenção simples, pequenas omissões).
- **Ruim:** Múltiplos desacordos técnicos ou descrição severamente distorcida/omisso-promocional.
- **Crítica:** Ensina arquitetura/APIs inexistentes, quebra convenções estruturais vitais ou ausência total de discriminantes.

**Régua de Bloat:** **ENXUTA** (0%) | **PODAR** (< 25%) | **INCHADA** (≥ 25%).

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

> **Origem Obrigatória dos Dados:** Esta consolidação deve ser compilada **exclusivamente a partir dos vereditos semânticos emitidos pelos subagentes de IA nas Fases 1, 2 e 3**. É expressamente proibido rodar scripts para inventar vereditos ou simular a saída desta fase.
> 
> **Regra de Formato:** A tabela apresentada ao humano deve conter **exatamente N linhas** (onde N = total de `SKILL.md` auditados), ordenada por severidade (`Crítica → Ruim → Regular → Boa → Excelente`) e nº de problemas decrescente. O relatório completo é salvo pelo Orquestrador em `docs/reports/fase_5_consolidado.md`:

| # | Skill | Estado | Nº de problemas | Destino | Descrição dos problemas |
|---|-------|--------|------------------|---------|--------------------------|
| 1 | `vue-axios-api-integration-best-practices` | Regular | 1 | CORRIGIR | Uso de rotas cruas `/api/...` no frontend — deve adotar Ziggy com `@maxvue/max-use`. |
| 2 | `frontend-design-best-practices` | Boa | 0 | MANTER | 100% aderente ao design system Engeapp, Vue 3 e MaxComponentsUi. |
| … | … | … | … | … | … |

Acompanhada de:
- Distribuição quantitativa por Estado e Destino.
- Seções de apoio opcionais (ex.: lista de pares `FUNDIR`, lista de `DEMARCAR`).

### Critério de Parada Rápida (No-Op)
Se todas as skills resultarem em destino **`MANTER`** (zero problemas confirmados pela auditoria de IA), o runbook encerra imediatamente exibindo: **"Nenhuma correção necessária — todas as skills em MANTER"**, economizando 100% dos tokens das Fases 6 a 8.

---

## Fase 6 — Plano de Correção em 5 Etapas (Contexto Quente)

> ### ⛔ PARADA OBRIGATÓRIA DE APROVAÇÃO HUMANA
> Após estruturar o plano de 5 etapas e **antes** de modificar qualquer arquivo, **PARE e apresente o plano ao humano**. Não execute nenhuma modificação sem autorização explícita.

Ao receber aprovação, execute as etapas organizadas para encolher a base e maximizar o reaproveitamento de contexto:

- **Etapa 1 — Remoções + Merges (Tier 2):**  
  Apaga as skills `REMOVER`, executa a fusão das skills `FUNDIR` sem perda de conteúdo e atualiza os manifestos de índice correspondentes na raiz:
  - `index.json` (para `created-skills/`)
  - `awesome_skills.json` (para `Agentic Awesome Skills/`)
  - `other_skills.json` (para `curated-youtube/`)  
  Encolhe o total de skills para as etapas seguintes.
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
- [ ] **0 Menções a AdonisJS em `created-skills/`:** Nenhuma referência à stack legada no ecossistema Engeapp.
- [ ] **0 Rotas `/api/...` no Frontend:** Utilização estrita de rotas Ziggy pontilhadas com `@maxvue/max-use`.
- [ ] **0 Violações MaxPinia:** Contrato `getKey()` respeitado, sem confusão com `options.key`.
- [ ] **Manifestos e Índices Atualizados:** `index.json`, `awesome_skills.json` e `other_skills.json` consistentes após qualquer remoção ou merge.
- [ ] **Relatórios Arquivados em `docs/reports/`:** Registro auditável de todas as fases mantido na pasta `docs/reports/`.

---

## Tabela de Impacto e Eficiência (Benchmark Estimado)

| Dimensão | Abordagem Anterior (Não Otimizada) | Runbook Otimizado de IA (Este) | Ganho / Eficiência Real |
| :--- | :--- | :--- | :--- |
| **Profundidade Semântica** | Risco de automações mecânicas rasas / regex | **100% IA Semântica (13 critérios avaliados por LLM)** | **Rigor técnico máximo sem atalhos artificiais de scripts** |
| **Arquitetura de Execução** | Subagente individual por skill (881 chamadas) | **Lotes Semânticos Controlados (5-10 skills/subagente)** | **Redução drástica de overhead sem perda cognitiva** |
| **Consumo de Tokens** | ~5.200.000 tokens (sem batching) | **~1.600.000 tokens** | **~69% de economia por contexto compartilhado** |
| **Chamadas de Revisão (Fase 3)** | 1 subagente / problema (~120 chamadas) | Micro-batching contextual (~30 chamadas) | **-75% de round-trips** |
| **Triagem Sintática Inicial** | 100% tokens de LLM para ler sintaxe | Pré-triagem determinística cadastral (Fase 0.5) | **Zero tokens gastos com parsing mecânico de YAML** |
| **Reaproveitamento de Contexto** | Releituras do zero a cada chamada | Pipelines de contexto quente por domínio | **Arquivos de projeto em projects/ lidos 1x por domínio** |
