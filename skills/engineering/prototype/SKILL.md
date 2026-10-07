---
name: prototype
description: Use when a design question needs evidence from a disposable implementation that must never land - isolate the spike, test the smallest question, record the evidence and decision, then discard the code. Trigger on "prototype this", "spike this", "test this design", "validate this approach", "build a throwaway".
argument-hint: "What design question should the spike answer?"
---

Answer one design question with a **throwaway spike**: a disposable implementation whose source never enters production.
The result records evidence and a decision. It does not create a feature branch.

## Procedure

1. State the question. When the argument is absent or underspecified, ask for the design question. Write one question with a falsifiable answer and the decision it informs.
   Name the competing approaches when the question compares designs.
   Set a stop condition before writing code.
   If the question is ambiguous and no user can answer (`standards`), take the narrowest defensible interpretation and record the assumption in the result.
2. Set the boundary. List the production entry point, seam, inputs, and constraints the spike must exercise.
   Test the real entry point when the question concerns integration.
   Keep the experiment to the smallest slice that can answer the question.
3. Isolate the workspace. Work in an OS temporary directory or another disposable workspace the host provides.
   Do not modify the current checkout's source, dependency declarations, lockfiles, or production configuration.
   The only tracked output allowed is a decision record the user requested.
   If the spike needs repository code, use a disposable copy or detached workspace and keep its changes there.
4. Build the smallest experiment. Write only the code needed to test the question, adding instrumentation, fixtures, or adapters as needed. Do not polish it toward production.
5. Run the experiment on the relevant inputs, alternatives, and failure cases.
   Record the commands, inputs, outputs, and environment needed to interpret the result.
   Stop when the pre-set decision criterion is met or the evidence cannot distinguish the options.
6. Write the result: question, assumption, setup, observations, limitations, answer, and recommended next step.
   Write "unknown" when the evidence does not answer the question.
   Save it where *Artifact location* (`standards`) puts a prototype result, never inside the spike workspace. A decision record contains no disposable source.
7. Discard the spike. Delete the disposable workspace and verify the original checkout has no source or configuration changes from the experiment.
   Never commit, push, open a pull request, merge, or copy spike source into a production directory.
   When no user can answer, stop here instead of expanding the spike into implementation.

## Related skills

- `design`, if installed, supplies vocabulary for structural judgments. The spike does not require it.
- `spec`, if used, can incorporate the result. `prototype` does not write an implementation plan or hand code to `dev-workflow`.
- An optimization claim that needs a numeric before-and-after measurement belongs in `perf`, if installed.
- Production work that follows a spike starts as a separate implementation from the written result. The spike source is never promoted.
