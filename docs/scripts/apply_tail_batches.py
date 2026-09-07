#!/usr/bin/env python3
"""
Aplica as correções semânticas dos 8 lotes (A-H) para purgar as caudas de preenchimento mecânicas.
"""
import glob
import json
import os
import yaml

def main():
    results = sorted(glob.glob('docs/reports/tail_batches/result_*.json'))
    print(f"Encontrados {len(results)} arquivos de resultados de cauda.")
    
    total_updated = 0
    errors = []

    for r in results:
        with open(r, 'r', encoding='utf-8') as f:
            batch = json.load(f)
        
        print(f"Aplicando {r} ({len(batch)} skills)...")
        for item in batch:
            skill_name = item['skillName']
            rel_path = item['relPath']
            clean_fm = item['cleanFrontmatter'].strip()
            if clean_fm.startswith('---'):
                clean_fm = clean_fm[3:].strip()
            if clean_fm.endswith('---'):
                clean_fm = clean_fm[:-3].strip()
            
            # Resolver caminho
            full_path = rel_path
            if not os.path.isabs(full_path):
                if os.path.exists(full_path):
                    pass
                elif os.path.exists(os.path.join('all_skills', full_path)):
                    full_path = os.path.join('all_skills', full_path)
                else:
                    errors.append(f"Arquivo não encontrado: {rel_path}")
                    continue
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                errors.append(f"Formato frontmatter inválido em {full_path}")
                continue
            
            new_content = "---\n" + clean_fm + "\n---" + parts[2]
            
            # Validação pré-gravação
            try:
                parsed = yaml.safe_load(clean_fm)
                if not isinstance(parsed, dict):
                    errors.append(f"Frontmatter não é dict para {skill_name}")
                    continue
                desc = parsed.get('description', '')
                if not (200 <= len(desc) <= 400):
                    errors.append(f"Description length ({len(desc)}) fora de [200, 400] para {skill_name}")
                    continue
            except Exception as e:
                errors.append(f"Erro no YAML de {skill_name}: {e}")
                continue
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            total_updated += 1

    print("\n" + "="*50)
    print(f"Total de skills atualizadas com sucesso: {total_updated}")
    print(f"Total de erros: {len(errors)}")
    if errors:
        for err in errors:
            print("  ERRO:", err)
        raise SystemExit(1)
    print("Aplicação de caudas concluída com 100% de integridade!")

if __name__ == '__main__':
    main()
