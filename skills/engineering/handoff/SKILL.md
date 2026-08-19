---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Run `/handoff` explicitly to write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS - not the current workspace.

The reader is an agent, not a person: follow the agent-facing rules in *Artifact audience* (`standards`) - exhaustive about facts (exact paths, symbols, commands, what was already tried and what it did), terse about prose, with anything unverified marked as such.

Include a "suggested skills" section in the document, which suggests skills that the agent should invoke.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.

Before saving, run the concision pass (`standards`) over the draft and apply what it returns. Its floor - never cut a fact - protects the paths, commands, and findings the next agent needs.
