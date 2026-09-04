import json, os

with open("docs/reports/phase1_consolidated.json", "r", encoding="utf-8") as f:
    phase1 = json.load(f)

with open("docs/reports/phase2_consolidated.json", "r", encoding="utf-8") as f:
    phase2 = json.load(f)

base_dir = "/home/johnattas/GitHub/MaxSkills/.max-code-worktrees/wt-21748545"

def to_abs(path):
    if path.startswith("/"):
        return path
    return f"{base_dir}/{path}"

microbatches = []

# Group 1: created-skills (44 skills)
for s in phase1:
    if "created-skills" in s["skillPath"]:
        probs = [p["text"] for p in s.get("problems", [])]
        cuts = [c["text"] for c in s.get("cuts", [])]
        all_items = probs + cuts
        if all_items:
            for i in range(0, len(all_items), 3):
                chunk = all_items[i:i+3]
                microbatches.append({
                    "id": f"MB_CREATED_{len(microbatches)+1:03d}",
                    "domain": "created-skills",
                    "skillName": s["skillName"],
                    "skillPath": to_abs(s["skillPath"]),
                    "items": chunk,
                    "reviewModel": "Tier 2 (High-Reasoning)" if any("Tier 2" in str(p) for p in s.get("problems", [])) else "Tier 1 (Fast)"
                })

# Group 2: All Crítica skills (20 skills)
for s in phase1:
    if s.get("state") == "Crítica":
        probs = [p["text"] for p in s.get("problems", [])]
        cuts = [c["text"] for c in s.get("cuts", [])]
        all_items = probs + cuts
        if all_items:
            for i in range(0, len(all_items), 3):
                chunk = all_items[i:i+3]
                microbatches.append({
                    "id": f"MB_CRIT_{len(microbatches)+1:03d}",
                    "domain": "critica",
                    "skillName": s["skillName"],
                    "skillPath": to_abs(s["skillPath"]),
                    "items": chunk,
                    "reviewModel": "Tier 2 (High-Reasoning)"
                })

# Group 3: Curated-youtube Ruim & Regular (11 skills)
for s in phase1:
    if "curated-youtube" in s["skillPath"] and s.get("state") in ["Ruim", "Regular"]:
        probs = [p["text"] for p in s.get("problems", [])]
        cuts = [c["text"] for c in s.get("cuts", [])]
        all_items = probs + cuts
        if all_items:
            for i in range(0, len(all_items), 3):
                chunk = all_items[i:i+3]
                microbatches.append({
                    "id": f"MB_CURATED_{len(microbatches)+1:03d}",
                    "domain": "curated-youtube",
                    "skillName": s["skillName"],
                    "skillPath": to_abs(s["skillPath"]),
                    "items": chunk,
                    "reviewModel": "Tier 1 (Fast)"
                })

# Group 4: Phase 2 Merge & Lapidar (17 clusters)
for cl in phase2:
    if cl.get("recommendation") in ["MERGE", "LAPIDAR"]:
        rec = cl["recommendation"]
        dest = cl.get("into")
        rat = cl.get("rationale", "")
        plan = cl.get("mergePlan", "")
        plan_desc = plan if plan else "Ajustar escopos sem perdas"
        microbatches.append({
            "id": f"MB_PHASE2_{len(microbatches)+1:03d}",
            "domain": "phase2_cluster",
            "skillName": " + ".join(cl["cluster"]),
            "skillPath": "Phase 2 Cluster",
            "items": [
                f"Proposta de {rec}: {rat}",
                f"Plano de integracao: {plan_desc}"
            ],
            "reviewModel": "Tier 2 (High-Reasoning)"
        })

print(f"Total micro-batches estruturados: {len(microbatches)}")
total_items = sum(len(mb["items"]) for mb in microbatches)
print(f"Total de itens a serem avaliados adversarialmente: {total_items}")

# Distribute into 8 batches: ADV1 to ADV8
num_batches = 8
batch_assignments = [[] for _ in range(num_batches)]
for idx, mb in enumerate(microbatches):
    batch_assignments[idx % num_batches].append(mb)

for b_idx, b_mbs in enumerate(batch_assignments):
    b_num = b_idx + 1
    items_count = sum(len(mb["items"]) for mb in b_mbs)
    print(f"ADV{b_num}: {len(b_mbs)} micro-batches, {items_count} itens")

# Save manifest
with open("docs/reports/phase3_microbatches_manifest.json", "w", encoding="utf-8") as f:
    json.dump(microbatches, f, indent=2, ensure_ascii=False)

# Generate prompt files
for b_idx, b_mbs in enumerate(batch_assignments):
    b_num = b_idx + 1
    prompt_lines = [
        f"Você é o Revisor Adversarial da Fase 3 para o lote ADV{b_num}.",
        f"Sua missão é atuar como Advogado do Diabo e avaliar rigorosamente os seguintes {len(b_mbs)} micro-lotes de problemas/cortes contra o código real em {base_dir}/projects/ e os arquivos SKILL.md:",
        ""
    ]
    for mb in b_mbs:
        mb_id = mb["id"]
        mb_name = mb["skillName"]
        mb_path = mb["skillPath"]
        mb_dom = mb["domain"]
        mb_mod = mb["reviewModel"]
        prompt_lines.append(f"### Micro-Lote [{mb_id}] - Skill: {mb_name}")
        prompt_lines.append(f"Caminho absoluto: {mb_path}")
        prompt_lines.append(f"Domínio: {mb_dom} | Modelo recomendado: {mb_mod}")
        prompt_lines.append("Problemas / Propostas a testar:")
        for it_idx, it in enumerate(mb["items"]):
            prompt_lines.append(f"  {it_idx+1}. {it}")
        prompt_lines.append("")

    prompt_lines.append("Diretrizes de Avaliação:")
    prompt_lines.append("1. Abra o arquivo SKILL.md da skill com view_file.")
    prompt_lines.append(f"2. Quando a acusação envolver conformidade técnica com o código de Engeapp/MaxVue, abra e confira os arquivos em {base_dir}/projects/ (projects/engeapp, projects/MaxComponentsUi, projects/MaxPinia, projects/MaxUse, projects/MaxCode).")
    prompt_lines.append("3. Para cada problema listado, decida:")
    prompt_lines.append("   - CONFIRMADO: se o defeito técnico, não conformidade ou necessidade de corte/merge for real e comprovado.")
    prompt_lines.append("   - REFUTADO: se for falso positivo, exagero, código existente ou sugestão puramente cosmética.")
    prompt_lines.append("4. Forneça evidence concreta (arquivo e linha/trecho).")
    prompt_lines.append("5. Se CONFIRMADO e envolver a description, proponha correctedDescription calibrada (200-400 chars). Senão, deixe string vazia.")
    prompt_lines.append("")
    prompt_lines.append("Retorne SEMPRE um array JSON contendo um objeto para CADA problema avaliado no formato:")
    prompt_lines.append("[")
    prompt_lines.append("  {")
    prompt_lines.append("    \"skillName\": \"nome da skill\",")
    prompt_lines.append("    \"problem\": \"texto exato ou resumo fiel do problema\",")
    prompt_lines.append("    \"verdict\": \"CONFIRMADO | REFUTADO\",")
    prompt_lines.append("    \"evidence\": \"arquivo e linha/trecho real\",")
    prompt_lines.append("    \"correctedDescription\": \"string se CONFIRMADO e impreciso, senao \"\"\"")
    prompt_lines.append("  }")
    prompt_lines.append("]")
    prompt_lines.append(f"Salve o resultado em {base_dir}/docs/reports/phase3_raw_ADV{b_num}.json usando write_to_file (sem ArtifactMetadata) e envie o resultado para o orquestrador via send_message.")

    with open(f"docs/reports/adv_prompt_ADV{b_num}.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(prompt_lines))

print("Prompt files adv_prompt_ADV1.txt a adv_prompt_ADV8.txt gerados com caminhos absolutos!")
