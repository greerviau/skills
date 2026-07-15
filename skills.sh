#!/usr/bin/env bash
# Installer for this skills repo. Invoked directly, or via `npx skills@latest add`.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  echo "usage: npx skills@latest add [skill ...] [--target <dir>]" >&2
  echo "       npx skills@latest list" >&2
  echo "" >&2
  echo "With no skill names, installs every skill. Default target: ~/.claude/skills" >&2
  exit 1
}

available_skills() {
  for skill_dir in "$SCRIPT_DIR"/skills/*/; do
    basename "$skill_dir"
  done
}

install_skill() {
  local name="$1" target_dir="$2"
  local skill_dir="$SCRIPT_DIR/skills/$name"
  if [ ! -d "$skill_dir" ]; then
    echo "unknown skill: $name" >&2
    echo "available skills:" >&2
    available_skills | sed 's/^/  /' >&2
    exit 1
  fi
  local link="$target_dir/$name"
  if [ -L "$link" ] || [ -e "$link" ]; then
    rm -rf "$link"
  fi
  ln -s "$skill_dir" "$link"
  echo "added $name -> $link"
}

CMD="${1:-}"
shift || true

case "$CMD" in
  add)
    TARGET_DIR="$HOME/.claude/skills"
    SKILLS=()
    while [ $# -gt 0 ]; do
      case "$1" in
        --target)
          [ $# -ge 2 ] || usage
          TARGET_DIR="$2"
          shift 2
          ;;
        -*)
          usage
          ;;
        *)
          SKILLS+=("$1")
          shift
          ;;
      esac
    done
    if [ ${#SKILLS[@]} -eq 0 ]; then
      while IFS= read -r name; do SKILLS+=("$name"); done < <(available_skills)
    fi
    mkdir -p "$TARGET_DIR"
    for name in "${SKILLS[@]}"; do
      install_skill "$name" "$TARGET_DIR"
    done
    ;;
  list)
    available_skills
    ;;
  *)
    usage
    ;;
esac
