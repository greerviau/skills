---
name: wayfinder
description: Plan work larger than one agent session as a shared GitHub issue map of decision tickets.
argument-hint: "A loose idea to chart, or a map issue URL or number to continue"
disable-model-invocation: true
---

# wayfinder

Run `/wayfinder` explicitly for an effort whose destination is known but whose route does not fit in one agent session.
The skill stores the route in GitHub Issues as one map issue and child decision tickets.

Wayfinder plans the route.
It does not implement the destination unless the user explicitly asks for implementation outside the map.
A decision ticket resolves a question or prerequisite that someone needs settled before implementation.
A ticket that says "build X" is an implementation ticket and belongs after the map.

## GitHub model

The map is one issue labelled `wayfinder:map`.
Each ticket is a child issue of the map and has one `wayfinder:<type>` label: `research`, `prototype`, `grilling`, or `task`.
GitHub native sub-issues and issue dependencies expose the map's structure in the tracker.

The map is an index.
A decision's detail lives in its ticket, while the map records only a short linked gist in `Decisions so far`.

Refer to tickets by their titles in narration and map entries.
Put the issue number and URL inside the linked title rather than using a bare issue number.

## Ticket types

| Type | Mode | Use when | Resolution |
| --- | --- | --- | --- |
| `research` | AFK | A fact outside the working directory blocks a decision. | Read primary sources or local resources, then link the findings from the ticket. |
| `prototype` | HITL | A rough artifact is needed to decide how something looks or behaves. | Make the smallest disposable artifact, show it to the user, and record the user's choice. |
| `grilling` | HITL | Conversation can settle the question. | Ask focused questions and record the user's answer. |
| `task` | HITL or AFK | Manual prerequisite work blocks a decision. | Complete the prerequisite or give the user a precise checklist and record the result. |

`task` never delivers a slice of the destination.
A HITL ticket requires the user to answer for themselves.
Do not invent the user's answer to a `grilling` or `prototype` ticket.

## Preflight

Run these checks before charting or working a map:

1. Confirm GitHub authentication with `gh auth status`.
2. Resolve the repository with `gh repo view --json nameWithOwner --jq .nameWithOwner`.
3. When working an existing map, read it with `gh issue view <number> --comments`.
4. Read the repository's existing labels with `gh label list --limit 100`.
5. When charting and `wayfinder:map` exists, check existing maps with `gh issue list --label wayfinder:map --state all --limit 20` and stop if one already covers the destination.
If the label is absent, no labelled map exists yet; include the label in the confirmation step.

The first chart may need these labels:

- `wayfinder:map`
- `wayfinder:research`
- `wayfinder:prototype`
- `wayfinder:grilling`
- `wayfinder:task`

If a required label is missing, list the missing labels in the proposed breakdown.
Create them only after the user confirms the breakdown, using `gh label create <name> --color <hex> --description <description>`.
If no user can answer, create missing labels with sensible distinct colors and record that assumption in the map's `Notes`.

## Chart a map

Use this mode when the argument is a loose idea rather than an existing map issue.

### 1. Name the destination

State what the end of the map produces in one or two lines.
Examples include a reviewed spec, a decision ready for implementation, a proof of concept, or a migration completed in place.
The destination fixes the map's scope.

Ask the user the questions needed to settle the destination, constraints, and explicit exclusions.
Ask in breadth-first order so the first pass covers the whole effort.

### 2. Map the frontier

List the decisions and prerequisites that can be stated precisely now.
Create a ticket only when its question is sharp, even when the ticket is blocked.
Put questions that are in scope but cannot yet be phrased sharply in `Not yet specified`.
Put ruled-out work in `Out of scope`.

When the first breadth-first pass finds no fog and the route fits in one session, stop without creating a map.
Tell the user to use `spec` or another single-session planning path instead.

### 3. Propose the map and tickets

Present the destination, notes, initial tickets with types, dependencies, and fog.
Wait for confirmation before creating issues or labels.
In autonomous mode, use the most defensible interpretation, record assumptions in `Notes`, and continue.

Create the map with a body shaped like this:

```markdown
## Destination

<what reaching the end of this map produces>

## Notes

<domain, constraints, installed skills, and assumptions>

## Decisions so far

<!-- One linked line per closed ticket. Keep detail on the ticket. -->

## Not yet specified

<!-- In-scope questions that are not sharp enough to ticket yet. -->

## Out of scope

<!-- Work ruled beyond the destination. -->
```

Use a plain descriptive map title and create it with `wayfinder:map`:

```bash
gh issue create --title "<map title>" --body-file map.md --label wayfinder:map
```

Create each child with a title that states a question, and a body containing only the question:

```markdown
## Question

<the decision or prerequisite this ticket resolves>
```

```bash
gh issue create --title "<question title>" --body-file ticket.md --label "wayfinder:<type>"
```

Link children after all issues exist so every issue id is available:

```bash
repository=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
child_id=$(gh api "repos/$repository/issues/<child-number>" --jq .id)
gh api --method POST "repos/$repository/issues/<map-number>/sub_issues" -F sub_issue_id="$child_id"
```

Wire blocking edges in a second pass.
The `issue_id` value is the blocker's numeric database id, not its issue number or node id:

```bash
blocker_id=$(gh api "repos/$repository/issues/<blocker-number>" --jq .id)
gh api --method POST "repos/$repository/issues/<blocked-number>/dependencies/blocked_by" -F issue_id="$blocker_id"
```

When GitHub does not provide native sub-issues or dependencies, use a fallback.
Add `Part of #<map-number>` to each child, add an `## Open tickets` section to the map with one linked line per open child, and add `Blocked by: #<number>, #<number>` to blocked children.
Treat an issue as blocked while any listed blocker is open.

For each `research` ticket, start an independent research pass when the environment supports parallel agents.
Use `tech-research` if it is installed; otherwise read the relevant primary sources directly.
Link the findings from the ticket and resolve the ticket only after the source and confidence are recorded.
Do not resolve other ticket types while charting.

## Work through a map

Use this mode when the argument is a map URL or issue number.

### 1. Load the map at low resolution

Verify that the issue is open and labelled `wayfinder:map`.
Read its body, but load child bodies only after choosing a ticket:

```bash
gh issue view <map-number> --json number,title,body,state,labels
```

List native children in their tracker order:

```bash
repository=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
gh api "repos/$repository/issues/<map-number>/sub_issues?per_page=100" \
  --jq '.[] | [.number, .title, .state, ([.assignees[].login] | join(","))] | @tsv'
```

For each open child, query its open blockers:

```bash
gh api "repos/$repository/issues/<child-number>/dependencies/blocked_by" \
  --jq '[.[] | select(.state == "open")] | length'
```

The frontier contains every open child with no open blocker and no assignee.
Select the first frontier ticket in tracker order.
A closed blocker does not keep a ticket off the frontier.
If the user names a ticket, use it only after checking that it is an open child and is unblocked.

With fallback links, read the map's `## Open tickets` section and each child's `Blocked by` line instead.

### 2. Claim one ticket

The assignment is the claim.
Assign the ticket before reading its full body or doing any work:

```bash
gh issue edit <ticket-number> --add-assignee @me
```

A session resolves one non-research ticket.
Research tickets are the only exception when independent research passes already run in parallel.

### 3. Resolve the question

Read the ticket and the map's `Notes`.
Apply any skills named there, or perform the required research, prototype, conversation, or prerequisite work directly.
Keep production implementation outside the map unless the user explicitly changes the destination and scope.

Link artifacts from the ticket rather than pasting large outputs into the issue.
For a HITL ticket, stop and ask the user when their decision is required.

### 4. Record and advance

Post the answer or resulting facts as a resolution comment, then close the ticket:

```bash
gh issue comment <ticket-number> --body-file resolution.md
gh issue close <ticket-number>
```

Fetch the latest map body before editing it so concurrent sessions do not overwrite newer decisions.
Append one line under `## Decisions so far`:

```markdown
- [<closed ticket title>](<ticket URL>) - <one-line gist of the answer>
```

Remove fog that has become a precise ticket.
Create newly surfaced tickets, then wire their child and blocking relationships in a second pass.
Add work beyond the destination to `Out of scope` and close any existing ticket that represents it; do not add it to `Decisions so far`.

Stop after advancing one ticket.
The next session reloads the map and recomputes the frontier.

## Completion

The map is clear when every child is closed, `Not yet specified` is empty, and `Out of scope` records deliberate exclusions.
The map is a record of decisions, not a build plan.
Use `spec`, if installed, to turn the cleared decisions into a reviewed implementation plan.
If no planning skill is installed, write the implementation plan from the closed tickets before creating implementation work.
Do not create implementation tickets from a wayfinder map without first collapsing its decisions into a reviewed plan.

## Interaction mode

Charting and ticket resolution can require a human.
In an interactive session, ask for confirmation before creating issues and ask the user to resolve HITL tickets.
In an autonomous session, do not block: choose the most defensible destination and ticket breakdown, record each assumption in `Notes` or the resolution comment, and continue.
Never claim a HITL ticket is resolved without the user's decision; leave it open for the user.
