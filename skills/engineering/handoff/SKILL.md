---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up.
argument-hint: "What will the next session be used for?"
disable-model-invocation: true
---

Run `/handoff` to write a document summarizing the current conversation so a fresh agent can continue the work. Save it to the OS temporary directory, not the current workspace.

The reader is an agent. Follow the agent-facing rules in *Artifact audience* (`standards`): exact paths, symbols, commands, and what was tried and what happened, in terse prose, with unverified items marked.

Include a "suggested skills" section naming skills the next agent should invoke.

Reference specs, plans, ADRs, issues, commits, and diffs by path or URL instead of repeating them.

Redact secrets and personal data, such as API keys, passwords, and personally identifiable information.

If the user passed arguments, treat them as the next session's focus and tailor the document to it.

Before saving, run the concision pass (`standards`) over the draft and apply what it returns. The never-cut-a-fact floor keeps the paths, commands, and findings the next agent needs.
