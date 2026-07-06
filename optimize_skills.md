# Auditar, Corrigir e Otimizar Skills

Runbook para auditar, validar e otimizar **todas as skills de `created-skills/`** contra o
código real dos projetos de referência em `projects/`. Escrito para ser executado por um agente
autônomo (Claude Code) do início ao fim, com orquestração multi-agente.

> **Idioma:** conduza toda a conversa com o humano em **pt-BR**.
> **Escopo:** somente `created-skills/`. **NÃO** altere `awesome-skills/`, `created-skills-adonis/`
> nem qualquer coisa fora de `created-skills/`.
> **Ferramenta de apoio:** os subagentes devem usar a `skill-creator@claude-plugins-official`
> (skill oficial da Anthropic) como referência do que caracteriza uma boa `SKILL.md`
> (description acionável, progressive disclosure, instruções imperativas com o *porquê*).

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

Três **detecções** rodam antes de qualquer plano. Só depois de conciliar os três sinais é que cada
skill recebe um **destino** e entra no plano de correção — assim nenhum subagente reescreve no
detalhe uma skill que deveria ser **removida, fundida ou podada**.

```
Fase 1  Auditoria de conformidade   → 1 verificador/skill                (skill × código real)
Fase 2  Auditoria de irrelevância   → 1 agente/skill                     (bloat interno, % de corte)
Fase 3  Auditoria de redundância    → map(1/skill) → cluster(1) → judge(1/cluster)
Fase 4  Revisão adversarial          → 1 revisor/problema                 (tenta refutar 1,2,3)
Fase 5  Conciliação                  → cruza tudo; atribui DESTINO por skill (regra de precedência)
Fase 6  Tabela consolidada           → estado + destino + nº + descrição
Fase 7  Plano de correção (5 etapas) → começa por remoções/merges; depois corrige o que sobra
Fase 8  Verificação adversarial final
```

Use a ferramenta **Workflow** para orquestrar cada fase (fan-out determinístico com `parallel`/
`pipeline` e saída estruturada via `schema`). O limite de concorrência (~16) é automático; pode
passar todos os itens de uma vez.

> **Por que as detecções vêm ANTES do plano:** irrelevância e redundância mudam o *destino* da
> skill. Se só forem descobertas depois, o plano gasta agentes reescrevendo algo que deveria sumir
> ou se fundir. Detectar primeiro faz cada skill entrar no plano **uma vez, no balde certo**.

---

## Fase 1 — Auditoria de conformidade (1 subagente verificador por skill)

1. Liste os alvos: `find created-skills -name SKILL.md`. (~90–100 skills.)
2. Dispare **1 subagente verificador por `SKILL.md`**.

**Ação do verificador:** verificar de forma profunda e detalhada se **todas** as informações da
skill condizem, em sua totalidade, com estrutura, uso, métodos, linguagem, bibliotecas, arquitetura
e coerência dos projetos em `projects/`.

Regras para o verificador:
- Ler o `SKILL.md` inteiro **e** os arquivos em `references/`/`rules/` dele.
- Para **cada** afirmação técnica verificável (rota, classe, config, tabela/coluna, componente, lib,
  método, caminho de arquivo), **abrir o código real** (`Grep`/`Read`/`Glob` em `projects/`) e
  **confirmar ou refutar**. Nunca julgar de memória.
- Conferir contra as convenções da seção 0. Consultar a `skill-creator` para forma/description.
- **Não editar nada** — só relatar.

**Saída estruturada** (um objeto por skill):

```json
{
  "skillName": "string",
  "skillPath": "string",
  "state": "Excelente | Boa | Regular | Ruim | Crítica",
  "problemCount": 0,
  "problems": ["1 problema concreto por item, com evidência (arquivo/linha real ou trecho da skill)"],
  "summary": "veredito em 1 frase"
}
```

Régua de estado:
- **Excelente** — totalmente de acordo, nenhuma correção necessária.
- **Boa** — apenas correções a nível da própria skill (formato, seções, otimização/redação).
- **Regular** — correções superficiais em desacordo com o projeto.
- **Ruim** — correções medianas em desacordo com o projeto e/ou estrutura da skill.
- **Crítica** — problemas graves (ex.: ensina API/lib/rota/arquitetura inexistente).

> **Dica de orquestração:** subagentes normalmente não conseguem escrever arquivos de relatório —
> faça-os **retornar** o objeto estruturado e persista você (agente principal) a partir do
> `journal.jsonl` do workflow.

---

## Fase 2 — Auditoria de irrelevância / bloat (1 subagente por skill)

Julgamento **dentro de uma skill** → paraleliza livre (1 agente por skill, ou lotes). Cada agente
avalia SÓ a própria skill: o conteúdo está enxuto e útil, ou há coisa "ocupando espaço à toa"?

O agente procura, com evidência:
- **Seções mortas** — descrevem algo que não corresponde a nada usável no projeto.
- **Redundância interna** — mesma instrução repetida em 3 seções; exemplos que provam o mesmo ponto.
- **Verbosidade** — texto que não muda o comportamento do leitor; enrolação, preâmbulo.
- **Desalinhamento com skill-creator** — falta de progressive disclosure, referências que ninguém lê.

**Saída estruturada** (um objeto por skill):

```json
{
  "skillName": "string",
  "bloatVerdict": "ENXUTA | PODAR | INCHADA",
  "estimatedCutPct": 0,
  "cuts": ["seção/trecho a remover ou condensar, com o porquê"]
}
```

- **ENXUTA** — nada a cortar.
- **PODAR** — cortes localizados (< ~25% do conteúdo).
- **INCHADA** — reestruturação/encolhimento significativo (≥ ~25%).

---

## Fase 3 — Auditoria de redundância entre skills (map → cluster → judge)

Redundância é um julgamento **entre pares** — não paraleliza de forma ingênua. Se você der lotes
cegos a N agentes, cada um só vê o próprio lote e **nunca compara** uma skill do lote 1 com uma do
lote 7 → duas skills quase idênticas em pastas diferentes escapam. Por isso: **map → cluster → judge**.

**3.1 Map (fan-out, 1 agente/skill).** Cada agente produz um resumo BARATO da sua skill, comprimindo
as ~98 skills numa tabela que cabe num único contexto:

```json
{
  "skillName": "string",
  "tema": "1 frase",
  "entidades": ["libs/classes/rotas/componentes citados"],
  "keywords": ["~10 palavras-chave"]
}
```

**3.2 Cluster (1 agente — BARREIRA).** Com a tabela dos 98 resumos junta, agrupa candidatos a
sobreposição por afinidade (tema + entidades em comum). Isso resolve o problema do "agente cego" e é
barato/determinístico. Saída: lista de **clusters suspeitos** (2–4 skills cada), ex.:
`vue-axios ↔ vue-pinia ↔ vue-max-use-usecachedapi` (todos falam de fetch/cache).

**3.3 Judge (fan-out, 1 agente/cluster).** Cada agente lê **só as skills daquele cluster** e decide:

```json
{
  "cluster": ["skillA", "skillB"],
  "recommendation": "MERGE | DEMARCAR | FALSO-POSITIVO",
  "into": "skill que absorve (se MERGE)",
  "rationale": "por que; o que cada uma tem de único",
  "mergePlan": "como fundir sem perda de conteúdo (se MERGE)"
}
```

- **MERGE** — fundir sem perda (já houve precedente: `vue-code-generators → vue-max-stack`).
- **DEMARCAR** — manter ambas, mas com escopos/cross-refs claros para os gatilhos não conflitarem.
- **FALSO-POSITIVO** — parecem, mas cobrem coisas distintas; deixar como está.

> **Barreira obrigatória:** o passo 3.2 precisa de TODOS os resumos juntos antes de agrupar →
> `parallel` no map, depois cluster (1 agente), depois `parallel` no judge.

---

## Fase 4 — Revisão adversarial (1 subagente revisor por problema)

Para **cada problema** apontado nas Fases 1–3 (conformidade, corte de bloat, recomendação de
merge/remoção), dispare **1 revisor** que tenta **refutar** — provar que não procede ou está mal
descrito. Ele abre o código real e checa independentemente, assumindo por padrão que a acusação
**pode estar errada**.

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

> Se o volume for grande, agrupe por skill (1 revisor refuta a lista da skill) — mas mantenha o
> veredito **por problema**.

---

## Fase 5 — Conciliação (define o DESTINO de cada skill)

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

---

## Fase 6 — Tabela consolidada

Apresente ao humano uma tabela completa, ordenada por severidade/destino:

| # | Skill | Estado | Destino | Nº de problemas | Descrição dos problemas |
|---|-------|--------|---------|-----------------|-------------------------|

`Destino ∈ { REMOVER, FUNDIR→X, PODAR (~N%), CORRIGIR, MANTER }`. Acompanhe com a distribuição por
estado **e** por destino, e o total.

---

## Fase 7 — Plano de correção (5 etapas)

Apresente o plano e **execute mediante confirmação**. Agora o plano já sabe o destino de cada skill,
então **começa encolhendo o conjunto** (remoções/merges) antes de gastar agentes corrigindo detalhe.
Cada subagente de correção **edita o `SKILL.md` in-place**, ancorado no código real, e usa a
`skill-creator` para forma/description.

- **Etapa 1 — Remoções + Merges → 1 subagente por remoção/merge.** Executa primeiro: apaga as
  REMOVER e funde as FUNDIR (sem perda de conteúdo). **Atualiza `manifests/` e o sync de skills** a
  cada remoção/rename. Encolhe o conjunto para as etapas seguintes.
- **Etapa 2 — Críticas (das que sobraram) → 1 subagente por skill.** Reescrita profunda: remover
  seções fabricadas, reconstruir a arquitetura conforme o projeto, corrigir a description. Onde o
  tema não existe no projeto, **não inventar**: reduzir o escopo ao real e sinalizar ao humano.
- **Etapa 3 — Ruins → 1 subagente por skill.** Correções medianas: nomes de config/env/rota/tabela/
  coluna reais, remover mecanismos inexistentes, alinhar a convenção de rotas Ziggy.
- **Etapa 4 — Regulares + podas de bloat → ~1 subagente para cada 3 skills.** Correções superficiais
  em lote temático **junto** com os cortes de bloat (PODAR/INCHADA) definidos na Fase 2.
- **Etapa 5 — Boas + verificação adversarial final → ~1 subagente por skill.** Nível-skill (headings,
  seções em pt-BR, refs quebradas, description 200–400) e verificação adversarial das skills de alto
  risco (todas as Críticas + Ruins + as que sofreram merge), que tentam **refutar** a versão final
  (`LIMPA` / `RESIDUAL` / `FALHA`). Spot-check das Excelentes. Corrija `FALHA` antes de fechar.

Para cada subagente de correção, forneça um **briefing por skill** (arquivo no scratchpad com o
destino + veredito conciliado + lista numerada de problemas confirmados) e mande o agente ler o
briefing antes de editar. Faça o subagente **retornar** um resumo estruturado:

```json
{ "name": "string", "changes": ["1 bullet por problema corrigido"], "descriptionLen": 0, "unresolved": ["o que não deu para resolver e por quê"] }
```

---

## Fase 8 — Verificação adversarial final

Já embutida na Etapa 5, mas registre o veredito final por skill de alto risco (`LIMPA`/`RESIDUAL`/
`FALHA`), corrija pontualmente qualquer `FALHA`, e **atualize a memória** do agente com as convenções
e armadilhas reconfirmadas (seção 0), para a próxima passada não repetir os mesmos erros.

---

## Ferramentas Anthropic a usar

A única dependência obrigatória é a **`skill-creator@claude-plugins-official`** — e vale explorar
duas capacidades internas dela (não é preciso nenhum plugin de terceiros; o diferencial da auditoria
é ler o código real em `projects/` com Grep/Read/Glob):

- **Description-improver (otimizador de *triggering*)** — na Etapa 4/5 e sempre que ajustar uma
  `description`, use o passo do skill-creator dedicado a otimizar a description para a skill disparar
  no contexto certo, dentro dos 200–400 caracteres. Relevante também na Fase 3: descriptions bem
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
- Prefira **fan-out amplo** (1 agente por unidade de trabalho) com `parallel`/`pipeline` e schema
  estruturado; agregue você mesmo lendo o `journal.jsonl` do run.
- **Redundância exige barreira** (map → cluster → judge): não dá para paralelizar cegamente, senão
  duplicatas em lotes diferentes escapam.
- Escreva **briefings por skill** no scratchpad em vez de embutir textos gigantes em `args`.
- Cada skill é um arquivo distinto → agentes de edição de skills **diferentes** rodam em paralelo sem
  worktree. Mas **merges/remoções** que mexem em `manifests/` (arquivo compartilhado) devem ser
  serializados ou reconciliados para não conflitar.
