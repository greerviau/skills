# Authoring skills in this repo

This repo is a set of skills.
A skill is a prompt the model reads at invocation time, so every word costs context and competes for attention.
Write for a capable reader who acts on instruction and does not need convincing.

## Voice

- Instruct, don't persuade. State what to do. Cut sentences that justify a rule to the model, such as "why it matters" clauses and "a fix built on a guess tends to..." reassurance. Keep rationale only when it changes how the reader applies the rule, for example when an edge case flips the decision.
- Say it once. Do not restate in a "Boundaries" or "Principles" section what the intro or procedure already said. Shared rules live in `standards`. Reference them and do not re-explain them.
- Match weight to the task. A simple single-shot skill is a few plain sentences with no headers (see `handoff`). A stateful multi-step workflow earns structure. Do not pad a small skill or force a complex one to be terse.
- Keep reference detail. Command examples, flag docs, and API mechanics (as in `lit-research`, `standards`, and the `gh` calls in `spec-to-tickets`) are substance. Cut rationale prose, not substance.
- Each skill stands alone. A skill does its own job to completion and works without any sibling skill installed. Name another skill only as an option for a step outside this skill's job (for example, "land the change with the `dev-workflow` skill, if you use it"), never as a required handoff. Cross-references position siblings and create no dependencies.
- Describe current behavior in present tense. Use semantic line breaks in prose markdown (one sentence per line). Use normal dashes or semicolons, never em dashes.
- Avoid the common AI-writing markers: figurative labels in place of claims ("load-bearing", "the lever", "surgical"), antithesis flourishes ("not X, but Y"), `**Bold term:** explanation` bullets, trailing "-ing" clauses that grade the previous sentence, and the vocabulary `standards` bans under "Plain language".

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
  Delete instructions that do not change behavior, and keep each shared rule in one authoritative skill.
- Keep skills standalone.
  When a procedure needs another model-invoked skill, call the Skill tool explicitly. User-invoked skills cannot be called by another skill.
- Keep execution instructions in `SKILL.md` and human-facing explanation in a separate docs surface when the repo has one.
