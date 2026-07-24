---
name: doc-audit
description: Use after finishing any code change, and whenever writing or editing documentation or code comments. Reviews and updates docstrings, nearby comments, directory READMEs, docs files, and examples so they match the current code, written in present tense describing current state rather than a change narrative. Trigger on "before you're done, check the docs", "update the docs", "write a comment/docstring", or as a final step before treating any code change as complete.
---

# doc-audit

Documentation and comments should describe the current state of the code, in present tense — never framed as a change narrative (how it used to work, what changed, what ticket motivated it).

## Style rules

The documentation and comment style rules — present tense, the decision-history exception, no repo layouts, semantic line breaks, mermaid over ASCII — live in the `standards` skill under "Documentation and comments". Apply them when auditing.

## Procedure: auditing after a code change

Before treating any non-trivial code change as done:

1. Identify what you touched: which functions, modules, or behaviors changed.
2. Check the documentation that covers that surface: docstrings on the changed functions, comments in the surrounding code, the nearest directory README, any `docs/` files describing the feature, and any examples that demonstrate it.
3. For each piece of documentation found, check whether it still matches the code as it now stands. Update anything that's gone stale — rewritten to reflect current reality, not appended with a change note (see the exception above for decision-history documents).
4. Briefly note what you checked or updated, so the user can see the audit happened rather than being skipped.

Skip this procedure for changes with no documentation surface (pure test-only changes, formatting-only diffs) — there's nothing to audit.
