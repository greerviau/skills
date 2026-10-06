---
name: standards
description: Shared engineering standards for documentation, naming, testing, branch and issue hygiene, pull requests and commits, and interactive or autonomous runs. Read when writing project artifacts or when another skill references standards.
---

# standards

The single source of truth for the compliance rules the engineering skills share: house policy, not structural judgment (`design` covers structure).
`spec`, `dev-workflow`, `review`, `doc-audit`, `refactor`, `debug`, `open-issue`, `open-pr`, `mermaid`, `design`, `tdd`, and `triage` reference this document instead of restating it.
Each rule is policy; the referencing skill supplies the procedure that applies it.

## Artifact audience

Every artifact has one primary reader: a person who reviews it or an agent who executes it.
Decide which before writing.

### Human-facing

Specs, issues, PR bodies, review comments, ADRs, docs.
The reader has the code and the diff and limited attention. The artifact orients them and stops.
The failure mode is bulk.

- Budget: issue and PR bodies about 200 words, rarely over 400. A spec is one to two screens, longer only when the scope spans repos.
- State each fact once, in one section. Repeating a fact across summary, requirements, and steps is the main source of length.
- Cut what the reader cannot act on: background essays, alternatives that were never close, restatements of the diff or the issue, self-assessment ("comprehensive", "robust", "thorough").
- An empty section is an answer. Write "None known" instead of prose that fills the heading.
- Put detail a reviewer would skip and an executor needs in an agent-facing artifact, and link to it.

### Agent-facing

Implementation plans, task briefs, structured findings, handoff documents.
Nobody skims these, and an ambiguity becomes a wrong edit.
The failure mode is vagueness.

- Give exact paths, symbols, signatures, commands, expected output, and the edge cases investigation surfaced. Every fact comes from investigation, never a guess. Mark anything unverified as unverified.
- Keep prose terse. Omit motivation, alternatives, and reassurance.
- Make each step executable in isolation and name how to verify it.
- Write to a scratch or ignored path unless the user asks otherwise. These are inputs to one run and are not maintained.

When one artifact has both readers, split it. The short one carries the review gate and links to the long one, which carries the detail.

### Tests for cutting

- Human-facing: keep a sentence only if a reviewer would decide differently without it.
- Agent-facing: cut a sentence only if an executor could not get it wrong without it.

### Justification

When asked to explain or defend a decision, answer in the reply.
The explanation goes into a comment, PR section, or docstring only where that artifact records decisions (the exception under *Documentation and comments*), never because someone asked.

### The concision pass

Before an artifact is created, published, or sent to a review gate, give the draft to a subagent that did not write it.
Pass the draft, its audience, and its budget, and leave out the conversation that produced it.
The subagent returns cuts, not a rewrite. Each cut is the quoted span, the rule it breaks, and what remains.

The subagent must never cut a fact.
Paths, symbols, versions, numbers, commands, acceptance criteria, citations, and stated uncertainty stay even when the draft is over budget; it reports "over budget, no filler left" instead.
Only words carrying no fact are cut.

Apply the cuts, and veto any that remove a fact the subagent misread as filler.
Run the check inline when no subagent is available.
Skip the pass when the draft is well inside its budget, such as a sixty-word PR body. Run it when the draft is over budget or longer than one screen.

## Documentation and comments

- Write documentation and code comments in present tense, describing what is, not what changed. When editing docs, rewrite the affected passages to match current behavior instead of appending "changed from ..." notes.
- Records that exist to capture a decision or history may describe before/after and motivation: ADRs, decision logs, design proposals, CHANGELOGs, release notes, migration guides, commit messages, and PR descriptions. Code comments and documentation next to the code do not get this exception.
- Do not add repo layouts to documentation.
- In prose markdown (docs, READMEs, plans, design docs), use semantic line breaks: one sentence per line, no hard-wrapping. Code, tables, and code blocks are exempt.
- Prefer mermaid to ASCII diagrams unless mermaid cannot express the diagram or the user asks otherwise. Draft mermaid with the `mermaid` skill's render-and-refine procedure.
- A comment carries a fact the code cannot state: a non-obvious constraint, a reason, a subtlety, or an external contract the code must match. Delete comments that narrate what the code does.
- For each comment, name the fact it carries and check whether the code on the lines it describes already states it. Delete the comment when the fact is unnamed, the code states it, or you cannot decide.
- Limit inline comments to two lines and never add an example. A comment that needs an example or a third line means the code needs fixing.
- A docstring states what the thing does, then parameters, return, and raises, in the language's standard format (PEP 257 or Google style for Python). Nothing else belongs in it.
- Keep a docstring summary to one line. Add a body only when a caller cannot use the thing correctly without it. A docstring that walks through the implementation, enumerates edge cases, or argues for the design is over budget at any length.
- Omit parameters the signature and types already state. "path: str, the path as a string" carries no fact.
- Module-level documentation is exempt from the two-line inline cap. The present-tense and no-narrative rules still apply.

### Precision

These apply to any document a person reads.

- Open a section with one sentence saying what the thing is, before any mechanism.
- State a problem in domain terms, not in terms of the document's own scoping.
- Link any prior work you cite.
- Do not write a conclusion the author has not reached. An option still being weighed is "we could do X", not a specified design.
- Explain a behavior with a concrete case and real numbers.
- Name the artifact: `manifest-000.json`, not "the per-part manifest file".
- Replace a vague quantifier with an estimate and its scope: "roughly 10-20 at today's volume", not "in the tens" or "plus a handful".
- Label an illustrative case as one example of several, so a single instance does not read as the whole subject.
- For every constraint, say whether it is impossible or only true today. "A GitHub runner carries only `metaflow boto3 kubernetes pyyaml`" is true today. "The Kubernetes API server owns the object-size limit" will not change.
- When a section depends on a mechanism from another document, restate it in one sentence first.
- A cross reference names its target: "see Phase 2 of this doc", never "see below".

### Plain language

- Use the short common word: start (not begin, commence, initiate), use (not utilize, leverage), help (not facilitate), before (not prior to), after (not subsequent to), about (not regarding, concerning), get (not obtain, acquire), show (not demonstrate), also (not additionally, furthermore, moreover).
- No marketing adjectives: seamless, robust, powerful, cutting-edge, effortless, world-class, next-generation, revolutionary.
- Use active voice with the actor named and a verb for the action: "the parser reads the file" and "analyze the log", not "the file is read by the parser" or "perform an analysis of the log".
- No stacked auxiliaries. Write "this improves X", not "it is important to note that this may help to improve X".
- Use one word per thing and one meaning per word. Repeat a term verbatim instead of varying it, because a second word reads as a second thing.
- Give every "this", "it", and "that" one antecedent in the same sentence or the one before. Otherwise name the thing.
- Write the mechanism in place of a figurative label: what breaks, what blocks what, or the parameter's name. "Load-bearing", "the lever", and "surgical" name no mechanism.
- State a contrast only when the reader would otherwise assume the rejected option. A "not X, but Y" written for rhythm adds no fact.
- End a sentence on its claim. A consequence that matters gets its own sentence with its mechanism, never a trailing "-ing" clause that grades the sentence before it.
- Bold a term once, where it is defined. A list item is a sentence, never a `**Bold term:** explanation` pair.

## Naming and ubiquitous language

- Name identifiers with full words, never abbreviations or truncations: `configuration` not `cfg`, `index` not `idx`, `sample_count` not `n_samps`. Domain acronyms the glossary records (`mz`, `xic`, `ms2`) are names and stay verbatim.
- Each repo, or bounded context within it, keeps a glossary of domain terms, by default `docs/UBIQUITOUS-LANGUAGE.md`, under version control.
- Read the relevant glossary before naming anything and use its terms verbatim in code (types, functions, endpoints, tables, tests) and prose (commits, PRs, docs). Never coin a synonym for a term the glossary defines.
- Extend the glossary in the same change when implementation forces a new domain term or exposes a stale entry.

## Testing

- Weight tests toward E2E over narrow unit tests. Exercise the functionality as a user does, through the real entry point (CLI, endpoint, UI flow).
- A bug fix carries a regression test built from the reproduction.
- Flakiness is a defect. Do not use unseeded randomness, real clocks, order-dependent tests, or un-stubbed network calls.

## Branch hygiene

Unrelated bugs or improvements found mid-work are not fixed on the current branch.
Flag them, then fix them on a separate worktree, branch, and PR through the normal workflow.
This rule stops a behavior change from riding in a refactor and an incidental fix from riding in an unrelated PR.

## Issue hygiene

- Work starts from an issue. A code change gets an issue before the branch, so the PR's closing reference attaches to it and closes it on merge. Exceptions: an issue already covers the work, or the change is trivial (a typo, a one-line fix).
- Issue titles are plain descriptive sentences naming the problem or request, not conventional-commit form. The type goes in the label; `feat(...)` and `fix(...)` go on the commit and PR.
- Label from the repo's existing labels, read with `gh label list`. Propose a new label only when none fits.

## PR and commit hygiene

- Titles use conventional-commit form, `feat(...)` or `fix(...)`, with a concise scope and summary.
- PR bodies are **evergreen**: written once and kept accurate as the branch changes. They cover problem or request, changes, testing, additional testing required, and regressions. Follow the repo's PR template if one exists.
- PR and issue bodies are human-facing. Hold them to the budget and cuts in *Artifact audience*.
- No AI attribution: no "generated by" notes in bodies and no agent co-author lines in commits.
- No volatile details that go stale, such as specific version bumps or transient counts.

## Interaction mode

A skill that can block on a human writes its autonomous fallback on the line of the checkpoint it governs, as "When no user can answer, ...", so the agent reads it at the moment it applies. The default at any checkpoint:

- Interactive: ask the user (via `AskUserQuestion` or a direct question) at decision points, and pause for review where the skill calls for it.
- Autonomous: never block on a prompt. Take the most defensible default, record the assumption in the skill's durable output (the spec, the PR body, the findings report), and proceed. Emit a verdict plus a structured list so a runner can gate on it.
- A review gate stays with a person. At a review gate with no user to answer, write the artifact with its recorded assumptions and stop with the gate open. Never approve your own artifact.

Run autonomous when no interactive user can answer, meaning there is no way to surface an `AskUserQuestion`.
