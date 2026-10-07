---
name: review
description: Use when reviewing a working-tree diff, branch, or pull request. Checks standards, tests, flakiness, correctness, structure, and conformance to an originating issue or spec when available.
---

# review

Review a diff, branch, or PR against this bar: lint clean, tests present and passing, no flakiness, and correctness weighted above development cost. Judge structure (simplicity, maintainability) with `design`'s vocabulary.

This adds a standards layer and an "any defect you see gets flagged, even if incidental" rule to the built-in `/code-review`, which hunts correctness bugs.
It reviews and reports and does not land changes.

## Procedure

1. Scope the diff: working tree, branch against base, or GitHub PR. Review that, not the whole codebase.
2. Correctness pass. Use `/code-review` where it helps and summarize its findings instead of re-deriving them.
3. Standards pass, run as a subagent in parallel with step 4. Check against `standards` and its `CODING-STANDARDS.md`, starting with the mechanical checks:

   | Standard | Mechanical check |
   | --- | --- |
   | Lint clean | Run the repo's linter over the diff. Any new violation fails. |
   | Tests pass | Run the suite. A failure fails. Confirm the diff adds or updates tests that exercise the change. |
   | Test-first | Run the tests the diff adds against the merge base with the test-first command below. Each added test must fail or error there. An added test that passes on the base does not prove the change. Skip changes `CODING-STANDARDS.md` exempts. |
   | Flakiness, AI attribution, full-word naming, comment form, issue references, plain language | Run `scripts/check_diff.py <base>` from this skill's directory, with the repo as the working directory. It checks the lines the change adds, including uncommitted and untracked files, and the branch's commit messages. Settle each finding against its rule. A finding the rule allows (a glossary acronym, an external tracker link that backs a stated constraint) is dropped. Read the PR body for attribution yourself. |
   | Ubiquitous language | For each glossary term the change touches, grep the diff for coined synonyms. |
   | Comment density | List every comment the diff adds with the comment command below and settle each against the comment rules in `CODING-STANDARDS.md`. A comment stating a fact the code already states is a finding. |

   The comment command:

   ```bash
   git diff <base>..HEAD | grep -E -C2 '^\+.*(#|//|/\*|--|<!--)'
   ```

   The pattern over-collects (shebangs, `#` inside strings), because a comment it misses escapes the check and a false positive costs one settle.
   Keep the context lines; the settle step compares each comment against them.

   The test-first command checks out the base in a temporary worktree, copies in the test files the diff adds or modifies, and runs them:

   ```bash
   base=$(git merge-base <base> HEAD); head=$(git rev-parse HEAD)
   tmp="$(mktemp -d)/base"; git worktree add --detach "$tmp" "$base"
   git diff -z --name-only --diff-filter=AM "$base" "$head" -- <test paths> | xargs -0 git -C "$tmp" checkout "$head" --
   (cd "$tmp" && git diff -z --name-only --diff-filter=AM "$base" "$head" -- <test paths> | xargs -0 <test command>)
   git worktree remove --force "$tmp"
   ```

   Read the result per test. Tests that already existed in a modified file may pass. Run past collection errors (`--continue-on-collection-errors` for pytest), because one file that fails to import can hide the other results.

   Then the judgment calls: order-dependent tests, whether structure meets `design`'s vocabulary or only took the cheapest path, whether the tests prove the behavior, and whether the touched documentation was audited (`doc-audit`).
4. Spec-conformance pass. Find the originating spec or issue: a `docs/plans/` reference in the PR body, a linked GitHub issue, a plan path named in the branch, or one the user supplies. If none resolves, report "no originating spec located, conformance not assessed" and stop. Never reconstruct a spec from the diff and grade against it. When a spec resolves, report scope drift, missing requirements, and out-of-scope additions.
5. Flag every lint error, test failure, or flakiness you see, even if unrelated, and say it belongs on its own branch.
6. Report findings ranked most severe first, each concrete and actionable, ending in a ship or don't-ship call. Merge the findings from both passes. A stopped spec-conformance pass contributes its one-line note.
   A review a person reads is human-facing (*Artifact audience* in `standards`): one or two sentences per finding naming the location and the fix. Include no preamble, no summary of the diff, no closing restatement, and no list of what was checked and found clean.
   Run the concision pass (`standards`) first when the report is posted as PR comments or a review body.
   When no user can answer and the review runs as a gate (`standards`), emit a machine-consumable verdict plus the ranked findings list.

Applying findings is a separate step (the `dev-workflow` skill, if you use it). Incidental defects are flagged, not fixed in place.
