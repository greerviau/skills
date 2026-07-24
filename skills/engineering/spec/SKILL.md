---
name: spec
description: Use when the user hands you a request to scope and plan before building — a feature they want, a bug to fix, a new pipeline, or a piece of infrastructure — and wants a reviewed plan of action rather than immediate code. Interviews the user to sharpen the requirements, explores the relevant code across one or many repos to discover scope, designs an approach, maintains the repo's ubiquitous-language glossary, writes the plan to a markdown file, and asks whether to execute or iterate. Trigger on "/spec", "spec this out", "plan this", "scope this out", "how should we approach", "figure out what it'll take to", "before we build", "write a spec/plan for ...".
---

# spec

Turn a raw request — a feature, a bug fix, a new pipeline, a piece of infrastructure — into a concrete, reviewed plan of action, whether it touches one file or spans many repos. **This skill plans; it does not build.** The only files it writes are the plan document and the ubiquitous-language glossary. Implementation starts only after the user reviews the plan and chooses to execute.

## Principles

- **Discover before designing.** Find the real code, call sites, and conventions first; never plan against assumed structure.
- **Be context-efficient.** Fan discovery out to `Explore` subagents and keep only distilled findings — paths, symbols, the shape of the code — in your own context. Don't read whole files in when a subagent can return the relevant excerpts.
- **Match the request's weight.** A one-file bug fix gets a short plan; a cross-repo pipeline gets a thorough one.
- **The plan is a contract.** Someone should be able to execute it without re-deriving scope. Name specific files, functions, and steps.
- **Speak the domain's ubiquitous language.** Spec, conversation, and code use the same words for the same concepts, recorded in the repo's glossary.

## The ubiquitous-language glossary

The core rule — read the glossary, use its terms verbatim, extend it when a term settles or goes stale — lives in the `standards` skill. During specing:

- **Read** the glossaries covering the affected contexts before the interview, and use their terms exactly.
- **Extend** them as the interview and exploration settle new terms or reveal stale entries, confirming definitions with the user. Glossary updates ship with the plan as part of its deliverable.

Layout (honor any existing location or convention over these defaults): one `docs/UBIQUITOUS-LANGUAGE.md` at the repo root, one entry per term (term, precise meaning, and where useful the code artifacts embodying it). In a large repo with distinct bounded contexts, each context keeps its own `UBIQUITOUS-LANGUAGE.md` and the root glossary maps them and records cross-context name mismatches. Scope entries to the repo, not the spec — never a per-spec section or a planning status like *(planned)*; group only by where in the repo the term belongs, and define in present tense. A term belongs in the glossary when it names a domain concept people could misunderstand — not every variable or utility.

## Procedure

### 1. Skim the territory

Restate the request to yourself: what outcome, and what kind of work (feature / bug / pipeline / infra)? Do a quick first-pass exploration — enough to know which repos and subsystems are in play — so the interview asks informed questions. Read the glossaries for the affected contexts here.

### 2. Interview the user

Before designing, grill the user (via `AskUserQuestion`) for the details that most often invalidate a spec, covering whichever the request leaves unclear:

- **Outcome and success criteria** — what does "done" look like, and for whom?
- **Scope boundaries** — what is explicitly *out* of scope?
- **Constraints** — backward compatibility, performance, security, deadlines, required tooling.
- **Design-fork preferences** — where exploration revealed a real fork, ask which way rather than guessing.
- **Terminology** — pin down any domain term the request uses ambiguously or the glossary doesn't cover. These become glossary entries.

Keep asking until the answers stop changing the plan. Record them in the spec. Questions the user can't answer better than exploration can go in the open-questions section instead.

### 3. Explore to discover scope

Map the real code the request touches: which repos, which files and symbols are the touch points, the existing conventions, and where the seams and risks are.

- Prefer `Explore` subagents for breadth — locate files, entry points, call sites, tests, config, and existing patterns; launch independent searches in parallel; ask each for paths + short excerpts, not whole files.
- Check explicitly whether the request implies changes in more than one repo (a shared library plus its consumers, infra plus its service) and discover each side.
- **For bug fixes:** identify how to reproduce end-to-end, as close to how a user hits it as possible. The plan's first step is reproduction.
- Note existing conventions (test framework, lint setup, layout, naming) so the plan fits the codebase.

Keep a running list: primary repo, other affected repos, key files/symbols, new or corrected glossary terms, open questions. If exploration surfaces a new fork, go back to the user before designing past it.

### 4. Design and build the plan

Decide on an approach and turn it into a step-by-step plan. Where the user hasn't settled a design fork, pick the option that best fits quality, correctness, simplicity, robustness, and maintainability, and note the alternative as a rejected option with the reason — don't present a menu.

The plan covers:

- **Summary** — the request and chosen approach, in a few sentences.
- **Requirements** — outcome, success criteria, scope boundaries, constraints from the interview.
- **Scope** — repos and files affected; call out cross-repo coordination.
- **Approach / design** — key decisions and, for anything non-trivial, why this over the obvious alternative.
- **Steps** — an ordered, concrete list; each step names the file(s)/symbol(s) it touches and what changes. For bugs, step 1 is reproduction.
- **Testing & verification** — how the change is proven end-to-end, using the repo's existing setup.
- **Risks & open questions** — anything that could invalidate the plan or needs a user decision. State uncertainty plainly.

Write the plan in the glossary's terms; refer to the glossary rather than defining terms inline.

### 5. Save the plan and update the glossary

Write the plan to a `.md` file with the Write tool. Honor an explicit location or standing convention; otherwise default to `docs/plans/` in the primary repo. Name it in kebab-case, prefixed with the current date, e.g. `2026-07-07-fix-xic-shard-lookup.md`.

Write any new or corrected glossary entries to the appropriate `UBIQUITOUS-LANGUAGE.md` file(s), creating them (and the root map, for multi-context repos) if needed. Follow the glossary scoping rules above.

Report only the file paths and a one-line description each — don't dump the plan back into the conversation.

### 6. Ask the user to review

Tell the user the plan is written and where, then ask how to proceed:

- **Execute** — start implementing as written (follow the plan step by step, keeping the file updated if reality diverges).
- **Iterate** — refine the plan together first, then re-present.

Ask as a genuine choice and stop for the answer.

**Interaction mode** (see `standards`): running autonomously, don't block on the interview or the review gate — resolve what exploration can, take the most defensible call on the rest, record every such assumption in "Risks & open questions", then write the plan and proceed to execute it (via the `dev-workflow` skill, if you use it).
