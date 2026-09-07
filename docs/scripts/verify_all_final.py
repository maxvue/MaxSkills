#!/usr/bin/env python3
"""
Script de Verificação Adversarial Final (Anti-Regressão) para o Ecossistema de Skills.
Executa varredura profunda em 100% dos SKILL.md e valida a consistência de 100% dos manifestos raiz.
"""
import os
import re
import json
import yaml
import sys

BASE_DIR = os.path.abspath('all_skills')

def verify_all():
    print("="*60)
    print("INICIANDO VERIFICAÇÃO ADVERSARIAL FINAL (100% DOS ARQUIVOS E MANIFESTOS)")
    print("="*60)
    
    counts = {
        'created-skills': 0,
        'Agentic Awesome Skills': 0,
        'curated-youtube': 0,
        'other': 0
    }
    
    errors = []
    generic_patterns = [
        'comprehensive engineering guide',
        'covers objectives, scope',
        'provides end-to-end guidance',
        'use when configuring, developing, debugging, or optimizing'
    ]
    
    adonis_violations = []
    frontend_api_violations = []
    skill_descs_by_path = {}
    
    total_skills = 0
    
    for root, dirs, files in os.walk(BASE_DIR):
        if 'SKILL.md' in files:
            total_skills += 1
            path = os.path.join(root, 'SKILL.md')
            rel = os.path.relpath(path, BASE_DIR)
            
            # Directory counting
            if rel.startswith('created-skills/'):
                counts['created-skills'] += 1
            elif rel.startswith('Agentic Awesome Skills/'):
                counts['Agentic Awesome Skills'] += 1
            elif rel.startswith('curated-youtube/'):
                counts['curated-youtube'] += 1
            else:
                counts['other'] += 1
                
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            parts = content.split('---', 2)
            if len(parts) < 3:
                errors.append(f"Header mal formatado (sem delimitadores --- válidos): {rel}")
                continue
                
            fm_text = parts[1]
            try:
                fm = yaml.safe_load(fm_text)
                if not isinstance(fm, dict):
                    errors.append(f"Frontmatter não é um mapeamento YAML: {rel}")
                    continue
            except Exception as e:
                errors.append(f"Erro de parsing YAML em {rel}: {e}")
                continue
                
            name = fm.get('name')
            if not name or not isinstance(name, str):
                errors.append(f"Campo 'name' inválido ou ausente em {rel}")
                
            desc = fm.get('description')
            if not desc or not isinstance(desc, str):
                errors.append(f"Campo 'description' ausente ou não-string em {rel}")
                continue
                
            desc_len = len(desc)
            if not (200 <= desc_len <= 400):
                errors.append(f"Description length ({desc_len}) fora de [200, 400] em {rel}")
                
            skill_descs_by_path[os.path.join('all_skills', rel)] = desc.strip()
                
            # Generic phrase check
            desc_lower = desc.lower()
            for pat in generic_patterns:
                if pat in desc_lower:
                    errors.append(f"Frase genérica proibida '{pat}' detectada na description de {rel}")
                    
            # Engeapp stack conventions
            if rel.startswith('created-skills/'):
                if 'adonis' in content.lower():
                    adonis_violations.append(rel)
                    
            if rel.startswith('created-skills/frontEnd/'):
                # Check for raw string literals like '/api/...'
                raw_api_matches = re.findall(r"['\"]/api/[a-zA-Z0-9_\-/]+['\"]", content)
                if raw_api_matches:
                    frontend_api_violations.append((rel, raw_api_matches))

    print(f"Total de SKILL.md verificados: {total_skills}")
    print(f"  - created-skills:         {counts['created-skills']} (esperado: 88)")
    print(f"  - Agentic Awesome Skills: {counts['Agentic Awesome Skills']} (esperado: 750)")
    print(f"  - curated-youtube:        {counts['curated-youtube']} (esperado: 28)")
    print(f"  - Outros:                 {counts['other']} (esperado: 0)")
    print("-"*60)
    print(f"Violações de convenção Adonis em created-skills: {len(adonis_violations)}")
    print(f"Violações de '/api/' literal em frontEnd:         {len(frontend_api_violations)}")
    print(f"Erros de frontmatter / description / parsing:    {len(errors)}")
    print("-"*60)
    
    # Validação de Manifestos
    manifest_errors = []
    manifests = [
        ('index.json', 88),
        ('awesome_skills.json', 750),
        ('other_skills.json', 28)
    ]
    
    total_manifest_items = 0
    for m_file, exp_count in manifests:
        if not os.path.exists(m_file):
            manifest_errors.append(f"Manifesto ausente: {m_file}")
            continue
        with open(m_file, 'r', encoding='utf-8') as mf:
            m_data = json.load(mf)
        if len(m_data) != exp_count:
            manifest_errors.append(f"Contagem em {m_file} ({len(m_data)}) difere do esperado ({exp_count})")
        total_manifest_items += len(m_data)
        
        for item in m_data:
            lp = item.get('local_path')
            if not lp or lp not in skill_descs_by_path:
                manifest_errors.append(f"local_path '{lp}' em {m_file} não encontrado no disco")
            else:
                if item.get('description_en') != skill_descs_by_path[lp]:
                    manifest_errors.append(f"description_en dessincronizada em {m_file} para {item.get('skill_name')}")

    print(f"Total de itens em manifestos validados: {total_manifest_items} (esperado: 866)")
    print(f"Erros de consistência de manifestos:    {len(manifest_errors)}")
    print("="*60)
    
    if adonis_violations or frontend_api_violations or errors or total_skills != 866 or manifest_errors:
        print("❌ FALHA NA VERIFICAÇÃO ADVERSARIAL:")
        for err in errors[:10]:
            print("  [ERRO]", err)
        for viol in adonis_violations:
            print("  [ADONIS]", viol)
        for viol, matches in frontend_api_violations:
            print("  [RAW API]", viol, matches)
        for merr in manifest_errors[:10]:
            print("  [MANIFEST]", merr)
        sys.exit(1)
    else:
        print("✅ SUCESSO ABSOLUTO! Todas as 866 skills e 3 manifestos cumprem 100% dos requisitos!")

if __name__ == '__main__':
    verify_all()
