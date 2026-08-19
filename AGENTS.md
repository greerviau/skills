# Authoring skills in this repo

This repo is a set of skills.
A skill is a prompt the model reads at invocation time, so every word costs context and competes for attention.
Write for a capable reader who will act on instruction, not one who needs convincing.

## Voice

- **Instruct, don't persuade.** State what to do. Cut sentences that justify a rule *to the model* — the "why it matters" clauses, the "a fix built on a guess tends to…" reassurance. The model doesn't need to be sold on the rule; it needs the rule. Keep rationale only when it changes *how* the reader applies the rule (e.g. when an edge case flips the decision).
- **Say it once.** Don't restate in a "Boundaries" or "Principles" section what the intro or procedure already said. Shared rules live in `standards`; reference them, never re-explain them.
- **Match weight to the task.** A simple, single-shot skill is a few plain sentences with no headers (see `handoff`). A stateful multi-step workflow earns structure. Don't pad a small skill into a big one, or force a genuinely complex one to be terse.
- **Reference detail earns its length.** Command examples, flag docs, and API mechanics (as in `lit-research`, `standards`, the `gh` calls in `spec-to-tickets`) are load-bearing — keep them. The target is rationale prose, not substance.
- **Each skill stands alone.** A skill does its own job to completion and must be usable without any sibling skill installed. Name another skill only as an *option* for a step that lives outside this skill's job (e.g. "land the change — the `dev-workflow` skill, if you use it"), never as a required handoff the skill depends on. Cross-references position siblings; they don't create dependencies.
- **Prose style.** Present tense describing current behavior. Semantic line breaks in prose markdown (one sentence per line). Normal dashes or semicolons, never em dashes.

## The test

Before keeping a sentence, ask: does it tell the reader something they'd act on differently, or is it reassuring them the rule is correct?
Cut the second kind.

## Writing skills

- Give each skill one job and state its defining constraint near the top.
- Treat the frontmatter description as a context pointer.
  Model-invoked descriptions name the trigger boundary and retain distinct trigger phrases.
  User-invoked descriptions give a short summary without trigger lists.
- Choose a leading term that names the skill's central behavior, then reuse it in the description and procedure.
- Make each phase executable and give it an observable completion condition.
  Prefer a real command, output, or artifact over a generic quality claim.
- Use progressive disclosure.
  Keep the main path in `SKILL.md`; move branch-specific reference material behind a pointer that says when to read it.
- Apply the no-op test and the duplication test sentence by sentence.
  Delete instructions that do not change behavior and keep each shared rule in one authoritative skill.
- Keep skills standalone.
  When a procedure needs another model-invoked skill, explicitly call the Skill tool; user-invoked skills cannot be called by another skill.
- Keep execution instructions in `SKILL.md` and human-facing explanation in a separate docs surface when the repo provides one.
