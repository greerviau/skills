# skills

Reusable agent skills for engineering, scientific research, and productivity.
Designed to get the most out of agents without sacrificing reliability or correctness.
Each skill is a plain-markdown procedure doc with a small YAML frontmatter header.

## Install with skills.sh

[skills.sh](https://skills.sh/greerviau/skills) copies the skills you pick into your project, where you can edit them.

```bash
npx skills@latest add greerviau/skills
```

## Install as a Claude Code plugin

The [Claude Code plugin](https://code.claude.com/docs/en/plugins) is a read-only bundle that updates as this repo changes.

```bash
/plugin marketplace add greerviau/skills
/plugin install greerviau@greerviau
```

## Skills reference

Every skill supports model invocation.
Each `SKILL.md` description states when the model should use it, including boundaries between related workflows.
Human-facing summaries live below and in `agents/openai.yaml`.
Skills that create issues or apply proposed rule changes retain their workflow-specific confirmation steps.

### Engineering

- [spec](skills/engineering/spec/SKILL.md) - turns a raw request into a reviewed spec. It interviews the user, explores the code, researches external behavior, checks each decision against the code, extends the repo's `UBIQUITOUS-LANGUAGE.md`, and writes a short human-facing spec whose work items become tickets.
- [spec-to-tickets](skills/engineering/spec-to-tickets/SKILL.md) - turns a reviewed spec into GitHub Issues, choosing a single-issue, flat, or parent-with-sub-issues shape from the spec's scope.
- [handoff](skills/engineering/handoff/SKILL.md) - compacts the current conversation into a handoff document for another agent.
- [retro](skills/engineering/retro/SKILL.md) - reads a finished session's log and proposes, for each mistake, the strongest fix that works: a structural change, a type, a lint or CI rule, or a test that fails on the mistake, and a written rule in a `CODING-STANDARDS.md` or a skill only for judgment calls.
- [implement](skills/engineering/implement/SKILL.md) - implements a prompt, issue, ticket, or spec in an isolated worktree, builds it test-first, reviews the diff, opens a PR, and finishes when CI passes or, in a repo with no CI, when the PR is open.
- [tdd](skills/engineering/tdd/SKILL.md) - the test-first loop every behavior change runs: pick the seam, write the failing test, confirm it fails for the right reason, write the minimum code to pass, and refactor under green.
- [diagnose](skills/engineering/diagnose/SKILL.md) - reproduces a failure, narrows to the root cause with evidence, and reports the cause before any fix.
- [why](skills/engineering/why/SKILL.md) - answers why code, a design, or a value is the way it is from the commits, PRs, reviews, and issues that shaped it, citing each source and marking inferences.
- [benchmark](skills/engineering/benchmark/SKILL.md) - vets a performance number before it is reported or acted on: names what limits it, checks that each side was tuned, counts errors, repeats alternating runs, measures the end-to-end share, and confirms the timed work ran.
- [prototype](skills/engineering/prototype/SKILL.md) - answers a design or feasibility question with a throwaway spike whose source is discarded.
- [ui-design](skills/engineering/ui-design/SKILL.md) - builds, restyles, or mocks up UI to a design standard for layout, type, colour, components, motion, and states, then renders it at desktop and phone widths and runs an axe-core accessibility and overflow audit before showing it. A mockup is a standalone artifact that leaves application source unchanged.
- [open-issue](skills/engineering/open-issue/SKILL.md) - checks for duplicates, honors the repo's issue template, writes a descriptive title and a short problem, reproduction, and acceptance-criteria body, and labels from `gh label list`.
- [open-pr](skills/engineering/open-pr/SKILL.md) - writes the `feat(...)` or `fix(...)` title and an evergreen body, then opens the PR.
- [stack-prs](skills/engineering/stack-prs/SKILL.md) - builds, submits, syncs, and merges GitHub stacked PRs with the `gh stack` extension, using the non-interactive form of each command.
- [review](skills/engineering/review/SKILL.md) - reviews a diff, branch, or PR for correctness, tests, flakiness, repo coding standards, structure, and conformance to the originating spec or issue.
- [verify](skills/engineering/verify/SKILL.md) - proves a change works by driving the running app the way a user does and keeping the evidence. On first use in a repo it writes a project-local `verify-<app>` skill with launch, doctor, drive, evidence, and cleanup steps and a feature map, and runs it once before relying on it.
- [refactor](skills/engineering/refactor/SKILL.md) - improves code structure without changing behavior, guarded by an unchanged test suite.
- [merge-conflict](skills/engineering/merge-conflict/SKILL.md) - resolves merge and rebase conflicts from both sides' intent, reruns the repository checks, and completes the operation.
- [doc-audit](skills/engineering/doc-audit/SKILL.md) - audits the documentation a change touched, rewrites stale passages in present tense, and checks the prose for plain language.

Skills write specs, plans, analyses, and glossaries into the repo by default (`docs/plans/`, `docs/analysis/`, `docs/UBIQUITOUS-LANGUAGE.md`).
Tell the agent, or put a line in the repo's agent instructions (`AGENTS.md` or equivalent), not to write documents to the repo, and they go to the OS temporary directory instead.

Coding rules live in `<repo>/CODING-STANDARDS.md` for one repo and in `~/CODING-STANDARDS.md` (referenced from your global agent instructions) for every repo. `retro` maintains both.

### General

- [doc-review](skills/general/doc-review/SKILL.md) - renders Markdown, text, HTML, PDF, or DOCX in the browser for inline comments, then returns each comment with its source location and quoted text so the document can be revised.
- [teach](skills/general/teach/SKILL.md) - teaches one topic over multiple sessions in chat, citing sources recorded in `RESOURCES.md`, quizzing for retrieval, and keeping a mission and learning records in the current directory.
- [plain-writing](skills/general/plain-writing/SKILL.md) - applies plain-writing rules informed by Simplified Technical English to answers, documents, messages, and agent instructions across domains.
  Its description requests invocation at session start, before the first response.
  The harness and agent determine whether it loads.
  It adapts STE principles without requiring full ASD-STE100 compliance.
- [visualize](skills/general/visualize/SKILL.md) - builds the smallest diagram, plot, or interactive single-file HTML page that demonstrates a concept, then renders it and checks the render before showing it.
- [lit-research](skills/general/lit-research/SKILL.md) - literature search, citation-graph snowballing, bibliography reference checks, and a literature-review workflow backed by OpenAlex, Semantic Scholar, PubMed, and Crossref, with every citation taken from API records.
- [diagram](skills/general/diagram/SKILL.md) - picks the diagram type (the 14 UML types plus ER) and runs the draft, render, critique, refine loop, with PlantUML for the types mermaid cannot draw.
- [ask-jev](skills/general/ask-jev/SKILL.md) - sends structured questions about supplied state to Jev's decision API and reports its probabilities, labels, or scores.
- [council](skills/general/council/SKILL.md) - does the requested work, then has judges from different providers score it out of 10 without seeing the threshold or earlier scores, merges their findings, and revises until every judge reaches the threshold or the round limit ends the loop. It runs only when the user asks for the council.
- [cook](skills/general/cook/SKILL.md) - takes a task the user will not watch to its end, whether code, research, writing, or operations. It asks every open question in one interview at the start, then works unattended, proves the deliverable meets each acceptance criterion, and reports once. A code change ends in a PR, and cook waits for CI and review bots. It never merges a PR, and it deploys, publishes, or sends only when the user explicitly allows it.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT, see [LICENSE](LICENSE).

## Attribution

These skills draw on the following collections:

- [mattpocock/skills](https://github.com/mattpocock/skills) by Matt Pocock.
- [t3dotgg/tstack](https://github.com/t3dotgg/tstack) by Theo Browne.
- [taste-skill](https://github.com/Leonxlnx/taste-skill) by Leonxlnx.
  The `ui-design` design standard and UI copy tells are adapted from it under the MIT License, Copyright (c) 2026 Leonxlnx.
- [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan.
  `benchmark`, `verify`, `why`, and parts of `retro`, `review`, `tdd`, `diagnose`, `cook`, and `plain-writing` are adapted from it under the MIT License, Copyright (c) 2026 Lauren Tan.
