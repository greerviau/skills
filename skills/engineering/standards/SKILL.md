---
name: standards
description: The shared engineering standards the other engineering skills enforce — documentation and plain-language style, naming and ubiquitous language, testing bias, branch hygiene, issue hygiene, PR and commit hygiene, and the interactive-vs-autonomous interaction contract. Read it when a skill references "the standards skill", or directly when writing code, docs, commits, or PRs so the same house rules apply everywhere. Trigger on "what are the house standards", "engineering standards", "house style", "write this in plain language".
---

# standards

The single source of truth for the **compliance** rules the engineering skills share: house policy, not structural judgment (`design` is the peer reference for that).
Other skills (`spec`, `dev-workflow`, `review`, `doc-audit`, `refactor`, `debug`, `open-issue`, `open-pr`, `mermaid`, `design`, `tdd`) reference this document instead of restating these rules, so a change here changes them everywhere.
Each rule is policy; the referencing skill supplies the procedure that applies it at the right moment.

## Artifact audience

Every artifact has one primary reader: a person who will review it, or an agent who will execute it.
Decide which before writing. The two have opposite failure modes.

**Human-facing** - specs, issues, PR bodies, review comments, ADRs, docs.
The reader has the code and the diff, and limited attention; the artifact orients them and stops.
The failure mode is bulk.

- Work to a budget: issue and PR bodies roughly 200 words, rarely over 400; a spec one to two screens, longer only where the scope genuinely spans repos.
- State each fact once, in one section. Length comes from repeating the same fact across summary, requirements, and steps.
- Cut what the reader can't act on: background essays, alternatives that were never close, restatements of the diff or the issue, self-assessment ("comprehensive", "robust", "thorough").
- An empty section is an answer. Write "None known" rather than prose that fills the heading.
- Detail a reviewer would skip but an executor needs belongs in an agent-facing artifact, linked rather than inlined.

**Agent-facing** - implementation plans, task briefs, structured findings, handoff documents.
Nobody skims it; an ambiguity becomes a wrong edit.
The failure mode is vagueness, not length.

- Be exhaustive about facts: exact paths, symbols, signatures, commands, expected output, and the edge cases investigation surfaced. Every fact comes from investigation, never from a guess; mark anything unverified as unverified.
- Stay just as terse about prose. Precision earns length; motivation, alternatives, and reassurance don't. No paragraph argues that a step is a good idea.
- Each step is executable in isolation and names how to verify it.
- Write to a scratch or ignored path unless the user asks otherwise. These are disposable inputs to one run, not documents to maintain.

When one artifact has both readers, split it rather than compromise: the short one carries the review gate, the long one carries the detail, and the short one links to it.

**The test.** Before keeping a sentence in a human-facing artifact, ask whether a reviewer would decide differently without it.
Before cutting one from an agent-facing artifact, ask whether an executor could get it wrong without it.

**Justification answers the person who asked, not the artifact.**
Asked to explain or defend a decision, answer in the reply.
The explanation becomes a comment, a PR section, or a docstring only where that artifact's purpose is to record decisions (the exception under *Documentation and comments*), never because someone asked for it.

### The concision pass

Before an artifact is created, published, or handed to a review gate, give the draft to a subagent that didn't write it.
An author rationalizes their own sentences; fresh eyes are the point.

Hand the subagent the draft, its audience, and its budget — not the conversation that produced it.
Ask for **cuts, not a rewrite**: a rewrite reintroduces in new words what it just removed.
Each cut comes back as the quoted span, the rule it breaks, and what remains after it.

State the floor to the subagent: **never cut a fact.**
Paths, symbols, versions, numbers, commands, acceptance criteria, citations, and stated uncertainty stay, even when the draft is over budget — it reports "over budget, no filler left" rather than cutting into substance.
Only words carrying no fact get cut.

Apply what comes back, keeping the veto for a cut that takes a fact the pass misread as filler.
Run the check inline when no subagent is available.

Skip the pass when the draft is already comfortably inside its budget — a sixty-word PR body doesn't need a second agent.
Run it whenever the draft is over budget or too long to hold in one screen.

## Documentation and comments

- Write documentation and code comments in **present tense**, describing what *is*, not what changed. When editing existing docs, rewrite the affected passages to reflect current reality instead of appending "changed from ..." notes.
- **Exception:** records whose purpose is to capture a decision or history may describe before/after and motivation — ADRs, decision logs, design proposals, CHANGELOGs, release notes, migration guides, commit messages, and PR descriptions. This exception does not extend to code comments or documentation living alongside the code.
- Don't add repo layouts to documentation.
- In prose markdown (docs, READMEs, plans, design docs), use **semantic line breaks**: one sentence per line, no hard-wrapping to a fixed column width. This keeps diffs and blame scoped to the sentence that changed. Does not apply to code, tables, or code blocks.
- Favor mermaid diagrams over ASCII diagrams, unless mermaid can't express the diagram or the user asks otherwise. Don't one-shot a mermaid diagram — the `mermaid` skill supplies the render-and-refine procedure.
- A comment earns its place by carrying a fact the code cannot state: a non-obvious constraint, a why, a subtlety a reader would otherwise miss, an external contract the code has to match. Narrating what the code plainly does is noise to delete.
- Settle each comment rather than deciding by feel. Name the fact the comment carries, then look for code on the lines it describes that already states it. Delete the comment when the fact is unnamed, the code already states it, or you can't settle the call.
- Keep inline comments to **two lines or less**, and never clarify one with an example. An inline comment that needs an example or a third line means the code is not clean enough; fix the code instead of explaining it.
- Docstrings and module-level documentation are exempt from the length cap; present tense and the no-narrative rule still apply.

### Plain language

- Prefer the short common word: start (not begin/commence/initiate), use (not utilize/leverage), help (not facilitate), before (not prior to), after (not subsequent to), about (not regarding/concerning), get (not obtain/acquire), show (not demonstrate), also (not additionally/furthermore/moreover).
- No marketing adjectives: seamless, robust, powerful, cutting-edge, effortless, world-class, next-generation, revolutionary.
- Active voice with the actor named, and a verb for an action: "the parser reads the file" and "analyze the log", not "the file is read by the parser" or "perform an analysis of the log".
- No stacked auxiliaries. Not "it is important to note that this may help to improve"; write "this improves X".
- One word for one thing, and one meaning per word. Reuse a term verbatim rather than varying it for style; a second word for the same thing reads as a second thing.
- Every "this", "it", and "that" has one clear antecedent in the same sentence or the one before it. Where it does not, name the thing.

## Naming and ubiquitous language

- Name identifiers with **fully expressed words**, never abbreviations or truncations: `configuration` not `cfg`, `index` not `idx`, `sample_count` not `n_samps`. Domain acronyms the glossary records (`mz`, `xic`, `ms2`) are the real names, not abbreviations, and stay verbatim.
- Each repo (or bounded context within it) carries a glossary of its domain terms, by default `docs/UBIQUITOUS-LANGUAGE.md`, version-controlled so it travels with the code.
- **Read** the relevant glossary before naming anything, and use its terms **verbatim** — in code (types, functions, endpoints, tables, tests) and in prose (commits, PRs, docs). Never coin a synonym for a concept the glossary already names.
- **Extend** the glossary in the same change when implementation forces a new domain term or exposes a stale entry.

## Testing

- Weight tests toward **E2E over narrow unit tests** — exercise the functionality as close to how a user interacts with it as possible, driving the real entry point (CLI, endpoint, UI flow).
- A bug fix carries a regression test built from the reproduction, so the bug can't return silently.
- Flakiness is a defect: no unseeded randomness, real clocks, order-dependent tests, or un-stubbed network.

## Branch hygiene

- Unrelated out-of-scope bugs or improvements that surface mid-work don't get fixed on the current branch. **Flag them, then fix them on a separate worktree/branch/PR** following the normal workflow. A behavior change smuggled into a refactor, or an incidental fix folded into an unrelated PR, is exactly what this rule prevents.

## Issue hygiene

- **Work starts from an issue.** A code change gets an issue before the branch, so the PR's closing reference attaches the work to it and closes it on merge. The exceptions: an issue already covers the work, or the change is trivial (a typo, a one-line fix).
- Issue titles are plain descriptive sentences naming the problem or the request, not conventional-commit form. The type belongs in the label; `feat(...)` / `fix(...)` belongs on the commit and PR.
- Label from the repo's existing labels, read rather than guessed at. Propose a new label only when nothing in the set fits.

## PR and commit hygiene

- Titles follow the conventional-commit `feat(...)` / `fix(...)` form with a concise scope and summary.
- PR bodies are **evergreen** — written once and kept accurate as the branch evolves — covering problem/request, changes, testing, additional testing required, and regressions. Honor a repo's PR template where one exists.
- PR bodies and issue bodies are human-facing: hold them to the budget and the cuts in *Artifact audience* above.
- **No AI attribution of any kind:** no "generated by" notes in bodies, no agent co-author lines in commits.
- No volatile details that go stale (specific version bumps, transient counts).

## Interaction mode

Skills that can block on a human must degrade gracefully when run by an autonomous agent (e.g. a wingman-style runner) that cannot answer prompts. Every human-blocking skill declares its own degradation; the default contract is:

- **Interactive** — ask the user (via `AskUserQuestion` or a direct question) at genuine decision points, and pause for review where the skill calls for it.
- **Autonomous** — never block on a prompt. Take the most defensible default, **record the assumption** in the skill's durable output (the spec, the PR body, the findings report), and proceed. Emit machine-consumable output (a verdict plus a structured list) rather than a conversational back-and-forth, so a runner can gate on it.

Detect the mode from the environment: if there is no interactive user to answer (no way to surface an `AskUserQuestion`), run autonomous.
