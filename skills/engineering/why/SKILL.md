---
name: why
description: Use when the user asks why code, a design, a config value, or a threshold is the way it is, or wants the history behind a decision, regression, or revert. Not for how the code works now.
---

# why

Answer from the record, not from the code: the commits, PRs, reviews, and issues that shaped the target.

1. Find the commit that introduced the target and each later commit that changed it.
   Use `git log -L <start>,<end>:<file>` for a line range, `git log -S '<string>'` for when a string appeared or vanished, and `git blame -w -C -C <file>` to see past moves and whitespace changes.
2. Find each commit's PR with `gh api repos/{owner}/{repo}/commits/<sha>/pulls --jq '.[].number'`, then read its description, review threads, and linked issues with `gh pr view <n> --comments` and `gh issue view <n> --comments`.
3. When that trail is thin, read the docs, design records, changelogs, and comments near the target.
4. Answer with what the authors wrote, cited by commit SHA, PR, or issue number.
   Mark your own inferences as inferences, and say what the record does not answer.
