# Engineering skill composition

How the engineering skills fit together: which are entry points a request lands on, which are components another skill invokes, and who hands off to whom.
An autonomous runner reads this to route a request to the right entry point without reverse-engineering each skill.

## The graph

```mermaid
%%{init: {'flowchart': {'defaultRenderer': 'elk'}}}%%
flowchart LR
    wayfinder[wayfinder]
    spec[spec]
    tdd[tdd]
    debug[debug]
    flakehunt[flake-hunt]
    mergeconflict[merge-conflict]
    refactor[refactor]
    perf[perf]
    review[review]
    s2t[spec-to-tickets]
    techresearch[tech-research]
    depupgrade[dep-upgrade]
    devworkflow[dev-workflow]
    docaudit[doc-audit]
    run[run]
    openissue[open-issue]
    openpr[open-pr]

    wayfinder -->|cleared map| spec
    spec -->|reviewed plan| s2t
    spec -->|reviewed plan| devworkflow
    spec -->|open question| techresearch
    s2t -->|GitHub issues| devworkflow
    s2t -->|per-issue authoring| openissue
    tdd -->|test-first change| devworkflow
    debug -->|confirmed cause| devworkflow
    flakehunt -->|confirmed flake| devworkflow
    mergeconflict -->|resolved integration| devworkflow
    refactor -->|test-guarded change| devworkflow
    perf -->|measured change| devworkflow
    depupgrade -->|verified dependency change| devworkflow
    review -->|findings to apply| devworkflow

    devworkflow -->|issue-first step| openissue
    devworkflow -->|validate: docs| docaudit
    devworkflow -->|validate: runtime| run
    devworkflow -->|PR step| openpr
```

Arrows are runtime hand-offs (one skill invokes or feeds the next).
`standards` and `design` are missing on purpose: both are model-invoked policy references, never workflow steps, so an edge from each node would repeat the same fact rather than add one. `standards` is read by nearly every skill above; `design` by `spec`, `refactor`, `review`, and `tdd`. `perf` doesn't join that list - its guard is a benchmark, not a structural judgment call.
`mermaid` is missing too, for a related reason: it's invoked rather than merely read, but by nearly every skill that writes a diagram, so drawing it in would clutter the graph the same way.
`tdd` doubles as a component: it's drawn above as an entry point handing a change to `dev-workflow`, and `dev-workflow` names it in turn as the option for building test-first. The back edge is omitted to keep the graph acyclic.
`tech-research` has the same shape in miniature: drawn as an entry point `spec` reaches at an open question, but its findings file exists so `spec` can cite it back instead of re-deriving the answer, which would be a `spec`-to-`tech-research`-to-`spec` loop. The back edge is omitted for the same reason as `tdd`'s.
See the role table for who reads or invokes what.
`handoff` is missing for the opposite reason: it hands off to nothing and nothing hands off to it, so it has no edge to draw.
`prototype` is missing for the same reason: it produces design evidence, discards its source, and hands no code to another skill.
`improve-codebase-architecture` is missing because it produces a report and waits for the user to select a candidate; it has no runtime hand-off.
`wayfinder-starmap` is missing because it produces a browser artifact and has no runtime hand-off.
`rfc` is missing because it stops at a draft: sharing it with the team, and whatever the team then decides, stay with the author, so it hands nothing to another skill.
`triage` is missing because it produces an agent-ready brief for a fleet-style runner rather than feeding another skill directly.

## Roles

`user` skills require an explicit command.
`model` skills remain available for automatic selection and composition.

| Skill | Invocation | Role | Lands on it when | Hands off to |
| --- | --- | --- | --- | --- |
| `wayfinder` | user | Entry - multi-session planning | An effort spans sessions and its destination is clear but its route is not | `spec` (to collapse the cleared map into a reviewed plan) |
| `triage` | user | Entry - inbound intake | An inbound GitHub issue or pull request needs a category, disposition, and agent-ready brief | none (a fleet-style runner consumes the brief) |
| `spec` | user | Entry - planning | A request needs scoping into a reviewed plan before building | `spec-to-tickets` (to file issues) or `dev-workflow` (to execute) |
| `spec-to-tickets` | user | Entry - ticketing | A reviewed spec should become GitHub Issues | `open-issue` (writes and files each one), then `dev-workflow` (executes each issue) |
| `tech-research` | model | Entry - research | A technical question needs a sourced, version-pinned answer about third-party or external behavior | none (produces a findings file); `spec` cites it instead of re-deriving |
| `rfc` | model | Entry - design proposal | A design needs agreement across people before anyone plans or builds it | none (produces a draft; the author shares it and carries the decision) |
| `dep-upgrade` | model | Entry - dependency maintenance | A uv-managed Python project needs a dependency, lockfile, or git-sourced internal tag upgraded | `dev-workflow` (lands the verified dependency change) |
| `tdd` | model | Entry - test-first loop | A request is explicitly test-first ("TDD this", "write the test first", "red, green, refactor") | `dev-workflow` (lands the test-driven change) |
| `debug` | model | Entry - diagnosis | Something is broken and the cause is unknown | `dev-workflow` (lands the fix as a regression-tested change) |
| `flake-hunt` | model | Entry - flake diagnosis | A test failure may be intermittent, order-dependent, seed-dependent, or limited to CI | `dev-workflow` (lands the fix or bounded quarantine) |
| `merge-conflict` | model | Entry - integration recovery | A Git merge or rebase has conflicts that require semantic resolution | `dev-workflow` (resumes validation and the remaining integration workflow) |
| `refactor` | model | Entry - restructuring | Working code needs its structure improved without behavior change | `dev-workflow` (lands the test-guarded change) |
| `perf` | model | Entry - optimization | A change needs to get faster, cheaper, or higher-throughput, and the improvement must be proven with a before/after measurement | `dev-workflow` (lands the measured change) |
| `prototype` | model | Entry - design spike | A design question needs evidence from a disposable implementation | none (produces a decision record and discards the spike) |
| `improve-codebase-architecture` | user | Entry - architecture scan | A codebase needs structural opportunities identified and ranked before implementation | none (produces a visual report and waits for candidate selection) |
| `wayfinder-starmap` | user | Entry - map visualization | A Wayfinder map needs a browser-based visual view | none (produces a standalone star map) |
| `dev-workflow` | model | Entry + spine | Any request to write and land code in a GitHub repo | invokes `open-issue`, `doc-audit`, `run`, `open-pr`, and `tdd` for an explicitly test-first request |
| `review` | model | Entry - gate | Changes need checking before they land | reports only; findings go to `dev-workflow` to apply |
| `handoff` | user | Entry - utility | A conversation needs compacting for another agent to continue | none (produces a document) |
| `open-issue` | model | Component | `dev-workflow` reaches its issue-first step, `spec-to-tickets` files a work item, or an issue is opened standalone | none |
| `open-pr` | model | Component | `dev-workflow` reaches its PR step, or a PR is opened standalone | none |
| `doc-audit` | model | Component | `dev-workflow` validates, or docs/comments are written standalone | none |
| `run` | n/a | Component - harness-provided, not a skill in this repo | `dev-workflow` validates a change with a runtime surface | none |
| `mermaid` | model | Component | Any skill drafts, renders, or refines a diagram in a doc, spec, PR, or ADR | none |
| `standards` | model | Reference | Any skill applies a house rule | none - read directly |
| `design` | model | Reference | Any skill judges or explains a structural decision | none - read directly |

## Composition rules

- **Invocation is a boundary.** User-invoked skills run only after an explicit command and may compose model-invoked skills. Model-invoked skills remain available for automatic selection and may compose other model-invoked skills, including `dev-workflow`, `open-issue`, and `open-pr` when the task or repository instruction requires them.
- **`wayfinder` owns multi-session decision mapping.** It advances decision tickets and hands a cleared map to `spec`; it does not turn decisions into implementation work.
- **`improve-codebase-architecture` stops at candidate selection.** It grounds structural opportunities in code evidence and the design vocabulary, then leaves interface design and implementation to a later workflow.
- **`dev-workflow` is the spine.** Every skill that produces a code change hands the landing of it to `dev-workflow` rather than opening worktrees or PRs itself.
- **Entry points don't invoke each other's mechanics.** `tdd` drives the red-green-refactor loop but doesn't touch worktree/PR mechanics; `debug` proves a cause but doesn't commit; `refactor` and `perf` each prove their own guarantee (an unchanged test suite, a before/after measurement) but don't commit either; `dep-upgrade` proves a lockfile and downstream-suite result but doesn't commit; `review` reports but doesn't apply; `tech-research` answers a question but doesn't build; `spec` plans but doesn't build. Each stays in its lane and hands off.
- **Components are leaves, except `tdd`.** `open-issue`, `open-pr`, `doc-audit`, `run`, and `mermaid` are invoked by another skill and don't hand off further. `tdd` is invoked by `dev-workflow`'s own step the same way, but as an entry point in its own right it hands back to `dev-workflow` rather than terminating there; see the dual-role note under "The graph".
- **Delegation isn't hand-off.** `doc-audit` (its language check) and `mermaid` (its render loop) hand work to a subagent rather than to another skill; both stay leaves.
- **`standards` and `design` are policy, not phases.** Each is referenced for its own kind of rule — compliance for `standards`, structural vocabulary for `design` — never inserted as a numbered step.
- **`merge-conflict` completes the active merge or rebase.** It returns to `dev-workflow` for any remaining validation, publication, or PR lifecycle work.
