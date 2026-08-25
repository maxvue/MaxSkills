# Auditar, Corrigir e Otimizar Skills

Runbook para auditar, validar e otimizar **todas as skills de `created-skills/`** contra o
código real dos projetos de referência em `projects/`. Escrito para ser executado por um agente
autônomo (Claude Code) do início ao fim, com orquestração multi-agente.

> **Idioma:** conduza toda a conversa com o humano em **pt-BR**.
> **Escopo:** somente `created-skills/`. **NÃO** altere `awesome-skills/`, `created-skills-adonis/`
> nem qualquer coisa fora de `created-skills/`.
> **Ferramenta de apoio (uso restrito — não carregar em toda fase):** a
> `skill-creator@claude-plugins-official` (skill oficial da Anthropic) é referência do que
> caracteriza uma boa `SKILL.md` (description acionável, progressive disclosure, instruções
> imperativas com o *porquê*). **Só instrua o subagente a carregá-la quando a tarefa envolve
> julgar/reescrever FORMA ou `description`** — ou seja, apenas em: Fase 1 quando o problema
> encontrado é de forma/gatilho (não em toda verificação técnica), Etapas 2 e 3 do plano (reescrita
> de Críticas/Ruins, que reconstroem a description), e Etapa 5 (Boas — é literalmente ajuste de
> forma). Nas Fases 2 e 3 e nas Etapas 1 e 4 do plano, a tarefa é técnica/factual (redundância,
> refutação, remoção/merge de conteúdo) — **não carregue a skill-creator ali**, ela não agrega e só
> consome tokens à toa.

### Agente principal (orquestrador): **Gemini 3.7 Flash (High)**

Rode a sessão principal em **Gemini 3.7 Flash (High)**. O motivo não é os subagentes (esses têm `model` declarado por
chamada e não herdam nada) — é o que o próprio orquestrador faz sozinho:
- A **conciliação (Fase 4) roda inline no agente principal** — recalcular estados e atribuir
  destinos é julgamento, e um erro ali contamina todo o plano.
- O orquestrador é a **rede de segurança entre fases**: já houve caso real em que ele detectou uma
  imprecisão que os próprios subagentes introduziram (contrato `getKey()` do MaxPinia), relendo o
  código-fonte — captura que valeu mais que o custo do loop principal inteiro.
- **Erro de orquestração é o mais caro do sistema**: um script de Workflow mal montado ou uma
  conciliação errada desperdiça fan-outs inteiros. O custo total é dominado pelos subagentes
  (~90%); economizar no principal rende pouco e concentra risco.

*Exceção:* re-execuções em base já polida (esperando o no-op da Fase 5) podem rodar com o principal
em Gemini 3.7 Flash (High) — ali só há orquestração de auditoria e a apresentação de "nada a fazer".

---

## 0. Verdade-base do projeto (verificar antes, nunca assumir de memória)

Os projetos reais ficam em `projects/` (symlinks). Hoje: `engeapp` (Laravel 13 + PHP 8.4 + MySQL,
front Vue 3 SPA), `MaxComponentsUi`, `MaxPinia`, `MaxUse`. **Confirme quais existem** com
`ls projects/` no início — pode haver alvos de skill sem projeto correspondente (ex.: MaxBanks):
nesse caso avalie pelo que der para inferir e registre como *limitação*, não como erro.

Convenções que já se provaram fonte recorrente de erro nas skills — todo subagente deve tratá-las
como verdade e conferir contra elas:

- **Rotas do front = NOMES Ziggy pontilhados**, não caminhos `/api/...`. Os helpers
  `apiGetRoute('cliente.data', params)` / `apiPostRoute('cliente.save', payload)` do `@maxvue/max-use`
  recebem o **nome** da rota. Ziggy **está** configurado (`resources/app.ts`: `ZiggyVue` + `route`).
- **Sem libs cruas de terceiros:** nada de `vueuse`/`lodash`/`primevue` direto. Usar `@maxvue/max-use`
  (reexporta VueUse + utilitários) e componentes `Max*` de `@maxvue/max-components-ui`.
- **Contrato MaxPinia:** store com `isCached = ref(true)` + `options` (`get.route`, `save`, `key`,
  `enabled`), `data`, `status.server.get.is_requested`/`is_success`. A chave real de cache do
  LocalForage é `getKey() = store.$id + (store.id ?? options.id)` — **`options.key` NÃO é a chave de
  cache** (é convenção que casa com `$id`). Todo GET de página passa por store MaxPinia.
- **Sem camada `services/` no front.** Mutações via `apiPostRoute` a partir de stores.
- **Laravel é v13 / PHP 8.4.** **Nenhuma menção a AdonisJS** em `created-skills/`.
- Comentários de código nas skills em **pt-BR**.

Grave/atualize essas descobertas na memória do agente ao final, para não repetir os mesmos erros.

---

## Visão geral do fluxo

Todas as **detecções** (conformidade, bloat e redundância) rodam antes de qualquer plano. Só depois
de conciliar os sinais é que cada skill recebe um **destino** e entra no plano de correção — assim
nenhum subagente reescreve no detalhe uma skill que deveria ser **removida, fundida ou podada**.

```
Fase 1  Auditoria unificada          → 1 verificador/skill: conformidade + bloat + resumo-map numa passada
Fase 2  Redundância entre skills     → cluster(1, barreira sobre os resumos da Fase 1) → judge(1/cluster)
Fase 3  Revisão adversarial          → 1 revisor/problema, modelo = reviewModel do achado (tenta refutar 1 e 2)
Fase 4  Conciliação                  → cruza tudo; atribui DESTINO por skill (regra de precedência)
Fase 5  Tabela consolidada           → estado + destino + nº + descrição  [no-op: para aqui se tudo MANTER]
Fase 6  Plano de correção (5 etapas) → ⛔ PARADA OBRIGATÓRIA: aprovar antes de executar
Fase 7  Verificação adversarial final
Fase 8  Versionamento (git)          → ⛔ commit/push/merge SÓ sob pedido explícito do humano
```

**Fases 1–5 executam SEMPRE, direto, SEM perguntar.** Elas são inteiramente **read-only** — leem o
código, avaliam e produzem a tabela consolidada; não modificam nenhuma skill, arquivo ou git. Não há
nada a autorizar. Ao receber a ordem de rodar o runbook, comece pela Fase 1 e vá até a Fase 5 sem
interromper para pedir confirmação (a única saída antecipada é o **no-op** da Fase 5, quando não há
nada a corrigir).

Há **dois checkpoints humanos obrigatórios**, ambos ANTES de qualquer efeito colateral: (a) após
montar o plano na Fase 6, antes de modificar qualquer skill; (b) na Fase 8, antes de qualquer
operação de git. Aprovar um **não** autoriza o outro, e autorizar auditar **não** autoriza nenhum
dos dois.

Use a ferramenta **Workflow** para orquestrar cada fase (fan-out determinístico com `parallel`/
`pipeline` e saída estruturada via `schema`). O limite de concorrência (~16) é automático; pode
passar todos os itens de uma vez.

> **Por que as detecções vêm ANTES do plano:** irrelevância e redundância mudam o *destino* da
> skill. Se só forem descobertas depois, o plano gasta agentes reescrevendo algo que deveria sumir
> ou se fundir. Detectar primeiro faz cada skill entrar no plano **uma vez, no balde certo**.

---

## Fase 1 — Auditoria unificada (1 subagente verificador por skill) — **Gemini 3.7 Flash (High)**

> **Execute as Fases 1–5 automaticamente, sem pedir confirmação.** São read-only (nenhuma edição em
> skills, arquivos ou git). Vá direto da Fase 1 à Fase 5; só pare cedo no no-op (Fase 5).

Uma única passada produz os **três sinais por skill**: conformidade + bloat + resumo-map. O motivo é
economia real: o verificador já pagou o custo de carregar a skill inteira e os arquivos relevantes de
`projects/` — julgar bloat e extrair o resumo no mesmo contexto custa algumas centenas de tokens de
*output*, contra duas releituras completas se fossem fases separadas. **Não divida em passadas
separadas.**

1. Liste os alvos: `find created-skills -name SKILL.md`. (~90–100 skills.)
2. Dispare **1 subagente verificador por `SKILL.md`**.

**Ação do verificador (3 sinais na mesma chamada):**

**(a) Conformidade** — verificar de forma profunda e detalhada se **todas** as informações da skill
condizem, em sua totalidade, com estrutura, uso, métodos, linguagem, bibliotecas, arquitetura e
coerência dos projetos em `projects/`:
- Ler o `SKILL.md` inteiro **e** os arquivos em `references/`/`rules/` dele.
- Para **cada** afirmação técnica verificável (rota, classe, config, tabela/coluna, componente, lib,
  método, caminho de arquivo), **abrir o código real** (`Grep`/`Read`/`Glob` em `projects/`) e
  **confirmar ou refutar**. Nunca julgar de memória.
- Conferir contra as convenções da seção 0. Só carregue a `skill-creator` se a suspeita de problema
  for de forma/description — não carregue por padrão em toda verificação técnica.
- **Não editar nada** — só relatar.

**(b) Bloat** — com a skill já carregada, avaliar se o conteúdo está enxuto e útil, ou se há coisa
"ocupando espaço à toa":
- **Seções mortas** — descrevem algo que não corresponde a nada usável no projeto.
- **Redundância interna** — mesma instrução repetida em 3 seções; exemplos que provam o mesmo ponto.
- **Verbosidade** — texto que não muda o comportamento do leitor; enrolação, preâmbulo.
- **Referências mortas** — arquivos em `references/`/`rules/` que nada aponta ou que ninguém leria.

(Julgamento de forma/progressive-disclosure via skill-creator fica para a Etapa 5 do plano — aqui o
foco é só conteúdo técnico redundante ou sem uso, não estrutura do documento.)

**(c) Resumo-map** — ainda no mesmo contexto, extrair o resumo que alimenta a detecção de
redundância da Fase 2: tema em 1 frase, entidades citadas (libs/classes/rotas/componentes) e ~10
palavras-chave. É extração mecânica; não gaste raciocínio extra aqui.

**`reviewModel` — classifique cada problema/corte:** quem encontrou o problema é quem está em melhor
posição para julgar sua complexidade (o revisor da Fase 3, sem esse contexto prévio, teria que
redescobri-la do zero). Critério:
- `"Gemini 3.7 Flash (High)"` — problema **factual pontual e localizado**: 1 citação (nome de rota/config/tabela/
  coluna/classe/caminho) que basta abrir 1 arquivo e comparar para confirmar/refutar. A maioria dos
  cortes de bloat cai aqui (checagem local — "essa seção repete a de cima, sim/não").
- `"Gemini 3.7 Flash (High)"` — problema **arquitetural/estrutural**: afirma um fluxo, contrato ou design que só se
  julga entendendo como várias peças se encaixam (ex.: "o multi-tenant usa X padrão", "o guard de
  rota segue Y lógica") — exige julgamento amplo, não uma checagem isolada. Em bloat, use `"Gemini 3.7 Flash (High)"`
  só quando o corte depende de julgar se a seção documenta algo raro/não-óbvio do projeto.
- Na dúvida, classifique como `"Gemini 3.7 Flash (High)"` (custo do falso-negativo aqui é maior que o de gastar mais).

**Saída estruturada** (um objeto por skill, com os 3 sinais):

```json
{
  "skillName": "string",
  "skillPath": "string",
  "state": "Excelente | Boa | Regular | Ruim | Crítica",
  "problemCount": 0,
  "problems": [
    { "text": "1 problema concreto, com evidência (arquivo/linha real ou trecho da skill)", "reviewModel": "Gemini 3.7 Flash (High) | Gemini 3.7 Flash (High)" }
  ],
  "bloatVerdict": "ENXUTA | PODAR | INCHADA",
  "estimatedCutPct": 0,
  "cuts": [
    { "text": "seção/trecho a remover ou condensar, com o porquê", "reviewModel": "Gemini 3.7 Flash (High) | Gemini 3.7 Flash (High)" }
  ],
  "mapSummary": {
    "tema": "1 frase",
    "entidades": ["libs/classes/rotas/componentes citados"],
    "keywords": ["~10 palavras-chave"]
  },
  "summary": "veredito em 1 frase"
}
```

Régua de estado (conformidade):
- **Excelente** — totalmente de acordo, nenhuma correção necessária.
- **Boa** — apenas correções a nível da própria skill (formato, seções, otimização/redação).
- **Regular** — correções superficiais em desacordo com o projeto.
- **Ruim** — correções medianas em desacordo com o projeto e/ou estrutura da skill.
- **Crítica** — problemas graves (ex.: ensina API/lib/rota/arquitetura inexistente).

Régua de bloat:
- **ENXUTA** — nada a cortar.
- **PODAR** — cortes localizados (< ~25% do conteúdo).
- **INCHADA** — reestruturação/encolhimento significativo (≥ ~25%).

> **Dica de orquestração:** subagentes normalmente não conseguem escrever arquivos de relatório —
> faça-os **retornar** o objeto estruturado e persista você (agente principal) a partir do
> `journal.jsonl` do workflow.

---

## Fase 2 — Redundância entre skills (cluster → judge) — **Gemini 3.7 Flash (High)**

Redundância é um julgamento **entre pares** — não paraleliza de forma ingênua. Se você der lotes
cegos a N agentes, cada um só vê o próprio lote e **nunca compara** uma skill do lote 1 com uma do
lote 7 → duas skills quase idênticas em pastas diferentes escapam. O insumo desta fase são os
`mapSummary` que a Fase 1 já produziu (não há passada de "map" separada — foi fundida na Fase 1).

**2.1 Cluster (1 agente — BARREIRA) — Gemini 3.7 Flash (High).** Com a tabela de TODOS os `mapSummary` da Fase 1 junta,
agrupa candidatos a sobreposição por afinidade (tema + entidades em comum). Ainda que o agrupamento
seja barato, é aqui que se decide quais skills são candidatas a MERGE/DEMARCAR — um julgamento cujo
erro (deixar passar um cluster de duplicatas, ou juntar skills que não se sobrepõem) se propaga para
o Judge; use Gemini 3.7 Flash (High). Saída: lista de **clusters suspeitos** (2–4 skills cada), ex.:
`vue-axios ↔ vue-pinia ↔ vue-max-use-usecachedapi` (todos falam de fetch/cache).

**2.2 Judge (fan-out, 1 agente/cluster) — Gemini 3.7 Flash (High).** Cada agente lê **só as skills daquele cluster** e
decide se são de fato redundantes — julgamento factual/crítico, não mecânico:

```json
{
  "cluster": ["skillA", "skillB"],
  "recommendation": "MERGE | DEMARCAR | FALSO-POSITIVO",
  "into": "skill que absorve (se MERGE)",
  "rationale": "por que; o que cada uma tem de único",
  "mergePlan": "como fundir sem perda de conteúdo (se MERGE)",
  "reviewModel": "Gemini 3.7 Flash (High) | Gemini 3.7 Flash (High)"
}
```

- **MERGE** — fundir sem perda (já houve precedente: `vue-code-generators → vue-max-stack`).
- **DEMARCAR** — manter ambas, mas com escopos/cross-refs claros para os gatilhos não conflitarem.
- **FALSO-POSITIVO** — parecem, mas cobrem coisas distintas; deixar como está.

`reviewModel` aqui costuma ser `"Gemini 3.7 Flash (High)"` (comparar 2-4 skills inteiras exige julgamento amplo), mas
use `"Gemini 3.7 Flash (High)"` nos casos óbvios — ex.: duas skills que são cópias quase literais uma da outra, onde
a checagem é só confirmar a sobreposição, não julgar nuance.

> **Barreira obrigatória:** o passo 2.1 precisa dos `mapSummary` de TODAS as skills → a Fase 1 deve
> ter concluído por completo antes do cluster; depois `parallel` no judge.

---

## Fase 3 — Revisão adversarial (1 subagente revisor por problema) — **modelo por `reviewModel`**

Para **cada problema** apontado nas Fases 1–2 (problemas de conformidade e cortes de bloat da Fase 1;
recomendações de merge/remoção do judge da Fase 2), dispare **1 revisor** que tenta **refutar** —
provar que não procede ou está mal descrito. Ele abre o código real e checa independentemente,
assumindo por padrão que a acusação **pode estar errada**.

**O modelo do revisor NÃO é fixo — vem do campo `reviewModel` que o próprio agente que encontrou o
problema já anexou.** Quem viu o problema primeiro está em melhor posição para julgar sua
complexidade do que um revisor sem esse contexto, que teria que redescobri-la do zero. Ao montar a
chamada de cada revisor, leia `problem.reviewModel` e propague direto:
`agent(prompt, { schema, phase: 'Revisar', model: problem.reviewModel })`. Não force Gemini 3.7 Flash (High) em tudo
por padrão — isso desperdiça o ganho de ter a classificação vinda da origem.

**Saída estruturada** (um objeto por problema):

```json
{
  "skillName": "string",
  "problem": "texto do problema/recomendação avaliado",
  "verdict": "CONFIRMADO | REFUTADO",
  "evidence": "arquivo/linha real que sustenta o veredito",
  "correctedDescription": "versão corrigida se CONFIRMADO e a descrição estava imprecisa; senão vazio"
}
```

> Se o volume for grande, agrupe por skill (1 revisor refuta a lista da skill) — mas **só agrupe
> problemas com o mesmo `reviewModel`** (não misture um lote `Gemini 3.7 Flash (High)` com um problema `Gemini 3.7 Flash (High)`; nesse
> caso o lote inteiro rodaria no modelo mais caro à toa, ou o problema `Gemini 3.7 Flash (High)` seria mal avaliado).
> Mantenha o veredito **por problema**.

---

## Fase 4 — Conciliação (define o DESTINO de cada skill)

Funde os três sinais (conformidade + bloat + redundância), já filtrados pela revisão adversarial, e
atribui a cada skill **um destino único**. Regra de **precedência** (resolve conflitos):

> **REMOVER** > **FUNDIR** (merge) > **PODAR** (bloat) > **CORRIGIR** (conformidade) > **MANTER**

Regra de ouro: **nunca reescrever no detalhe uma skill marcada para FUNDIR ou REMOVER.** Um MERGE já
reconcilia o conteúdo das duas; uma REMOÇÃO dispensa correção. Só as skills que **sobrevivem** ao
filtro de redundância/irrelevância entram nas etapas de correção de conformidade.

Passos:
- Mantenha apenas problemas **CONFIRMADOS**; descarte **REFUTADOS**. Use as descrições corrigidas.
- **Recalcule o estado** de conformidade a partir dos problemas sobreviventes.
- Atribua o **destino** por precedência.
- Persista o conciliado (ex.: `created-skills/AUDIT-CONFORMIDADE-PROJECTS.md` + um JSON compacto no
  scratchpad para as fases seguintes).

### Guarda anti-churn (regra dura)

Um problema **não CONFIRMADO** pela revisão adversarial da Fase 3 é **IGNORADO** — ponto. Não entra
na conciliação, não vira briefing, não gera edição. Isto vale inclusive para sugestões puramente
estéticas ("eu redigiria diferente", "ficaria mais bonito assim"): **sem problema confirmado, não se
edita**. O objetivo é impedir que rodadas sucessivas fiquem reescrevendo o mesmo texto por gosto
(churn) — o workflow **converge**, não acumula. Só há edição onde há defeito confirmado contra o
código real.

---

## Fase 5 — Tabela consolidada

> **Formato OBRIGATÓRIO: uma linha por skill, sem exceção.** A tabela final apresentada ao humano
> tem **exatamente N linhas de dados**, onde N = quantidade de `SKILL.md` auditados na Fase 1 —
> nunca um resumo agrupado por destino, cluster ou "principais problemas". Agrupar por
> destino/cluster é útil como **seção de apoio depois** da tabela (ex.: destacar os pares FUNDIR, ou
> os Críticos), mas **não substitui** a listagem completa skill-a-skill. Se a tabela sair com menos
> linhas do que skills auditadas, está errada — refaça.

Apresente ao humano a tabela completa, ordenada por severidade (Crítica → Ruim → Regular → Boa →
Excelente) e, dentro do mesmo estado, por nº de problemas decrescente:

| # | Skill | Estado | Nº de problemas | Destino | Descrição dos problemas |
|---|-------|--------|------------------|---------|--------------------------|
| 1 | `laravel-editorial-calendar-event-workflow` | Crítica | 9 | CORRIGIR | Ensina `AiPipeline`/trait `AdvancesEventStatus`/enum/model/observer inexistentes — real é `EventObserver::updated()` + `App\Models\Calendar\Event`. |
| 2 | `laravel-social-media-oauth-token-lifecycle` | Crítica | 8 | CORRIGIR | Ensina padrão Strategy/Driver/Manager e job de renovação e colunas cifradas que não existem no projeto. |
| … | … | … | … | … | … |

Colunas:
- **Skill** — nome exato (campo `name` do frontmatter), não o caminho.
- **Estado** — `Excelente | Boa | Regular | Ruim | Crítica` (régua da Fase 1, já conciliada na Fase 4).
- **Nº de problemas** — contagem de problemas **CONFIRMADOS** que sobreviveram à Fase 3 (revisão
  adversarial); não conte os REFUTADOS.
- **Destino** — `REMOVER | FUNDIR→<skill-alvo> | PODAR (~N%) | CORRIGIR | MANTER`, da Fase 4.
- **Descrição dos problemas** — 1–2 frases objetivas resumindo os problemas confirmados dessa skill
  específica (não uma frase genérica de categoria). Se `problemCount = 0`, escreva "Nenhuma correção
  necessária.".

Depois da tabela completa, **acompanhe com**:
- Distribuição por **Estado** (quantas Excelente/Boa/Regular/Ruim/Crítica) e por **Destino**
  (quantas REMOVER/FUNDIR/PODAR/CORRIGIR/MANTER), com o total geral.
- Se quiser, seções de apoio agrupadas (ex.: lista dos pares FUNDIR, lista dos DEMARCAR) — mas
  **depois** da tabela linha-a-linha, nunca no lugar dela.

### Critério de parada (no-op)

Se, após a conciliação, **nenhuma** skill tiver destino diferente de `MANTER` (ou seja, zero
problemas CONFIRMADOS e zero recomendações de remover/fundir/podar), o runbook **encerra aqui**:
apresenta a tabela consolidada normalmente e, no lugar do plano, informa **"Nenhuma correção a ser
executada — todas as skills em MANTER"**. Não monta as Fases 6–7. Assim, re-rodar numa base já polida
custa apenas a auditoria (rápida) e termina limpo, sem risco de churn. O gatilho real para haver
trabalho é o **código de `projects/` ter mudado** desde a última passada.

---

## Fase 6 — Plano de correção (5 etapas)

> ### ⛔ PARADA OBRIGATÓRIA — após preparar o plano
> Depois de montar o plano de 5 etapas (e antes de disparar QUALQUER agente de correção,
> remoção, merge ou poda), **PARE e apresente o plano ao humano**. **NÃO** execute nenhuma etapa
> sem aprovação explícita. Isto é obrigatório mesmo que o humano já tenha dito "avançar" nas fases
> de auditoria — a autorização para auditar **não** se estende a modificar/remover skills. Aguarde
> um "pode executar" (ou equivalente) antes de seguir. Se o humano pedir ajustes no plano, revise e
> apresente de novo — a parada se repete a cada versão do plano.

Apresente o plano e **execute somente mediante confirmação explícita**. Agora o plano já sabe o destino de cada skill,
então **começa encolhendo o conjunto** (remoções/merges) antes de gastar agentes corrigindo detalhe.
Cada subagente de correção **edita o `SKILL.md` in-place**, ancorado no código real. Só as Etapas 2,
3 e 5 (que reescrevem estrutura/description) carregam a `skill-creator`; as Etapas 1 e 4 são
técnicas/mecânicas e não precisam dela (ver regra de uso restrito no topo do documento).

- **Etapa 1 — Remoções + Merges → 1 subagente por remoção/merge. Gemini 3.7 Flash (High).** Executa primeiro:
  apaga as REMOVER e funde as FUNDIR (sem perda de conteúdo). **Atualiza `manifests/` e o sync de
  skills** a cada remoção/rename. Encolhe o conjunto para as etapas seguintes.
- **Etapa 2 — Críticas (das que sobraram) → 1 subagente por skill. Gemini 3.7 Flash (High).** Reescrita
  profunda: remover seções fabricadas, reconstruir a arquitetura conforme o projeto, corrigir a
  description. Onde o tema não existe no projeto, **não inventar**: reduzir o escopo ao real e
  sinalizar ao humano.
- **Etapa 3 — Ruins → 1 subagente por skill. Gemini 3.7 Flash (High).** Correções medianas: nomes de config/
  env/rota/tabela/coluna reais, remover mecanismos inexistentes, alinhar a convenção de rotas Ziggy.
- **Etapa 4 — Regulares + podas de bloat → lotes de 3–5 skills/agente. Gemini 3.7 Flash (High).**
  Correções superficiais em lote temático **junto** com os cortes de bloat (PODAR/INCHADA) definidos
  na Fase 1. Monte os lotes agrupando por prefixo/pasta (`laravel-*`, `vue-*`) e, dentro disso, por
  área do projeto que a skill mais referencia (Stores, Controllers, componentes Max*, etc.) — skills
  do mesmo grupo tendem a citar os mesmos arquivos reais, maximizando o reaproveitamento de leitura.
- **Etapa 5 — Boas → lotes de 3–5 skills/agente. Gemini 3.7 Flash (High).** Só nível-skill: headings, seções em
  pt-BR, refs quebradas, description 200–400. Sem tocar em técnica — por isso lotes maiores cabem
  bem aqui (é ajuste mecânico, baixo risco de um erro contaminar as demais skills do lote).

> **Lote via `pipeline`, não `parallel`, quando o tema se repete em sequência.** Se você já sabe que
> vários lotes seguidos tocam a mesma área do projeto (ex.: 4 lotes de skills `laravel-*` que citam
> `app/Stores`/`app/Services/Calendar`), rode esses lotes com `pipeline` num único agente (chamadas
> sequenciais que reaproveitam o que já foi lido) em vez de `parallel` com agentes novos a cada lote —
> um agente novo por lote reabre os mesmos arquivos do zero; encadear em `pipeline` mantém o contexto
> "quente". Use `parallel` entre grupos de temas **diferentes** (não há nada a reaproveitar) e
> `pipeline` dentro do mesmo tema.

Concluídas as 5 etapas, siga para a **Fase 7** (verificação adversarial final) — ela não é uma etapa
do plano, é a rede de segurança que valida o resultado das etapas.

Para cada subagente de correção, forneça um **briefing por skill** (arquivo no scratchpad com o
destino + veredito conciliado + lista numerada de problemas confirmados) e mande o agente ler o
briefing antes de editar. Faça o subagente **retornar** um resumo estruturado:

```json
{ "name": "string", "changes": ["1 bullet por problema corrigido"], "descriptionLen": 0, "unresolved": ["o que não deu para resolver e por quê"] }
```

---

## Fase 7 — Verificação adversarial final — **Gemini 3.7 Flash (High)**

Após as 5 etapas do plano, dispare **1 verificador por skill de alto risco** (todas as Críticas +
Ruins + as que sofreram merge) tentando **refutar** a versão final contra o código real — veredito
`LIMPA` / `RESIDUAL` / `FALHA` por skill. Faça também um spot-check das Excelentes (garantir que
ficaram intocadas). Corrija pontualmente qualquer `FALHA` (e os `RESIDUAL` relevantes) antes de
fechar, e **atualize a memória** do agente com as convenções e armadilhas reconfirmadas (seção 0),
para a próxima passada não repetir os mesmos erros.

---

## Fase 8 — Versionamento (git) — SOMENTE sob pedido explícito

> ### ⛔ O AGENTE NÃO FAZ COMMIT / PUSH / MERGE POR CONTA PRÓPRIA
> Concluídas as correções e a verificação final, **o agente NÃO deve** executar `git commit`,
> `git push` nem merge por iniciativa própria. Em vez disso, **solicite confirmação ao humano**,
> apresentando o que seria versionado (arquivos alterados, quantas skills, relatórios, manifests).
>
> Regras:
> - **Commit** só acontece se o humano **pedir explicitamente** ("pode commitar", "faça o commit").
>   Nunca commite "para não perder o trabalho" sem esse pedido.
> - **Push** e **merge** são pedidos **separados**: aprovar o commit **não** autoriza push nem merge.
>   Cada um exige seu próprio "ok".
> - Se estiver na branch padrão (`main`), pergunte se deve criar uma branch dedicada antes.
> - Mensagem de commit conforme a convenção do repositório (trailer `Co-Authored-By: …`).
>
> Em resumo: ao final, **pergunte** — "Quer que eu faça o commit? E push/merge?" — e **espere** a
> resposta. O silêncio ou um "obrigado" não é autorização.

---

## Ferramentas a usar

As únicas dependências (SKILLS) obrigatórias para esta execução são:
1. skill-audit
2. skill-creator
3. skill-optimizer
4. manage-skills

O diferencial da auditoria é ler o código real em `projects/` com Grep/Read/Glob):

- **Description-improver (otimizador de *triggering*)** — nas Etapas 2, 3 e 5 (as que reescrevem
  `description`), use o passo do skill-creator dedicado a otimizar a description para a skill disparar
  no contexto certo, dentro dos 200–400 caracteres. Relevante também na Fase 2: descriptions bem
  demarcadas reduzem gatilhos sobrepostos entre skills parecidas.
- **Harness de avaliação (opcional, aprofundamento)** — para as poucas skills de altíssimo valor, use
  o fluxo de eval do skill-creator (`evals/evals.json` → `eval-viewer/generate_review.py` →
  `aggregate_benchmark`) para comparar *com skill* × *sem skill* e provar que a correção/merge
  melhorou o resultado — em vez de confiar só na verificação adversarial qualitativa.

> **Não** adicione skills de processo do harness (systematic-debugging, brainstorming etc.) a este
> runbook: elas orientam *como trabalhar*, não *como auditar skill × código*, e só poluiriam o fluxo.

---

## Checklist de integridade (rodar após cada etapa de edição)

- **YAML válido** em todo `SKILL.md`. Armadilha comum: description **sem aspas** contendo `:` quebra o
  frontmatter → **sempre** colocar a description entre aspas quando houver `:` (ou por padrão).
- **`description` entre 200 e 400 caracteres**, acionável e fiel ao que o projeto realmente faz.
- **0 menções a AdonisJS** em `created-skills/` (fora dos relatórios de auditoria).
- **0 rotas string `/api/...`** passadas a `apiGetRoute`/`apiPostRoute` (preservar `/api` legítimo do
  backend Laravel, DevTools e proxy Vite).
- **0 afirmações “sem Ziggy” / “não passe key” / `options.key` como chave de cache.**
- Após remoções/merges/renames, **`manifests/` e o sync de skills atualizados** e consistentes.

## Notas de orquestração (aprendidas na prática)

- Passe listas para o `Workflow` como **valor JSON real** em `args` (não string JSON), ou faça o
  script `JSON.parse(args)` defensivamente — args stringificado quebra `.map`.
- **Uma passada, três sinais:** a Fase 1 retorna conformidade + bloat + resumo-map do mesmo agente —
  nunca reintroduza passadas separadas de bloat/map: o contexto (skill + código) já foi pago; separar
  triplicaria a leitura para o mesmo resultado.
- **1 agente por unidade só onde há julgamento crítico** (Fase 1; Fase 2 cluster/judge; Fase 3 —
  modelo do `reviewModel` de cada problema; Etapas 1–3 do plano; Fase 7). **Lotes de 3–5 skills por
  agente onde o trabalho é mecânico/padronizado** (Etapas 4–5 — Gemini 3.7 Flash (High)): o ganho não é só menos
  chamadas, é que o agente do lote reaproveita a leitura de `projects/` entre as skills do mesmo
  tema, em vez de cada skill pagar sozinha o custo de reabrir os mesmos arquivos do zero.
- **Dentro do mesmo tema, prefira `pipeline` a `parallel`** para encadear lotes sucessivos no mesmo
  agente (contexto de arquivos já lidos continua "quente"); use `parallel` **entre** temas diferentes,
  onde não há nada para reaproveitar.
- Sempre agregue você mesmo os resultados lendo o `journal.jsonl` do run.
- **Redundância exige barreira**: o cluster (Fase 2.1) só roda com os `mapSummary` de TODAS as skills
  da Fase 1 — não dá para paralelizar cegamente, senão duplicatas em lotes diferentes escapam.
- Escreva **briefings por skill** (ou por lote, nas etapas mecânicas) no scratchpad em vez de embutir
  textos gigantes em `args`.
- Cada skill é um arquivo distinto → agentes de edição de skills **diferentes** rodam em paralelo sem
  worktree. Mas **merges/remoções** que mexem em `manifests/` (arquivo compartilhado) devem ser
  serializados ou reconciliados para não conflitar.
- Se um run de Workflow falhar no meio, **retome com `resumeFromRunId`** em vez de relançar do zero —
  agentes já concluídos retornam do cache sem custo.
