#!/usr/bin/env bash
#
# sync-project-skills.sh — Sincroniza .claude/skills/ e .agents/skills/ de cada projeto a partir de
# manifests/<projeto>.manifest, criando symlinks POR SKILL para created-skills/.
#
# Substitui o modelo antigo (symlink único .claude/skills ou .agents/skills -> created-skills inteiro),
# que carregava todas as ~109 descriptions em toda sessão de agente. Com o manifesto,
# cada projeto expõe só as skills relevantes ao seu stack em .claude/skills/ e .agents/skills/.
#
# Uso:
#   bash scripts/sync-project-skills.sh --all           # todos os projetos em ~/GitHub
#   bash scripts/sync-project-skills.sh engeapp MaxUse  # projetos específicos
#

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_ROOT="$REPO_ROOT/created-skills"
MANIFESTS_DIR="$REPO_ROOT/manifests"
PROJECTS_ROOT="${PROJECTS_ROOT:-$HOME/GitHub}"

errors=0

sync_project() {
  local name="$1"
  local manifest="$MANIFESTS_DIR/$name.manifest"
  local project_dir="$PROJECTS_ROOT/$name"

  # Suporte a worktrees/variantes sem manifesto próprio (ex: engeapp-wt-xxx, MaxComponentsUi-mig2)
  if [[ ! -f "$manifest" ]]; then
    for prefix in "engeapp" "MaxComponentsUi" "MaxUse" "SocialMedia" "AgenteDeBolso" "MaxMoney" "Skills"; do
      if [[ "$name" == "$prefix-"* && -f "$MANIFESTS_DIR/$prefix.manifest" ]]; then
        manifest="$MANIFESTS_DIR/$prefix.manifest"
        break
      fi
    done
  fi

  if [[ ! -f "$manifest" ]]; then
    echo "ERRO [$name]: manifesto não encontrado: $manifest" >&2
    errors=$((errors + 1)); return
  fi
  if [[ ! -d "$project_dir" ]]; then
    echo "ERRO [$name]: projeto não encontrado: $project_dir" >&2
    errors=$((errors + 1)); return
  fi

  # Skills desejadas segundo o manifesto.
  declare -A wanted=()
  local line skill_name missing=0
  while IFS= read -r line; do
    line="${line%%#*}"
    line="$(echo "$line" | xargs)"   # trim
    [[ -z "$line" ]] && continue
    skill_name="$(basename "$line")"

    local real_skill_dir=""
    if [[ -f "$SKILLS_ROOT/$line/SKILL.md" ]]; then
      real_skill_dir="$SKILLS_ROOT/$line"
    elif [[ -f "$REPO_ROOT/$line/SKILL.md" ]]; then
      real_skill_dir="$REPO_ROOT/$line"
    elif [[ -f "$REPO_ROOT/created-skills-adonis/$line/SKILL.md" ]]; then
      real_skill_dir="$REPO_ROOT/created-skills-adonis/$line"
    else
      echo "ERRO [$name]: skill inexistente no manifesto: $line" >&2
      missing=$((missing + 1)); continue
    fi

    if [[ -n "${wanted[$skill_name]:-}" ]]; then
      echo "AVISO [$name]: nome duplicado no manifesto: $skill_name" >&2
      continue
    fi
    wanted[$skill_name]="$real_skill_dir"
  done < "$manifest"

  # Se .agents não existir, usa .claude como modelo para criar .agents
  if [[ ! -d "$project_dir/.agents" && -d "$project_dir/.claude" ]]; then
    echo "[$name] Criando .agents a partir da pasta .claude como modelo..."
    mkdir -p "$project_dir/.agents"
    cp -r "$project_dir/.claude"/* "$project_dir/.agents/" 2>/dev/null || true
  fi

  # Garante a pasta/symlink .agent em todos os projetos (se não for um diretório independente, cria symlink para .agents)
  if [[ ! -e "$project_dir/.agent" ]]; then
    ln -sfn .agents "$project_dir/.agent"
    echo "[$name] Symlink .agent -> .agents criado."
  elif [[ -L "$project_dir/.agent" ]]; then
    ln -sfn .agents "$project_dir/.agent"
  fi

  # Sincroniza em AMBAS as pastas de agente (.claude e .agents)
  for agent_type in ".claude" ".agents"; do
    local agent_parent="$project_dir/$agent_type"
    local target="$agent_parent/skills"

    mkdir -p "$agent_parent"

    # Modelo antigo: $target é um symlink para a coleção inteira → remover.
    if [[ -L "$target" ]]; then
      echo "[$name] [$agent_type] removendo symlink antigo: $target -> $(readlink "$target")"
      rm "$target"
    fi
    mkdir -p "$target"

    local linked=0 kept=0

    # Remove symlinks gerenciados que não estão mais no manifesto.
    local entry base dest
    for entry in "$target"/*; do
      [[ -e "$entry" || -L "$entry" ]] || continue
      base="$(basename "$entry")"
      if [[ -L "$entry" ]]; then
        dest="$(readlink -f "$entry" || true)"
        if [[ "$dest" == "$REPO_ROOT"* || -z "$dest" ]]; then
          if [[ -z "${wanted[$base]:-}" ]]; then
            rm "$entry"
            echo "[$name] [$agent_type] removido (fora do manifesto): $base"
          fi
        else
          echo "AVISO [$name] [$agent_type]: symlink não gerenciado preservado: $base -> $dest" >&2
        fi
      else
        kept=$((kept + 1))  # arquivo/dir real do projeto: preservar
      fi
    done

    # Cria/atualiza os symlinks do manifesto.
    for skill_name in "${!wanted[@]}"; do
      ln -sfn "${wanted[$skill_name]}" "$target/$skill_name"
      linked=$((linked + 1))
    done

    echo "[$name] [$agent_type] OK: $linked skills linkadas$( ((kept)) && echo ", $kept entradas próprias preservadas" )"
  done

  errors=$((errors + missing))
  unset wanted
}

if [[ "${1:-}" == "--all" ]]; then
  projects=()
  for p_path in "$PROJECTS_ROOT"/*; do
    [[ -d "$p_path" ]] || continue
    p="$(basename "$p_path")"
    [[ "$p" == .* || "$p" == "worktrees" || "$p" == "cadyfile" || "$p" == "github_deploy_key"* ]] && continue
    projects+=("$p")
  done
elif [[ $# -ge 1 ]]; then
  projects=("$@")
else
  echo "Uso: $0 --all | <projeto> [projeto...]" >&2
  exit 2
fi

for p in "${projects[@]}"; do
  sync_project "$p"
done

if (( errors > 0 )); then
  exit 1
else
  exit 0
fi
