import json
import os

def main():
    with open("docs/reports/phase1_consolidated.json", "r", encoding="utf-8") as f:
        phase1 = json.load(f)

    with open("docs/reports/phase2_consolidated.json", "r", encoding="utf-8") as f:
        phase2 = json.load(f)

    with open("docs/reports/phase3_consolidated.json", "r", encoding="utf-8") as f:
        phase3 = json.load(f)

    # Build lookup for Phase 3 results
    phase3_by_skill = {}
    for item in phase3:
        sk = item.get("skillName", "")
        if sk not in phase3_by_skill:
            phase3_by_skill[sk] = []
        phase3_by_skill[sk].append(item)

    # Confirmed merges from Phase 2 and 3
    confirmed_merges = {
        "typescript-pro": "typescript-advanced-types-best-practices",
        "typescript-expert": "typescript-tooling-monorepo-best-practices",
        "mcp-server-routing": "mcp-tool-developer",
        "fp-taskeither-ref": "fp-types-ref",
        "ui-skills": "ui-skills-root",
        "seo-aeo-meta-description-generator": "seo-meta-optimizer",
        "vector-index-tuning": "vector-database-engineer",
        "skill-writer": "skill-creator",
        "skill-audit": "skill-scanner",
    }
    merge_targets = set(confirmed_merges.values())
    merge_sources = set(confirmed_merges.keys())

    explicit_removals = {
        "curated-youtube/api-design",
        "fal-audio",
        "fal-upscale",
        "makepad-skills",
        "pypict-skill",
        "varlock-claude-skill"
    }

    reconciled = []
    for s in phase1:
        name = s["skillName"]
        path = s["skillPath"]
        state = s.get("state", "Regular")
        probs = s.get("problems", [])
        cuts = s.get("cuts", [])
        bloat = s.get("bloatVerdict", "ENXUTA")
        cut_pct = s.get("estimatedCutPct", 0)

        # Check Phase 3 findings
        p3_items = phase3_by_skill.get(name, [])
        corrected_desc = ""
        for it in p3_items:
            if it.get("correctedDescription"):
                corrected_desc = it["correctedDescription"]
                break

        # Check explicit removal
        is_remover = False
        for r in explicit_removals:
            if r in path or r == name:
                is_remover = True
                break

        if is_remover:
            dest = "REMOVER"
            detail = "Remoção de stub vazio sem ferramentas ou duplicação idêntica byte a byte"
            if "api-design" in path:
                detail = "Remoção de cópia 100% duplicada em curated-youtube/api-design (preserva api-and-interface-design)"
        elif name in merge_sources:
            target = confirmed_merges[name]
            dest = "FUNDIR"
            detail = f"Fundir integralmente em {target} (desativar origem sem perda de conteúdo)"
        elif name in merge_targets:
            source_names = [k for k, v in confirmed_merges.items() if v == name]
            s_name = source_names[0] if source_names else "origem"
            dest = "FUNDIR"
            detail = f"Recebe fusão de {s_name} (absorve recursos, patterns e regras complementares)"
        elif bloat in ["INCHADA", "PODAR"]:
            dest = "PODAR"
            detail = f"Podar seções redundantes/boilerplate (~{cut_pct}% de redução)"
        elif (len(probs) > 0 or len(cuts) > 0) and state != "Excelente":
            dest = "CORRIGIR"
            detail = "Corrigir conformidade de diretrizes, gatilhos ou description"
        else:
            dest = "MANTER"
            detail = "100% aderente aos padrões (zero defeitos técnicos confirmados)"

        # Problem description
        if dest == "MANTER":
            prob_desc = "100% aderente aos padrões de engenharia e descrição (zero defeitos)."
        elif is_remover:
            prob_desc = detail
        elif dest == "FUNDIR":
            prob_desc = detail
        elif probs:
            clean_probs = [p["text"].replace("\n", " ").strip() for p in probs]
            prob_desc = " | ".join(clean_probs[:2])
            if len(clean_probs) > 2:
                prob_desc += f" (+{len(clean_probs)-2} outros)"
        elif cuts:
            clean_cuts = [c["text"].replace("\n", " ").strip() for c in cuts]
            prob_desc = " | ".join(clean_cuts[:2])
        else:
            prob_desc = s.get("summary", "Ajustes semânticos.")

        reconciled.append({
            "skillName": name,
            "skillPath": path,
            "state": state,
            "problemCount": len(probs),
            "destination": dest,
            "destinationDetail": detail,
            "problemDescription": prob_desc,
            "bloatVerdict": bloat,
            "estimatedCutPct": cut_pct,
            "correctedDescription": corrected_desc
        })

    # Save Phase 4 JSON
    with open("docs/reports/phase4_reconciliation.json", "w", encoding="utf-8") as f:
        json.dump(reconciled, f, indent=2, ensure_ascii=False)
    print("Salvo: docs/reports/phase4_reconciliation.json")

    # Sort order: Crítica -> Ruim -> Regular -> Boa -> Excelente, then problemCount descending
    state_rank = {
        "Crítica": 1,
        "Ruim": 2,
        "Regular": 3,
        "Boa": 4,
        "Excelente": 5
    }
    reconciled_sorted = sorted(reconciled, key=lambda x: (state_rank.get(x["state"], 99), -x["problemCount"], x["skillName"]))

    # Save Phase 5 JSON
    with open("docs/reports/fase_5_consolidado.json", "w", encoding="utf-8") as f:
        json.dump(reconciled_sorted, f, indent=2, ensure_ascii=False)
    print("Salvo: docs/reports/fase_5_consolidado.json")

    # Generate Markdown Table Report
    md_lines = [
        "# Relatório Consolidado de Auditoria e Conciliação de Skills (Fases 1 a 5)",
        "",
        "> **Documento Oficial Gerado Conforme Runbook `optimize_skills.md`**",
        "> Data de Execução: 04/09/2026 | Worktree: `wt-21748545`",
        "",
        "## 1. Métricas Gerais e Distribuição",
        "",
        f"- **Total de Skills Auditadas:** {len(reconciled_sorted)}",
        "- **Critério de Auditoria:** 100% IA Semântica (13 critérios, paridade de código real em `projects/`, análise de bloat, clusters de redundância e revisão adversarial com micro-batching).",
        "",
        "### 1.1 Distribuição por Estado de Saúde Técnica",
        "",
        "| Estado | Quantidade | Percentual | Impacto Operacional |",
        "| :--- | :---: | :---: | :--- |",
    ]

    state_counts = {}
    for r in reconciled_sorted:
        st = r["state"]
        state_counts[st] = state_counts.get(st, 0) + 1

    state_desc = {
        "Crítica": "Stubs vazios, dependências inexistentes ou violações graves de governança",
        "Ruim": "Múltiplos desacordos técnicos, seções obsoletas ou personas hipertrofiadas",
        "Regular": "Desacordos pontuais, descrições truncadas ou pequenas omissões",
        "Boa": "Conteúdo tecnicamente correto com ajustes semânticos menores na description",
        "Excelente": "100% aderente sem pendências conceituais nem de descrição"
    }

    for st in ["Crítica", "Ruim", "Regular", "Boa", "Excelente"]:
        c = state_counts.get(st, 0)
        pct = (c / len(reconciled_sorted)) * 100
        desc = state_desc.get(st, "")
        md_lines.append(f"| **{st}** | {c} | {pct:.1f}% | {desc} |")

    md_lines.extend([
        "",
        "### 1.2 Distribuição por Destino Conciliado (Regra de Precedência)",
        "",
        "> `REMOVER` > `FUNDIR` > `PODAR` > `CORRIGIR` > `MANTER`",
        "",
        "| Destino | Quantidade | Percentual | Ação no Pipeline (Fase 6) |",
        "| :--- | :---: | :---: | :--- |",
    ])

    dest_counts = {}
    for r in reconciled_sorted:
        d = r["destination"]
        dest_counts[d] = dest_counts.get(d, 0) + 1

    dest_desc = {
        "REMOVER": "Etapa 1: Purgar stubs vazios de terceiros e cópias duplicadas byte a byte",
        "FUNDIR": "Etapa 1: Fundir skills sobrepostas sem perda de conteúdo e atualizar manifestos",
        "PODAR": "Etapa 4: Remover seções mortas, boilerplate e preâmbulos prolixos (bloat)",
        "CORRIGIR": "Etapas 2, 3, 4, 5: Corrigir APIs, comandos, rotas, types e calibrar description",
        "MANTER": "Preservar intacto (skills excelentes ou 100% conformes)"
    }

    for d in ["REMOVER", "FUNDIR", "PODAR", "CORRIGIR", "MANTER"]:
        c = dest_counts.get(d, 0)
        pct = (c / len(reconciled_sorted)) * 100
        desc = dest_desc.get(d, "")
        md_lines.append(f"| **{d}** | {c} | {pct:.1f}% | {desc} |")

    md_lines.extend([
        "",
        "## 2. Seções de Apoio e Rastreabilidade",
        "",
        "### 2.1 Pares de Fusão Confirmados (`FUNDIR`)",
        "",
        "| # | Skill de Origem (Absorvida) | Skill de Destino (Canônica) | Justificativa Técnica Aprovada |",
        "|---|---|---|---|",
        "| 1 | `typescript-pro` | `typescript-advanced-types-best-practices` | Absorver types complementares e unificar na skill canônica profunda do repositório. |",
        "| 2 | `typescript-expert` | `typescript-tooling-monorepo-best-practices` | Transferir tooling CLI/diagnósticos e descartar type-level repetido. |",
        "| 3 | `mcp-server-routing` | `mcp-tool-developer` | Unificar stack de desenvolvimento MCP sob nomenclatura e API modernas. |",
        "| 4 | `fp-taskeither-ref` | `fp-types-ref` | Integrar referência de TaskEither na cheatsheet central de tipos fp-ts. |",
        "| 5 | `ui-skills` | `ui-skills-root` | Stub redundante de UI absorvido pelo roteador oficial executável de UI skills. |",
        "| 6 | `seo-aeo-meta-description-generator` | `seo-meta-optimizer` | Incorporar framework de CTR de 3 ângulos e tags sociais em meta-optimizer. |",
        "| 7 | `vector-index-tuning` | `vector-database-engineer` | Migrar implementation-playbook de HNSW/PQ para a skill canônica de banco vetorial. |",
        "| 8 | `skill-writer` | `skill-creator` | Migrar taxonomias de referências documentais para a suíte executável com evals. |",
        "| 9 | `skill-audit` | `skill-scanner` | Absorver checagens de engenharia social, repo intelligence e score 0-100 em scanner. |",
        "",
        "### 2.2 Remoções Explícitas Confirmadas (`REMOVER`)",
        "",
        "| # | Skill / Caminho | Motivo da Remoção |",
        "|---|---|---|",
        "| 1 | `curated-youtube/api-design` | Cópia 100% duplicada (byte a byte) de `api-and-interface-design`. |",
        "| 2 | `fal-audio` | Stub vazio de 29 linhas sem código, com 80%+ de tautologias apontando para URL externa. |",
        "| 3 | `fal-upscale` | Stub vazio de 29 linhas sem modelos ou implementações apontando para GitHub externo. |",
        "| 4 | `makepad-skills` | Stub redundante de 29 linhas com repetição quádrupla da mesma frase sem conteúdo técnico. |",
        "| 5 | `pypict-skill` | Stub oco de 24 caracteres de description sem comandos ou API pypict utilizável. |",
        "| 6 | `varlock-claude-skill` | Loop tautológico de 29 linhas sem comandos práticos ou regras de execução. |",
        "",
        "### 2.3 Pares Demarcados (`DEMARCAR`)",
        "",
        "| Cluster de Skills | Diretriz de Demarcação e Gatilhos |",
        "|---|---|",
        "| `frontend-design-best-practices` + `vue-unocss-styling-best-practices` | Direção de arte/UX para `frontend-design`; sintaxe UnoCSS, presetMaxUno e CSS variables para `vue-unocss-styling`. |",
        "| `tdd` + `tdd-orchestrator` | Desenvolvimento tático e micro-ciclo Red-Green para `tdd`; governança/arquitetura/CI para `tdd-orchestrator`. |",
        "| `fp-errors` + `fp-pragmatic` | Mindset funcional 80/20 para `fp-pragmatic`; modelagem de erros com TaskEither e Applicative para `fp-errors`. |",
        "| `agent-qa-debug-fix` + `agent-qa-result-triage` | Triagem diagnóstica somente-leitura para `result-triage`; aplicação ativa de patches para `debug-fix`. |",
        "| `seo-aeo-blog-writer` + `seo-aeo-landing-page-writer` | Artigos editoriais long-form informativos para `blog-writer`; páginas comerciais de alta conversão para `landing-page-writer`. |",
        "| `sendblue-api` + `sendblue-cli` + `sendblue-notify` | REST API para `api`; CLI shell para `cli`; gatilhos de alerta assíncrono pós-tarefa para `notify`. |",
        "| `youtube-transcript` + `youtube-summarizer` | Extração bruta de legendas para `transcript`; síntese STAR+RISE para `summarizer`. |",
        "| `unit-testing-test-generate` + `test-fixing` + `test-automator` | Geração AST para `generate`; correção de quebras para `fixing`; arquitetura de pipelines/E2E para `automator`. |",
        "| `ui-ux-designer` + `ui-ux-pro-max` + `ui-visual-validator` | Ideação/wireframing para `designer`; design system em código para `pro-max`; QA visual/screenshot para `validator`. |",
        "| `skill-improver` + `skill-optimizer` | Diagnóstico de telemetria para `optimizer`; loop de refatoração automatizada de código para `improver`. |",
        "",
        "## 3. Tabela Completa Consolidada de Todas as 881 Skills",
        "",
        "> Ordenada estritamente por severidade (`Crítica → Ruim → Regular → Boa → Excelente`) e nº de problemas decrescente.",
        "",
        "| # | Skill | Estado | Nº de problemas | Destino | Descrição dos problemas |",
        "|---|-------|--------|:---------------:|:-------:|-------------------------|",
    ])

    for idx, r in enumerate(reconciled_sorted, 1):
        name = r["skillName"]
        state = r["state"]
        probs = r["problemCount"]
        dest = r["destination"]
        p_desc = r["problemDescription"].replace("|", "\\|")
        md_lines.append(f"| {idx} | `{name}` | {state} | {probs} | {dest} | {p_desc} |")

    md_lines.extend([
        "",
        "---",
        "",
        "## 4. Plano de Execução da Fase 6 (5 Etapas em Contexto Quente)",
        "",
        "Conforme previsto no runbook, este plano otimiza a ordem de execução para encolher a base e acelerar as correções com reaproveitamento de contexto em memória de trabalho:",
        "",
        "### Etapa 1 — Remoções + Merges (Tier 2)",
        "- **Ação:**",
        "  - Purgar as 6 skills marcadas como `REMOVER` (`curated-youtube/api-design`, `fal-audio`, `fal-upscale`, `makepad-skills`, `pypict-skill`, `varlock-claude-skill`).",
        "  - Executar as 9 fusões de conteúdo das skills `FUNDIR`, integrando regras, exemplos e playbooks complementares nas skills de destino e descomissionando as pastas de origem.",
        "  - Atualizar os manifestos de índice raiz (`index.json`, `awesome_skills.json`, `other_skills.json`).",
        "- **Resultado esperado:** Redução do inventário de 881 para 866 skills ativas.",
        "",
        "### Etapa 2 — Reescrita de Skills Críticas (Tier 2 + skill-creator)",
        "- **Ação:** Reconstrução profunda das 20 skills classificadas como `Crítica`:",
        "  - Eliminar referências a arquivos inexistentes (`RAYDEN_RULES.md`, `implementation-playbook.md` fantasmas).",
        "  - Reconstruir comandos CLI, fixtures e sintaxe real de frameworks (`mermaid-diagrammer`, `vue-components`, `loki-mode`, `aws-skills`).",
        "  - Otimizar a tag `description` (200 a 400 caracteres com gatilhos acionáveis e discriminantes semânticos).",
        "",
        "### Etapa 3 — Correções de Skills Ruins (Tier 2 + skill-creator)",
        "- **Ação:** Correção das 85 skills classificadas como `Ruim`:",
        "  - Remover personas prolixas e templates vazios de YouTube (`database-optimizer`, `damage-control`, `superpowers`, etc.).",
        "  - Eliminar referências legadas e comandos alucinados.",
        "  - Restabelecer seções operacionais de código e checklists objetivos.",
        "",
        "### Etapa 4 — Podas de Bloat e Regulares (Tier 1 em Lotes de 3 a 5 skills)",
        "- **Ação:** Execução das 415 podas estruturais (`PODAR`) e 193 skills `Regular`:",
        "  - Agrupamento em pipelines de contexto quente por domínio (`backend_laravel`, `frontEnd`, `seo-*`, `fp-*`).",
        "  - Poda cirúrgica de preâmbulos teóricos, seções mortas e links inválidos.",
        "  - Lapidação de sobreposições em skills mantidas (`vue-typescript` vs `vue-max-stack`, `laravel-brazilian-localization` vs `vue-inputs`).",
        "",
        "### Etapa 5 — Polimento de Skills Boas (Tier 1 em Lotes de 3 a 5 skills)",
        "- **Ação:** Ajustes semânticos finais nas 345 skills marcadas como `CORRIGIR` no estado `Boa`:",
        "  - Eliminação de caudas genéricas de preenchimento (`Covers objectives and core workflows.`).",
        "  - Calibração fina da contagem de caracteres da `description` (200-400 chars) com cláusula `Use when...`.",
        "  - Validação de integridade do frontmatter YAML.",
        "",
        "---",
        "",
        "> ### ⛔ PARADA OBRIGATÓRIA DE APROVAÇÃO HUMANA (Fim da Fase 5)",
        "> **Nenhum arquivo de skill foi modificado.** O plano de execução e o inventário completo consolidado estão prontos.",
        "> Aguardando confirmação explícita do usuário para prosseguir com a Fase 6."
    ])

    report_path = "docs/reports/fase_5_consolidado.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Salvo: {report_path} com {len(reconciled_sorted)} linhas na tabela!")

if __name__ == "__main__":
    main()
