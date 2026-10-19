---
name: teach
description: Teach one topic over multiple sessions from vetted sources, quizzing for retrieval and recording what the user has demonstrated.
argument-hint: "What would you like to learn?"
disable-model-invocation: true
---

# teach

Invoke `/teach` in Claude Code or `$teach` in Codex to learn one topic in chat.
Every explanation cites a recorded source, the user retrieves what they learned before the topic advances, and the current directory keeps state so the next session continues from files.

Run it from a directory dedicated to one topic.
A directory holds one mission.

## Workspace files

Read these at the start of every invocation. Create each lazily, when first needed.

- `MISSION.md`: why the user is learning the topic.
- `RESOURCES.md`: vetted sources, each with a one-line note on what it covers.
- `learning-records/NNNN-slug.md`: what the user has demonstrated, numbered from `0001`.

## Procedure

### 1. Establish the mission

When `MISSION.md` is missing, interview the user one question at a time until it holds all four sections, then write it.
When no user can answer, stop and report that `/teach` needs a user.

```md
# Mission: {topic}

## Why
{The concrete outcome the user wants, in 1-3 sentences.}

## Success looks like
- {A specific thing the user can do}

## Constraints
- {Time, tools, preferred teaching style}

## Out of scope
- {Adjacent topics to skip for now}
```

Push back on goals stated as "understand X". Ask what the user will do with the understanding.
Confirm with the user before changing an existing mission, and write a learning record for the change.

### 2. Diagnose

When `learning-records/` is empty, ask three questions before any teaching: explain the topic's core idea in their own words, apply it to a small case, and explain one prerequisite.
Write one learning record per claim of prior knowledge, stating the depth the user showed.
Skip this step when records exist.

### 3. Ground in sources

Before explaining anything, search for primary sources, recognized experts, and peer-reviewed work. Add each to `RESOURCES.md` with its note.
Cite a source from `RESOURCES.md` for every claim in an explanation.
Mark a claim with no source as `unverified`.
When no search tool is available, mark every claim `unverified` and say why.

### 4. Review

Run `date +%F`.
Pick the oldest learning record whose `Reviewed:` date is 7 or more days old, and ask one retrieval question on it before new material.
Update that record's `Reviewed:` date after the user answers.

### 5. Teach one concept

Pick the next concept from the mission and the learning records. Choose one that takes effort and is within the user's reach.
Explain it in about 150 words, with a worked example, then ask a retrieval question that needs recall and not recognition.

Scale support to the user's answers:

1. Wrong answer or "I don't know": ask a narrower question that points at the gap.
2. Second miss: explain the point directly, then ask again in a different form.
3. Third miss: give a worked example of a similar case, then ask again.

When the user's answers show the concept is too hard, teach its prerequisite first.

For multiple-choice questions, make every option the same length and style.
Run `awk 'BEGIN{srand(); print int(rand()*4)+1}'` and put the correct option at that position.
Do not reveal the answer until the user commits.

### 6. Record and stop

Write a learning record when the user shows they can use a concept correctly, discloses prior knowledge, has a misconception corrected, or shifts the mission.
Material that was only covered does not qualify.
When a later record contradicts an earlier one, set the earlier record's status to `superseded by NNNN`.

```md
# {What was learned or established}

Reviewed: {YYYY-MM-DD}

{1-3 sentences: what the user demonstrated, the evidence, and what it changes about the next session.}
```

When the user answers three consecutive questions correctly without hints, stop new material and propose a real task from the mission's success criteria.

End each session with the next concept to teach, stated in one sentence.
