path_yaml = "/home/johnattas/GitHub/Skills/list-skills.yaml"

with open(path_yaml, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. Extrair e remover a skill de laravel-vue-inertia-partial-reloads-lazy-loading-best-practices
# Ela ocupa as linhas de index 1 a 7 (linhas 2 a 8 do arquivo, 1-indexed)
skill_block = []
found_skill = False
new_lines = []

i = 0
while i < len(lines):
    line = lines[i]
    if "- nome: laravel-vue-inertia-partial-reloads-lazy-loading-best-practices" in line:
        found_skill = True
        skill_block.append(line)
        i += 1
        # Captura as próximas linhas até achar o próximo "- nome:" ou o fim do arquivo
        while i < len(lines) and not lines[i].strip().startswith("- nome:"):
            skill_block.append(lines[i])
            i += 1
        continue
    new_lines.append(line)
    i += 1

if not found_skill:
    print("Skill not found!")
    exit(1)

# Atualizar o status no skill_block de EXECUTANDO para CONCLUIDA
for idx, line in enumerate(skill_block):
    if "status: EXECUTANDO" in line:
        skill_block[idx] = line.replace("status: EXECUTANDO", "status: CONCLUIDA")

# 2. Localizar onde inserir a skill
# Queremos inserir antes de "- nome: laravel-code-generators-best-practices"
insert_idx = -1
for idx, line in enumerate(new_lines):
    if "- nome: laravel-code-generators-best-practices" in line:
        insert_idx = idx
        break

if insert_idx != -1:
    # Insere o bloco da skill
    new_lines[insert_idx:insert_idx] = skill_block
else:
    # Se não achar, insere no final
    new_lines.extend(skill_block)

with open(path_yaml, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Moved skill to CONCLUIDA section and updated list-skills.yaml successfully.")
