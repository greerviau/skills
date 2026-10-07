---
name: spec
description: Turn a raw request into a reviewed, human-facing spec broken into work items.
disable-model-invocation: true
---

# spec

Run `/spec` to turn a raw request (a feature, bug fix, pipeline, or infrastructure change, in one file or many repos) into a reviewed spec.
This skill plans and does not build. It writes the spec and the ubiquitous-language glossary updates. Implementation starts after the user reviews the spec.

The spec is human-facing (*Artifact audience* in `standards`). It states what, why, what "done" means, what is out of scope, and the work items that deliver it.
It does not carry step-level detail (files to edit, order of edits, commands). Whoever implements a work item works that out against the code as it is then.

## Principles

- Find the real code, call sites, and conventions before designing. Never plan against assumed structure.
- Fan discovery out to `Explore` subagents and keep only distilled findings (paths, symbols, code shape) in your context. Do not read whole files when a subagent can return the relevant excerpts.
- Size the spec to the request's scope. A one-file bug fix gets a short spec and a cross-repo pipeline gets a thorough one. A spec grows because it covers more decisions, not because it explains each at more length.
- Every decision in the spec holds against the real code. Implementation decides how to make each change, never whether the approach is possible.
- Use the domain's ubiquitous language in the spec, conversation, and code, as recorded in the repo's glossary.

## The ubiquitous-language glossary

The core rule (read the glossary, use its terms verbatim, extend it when a term settles or goes stale) is in `standards`. While specing:

- Read the glossaries for the affected contexts before the interview and use their terms exactly.
- Extend them as the interview and exploration settle new terms or reveal stale entries, confirming definitions with the user. Glossary updates ship with the spec.

Layout (an existing location or convention overrides these defaults): one `docs/UBIQUITOUS-LANGUAGE.md` at the repo root with one entry per term (term, precise meaning, and where useful the code artifacts that embody it).
A large repo with distinct bounded contexts gives each context its own `UBIQUITOUS-LANGUAGE.md`; the root glossary maps them and records cross-context name mismatches.
Scope entries to the repo, not the spec: no per-spec section and no planning status like *(planned)*. Group only by where in the repo the term belongs, and define in present tense.
Add a term when it names a domain concept people could misunderstand, not for every variable or utility.

## Procedure

### 1. Skim the territory

Identify the outcome and the kind of work (feature, bug, pipeline, infra).
Explore enough to know which repos and subsystems are involved, so the interview asks informed questions.
Read the glossaries for the affected contexts.

### 2. Interview the user

Before designing, ask the user (via `AskUserQuestion`) about whichever of these the request leaves unclear:

- Outcome and success criteria: what "done" looks like, and for whom.
- Scope boundaries: what is out of scope.
- Constraints: backward compatibility, performance, security, deadlines, required tooling.
- Design forks: where exploration found a real fork, which way to go.
- Terminology: domain terms the request uses ambiguously or the glossary does not cover. These become glossary entries.

Keep asking until the answers stop changing the spec, and record them in it.
When no user can answer (`standards`), resolve what exploration can, take the most defensible call on the rest, and record each assumption under "Risks and open questions".
Questions the user cannot answer better than exploration can go in the open-questions section.

### 3. Explore to discover scope

Map the real code the request touches: repos, subsystems, entry points, existing conventions, and risks.

- Use `Explore` subagents for breadth: locate files, entry points, call sites, tests, config, and existing patterns. Launch independent searches in parallel and ask for paths and short excerpts, not whole files.
- Check whether the request implies changes in more than one repo (a shared library and its consumers, infra and its service) and explore each.
- For bug fixes, identify how to reproduce end to end as a user hits it. The first work item starts with that reproduction.
- Note how the change can be proven end to end with the repo's existing tests or entry points.

Keep a running list: primary repo, other affected repos, key subsystems, new or corrected glossary terms, open questions.
If exploration surfaces a new fork, return to the user before designing past it. When no user can answer, settle it in step 4 and record it as an assumption.

### 4. Choose the approach and check it against the code

Pick the approach. Where the user has not settled a design fork, pick the option that best fits quality, correctness, and the structural standard in `design`, and record each rejected option with the reason it lost. Do not present a menu.

Then check each decision against the code it depends on.
Read the signatures, call sites, and input shapes involved, and confirm the code supports the decision: the function takes the argument the approach passes, the component accepts the input the new flow produces, the schema has the field the change reads.
Send the reads to `Explore` subagents and ask for the exact signatures and excerpts.

A failed check is a finding. Change the approach, add a prerequisite work item, or record it under "Risks and open questions".
If it contradicts something the user settled in the interview, return to them before writing the spec. When no user can answer, take the most defensible call and record it as an assumption.

### 5. Write the spec

Cover these at the density a reviewer needs:

- Summary: the request and chosen approach, in a few sentences.
- Requirements: outcome, success criteria, scope boundaries, and constraints from the interview.
- Scope: repos and subsystems affected, with cross-repo coordination called out.
- Approach: the key decisions, and for each real fork, why this option over the alternative. Skip forks that were never close.
- Work items: an ordered list, one line per item, each naming what it changes and the outcome that shows it is done. Size each so one PR lands it, and state dependencies between items and across repos. A one-file bug fix is one work item.
- Testing strategy: how the change is proven end to end, in a sentence or two.
- Risks and open questions: anything that could invalidate the approach or needs a user decision, including what the check in step 4 surfaced. State uncertainty plainly.

Hold it to the spec budget in *Artifact audience* (`standards`). Cut detail a reviewer cannot act on.

Write in the glossary's terms and refer to the glossary instead of defining terms inline.

### 6. Save the spec and update the glossary

Run the concision pass (`standards`) over the draft and apply what it returns.

Write the spec to a `.md` file with the Write tool. Use an explicit location or standing convention if there is one; otherwise `docs/plans/` in the primary repo. Name it in kebab-case with a date prefix, such as `2026-07-07-fix-xic-shard-lookup.md`.

Write new or corrected glossary entries to the appropriate `UBIQUITOUS-LANGUAGE.md` files, creating them (and the root map for multi-context repos) if needed, following the scoping rules above.

Report the file paths (spec and any glossary file) with a one-line description each. Do not paste their contents into the conversation.

### 7. Ask the user to review the spec

Say where the spec is and ask how to proceed:

- Ticket: the user files the work items as GitHub Issues, with `/spec-to-tickets` if installed.
- Implement: build the work items in order, reading the code each one touches before editing it.
- Iterate: refine the spec with the user and present again.

Stop for the answer.
When no user can answer, the review gate stays open (`standards`): report the spec path and the recorded assumptions, and stop without executing.
