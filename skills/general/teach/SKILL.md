---
name: teach
description: Teach one topic over multiple sessions from vetted sources, quizzing for retrieval and recording what the user has demonstrated.
argument-hint: "What would you like to learn?"
disable-model-invocation: true
---

# teach

Teach one topic in chat across sessions.
State lives in the workspace directory, so each session continues from files.

## Workspace

The workspace is one directory that holds one topic's state and one mission.
Workspace paths (`MISSION.md` and the rest) resolve from the workspace directory.
Links to `references/` resolve from this skill's folder.

Choose the workspace before anything else:

- When the session directory contains `MISSION.md`, it is the workspace. Continue from its files.
- When the session directory is empty, make it the workspace.
- When the session directory holds anything else, such as a code project, write nothing there.
  Ask the user for a path, create it with `mkdir -p <path>`, and write all workspace files there.
  Tell the user to start the next session in that path.
  When no user can answer, stop and report that teaching needs a user.

Workspace files, each created when first needed and all read at the start of each invocation:

- `MISSION.md`: why the user is learning the topic.
- `RESOURCES.md`: vetted sources.
- `learning-records/NNNN-slug.md`: what the user has demonstrated, numbered from `0001`.
- `visuals/`: diagrams, plots, and pages built for lessons.

## Procedure

### 1. Establish the mission

When `MISSION.md` is missing, interview the user one question at a time until it holds all four sections of [references/mission-format.md](references/mission-format.md), then write it.
When no user can answer, stop and report that teaching needs a user.

Ask how the user prefers to be taught, including whether visuals help them most, and record the answers as the teaching style under Constraints.
Update the teaching style when the user states a new preference.

Push back on goals stated as "understand X". Ask what the user will do with the understanding.
Confirm with the user before changing an existing mission, and write a learning record for the change.

### 2. Diagnose

When `learning-records/` is empty, ask three questions before any teaching: explain the topic's core idea in their own words, apply it to a small case, and explain one prerequisite.
Write one learning record per claim of prior knowledge, stating the depth the user showed.

### 3. Ground in sources

Before explaining anything, search for primary sources, recognized experts, and peer-reviewed work. Add each to `RESOURCES.md` in the format in [references/resources-format.md](references/resources-format.md).
When the `lit-research` skill is available, use it to find scholarly sources and take each citation from its output.
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

When the concept is a structure, a flow, a process over time, a plot of numbers, or behavior that depends on a parameter, demonstrate it with a visual: a diagram, a plot, or a small interactive page.
Build it, render it, and look at the render before showing it, and save it in `visuals/`.
Show the visual first, then explain in prose that labels what it shows.
When the teaching style favors visuals, use one for every concept whose shape allows it.
Otherwise use one when it shows the point faster than prose.
Ask the user to predict the outcome before revealing it, and ask the retrieval question in chat after the visual.

Scale support to the user's answers:

1. Wrong answer or "I don't know": ask a narrower question that points at the gap.
2. Second miss: explain the point directly, then ask again in a different form.
3. Third miss: give a worked example of a similar case, then ask again.

When the user's answers show the concept is too hard, teach its prerequisite first.

For multiple-choice questions, make every option the same length and style.
Run `awk 'BEGIN{srand(); print int(rand()*4)+1}'` and put the correct option at that position.

### 6. Record and stop

Write a learning record when the user shows they can use a concept correctly, discloses prior knowledge, has a misconception corrected, or shifts the mission.
Material that was only covered does not qualify.
When a later record contradicts an earlier one, mark the earlier record superseded.
Write each record in the format in [references/learning-record-format.md](references/learning-record-format.md).

When the user answers three consecutive questions correctly without hints, stop new material and propose a real task from the mission's success criteria.

End each session with the next concept to teach, stated in one sentence.
