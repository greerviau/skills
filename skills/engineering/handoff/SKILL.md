---
name: handoff
description: 'Use when the user asks to summarize the current session so another agent or a fresh session can continue the work.'
argument-hint: "What will the next session be used for?"
---

Write a document summarizing the current conversation so a fresh agent can continue the work.
Save it to the OS temporary directory.

The reader is an agent. Give exact paths, symbols, commands, and what was tried and what happened, in terse prose, with unverified items marked. Omit motivation and reassurance.

Include a "suggested skills" section naming skills the next agent should invoke.

Reference specs, plans, ADRs, issues, commits, and diffs by path or URL instead of repeating them.

Redact secrets and personal data, such as API keys, passwords, and personally identifiable information.

If the user passed arguments, treat them as the next session's focus and tailor the document to it.

