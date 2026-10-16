---
name: spec
description: Turn a raw request into a reviewed, human-facing spec grounded in the real code and broken into work items.
disable-model-invocation: true
---

# spec

Invoke `/spec` in Claude Code or `$spec` in Codex to turn a raw request (a feature, bug fix, pipeline, or infrastructure change, in one file or many repos) into a reviewed spec.
This skill plans and does not build. Implementation starts after the user reviews the spec.

The spec is human-facing: it states what, why, what "done" means, what is out of scope, and the work items that deliver it. It carries no step-level detail (files to edit, commands). The implementer works that out against the code as it is then.

## Procedure

1. Skim the territory. Identify the outcome and the kind of work, find which repos and subsystems are involved, and read the repo's `UBIQUITOUS-LANGUAGE.md` files for the affected contexts.
2. Interview the user about what the request leaves unclear: success criteria, scope boundaries, constraints, design forks, and ambiguous domain terms. Keep asking until the answers stop changing the spec.
   When no user can answer, resolve what exploration can, take the most defensible call on the rest, and record each assumption under "Risks and open questions".
3. Explore the code. Fan discovery out to read-only subagents in parallel when subagents are available and ask for paths, signatures, and short excerpts, not whole files. Check whether the request spans more than one repo. For a bug, find how to reproduce it end to end. Find how the change can be proven end to end with the repo's existing tests or entry points.
4. Research what you cannot read in the repo. For a claim about third-party or external behavior, check the installed source and tests first, then the vendor docs for the pinned version, then standards and release notes. Record each claim with its citation and a confidence level (high, moderate, low, unknown). When a decision depends on something you have not seen work, run a throwaway experiment.
5. Choose the approach. Where the user has not settled a design fork, pick the option that best fits quality, correctness, simplicity, scalability, and maintainability, giving development cost little weight, and record each rejected option with the reason it lost. Prefer the smallest change that fully solves the problem. A smaller change that only patches the symptom is not a candidate, and the spec says so. List real alternatives as follow-ups. Reuse an existing mechanism before adding a parallel one. When a new concept enters the design, re-derive the interfaces around it instead of keeping the old shape for compatibility.
   Then check each decision against the code it depends on: read the signatures, call sites, and input shapes and confirm the code supports it. A failed check changes the approach, adds a prerequisite work item, or goes under "Risks and open questions". When it contradicts something the user settled, return to the user.
6. Write the spec:
   - Summary: the request and the chosen approach.
   - Requirements: outcome, success criteria, scope boundaries, constraints.
   - Scope: repos and subsystems affected, with cross-repo coordination.
   - Approach: the key decisions, and why this option over the alternative for each real fork.
   - Work items: an ordered list, one line each, naming what it changes and the outcome that shows it is done. Size each so one PR lands it, and state dependencies. A one-file bug fix is one work item.
   - Testing strategy: how the change is proven end to end.
   - Risks and open questions, including external claims with their citations.

   Keep it to one or two screens, longer only when the scope spans repos. State each fact once and cut what a reviewer cannot act on.
7. Save the spec to `docs/plans/<date>-<name>.md` in the primary repo, in kebab-case with a date prefix such as `2026-07-07-fix-xic-shard-lookup.md`.
   When the user or the repo's agent instructions (`AGENTS.md` or equivalent) say not to write documents to the repo, write it to the OS temporary directory.
8. Update the glossary. Write new or corrected terms to the existing `UBIQUITOUS-LANGUAGE.md`, and create `docs/UBIQUITOUS-LANGUAGE.md` when none exists. Under a no-documents-in-the-repo instruction, extend an existing glossary and put new terms in the spec's text instead.
   One entry per term: the term, its precise meaning, and where useful the code artifacts that embody it. Scope entries to the repo, in present tense, with no planning status. Add a term only when it names a domain concept people could misunderstand. A repo with distinct bounded contexts gives each its own glossary, and the root glossary maps them.
9. Report the file paths with a one-line description each, and ask how to proceed: file the work items as issues, implement them in order, or iterate on the spec.
   Stop for the answer. When no user can answer, report the spec path and the recorded assumptions and stop without executing.
   When the spec supersedes an open PR, say so in the spec and close the PR.
