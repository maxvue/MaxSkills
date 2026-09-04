import os
import json
import re

base_dir = "/home/johnattas/GitHub/MaxSkills/.max-code-worktrees/wt-21748545"

print("Executando Checklist de Integridade de Saída...")

# 1. Manifests check
with open(os.path.join(base_dir, "index.json"), "r", encoding="utf-8") as f:
    idx_data = json.load(f)
with open(os.path.join(base_dir, "awesome_skills.json"), "r", encoding="utf-8") as f:
    awe_data = json.load(f)
with open(os.path.join(base_dir, "other_skills.json"), "r", encoding="utf-8") as f:
    oth_data = json.load(f)

total_manifest_skills = len(idx_data) + len(awe_data) + len(oth_data)
print(f"Manifestos: index.json={len(idx_data)}, awesome_skills.json={len(awe_data)}, other_skills.json={len(oth_data)}")
print(f"Total nos manifestos: {total_manifest_skills} skills ativas")

# 2. Disk scan of all SKILL.md files
all_skills_dir = os.path.join(base_dir, "all_skills")
found_skills = []
yaml_errors = []
desc_length_errors = []
adonis_mentions = []
raw_api_mentions = []

for root, dirs, files in os.walk(all_skills_dir):
    if "SKILL.md" in files:
        fpath = os.path.join(root, "SKILL.md")
        found_skills.append(fpath)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        # Frontmatter check
        if not content.startswith("---"):
            yaml_errors.append((fpath, "Não inicia com ---"))
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            yaml_errors.append((fpath, "Frontmatter não fechado"))
            continue

        fm = parts[1]
        m_desc = re.search(r'description:\s*([^\n]+)', fm)
        if not m_desc:
            desc_length_errors.append((fpath, "Sem description"))
        else:
            d_val = m_desc.group(1).strip().strip('"').strip("'")
            if len(d_val) < 200 or len(d_val) > 400:
                desc_length_errors.append((fpath, f"Tamanho {len(d_val)} fora de [200, 400]"))

        # Check Adonis in created-skills
        if "created-skills" in fpath and "adonis" in content.lower():
            adonis_mentions.append(fpath)

print(f"Disco: {len(found_skills)} arquivos SKILL.md encontrados (esperado: 866).")
print(f"Erros de YAML: {len(yaml_errors)}")
print(f"Erros de tamanho de Description: {len(desc_length_errors)}")
print(f"Menções a Adonis em created-skills: {len(adonis_mentions)}")

if desc_length_errors:
    print(f"Exemplo de desc_length_errors (primeiros 5 de {len(desc_length_errors)}):")
    for err in desc_length_errors[:5]:
        print(f"  {err[0]}: {err[1]}")

print("\nValidação de integridade concluída!")
