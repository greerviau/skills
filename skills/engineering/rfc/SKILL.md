---
name: rfc
description: Draft an RFC against a template: a design proposal for circulation to the people who have to agree before anyone implements it.
disable-model-invocation: true
---

# rfc

Run `/rfc` explicitly to draft an RFC: a design proposal circulated for agreement before anyone implements it.
Its reader is a person deciding whether to agree, so it follows the human-facing rules in *Artifact audience* (`standards`): one fact in one section, nothing the reader cannot act on, and "None known" in place of prose that fills a heading.

This skill produces a draft and stops.
The status stays `Draft` throughout, including after the author is satisfied with it: agreement comes from the team, not from the conversation that wrote the document.
Sharing the draft, moving the status, and recording what the team decides are the author's, after this skill hands back.

## Structure

Read `TEMPLATE.md` in this skill directory and write against it.
Its order is load-bearing in one place: `Background / Context` precedes its `## Motivation` subsection, so the system is described before anything is wrong with it.
Drop a section that does not apply instead of filling it.

**Phase a proposal that lands in more than one piece.**
Each phase becomes a top-level section holding its own `## Alternatives considered` and `## Acceptance`, and the top-level `# Alternatives Considered` keeps only the choices that span every phase.
Order the phases by dependency and state in the Summary what forces the order.

## Section rules

- **Header block.** Link the document this work continues as `**Precursor:**`, not only from the body.
- **Background / Context.** Describe the system as it is before listing what is wrong with it.
  Separate what limits the system today from what the design has to preserve; a property working as intended is not a limitation.
- **Motivation.** State the problem. Do not argue for the solution here.
- **Goals.** A goal is an end state, never a mechanism and never a contrast with how things work today.
  State what must not happen, concretely.
- **Non-goals.** A non-goal names a real thing and links to it, or it is deleted.
- **Proposal.** Do not explain the mechanics of an option you did not take. That belongs in Alternatives Considered, or nowhere.
- **Alternatives Considered.** Each alternative gets `**Pros:**` and `**Cons:**` and stops there. No `Verdict` line under the list.
- **Trade-offs.** A mechanism claimed to recover a cost states what it leaves behind, tested against the worst case.
- **Acceptance.** Each criterion states an observable outcome, names what decides anything it leaves open, and rests only on capabilities this RFC proposes.
- **Open Questions.** Each is phrased as a question.
- **A section that is not part of the proposal** opens by saying why it is in the document.

## Procedure

### 1. Open the file and fill the header block

Write to the repo's RFC directory, `docs/rfc/` by default, honoring an existing location.
Name it date-prefixed kebab-case, e.g. `2026-08-17-staged-gpu-featurization-and-caching.md`.
Fill author, date, the tracking issue, and the precursor if one exists.

Done when the file exists with every header field either filled or deleted.

### 2. Ground the background in the real system

Read the code, config, and measurements the RFC describes before writing about them.
Name real artifacts (`featurize_flow`, `manifest-000.json`) rather than describing them.
Give each quantity an estimate and its scope, and mark each constraint as an impossibility or as only true today.

Done when every claim in Background traces to something read, and anything unmeasured is called out as unmeasured in the section that depends on it.

### 3. Write the proposal

Structure it per "Structure" above and write each section under its rule.
Where a design fork was real, record the rejected option under Alternatives Considered with its pros and cons; skip the ones that were never close.

Done when every section the RFC keeps satisfies its rule in "Section rules".

### 4. Cut it

Run the concision pass (`standards`) over the draft and apply what it returns.

### 5. Take a review round with the author

The draft gets inline review from the author before it reaches the team.
Ask the user to run `/doc-review` if they use it; it renders the draft for inline commenting and hands each comment back with its source location and quoted text.
Otherwise ask for comments against the draft directly.

Revise against every comment, then run another round.
Done when a round returns no comment that changes the design or the text of a section.

Hand back with the file path, the status still `Draft`, and anything a section rule could not be satisfied on.

**Interaction mode** (see `standards`): running autonomously, skip step 5's request for comments, review the draft against the section rules yourself, and report which rules the draft could not satisfy.
