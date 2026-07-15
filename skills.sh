#!/usr/bin/env bash
# Installer for this skills repo. Invoked directly, or via `npx skills@latest add`.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CMD="${1:-}"
TARGET_DIR="${2:-$HOME/.claude/skills}"

case "$CMD" in
  add)
    mkdir -p "$TARGET_DIR"
    for skill_dir in "$SCRIPT_DIR"/skills/*/; do
      name="$(basename "$skill_dir")"
      link="$TARGET_DIR/$name"
      if [ -L "$link" ] || [ -e "$link" ]; then
        rm -rf "$link"
      fi
      ln -s "${skill_dir%/}" "$link"
      echo "added $name -> $link"
    done
    ;;
  *)
    echo "usage: npx skills@latest add [target-dir]" >&2
    exit 1
    ;;
esac
