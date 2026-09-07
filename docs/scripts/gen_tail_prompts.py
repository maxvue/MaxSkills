import json, os, math

with open('docs/reports/fix_batches/tail_skills.json') as f:
    skills = json.load(f)

os.makedirs('docs/reports/tail_batches', exist_ok=True)

batch_size = 11
num_batches = math.ceil(len(skills) / batch_size)
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

for idx in range(num_batches):
    batch = skills[idx * batch_size : (idx + 1) * batch_size]
    letter = letters[idx]
    
    batch_file = f'docs/reports/tail_batches/batch_{letter}.json'
    with open(batch_file, 'w', encoding='utf-8') as f:
        json.dump(batch, f, indent=2, ensure_ascii=False)
        
    skills_list_str = "".join([f"- {s['path']}\n" for s in batch])
    
    prompt = f"""Você é um Auditor e Redator Semântico Especialista em Skills de IA.
Sua missão é realizar a auditoria semântica profunda e a calibração de description para o seguinte lote de skills no workspace:
{skills_list_str}
Para CADA skill:
1. Leia o arquivo SKILL.md usando suas ferramentas de leitura (caminho absoluto /home/johnattas/GitHub/MaxSkills/.max-code-worktrees/wt-e15fb46e/<relPath>).
2. Identifique o real propósito técnico da skill, suas ferramentas, bibliotecas, comandos e capacidades reais.
3. Formule uma DESCRIPTION de alta densidade semântica que cumpra ESTRITAMENTE os 13 Critérios:
   - Exatamente entre 200 e 400 caracteres.
   - Clareza de ação imediata (o que ela faz).
   - Cláusula de gatilho formal de ativação contextual ("Use when..." ou "Ative quando...").
   - Termos discriminantes específicos (nomes exatos de APIs, bibliotecas, ferramentas, frameworks).
   - Fidelidade absoluta ao conteúdo real do documento.
   - Zero marketing, zero adjetivos vazios (nada de "poderosa", "incrível", etc.).
   - Zero caudas de preenchimento ou clichês genéricos (NUNCA usar "Comprehensive engineering guide...", "Provides end-to-end guidance...", etc.).
   - Sem tutoriais passo a passo na description.
4. Monte o frontmatter YAML completo e limpo, garantindo que seja 100% válido, com strings adequadamente cotadas, sem quebras inválidas e sem linhas órfãs de descrições anteriores.

Retorne OBRIGATORIAMENTE um array JSON contendo um objeto para cada skill no seguinte formato:
```json
[
  {{
    "skillName": "string",
    "relPath": "string",
    "correctedDescription": "string (entre 200 e 400 caracteres)",
    "charCount": 250,
    "discriminants": ["termo1", "termo2"],
    "cleanFrontmatter": "name: ...\\ndescription: \\\"...\\\"\\n..."
  }}
]
```"""
    prompt_file = f'docs/reports/tail_batches/prompt_{letter}.txt'
    with open(prompt_file, 'w', encoding='utf-8') as f:
        f.write(prompt)

print(f"Sucesso: {num_batches} lotes gerados.")
