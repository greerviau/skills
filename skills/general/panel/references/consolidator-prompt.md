Merge the reviews below into one feedback list for the person who revises the work.
Do not judge the work or add findings of your own.

## Inputs

- Reviews: {{REVIEW_FILES}}
  Each file is named `round-<n>-<judge>.md`.
  A finding's id is `<judge>.F<number>`, for example `j2.F3`.
- Previous feedback: {{PREVIOUS_FEEDBACK}}

## Rules

- Cite every finding id from every review in exactly one item.
- Keep each finding's location and requested change.
  Do not drop, soften, or reinterpret a finding.
- Merge findings that ask for the same change into one item, and cite all of their ids.
- When findings ask for changes that cannot both be made, put them under Conflicts and state each side.
- Mark an item `repeat` when the previous feedback contains the same problem.
- Order Findings by the most severe label among the item's sources, then by the number of judges who raised it.

## Output

Write the feedback to `{{FEEDBACK_FILE}}` in this format:

```
## Findings

1. [blocking, 2 judges, repeat] <location>: <problem>. Change: <change>. Sources: j1.F1, j3.F2

## Conflicts

1. [repeat] <subject>. Side A (j1.F3): <change>. Side B (j2.F1): <change>.
```

Omit `repeat` when it does not apply.
Write `None.` under a heading with no items.
After you write the file, reply with only the word `done`.
