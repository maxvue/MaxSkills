---
name: git-worktree
description: "Manage isolated Git worktrees for concurrent agent workflows, feature branches, and safe experimentation. Use when creating clean branch environments, switching contexts without stash conflicts, or pruning stale worktrees."
risk: safe
source: curated-youtube
---
# Git Worktree Operations

## When to Use
- An agent needs to work on a feature, bugfix, or long-running experiment in parallel without touching the current working tree.
- You want to avoid `git stash`, merge conflicts, and dirty working tree errors during multi-tasking.
- Running multi-agent builds where each agent requires its own dedicated directory.

## Core Commands

### 1. Criar Nova Worktree
```bash
# Criar branch nova a partir de main em pasta isolada
git worktree add -b feat/nova-funcionalidade ../wt-nova-funcionalidade main

# Conectar a uma branch remota existente
git worktree add ../wt-hotfix hotfix/correcao-urgente
```

### 2. Listar Worktrees Ativas
```bash
git worktree list
# Exibe caminho absoluto, hash do commit e branch associada
```

### 3. Remover e Limpar Worktrees
```bash
# Após merge ou descarte da tarefa:
git worktree remove ../wt-nova-funcionalidade

# Limpar metadados de worktrees excluídas manualmente em disco:
git worktree prune
```

## Regras de Isolamento
- **Nunca executar `git worktree remove --force`** sem conferir se há alterações não commitadas ou arquivos untracked valiosos.
- **Node modules / Dependências:** Cada worktree possui seu próprio sistema de arquivos; execute `npm install` ou `composer install` dentro da nova pasta se os artefatos de build não forem compartilhados.
