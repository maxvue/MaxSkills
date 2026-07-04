#!/usr/bin/env bash
#
# sync-project-skills.sh — Sincroniza .claude/skills/ de cada projeto a partir de
# manifests/<projeto>.manifest, criando symlinks POR SKILL para created-skills/.
#
# Substitui o modelo antigo (symlink único .claude/skills -> created-skills inteiro),
# que carregava as ~109 descriptions em toda sessão de agente. Com o manifesto,
# cada projeto expõe só as skills relevantes ao seu stack.
#
# Uso:
#   bash scripts/sync-project-skills.sh --all           # todos os manifests/
#   bash scripts/sync-project-skills.sh engeapp MaxUse  # projetos específicos
#
# Convenções:
#   - manifests/<nome>.manifest → projeto em $PROJECTS_ROOT/<nome> (default ~/GitHub)
#   - Linhas do manifesto: caminho relativo a created-skills/ (ex.: frontEnd/vue).
#     Linhas vazias ou iniciadas por # são ignoradas.
#   - Em .claude/skills/ só são gerenciados (criados/removidos) symlinks que apontam
#     para dentro de created-skills/. Arquivos e diretórios reais são preservados.
#
# Saída != 0 se alguma entrada do manifesto não existir em created-skills/.

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
  local target="$project_dir/.claude/skills"

  if [[ ! -f "$manifest" ]]; then
    echo "ERRO [$name]: manifesto não encontrado: $manifest" >&2
    errors=$((errors + 1)); return
  fi
  if [[ ! -d "$project_dir" ]]; then
    echo "ERRO [$name]: projeto não encontrado: $project_dir" >&2
    errors=$((errors + 1)); return
  fi

  mkdir -p "$project_dir/.claude"

  # Modelo antigo: .claude/skills é um symlink para a coleção inteira → remover.
  if [[ -L "$target" ]]; then
    echo "[$name] removendo symlink antigo: $target -> $(readlink "$target")"
    rm "$target"
  fi
  mkdir -p "$target"

  # Skills desejadas segundo o manifesto.
  declare -A wanted=()
  local line skill_name missing=0 linked=0 kept=0
  while IFS= read -r line; do
    line="${line%%#*}"
    line="$(echo "$line" | xargs)"   # trim
    [[ -z "$line" ]] && continue
    skill_name="$(basename "$line")"
    if [[ ! -f "$SKILLS_ROOT/$line/SKILL.md" ]]; then
      echo "ERRO [$name]: skill inexistente no manifesto: $line" >&2
      missing=$((missing + 1)); continue
    fi
    if [[ -n "${wanted[$skill_name]:-}" ]]; then
      echo "AVISO [$name]: nome duplicado no manifesto: $skill_name (${wanted[$skill_name]} vs $line)" >&2
      continue
    fi
    wanted[$skill_name]="$line"
  done < "$manifest"

  # Remove symlinks gerenciados que não estão mais no manifesto.
  local entry base dest
  for entry in "$target"/*; do
    [[ -e "$entry" || -L "$entry" ]] || continue
    base="$(basename "$entry")"
    if [[ -L "$entry" ]]; then
      dest="$(readlink -f "$entry" || true)"
      if [[ "$dest" == "$SKILLS_ROOT"/* || -z "$dest" ]]; then
        if [[ -z "${wanted[$base]:-}" ]]; then
          rm "$entry"
          echo "[$name] removido (fora do manifesto): $base"
        fi
      else
        echo "AVISO [$name]: symlink não gerenciado preservado: $base -> $dest" >&2
      fi
    else
      kept=$((kept + 1))  # arquivo/dir real do projeto: preservar
    fi
  done

  # Cria/atualiza os symlinks do manifesto.
  for skill_name in "${!wanted[@]}"; do
    ln -sfn "$SKILLS_ROOT/${wanted[$skill_name]}" "$target/$skill_name"
    linked=$((linked + 1))
  done

  errors=$((errors + missing))
  echo "[$name] OK: $linked skills linkadas$( ((kept)) && echo ", $kept entradas próprias preservadas" )$( ((missing)) && echo ", $missing FALTANDO" )"
  unset wanted
}

if [[ "${1:-}" == "--all" ]]; then
  projects=()
  for m in "$MANIFESTS_DIR"/*.manifest; do
    [[ -e "$m" ]] || { echo "Nenhum manifesto em $MANIFESTS_DIR" >&2; exit 2; }
    projects+=("$(basename "$m" .manifest)")
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

exit $(( errors > 0 ? 1 : 0 ))
