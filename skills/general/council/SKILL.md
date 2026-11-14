---
name: council
description: Use only when the user explicitly asks for a council of judges, for example "use the council", "run this past the council", or "until the council scores 8". Do not use for an ordinary review, critique, or quality request that does not name a council.
---

# council

Do the requested work, then have a **council** of **judges**, one model from each of several providers, score it out of 10.
Revise and rescore until every judge scores at or above the **threshold** in the same **round**, or until the round limit is reached.

## Set up

Take the judges, the threshold, and the round limit from the request.
When any of them is missing, ask for all missing values in one question before you start, and offer the defaults: the latest flagship model from three providers other than your own at high reasoning effort, threshold 8, and 3 rounds. When no user can answer, use the defaults and list them in the report.

In T3 Code, resolve the models with `orchestrator_capabilities` and start each judge with `delegate_task`.
Elsewhere, use the harness's subagent tool with its model option.
When a judge's model is unavailable, tell the user and ask for a replacement, and do not substitute one yourself. When no user can answer, stop and report the unavailable model.

Create a review directory outside the work tree with `mktemp -d`.
Before round 1, write the judge prompt once, and send it unchanged to every judge in every round.
The prompt contains:

- The user's request, without the council instructions.
- Where the work is and how to view it, for example `git diff <base>` for code or screenshot files for visual work, and that the review is read-only.
- The scale: 9 means a demanding expert would accept the work as it is, 7 means it meets the task with defects an expert would fix first, and 5 means major parts are missing or wrong.
- The output: write every change that would raise the score, most important first, with its location and fix, to `<review dir>/<judge id>.md`, then reply with only `SCORE: <n>`.

Leave the threshold, the round number, earlier scores and findings, and any mention of revisions out of the prompt.

## Run rounds

Do the work.
When the work already exists, start with round 1.
Before each round, fix known issues and run the relevant checks.

Start every judge in parallel as a fresh session without your conversation history.
Do not edit the work while judges review it.
When a judge replies without a valid score, relaunch it once, then record `no score`, which does not pass.

Have a fresh subagent read the round's review files and write one merged list of findings.
It merges duplicates and names the judges who raised each one, keeps every finding's location and fix, and lists findings that ask for opposite changes as conflicts.
Read the merged list and the scores, not the review files.

Stop when every judge scores at or above the threshold, or when the round reaches the limit.
Otherwise fix each finding you agree with, record each rejected finding with its reason, pick a side on each conflict, and start the next round.
Reject findings that ask for work outside the request.
Commit messages for revisions describe the change and do not mention the council or a round.

## Report

Report the outcome (passed in round `<n>`, or stopped at the round limit), the score table, the open findings from the last round, and the rejected findings with reasons.
When the work ends in a pull request, put the table in the PR description by editing it, and do not post a comment:

```markdown
## Council review

Threshold: 8. Rounds: 2.

| Judge | Round 1 | Round 2 |
| --- | --- | --- |
| Claude Opus | 7/10 | 9/10 |
| GPT Sol | 8/10 | 10/10 |
| Gemini Pro | 6/10 | 8/10 |
```
