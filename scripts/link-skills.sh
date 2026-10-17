#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd -P)"
# Codex, Pi, and OpenCode share .agents/skills. T3 uses its selected harness.
DESTS=("$HOME/.agents/skills" "$HOME/.claude/skills")

names=()
srcs=()
while IFS= read -r -d '' skill_md; do
  src="$(dirname "$skill_md")"
  names+=("$(basename "$src")")
  srcs+=("$src")
done < <(find "$REPO/skills" -name SKILL.md -not -path '*/node_modules/*' -print0)

# Check all destinations before replacing links or creating directories.
for dest in "${DESTS[@]}"; do
  if [ -L "$dest" ]; then
    echo "error: $dest is a symlink. Replace it with a directory before linking skills." >&2
    exit 1
  fi
  for name in "${names[@]}"; do
    target="$dest/$name"
    if [ -e "$target" ] && [ ! -L "$target" ]; then
      echo "error: $target is an installed copy. Uninstall it with its package manager first." >&2
      exit 1
    fi
  done
done

for dest in "${DESTS[@]}"; do
  mkdir -p "$dest"
  for target in "$dest"/*; do
    [ -L "$target" ] || continue
    source_path="$(readlink "$target")"
    case "$source_path" in
      "$REPO/skills/"*)
        if [ ! -f "$source_path/SKILL.md" ]; then
          rm "$target"
          echo "removed retired link $target"
        fi
        ;;
    esac
  done
  for i in "${!names[@]}"; do
    target="$dest/${names[$i]}"
    ln -sfn "${srcs[$i]}" "$target"
    echo "linked $target -> ${srcs[$i]}"
  done
done
