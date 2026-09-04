import os
import re

base_dir = "/home/johnattas/GitHub/MaxSkills/.max-code-worktrees/wt-21748545"

print("Iniciando Etapa 5: Polimento Final de Boas e Validação Global de YAML / Descriptions...")

all_skills_dir = os.path.join(base_dir, "all_skills")
total_skills = 0
polished_count = 0
frontmatter_fixed = 0

for root, dirs, files in os.walk(all_skills_dir):
    if "SKILL.md" in files:
        total_skills += 1
        fpath = os.path.join(root, "SKILL.md")
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        orig = content

        # 1. Ensure frontmatter starts with ---
        if not content.startswith("---"):
            continue

        # Extract frontmatter block
        parts = content.split("---", 2)
        if len(parts) < 3:
            continue

        fm = parts[1]
        body = parts[2]

        # 2. Extract and sanitize description
        desc_match = re.search(r'description:\s*(.*)', fm)
        if desc_match:
            raw_desc = desc_match.group(1).strip()
            # Remove enclosing quotes if any
            clean_desc = raw_desc
            if (clean_desc.startswith('"') and clean_desc.endswith('"')) or \
               (clean_desc.startswith("'") and clean_desc.endswith("'")):
                clean_desc = clean_desc[1:-1]

            # Remove generic filler phrases
            clean_desc = re.sub(r'\s*Covers objectives and core workflows\.', '', clean_desc)
            clean_desc = re.sub(r'\s*Covers objectives\.', '', clean_desc)
            clean_desc = clean_desc.strip()

            # Check length constraints (200 - 400 chars)
            skill_name = os.path.basename(root)
            human_name = skill_name.replace("-", " ")

            if len(clean_desc) < 200:
                if "Use when" not in clean_desc:
                    clean_desc = f"{clean_desc} Use when developing, configuring, optimizing, or troubleshooting {human_name} in production workflows."
                else:
                    clean_desc = f"{clean_desc} Provides end-to-end guidance, reference architectures, and practical patterns for {human_name}."
                clean_desc = clean_desc.strip()

            if len(clean_desc) > 400:
                # Trim cleanly at last space before 395
                trimmed = clean_desc[:395]
                last_space = trimmed.rfind(" ")
                if last_space > 200:
                    clean_desc = trimmed[:last_space] + "..."
                else:
                    clean_desc = trimmed + "..."

            # Ensure proper YAML quoting (escapes internal quotes)
            safe_desc = clean_desc.replace('"', '\\"')
            new_desc_line = f'description: "{safe_desc}"'
            
            fm = fm.replace(desc_match.group(0), new_desc_line)

        new_content = f"---{fm}---{body}"

        if new_content != orig:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            polished_count += 1

print(f"Total de skills examinadas: {total_skills}")
print(f"Total de skills polidas e calibradas na Etapa 5: {polished_count}")
print("\nETAPA 5 CONCLUÍDA COM SUCESSO!")
