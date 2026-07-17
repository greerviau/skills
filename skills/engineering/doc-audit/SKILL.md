---
name: doc-audit
description: Use after finishing any code change, and whenever writing or editing documentation or code comments. Reviews and updates docstrings, nearby comments, directory READMEs, docs files, and examples so they match the current code, written in present tense describing current state rather than a change narrative. Trigger on "before you're done, check the docs", "update the docs", "write a comment/docstring", or as a final step before treating any code change as complete.
---

# doc-audit

Documentation and comments should describe the current state of the code, in present tense — never framed as a change narrative (how it used to work, what changed, what ticket motivated it).

## Style rules

- Write documentation and code comments in present tense, describing what *is*, not what changed.
- When editing existing docs, rewrite the affected passages to reflect current reality instead of appending "changed from ..." notes.
- **Exception**: records whose purpose is to capture a decision or history may describe before/after and motivation — ADRs, decision logs, design proposals, CHANGELOGs, release notes, migration guides, commit messages, and PR descriptions. This exception does not extend to code comments or documentation living alongside the code.
- Don't add repo layouts to documentation.
- In prose markdown (docs, READMEs, plans, design docs), use semantic line breaks: one sentence per line, no hard-wrapping to a fixed column width. This keeps diffs and blame scoped to the sentence that changed. Does not apply to code, tables, or code blocks.
- Favor mermaid diagrams over ASCII diagrams, unless mermaid can't express the diagram or the user asks otherwise.
- When writing mermaid diagrams in documentation, dont just one shot it. Refine it until it looks good, use subagents to do so if necessary.

## Procedure: auditing after a code change

Before treating any non-trivial code change as done:

1. Identify what you touched: which functions, modules, or behaviors changed.
2. Check the documentation that covers that surface: docstrings on the changed functions, comments in the surrounding code, the nearest directory README, any `docs/` files describing the feature, and any examples that demonstrate it.
3. For each piece of documentation found, check whether it still matches the code as it now stands. Update anything that's gone stale — rewritten to reflect current reality, not appended with a change note (see the exception above for decision-history documents).
4. Briefly note what you checked or updated, so the user can see the audit happened rather than being skipped.

Skip this procedure for changes with no documentation surface (pure test-only changes, formatting-only diffs) — there's nothing to audit.
