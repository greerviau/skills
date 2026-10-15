---
name: prototype
description: Use when a design choice, library or API behavior, or feasibility question is uncertain and a disposable experiment would settle it before committing to an approach - while planning, specifying, or mid-implementation. Builds a throwaway spike, records the evidence, and discards the code. Trigger on "prototype this", "spike this", "validate this approach", "will this work", "try it before we build it".
argument-hint: "What question should the spike answer?"
---

# prototype

Answer one question with a **throwaway spike**: a disposable implementation whose source never enters production.
Reach for it whenever a plan depends on something you have not seen work.

## Procedure

1. State one falsifiable question and the decision it informs. When the question compares approaches, name them. Set the stop condition before writing code.
2. Isolate. Work in the OS temporary directory or a disposable copy of the repo. Leave the current checkout's source, dependencies, lockfiles, and configuration unchanged.
3. Build the smallest experiment that can answer the question, through the real entry point when the question concerns integration. Do not polish it.
4. Run it on the relevant inputs and failure cases. Record the commands, inputs, outputs, and environment.
5. Write the result: question, setup, observations, limitations, answer, and recommended next step. Write "unknown" when the evidence does not decide.
   Save it to `docs/analysis/<date>-<name>.md` in the repo, or to the OS temporary directory when the user or the repo's agent instructions (`AGENTS.md` or equivalent) say not to write documents to the repo. The result never contains spike source.
6. Delete the spike and confirm the original checkout has no changes from the experiment.

Never commit, push, or copy spike source into production. Implementation that follows starts fresh from the written result.
