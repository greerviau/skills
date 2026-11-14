You are reviewing work done for the task below.
Score the work on its own merits.

## Task

{{TASK}}

## What to review

{{WORK}}

Read, build, and run whatever you need.
Change files only inside `{{WORK_DIR}}`.
Your changes there are discarded.

## Score

Give one integer from 1 to 10 for how well the work completes the task:

- 10: a demanding expert would change nothing.
- 9: a demanding expert would accept it as it is, and only optional polish remains.
- 7: it meets the task, with defects an expert would ask to fix before accepting it.
- 5: it meets part of the task, and major parts are missing or wrong.
- 3: it attempts the task but mostly fails.
- 1: it does not address the task.

Use the numbers between these levels when the work falls between them.

## Findings

List every change that would raise your score, most important first.
For each finding, state what is wrong, where it is, and what to change.
List problems only.

## Output

Write your review to `{{REVIEW_FILE}}` in this format:

```
SCORE: <integer from 1 to 10>
F1: [blocking|major|minor] <location>: <problem>. Change: <change>.
F2: [blocking|major|minor] <location>: <problem>. Change: <change>.
```

Start each finding on a new line with `F` and its number.
A finding can continue on the lines after it.
When you have no findings, write only the score line.

After you write the file, reply with only the word `done`.
