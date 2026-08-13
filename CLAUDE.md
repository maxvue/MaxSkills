# CLAUDE.md

Este repositório usa `index.md` (e `general-instructions/`, `global-workflows/`) como fonte principal do fluxo de trabalho do agente gerenciador de skills. Este arquivo complementa esse fluxo apenas com a regra abaixo.

## Diretrizes de Idioma

1. **Usar Português do Brasil (pt-BR) para:**
   - Comunicação entre Usuário <=> Agente de IA
   - Comentários no Código (comentários em inglês devem ser substituídos por comentários em português do Brasil)

2. **Usar Inglês (en-US) para:**
   - Nomes de funções
   - Nomes de variáveis
   - Nomes de tabelas do banco de dados
   - Nomes de colunas do banco de dados

## Execução de Agentes em Worktree

- Toda execução de agentes/subagentes que proponha modificações de código/arquivos neste repositório deve ocorrer em um **git worktree separado**, criado especificamente para as alterações propostas dentro da pasta oculta `.worktrees/` na raiz do projeto (`git worktree add .worktrees/wt-<slug> -b <slug>`) — nunca diretamente no working tree principal. A pasta `.worktrees/` é ignorada pelo Git (`.gitignore`).
- Valide as mudanças no worktree isolado e só então integre (merge) ao branch principal.
