---
name: prototype
description: Use when a design question needs evidence from a disposable implementation that must never land - isolate the spike, test the smallest question, record the evidence and decision, then discard the code. Trigger on "prototype this", "spike this", "test this design", "validate this approach", "build a throwaway".
argument-hint: "What design question should the spike answer?"
---

Answer one design question with a **throwaway spike**: a disposable implementation whose source never enters production.
The result records evidence and a decision; it does not create a feature branch.

## Procedure

1. **State the question.** Write one question with a falsifiable answer and the decision it informs.
   Name the competing approaches when the question compares designs.
   Set a stop condition before writing code.
   If the question is ambiguous and the run is autonomous, choose the narrowest defensible interpretation and record the assumption in the result.
2. **Set the boundary.** List the production entry point, seam, inputs, and constraints the spike must exercise.
   Test the real entry point when the question concerns integration.
   Keep the experiment to the smallest slice that can answer the question.
3. **Isolate the workspace.** Work in an OS temporary directory or another disposable workspace provided by the host.
   Do not modify the current checkout's source, dependency declarations, lockfiles, or production configuration.
   A user-requested decision record is the only tracked output allowed from the spike.
   If the spike needs repository code, use a disposable copy or detached workspace and keep its changes local to that workspace.
4. **Build the smallest experiment.** Implement only the code needed to test the question.
   Add instrumentation, fixtures, or adapters as needed, but do not polish the spike into production code.
5. **Run the experiment.** Exercise the relevant inputs, alternatives, and failure cases.
   Record the commands, inputs, outputs, and environment needed to interpret the result.
   Stop when the pre-set decision criterion is met or the evidence cannot distinguish the options.
6. **Write the result.** Report the question, assumption, setup, observations, limitations, answer, and recommended next step.
   State "unknown" when the evidence does not answer the question.
   Save the result outside the spike workspace, or in a user-requested decision record that contains no disposable source.
7. **Discard the spike.** Delete the disposable workspace and verify that the original checkout has no source or configuration changes from the experiment.
   Never commit, push, open a pull request, merge, or copy spike source into a production directory.

## Interaction mode

In interactive use, ask for the design question when the argument is absent or underspecified.
In autonomous use, take the narrowest defensible interpretation, record it in the result, and stop rather than expanding the spike into implementation work.

## Boundaries

- `prototype` answers a design question with empirical evidence.
  When `design` is installed, its vocabulary can guide structural judgments, but the spike does not require it.
- `spec`, if used, can incorporate the result; `prototype` does not write an implementation plan or hand off code to `dev-workflow`.
- An optimization claim that requires a numeric before-and-after measurement belongs in `perf`, if that skill is installed.
- A spike that becomes production work starts as a separate implementation from the written result; its source is never promoted.
