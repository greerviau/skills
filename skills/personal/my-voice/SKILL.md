---
name: my-voice
description: Capture the user's writing voice or rewrite a finished human-facing document in it.
disable-model-invocation: true
---

# my-voice

Run `/my-voice` to capture or apply the user's writing voice.

`~/VOICE.md` records how the user writes, in enough detail that a rewriter can match it.
The skill has two jobs: capture that record from writing samples, and rewrite a finished draft against it.

Run it only when asked.
Never draft a document in the user's voice from the start. Write the document normally and run the pass afterward.

## Which job

- Capture: `~/VOICE.md` does not exist, the user supplies writing samples, or the user asks to learn, update, or refresh the voice.
- Rewrite: otherwise, when a document is in play.
- `/my-voice capture` forces capture, for refreshing a profile when no document is in play.
- If asked to rewrite and `~/VOICE.md` is missing, capture first, then rewrite.

## Scope

The pass runs on prose a person reads: specs, READMEs, reports, announcements, emails, issue and PR bodies.

It does not run on artifacts an agent executes: implementation plans, task briefs, handoff documents, structured findings, `AGENTS.md` or `CLAUDE.md`, code comments, and docstrings.
These are written for precision under a house style, and a voice pass would trade precision for personality.
Decline such a target and say which rule excluded it.

## Capture

### 1. Collect samples

If the user supplied none, ask for three to five pieces of a few hundred words each that the user wrote without agent help.
Accept pasted text or file paths.
Ask which register each is when it is not obvious. A Slack post and a design doc are different voices, and a profile that averages them matches neither.

### 2. Extract what a rewriter can act on

Prefer a rule naming the words and constructions ("writes *use*, never *utilize*"; "opens with the conclusion, then the evidence") over an adjective ("conversational", "direct") that no rewriter can apply.

Keep a rule only if it is distinctive. A rule that describes competent writing in general changes no sentence and costs attention. The test: would a draft that violates the rule still read as written by someone else?

Claim nothing the samples do not show. Where they are too few or too uniform to support an observation, leave it out.

### 3. Write `~/VOICE.md`

Every line is a rule the writer applies or a verbatim sample they match against.
Leave out sample counts, capture dates, which registers back the profile, evidence for a rule, caveats about the corpus, and commentary around an excerpt. Report those to the user in step 4.

Write rules as instructions to a writer, not observations about the user.
"Append hedges at the end of the sentence" is a rule. "He tends to hedge at the end of the sentence, consistently across the informal samples" is an observation with its evidence attached.

Use these sections, dropping any the samples do not support:

```markdown
# Voice

## Stance
Who to write as, how formal, how close to the reader. A few imperative lines.

## Sentences
Sentence length and how much it varies, fragments, paragraph length, when prose becomes a list.

## Diction
Words and constructions to reach for, quoted. Contractions, jargon tolerance, how technical
terms get introduced, which words not to swap out.

## Mechanics
Dashes, semicolons, parentheticals, Oxford comma, heading capitalization, emphasis,
how identifiers and paths are written.

## Moves
Structural habits: how a piece opens and closes, whether the conclusion leads or lands,
how the user hedges or refuses to.

## Never
Words and constructions absent from every sample.

## Excerpts
Three to six verbatim passages, two to four sentences each, labeled by register and copied
exactly. These calibrate the rewriter better than any rule above them. Label and text only.
```

Give a rule an inline example only where it is unusable without one, and keep the example inside the rule.

### 4. Report what was captured

Ask whether it reads right.
Say which registers the samples covered and which they did not, and name any rule the samples were too thin to support.

When updating an existing profile, revise the entries the new samples contradict, add the ones they support, and replace excerpts the voice has outgrown.
Do not append a second set of rules beside the first. A profile that contradicts itself gives the rewriter no answer.

## Rewrite

### 1. Confirm the target

Name the file and check it against Scope. Stop if it is excluded.
Confirm the draft is final in content. A voice pass over a draft still being edited is wasted.

### 2. Make the original recoverable

Before any edit, commit the original or copy it aside if the file is untracked.
The diff is how you and the user check the pass.

### 3. Hand the rewrite to a subagent

Give it the target path, `~/VOICE.md`, and the bounds below verbatim.
Rewrite inline only when no subagent is available, because an author matching a voice profile against their own draft mostly rediscovers their own phrasing.

Ask it to edit the file in place and report what it changed and what it deliberately left alone.

Bounds:

- Change wording, sentence structure, rhythm, transitions, paragraph breaks, and heading wording.
- Change no fact: no number, name, path, URL, citation, command, version, or code block.
- Preserve every stated uncertainty. The voice governs how a hedge is worded, not whether it is there.
- Add, remove, reorder, and merge no section. Heading count and order stay unchanged.
- Add no information that is not in the draft, and drop none that is.
- Keep the markdown structure: lists stay lists, tables stay tables, links keep their targets.
- Where voice and correctness conflict, correctness wins. Report the conflict instead of resolving it silently.

### 4. Read the diff yourself

Before showing the user, check every changed line against the bounds and revert anything that crossed one.

### 5. Report

Give the file, one or two lines on what shifted, and any passage the pass left in its original voice.

## Notes

- The profile describes the user, so the user is the only authority on whether it is right. Correct a captured rule they reject instead of defending it.
- Run one document per pass. Run a set one at a time so each diff stays reviewable.
