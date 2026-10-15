#!/usr/bin/env bash
# Run the tests a branch adds or modifies against the merge base.
# Each added test must fail or error there; one that passes on the base does not prove the change.
# Usage: tests_fail_on_base.sh <base-ref> <test-path-glob> -- <test command and args>
# Example: tests_fail_on_base.sh origin/main 'tests/*' -- uv run pytest --continue-on-collection-errors
set -euo pipefail

base_ref=$1
paths=$2
shift 2
[ "$1" = "--" ] && shift

base=$(git merge-base "$base_ref" HEAD)
head=$(git rev-parse HEAD)
tmp="$(mktemp -d)/base"
git worktree add --detach "$tmp" "$base" >/dev/null
trap 'git worktree remove --force "$tmp"' EXIT

git diff -z --name-only --diff-filter=AM "$base" "$head" -- "$paths" | xargs -0 git -C "$tmp" checkout "$head" --
(cd "$tmp" && git diff -z --name-only --diff-filter=AM "$base" "$head" -- "$paths" | xargs -0 "$@") || true
