# Authoring skills in this repo

This repo is a set of skills.
A skill is a prompt the model reads at invocation time, so every word costs context and competes for attention.
Write for a capable reader who acts on instruction and does not need convincing.

## Voice

- Instruct, don't persuade. State what to do. Cut sentences that justify a rule to the model, such as "why it matters" clauses and "a fix built on a guess tends to..." reassurance. Keep rationale only when it changes how the reader applies the rule, for example when an edge case flips the decision.
- Say it once. Do not restate in a "Boundaries" or "Principles" section what the intro or procedure already said. A skill states the rules it applies in its own body. No shared rules skill exists.
- Match weight to the task. A simple single-shot skill is a few plain sentences with no headers (see `handoff`). A stateful multi-step workflow earns structure. Do not pad a small skill or force a complex one to be terse.
- Keep reference detail. Command examples, flag docs, and API mechanics (as in `lit-research` and the `gh` calls in `spec-to-tickets`) are substance. Cut rationale prose, not substance.
- Each skill stands alone. A skill does its own job to completion and works without any sibling skill installed. Do not name another skill in a procedure. Write the action ("open a PR", "build test-first") and let the sibling's description trigger it.
- Describe current behavior in present tense. Use semantic line breaks in prose markdown (one sentence per line).
- Where a sentence reaches for an em dash, rewrite it with a comma, colon, period, or parentheses, whichever the sentence needs. A hyphen swapped in for the dash is not a rewrite.
- Write each rule as the claim or mechanism it states, in plain language: short common words, active voice, and the mechanism in place of a figurative label. Bold a term once, where it is defined.
- Write the autonomous fallback on the line of the checkpoint it governs, as "When no user can answer, ...".

## The test

Before keeping a sentence, ask whether it tells the reader something they would act on differently or only reassures them the rule is correct.
Cut the second kind.

## Writing skills

- Give each skill one job and state its defining constraint near the top.
- Treat the frontmatter description as a context pointer.
  Model-invoked descriptions name the trigger boundary and keep distinct trigger phrases.
  User-invoked descriptions give a short summary without trigger lists.
- Choose a leading term that names the skill's central behavior, then reuse it in the description and procedure.
- Make each phase executable with an observable completion condition.
  Prefer a real command, output, or artifact to a generic quality claim.
- Use progressive disclosure.
  Keep the main path in `SKILL.md`, and move branch-specific reference material behind a pointer that says when to read it.
- Apply the no-op test and the duplication test to each sentence.
  Delete instructions that do not change behavior, and keep each rule in the one skill that applies it.
- Keep execution instructions in `SKILL.md` and human-facing explanation in a separate docs surface when the repo has one.
- Write documents a skill produces (specs, plans, analyses, glossaries) into the repo by default, and write them to the OS temporary directory when the user or the repo's agent instructions (`AGENTS.md` or equivalent) say not to write documents to the repo. Do not add a setting for this.
