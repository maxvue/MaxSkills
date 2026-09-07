#!/usr/bin/env python3
"""
Sincroniza os manifestos raiz (index.json, awesome_skills.json, other_skills.json)
com as descriptions oficiais e calibradas de cada SKILL.md.
"""
import json
import os
import yaml

MANIFESTS = [
    'index.json',
    'awesome_skills.json',
    'other_skills.json'
]

def main():
    total_synced = 0
    total_checked = 0
    
    for fname in MANIFESTS:
        with open(fname, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        manifest_updated = 0
        for item in data:
            total_checked += 1
            lp = item.get('local_path')
            if not lp or not os.path.exists(lp):
                raise FileNotFoundError(f"Arquivo não encontrado para {item.get('skill_name')}: {lp}")
                
            with open(lp, 'r', encoding='utf-8') as sf:
                content = sf.read()
                
            parts = content.split('---', 2)
            if len(parts) < 3:
                raise ValueError(f"SKILL.md sem frontmatter válido: {lp}")
                
            fm = yaml.safe_load(parts[1])
            skill_desc = fm.get('description', '').strip()
            
            if item.get('description_en') != skill_desc:
                item['description_en'] = skill_desc
                manifest_updated += 1
                total_synced += 1
                
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
            
        print(f"✅ {fname}: {len(data)} itens verificados, {manifest_updated} sincronizados.")

    print("="*60)
    print(f"Total de itens verificados: {total_checked}")
    print(f"Total de descriptions sincronizadas: {total_synced}")
    print("Sincronização concluída com 100% de sucesso!")

if __name__ == '__main__':
    main()
