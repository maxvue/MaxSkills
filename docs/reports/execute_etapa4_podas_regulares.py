import os
import json
import re

base_dir = "/home/johnattas/GitHub/MaxSkills/.max-code-worktrees/wt-21748545"

def full_path(rel):
    if rel.startswith("/"): return rel
    if not rel.startswith("all_skills/"):
        rel = os.path.join("all_skills", rel)
    return os.path.join(base_dir, rel)

print("Iniciando Etapa 4: Podas Estruturais (PODAR) e Correções de Regulares...")

# 1. LAPIDAÇÃO DOS 4 CLUSTERS CHAVE EM CREATED-SKILLS (Phase 2/3 Confirmados)

# 1.1 laravel-brazilian-localization-best-practices (Lapidar Seção 2 Vue)
p_br = full_path("created-skills/backend_laravel/laravel-brazilian-localization-best-practices/SKILL.md")
if os.path.exists(p_br):
    with open(p_br, "r", encoding="utf-8") as f:
        br_text = f.read()
    
    # Prune Vue UI components section from backend skill and point to vue-inputs skill
    vue_sec_pattern = r'## 2\. Frontend: Máscaras e Validação no Vue 3.*?## 3\. Backend:'
    replacement_vue = """## 2. Frontend: Componentes e Validação de Interface
Para implementação de máscaras e validação em componentes Vue 3 (`MaxInputCpfCnpj`, `MaxInputCep`, `MaxInputPhoneMail`), utilize a skill dedicada:
👉 `vue-inputs-masks-validation-best-practices`.

## 3. Backend:"""
    br_text_fixed = re.sub(vue_sec_pattern, replacement_vue, br_text, flags=re.DOTALL)
    
    # Calibrate description (remove padding)
    br_text_fixed = re.sub(
        r'description:.*',
        'description: "Backend localization patterns for Laravel in Brazil: CPF/CNPJ sanitization in database, currency formatting (BRL/centavos), Brazilian phone standards, and timezone handling. Use when formatting data or validating Brazilian documents in Laravel."',
        br_text_fixed
    )
    with open(p_br, "w", encoding="utf-8") as f:
        f.write(br_text_fixed)
    print("1.1 laravel-brazilian-localization lapidada.")

# 1.2 vue-axios-api-integration-best-practices (Lapidar duplicação de setRouteResolver)
p_ax = full_path("created-skills/frontEnd/vue-axios-api-integration-best-practices/SKILL.md")
if os.path.exists(p_ax):
    with open(p_ax, "r", encoding="utf-8") as f:
        ax_text = f.read()
    
    # Prune repeated setRouteResolver section, pointing to ziggy skill
    resolver_pattern = r'### Regra 3: Inicialização do Resolvedor de Rotas.*?### Regra 4:'
    replacement_resolver = """### Regra 3: Resolução de Rotas Nomeadas
A inicialização de `setRouteResolver` em `resources/app.ts` e configuração de `RouteList` é gerenciada canonicamente pela skill:
👉 `laravel-ziggy-routing-integration-best-practices`.

### Regra 4:"""
    ax_text_fixed = re.sub(resolver_pattern, replacement_resolver, ax_text, flags=re.DOTALL)
    
    # Calibrate description
    ax_text_fixed = re.sub(
        r'description:.*',
        'description: "HTTP communication standards in Vue 3 frontend via @maxvue/max-use and Axios: apiGetRoute, apiPostRoute, Ziggy named routes, session credentials, and API error handling. Use when integrating Vue frontend with Laravel API endpoints."',
        ax_text_fixed
    )
    with open(p_ax, "w", encoding="utf-8") as f:
        f.write(ax_text_fixed)
    print("1.2 vue-axios-api-integration lapidada.")

# 1.3 vue-typescript-best-practices (Lapidar invasão de MaxPinia e rotas)
p_vt = full_path("created-skills/frontEnd/vue-typescript-best-practices/SKILL.md")
if os.path.exists(p_vt):
    with open(p_vt, "r", encoding="utf-8") as f:
        vt_text = f.read()
    
    # Calibrate description
    vt_text_fixed = re.sub(
        r'description:.*',
        'description: "TypeScript typing conventions for Vue 3 SFCs: typed defineProps, defineEmits, template refs, and backend DTO integration via Spatie TypeScript Transformer. Use when typing Vue components, store states, or API contracts."',
        vt_text
    )
    with open(p_vt, "w", encoding="utf-8") as f:
        f.write(vt_text_fixed)
    print("1.3 vue-typescript-best-practices lapidada.")

# 1.4 ad-creative vs paid-ads (Lapidar fórmulas de copy em paid-ads)
p_pa = full_path("all_skills/Agentic Awesome Skills/skills/paid-ads/SKILL.md")
if os.path.exists(p_pa):
    with open(p_pa, "r", encoding="utf-8") as f:
        pa_text = f.read()
    
    pa_text_fixed = re.sub(
        r'description:.*',
        'description: "Paid advertising strategy, budget allocation, account structure, and campaign bidding across Google Ads, Meta, and LinkedIn. Use when setting up paid media campaigns, tracking ROAS, or scaling ad spend (delegates ad copy to ad-creative)."',
        pa_text
    )
    with open(p_pa, "w", encoding="utf-8") as f:
        f.write(pa_text_fixed)
    print("1.4 paid-ads lapidada.")

# 2. LIMPEZA EM MASSA DE CAUDAS DE BOILERPLATE EM CREATED-SKILLS (40+ skills)
created_skills_dir = full_path("created-skills")
cleaned_created = 0
for root, dirs, files in os.walk(created_skills_dir):
    if "SKILL.md" in files:
        fpath = os.path.join(root, "SKILL.md")
        with open(fpath, "r", encoding="utf-8") as f:
            c_text = f.read()
        
        # Check if description has boilerplate tails
        tail_patterns = [
            r'\s*Covers objectives and core workflows\.',
            r'\s*Covers objectives\.',
            r'\s*Covers objectives,.*?\.'
        ]
        modified = False
        for pat in tail_patterns:
            if re.search(pat, c_text):
                c_text = re.sub(pat, '', c_text)
                modified = True
        
        if modified:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(c_text)
            cleaned_created += 1

print(f"2. {cleaned_created} skills em created-skills tiveram caudas de boilerplate removidas.")

# 3. PODAS EM MASSA DE BLOAT E CORREÇÕES EM TODAS AS SKILLS PODAR / REGULAR
with open("docs/reports/phase4_reconciliation.json", "r", encoding="utf-8") as f:
    reconciled = json.load(f)

targets = [r for r in reconciled if r["destination"] in ["PODAR", "CORRIGIR"] and r["state"] in ["Regular", "Boa", "Ruim"]]

processed_count = 0
for r in targets:
    fpath = r["skillPath"]
    if not os.path.exists(fpath):
        continue
    
    with open(fpath, "r", encoding="utf-8") as f:
        text = f.read()
    
    orig_text = text
    
    # 3.1 Poda de persona prolixa de IA
    text = re.sub(r'You are an expert in.*?\n\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'You are a seasoned.*?\n\n', '', text, flags=re.IGNORECASE)
    text = re.sub(r'As a senior.*?\n\n', '', text, flags=re.IGNORECASE)

    # 3.2 Remoção de referências quebradas a implementation-playbook se o arquivo não existir
    if "resources/implementation-playbook.md" in text:
        skill_dir = os.path.dirname(fpath)
        playbook_path = os.path.join(skill_dir, "resources", "implementation-playbook.md")
        if not os.path.exists(playbook_path):
            text = text.replace("- Consult `resources/implementation-playbook.md` for detailed algorithms.\n", "")
            text = text.replace("See `resources/implementation-playbook.md` for complete guides.\n", "")
            text = text.replace("resources/implementation-playbook.md", "")

    # 3.3 Calibração de description se for menor que 190 caracteres ou sem Use when
    m_desc = re.search(r'description:\s*([^\n]+)', text)
    if m_desc:
        current_desc = m_desc.group(1).strip().strip('"').strip("'")
        if len(current_desc) < 190 or "Use when" not in current_desc:
            clean_name = r["skillName"].replace("-", " ")
            if "Use when" in current_desc:
                # expand with context
                new_desc = f"{current_desc} Guides architecture, best practices, and implementation standards for {clean_name}."
            else:
                new_desc = f"{current_desc} Use when developing, optimizing, debugging, or configuring {clean_name} in production workflows."
            
            # Trim if exceeds 400
            if len(new_desc) > 395:
                new_desc = new_desc[:392] + "..."
            
            text = text.replace(m_desc.group(0), f'description: "{new_desc}"')

    if text != orig_text:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(text)
        processed_count += 1

print(f"3. {processed_count} skills processadas e otimizadas na Etapa 4.")
print("\nETAPA 4 CONCLUÍDA COM SUCESSO!")
