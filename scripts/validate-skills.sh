#!/usr/bin/env bash
#
# validate-skills.sh — Auditoria de conformidade das skills do repositório.
#
# Verifica, em created-skills/ (EN, primária) e created-skills-pt-br/ (PT-BR, espelho):
#   1. Paridade EN <-> PT-BR (cada skill EN deve ter exatamente 1 par PT-BR e vice-versa).
#   2. YAML frontmatter válido (name + description) e name == nome da pasta.
#   3. Wake word (description) entre 18 e 75 palavras.
#   4. Seções obrigatórias: Goal / Instructions / Constraints
#      (aceita os equivalentes pt-BR: Objetivo / Instruções / Restrições).
#   5. Idioma da pasta EN: corpo não deve estar majoritariamente em português.
#   6. Coerência com list-skills.yaml (skills CONCLUIDA devem existir nas duas pastas).
#
# Uso:  bash scripts/validate-skills.sh
# Saída: relatório no stdout; código de saída != 0 se houver problemas.

set -uo pipefail
cd "$(dirname "$0")/.." || exit 2

python3 - "$@" <<'PY'
import os, re, sys

EN  = 'created-skills'
PT  = 'created-skills-pt-br'
YAML = 'list-skills.yaml'

problems = 0
def warn(msg):
    global problems
    problems += 1
    print(f"  [!] {msg}")

def parse(path):
    txt = open(path, encoding='utf-8').read()
    issues = []
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n', txt, re.S)
    name = desc = None
    if not m:
        issues.append('frontmatter ausente')
    else:
        fm = m.group(1)
        nm = re.search(r'^name:\s*(.+)$', fm, re.M)
        dm = re.search(r'description:\s*(.+(?:\n\s+.+)*)', fm)
        name = nm.group(1).strip() if nm else None
        if not name: issues.append('name ausente')
        if not dm:
            issues.append('description ausente')
        else:
            desc = re.sub(r'\s+', ' ', dm.group(1).replace('>-', '')).strip()
            wc = len(desc.split())
            if wc < 18: issues.append(f'description curta ({wc} palavras)')
            if wc > 75: issues.append(f'description longa ({wc} palavras)')
    body = txt[m.end():] if m else txt
    sections = {
        'Goal':        r'^#+\s*(Goal|Objetivo)\b',
        'Instructions':r'^#+\s*(Instructions|Instru[çc][õo]es)\b',
        'Constraints': r'^#+\s*(Constraints|Restri[çc][õo]es)\b',
    }
    for label, pat in sections.items():
        if not re.search(pat, body, re.M | re.I):
            issues.append(f'seção {label} ausente')
    return name, body, issues

def folders(base):
    # Retorna um mapeamento de {nome_da_skill: caminho_relativo_do_SKILL.md}
    found = {}
    if not os.path.isdir(base):
        return found
    for root, dirs, files in os.walk(base):
        if 'SKILL.md' in files:
            skill_path = os.path.join(root, 'SKILL.md')
            rel = os.path.relpath(skill_path, base)
            parts = rel.split(os.sep)
            skill_name = parts[-2] if len(parts) >= 2 else parts[0].replace('.md', '')
            found[skill_name] = rel
    return found

en = folders(EN)
pt = folders(PT)

print("== 1. Paridade EN <-> PT-BR ==")
only_en = sorted(en.keys() - pt.keys())
only_pt = sorted(pt.keys() - en.keys())
for d in only_en: warn(f"{d}: existe em EN mas falta em PT-BR")
for d in only_pt: warn(f"{d}: existe em PT-BR mas falta em EN")
if not only_en and not only_pt:
    print("  OK — pastas espelhadas")

PT_MARKERS = re.compile(
    r'\b(Objetivo|Instru[çc][õo]es|Restri[çc][õo]es|Voc[êe] deve|Garantir|'
    r'gera[çc][ãa]o|Diretrizes|Sempre|Nunca|melhores pr[áa]ticas|Utilizar)\b', re.I)

for base, label in [(EN, 'EN'), (PT, 'PT-BR')]:
    print(f"\n== 2-4. Estrutura/frontmatter ({label}) ==")
    clean = True
    fmap = folders(base)
    for d in sorted(fmap.keys()):
        rel_skill = fmap[d]
        name, body, issues = parse(os.path.join(base, rel_skill))
        if name and name != d and d not in ['project-history', 'project-setup']:
            issues.append(f'name "{name}" != pasta')
        if base == EN and len(PT_MARKERS.findall(body)) >= 3:
            issues.append('corpo aparenta estar em PORTUGUÊS (pasta EN deve ser inglês)')
        if issues:
            clean = False
            warn(f"{d}: " + '; '.join(issues))
    if clean:
        print("  OK")

print("\n== 5. Coerência com list-skills.yaml ==")
if os.path.isfile(YAML):
    try:
        import yaml
        ydata = yaml.safe_load(open(YAML, encoding='utf-8')) or {}
        items = [(s.get('nome'), s.get('status', '')) for s in ydata.get('skills', []) if 'nome' in s]
    except Exception:
        ytxt = open(YAML, encoding='utf-8').read()
        items = re.findall(r'nome:\s*(\S+)[\s\S]*?status:\s*([A-ZÇÃ ]+)', ytxt)

    concl = [n for n, s in items if 'CONCLUIDA' in s and 'SUBSTITUIDA' not in s and 'DESCONTINUADA' not in s]
    for n in concl:
        if n not in en: warn(f"{n}: CONCLUIDA no yaml mas sem pasta EN")
        if n not in pt: warn(f"{n}: CONCLUIDA no yaml mas sem pasta PT-BR")
    all_active = {n for n, s in items if 'SUBSTITUIDA' not in s}
    untracked = sorted(en.keys() - all_active)
    for d in untracked:
        warn(f"{d}: pasta EN ausente do list-skills.yaml")
    stale = [n for n, s in items if 'EXECUTANDO' in s and n not in en and n not in pt]
    for n in stale:
        warn(f"{n}: status EXECUTANDO mas sem pasta (execução abandonada?)")
else:
    print("  (list-skills.yaml não encontrado — pulado)")

print(f"\n=== {problems} problema(s) encontrado(s) ===")
sys.exit(1 if problems else 0)
PY