---
name: spec
description: Use when the user hands you a request to scope and plan before building — a feature they want, a bug to fix, a new pipeline, or a piece of infrastructure — and wants a reviewed plan of action rather than immediate code. Explores the relevant code across one or many repos to discover scope, designs an approach, writes the plan to a markdown file, and asks whether to execute or iterate. Trigger on "/spec", "spec this out", "plan this", "scope this out", "write a spec/plan for ...".
---

# spec

Turn a raw request into a concrete, reviewed plan of action. The request may be a feature, a bug fix, a new pipeline, or a piece of infrastructure. It may be confined to a single file in a single repo, or span many files across many repos. **Do not write implementation code in this skill** — the deliverable is a plan the user reviews before any building starts.

## Principles

- **Discover before designing.** Never plan against assumed structure. Find the real code, the real call sites, the real conventions first.
- **Be context-efficient.** Exploration across a multi-repo workspace produces a lot of bytes. Fan discovery out to `Explore` subagents (or the sandbox) and keep only the distilled findings — file paths, symbols, and the shape of the code — in your own context. Don't read whole files into context when a subagent can return the relevant excerpts.
- **Match the request's weight.** A one-file bug fix gets a short plan; a new cross-repo pipeline gets a thorough one. Don't pad a small request into a big document, and don't under-specify a large one.
- **The plan is a contract.** Someone (you, later, or a teammate) should be able to execute it without re-deriving the scope. Name specific files, functions, and steps — not vague intentions.

## Procedure

### 1. Understand the request

Restate the request in one or two sentences to yourself: what outcome does the user want, and what kind of work is it (feature / bug / pipeline / infra)? If the request is genuinely ambiguous in a way that changes the plan (which system, which behavior, which of two repos), ask 1–3 focused clarifying questions now — before spending exploration effort. Otherwise proceed; you'll surface open questions in the plan.

### 2. Explore to discover scope

Map the real code the request touches. The goal is to know, concretely: which repos are involved, which files and symbols are the touch points, what the existing conventions are, and where the seams and risks are.

- Prefer `Explore` subagents for breadth — dispatch them to locate relevant files, entry points, call sites, tests, config, and existing patterns across the workspace. Launch independent searches in parallel. Ask each to return paths + short excerpts, not whole files.
- The scope may cross repo boundaries. Explicitly check whether the request implies changes in more than one repo (e.g. a shared library plus its consumers, infra plus the service it runs) and discover each side.
- **For bug fixes specifically:** identify how to reproduce the bug end-to-end, as close to how a user hits it as possible. The plan's first step should be reproduction, so the eventual fix targets the real cause rather than a guess.
- Note the existing conventions (test framework, lint setup, directory layout, naming) so the plan proposes work that fits the codebase rather than fighting it.

Keep a running list of: **primary repo**, other affected repos, key files/symbols, and open questions.

### 3. Design and build the plan

Decide on an approach and turn it into a step-by-step plan of action. If there's a real fork in the design (two viable architectures), pick the one that best fits quality, correctness, simplicity, robustness, and long-term maintainability, and note the alternative briefly as a rejected option with the reason — don't present a menu.

The plan should cover:

- **Summary** — what the request is and the chosen approach, in a few sentences.
- **Scope** — repos and files affected; call out cross-repo coordination if any.
- **Approach / design** — the key decisions and why. For anything non-trivial, why this over the obvious alternative.
- **Steps** — an ordered, concrete list of the work. Each step names the file(s)/symbol(s) it touches and what changes. For bugs, step 1 is reproduction.
- **Testing & verification** — how the change will be proven to work end-to-end, using the repo's existing test/verify setup.
- **Risks & open questions** — anything that could invalidate the plan or needs a decision from the user.

### 4. Save the plan to a markdown file

Write the plan to a `.md` file. Choose the location in this order:

1. **Explicit location in the request** — if the user said where to put it, use that.
2. **A standing convention** — check for a project or user instruction about where planning / scratch / design docs belong (e.g. a `CLAUDE.md` directive, a memory, or a location the user has told you to use before). If one exists, honor it. This lets the same skill adapt to each machine and to the user changing their preference later — do not hardcode a path.
3. **Default** — a `docs/plans/` folder inside the primary repo the request targets. Create the folder if it doesn't exist.

Name the file descriptively in kebab-case, prefixed with the current date, e.g. `2026-07-07-fix-xic-shard-lookup.md`. Use the actual current date.

Write the file with the native Write tool. After writing, report only the file path and a one-line description — don't dump the plan's full contents back into the conversation.

### 5. Ask the user to review

Tell the user the plan is written and where. Then ask how they want to proceed:

- **Execute** — start implementing the plan as written.
- **Iterate** — refine the plan together first (they'll give feedback; update the file and re-present).

Ask this as a genuine choice and stop for their answer. Do not begin implementation until they choose to execute.

## Notes

- This skill plans; it does not build. The only files it writes are the plan document itself.
- If execution is chosen, follow the plan step by step, and keep the plan file updated if reality diverges from it during the build.
- Keep the plan honest about uncertainty — an open question stated plainly is more useful than a confident guess that sends the implementation the wrong way.
