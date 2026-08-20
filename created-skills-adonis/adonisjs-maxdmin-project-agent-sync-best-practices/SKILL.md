---
name: adonisjs-maxdmin-project-agent-sync-best-practices
description: Use when designing, implementing, modifying, or debugging the synchronization logic between Maxdmin database resources (projects, instructions, processes, skills) and local project directories. Triggers on files modifying ProjectsController synchronization methods, generating CLAUDE.md or .agents/AGENTS.md files, handling Node fs/promises file writes, validating local paths, or generating structured Markdown content for local AI agents.
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Orientar o design, a implementação e a modificação da lógica de sincronização de projetos no Maxdmin. Ela garante que os recursos do banco de dados (projetos, templates, instruções, processos e skills) sejam formatados corretamente e escritos como configurações Markdown locais para agentes de IA locais (ClaudeCode e Antigravity) de forma segura, robusta e eficiente.

## Instruções
Ao implementar ou modificar a lógica de sincronização em `ProjectsController.sync()` ou classes relacionadas, siga estes padrões:

1. **Validação de Caminho & Verificação de Acessibilidade**
   - Verifique se o caminho do diretório de destino existe e é gravável usando imports dinâmicos do módulo nativo `promises` do Node:
     ```typescript
     const fs = await import('node:fs/promises');
     const path = await import('node:path');
     ```
   - Execute `await fs.access(projectPath)` para verificar a acessibilidade antes de realizar qualquer operação de escrita.
   - Retorne uma resposta HTTP `400 Bad Request` com uma mensagem de erro descritiva se o caminho for inválido ou inacessível:
     `{ "message": "O caminho do projeto é inválido ou inacessível no sistema de arquivos." }`

2. **Geração de Conteúdo Markdown Comum (`mdContent`)**
   - Construa um layout Markdown comum contendo o cabeçalho do projeto, descrição, templates, instruções e processos:
     - **Cabeçalho & Descrição:**
       ```markdown
       # Projeto: [Project Name]

       [Project Description]
       ```
     - **Regras Gerais (a partir de `project.templates`):** Concatene o conteúdo dos templates usando quebras de linha duplas sob `## Regras Gerais`.
     - **Regras do Projeto (a partir de `project.instructions`):** Formate cada instrução com `### [Title]` seguido de seu conteúdo sob `## Regras do Projeto`.
     - **Processos (a partir de `project.processes`):** Formate cada processo com `### [Title]` seguido de sua descrição sob `## Processos`.

3. **Sincronização no Modo ClaudeCode (`claudecode` ou `both`)**
   - Incorpore as skills diretamente no arquivo Markdown principal:
     - Adicione `## Skills Adicionais` como uma seção.
     - Mapeie cada skill para um cabeçalho de nível 3: `### [Skill Title]` seguido de seu conteúdo.
   - Escreva o markdown unificado em `path.join(projectPath, 'CLAUDE.md')` usando codificação `utf-8`.

4. **Sincronização no Modo Antigravity (`antigravity` ou `both`)**
   - Crie o diretório de configuração `.agents/`: `await fs.mkdir(agentsDir, { recursive: true })`.
   - Escreva o `mdContent` base em `path.join(agentsDir, 'AGENTS.md')` usando `utf-8`.
   - Para cada skill vinculada, gere diretórios individuais sob `skills/`:
     - Normalize o nome da pasta para kebab-case em minúsculas: `skill.title.toLowerCase().replace(/[^a-z0-9]/g, '-')`.
     - Crie o diretório: `await fs.mkdir(skillDir, { recursive: true })`.
     - Gere um YAML Frontmatter válido para cada `SKILL.md` com:
       ```markdown
       ---
       name: [Skill Title]
       description: Instruções para [Skill Title]
       ---

       [Skill Content]
       ```
     - Escreva em `path.join(skillDir, 'SKILL.md')`.

5. **Limpeza de Recursos & Segurança de Escrita**
   - Use operações de sistema de arquivos assíncronas (`fs.writeFile`, `fs.mkdir`) exclusivamente. Evite operações síncronas `fs.*Sync` para prevenir o bloqueio do event loop.
   - Garanta que todas as operações de escrita especifiquem a codificação `utf-8`.

## Exemplos
Consulte os seguintes arquivos mock para representações estruturadas de entrada e saída:
- Estrutura JSON de entrada contendo os models do banco de dados: [input_data.json](examples/input_data.json)
- Saída esperada do CLAUDE.md gerado: [output_claude.md](examples/output_claude.md)
- Saída esperada do AGENTS.md gerado: [output_agents.md](examples/output_agents.md)
- Saída esperada de um SKILL.md individual gerado: [output_skill_example.md](examples/output_skill_example.md)

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- Nunca escreva arquivos no diretório do projeto de destino sem antes verificar a disponibilidade do caminho usando `fs.access`.
- Não deixe caminhos de sistema de arquivos ou separadores de caminho fixos no código. Use o módulo `path` do Node (`path.join`) para manter a compatibilidade multiplataforma.
- Não escreva skills diretamente no arquivo `AGENTS.md` no modo Antigravity; elas devem residir em seus respectivos locais `.agents/skills/[folder-name]/SKILL.md`.
