---
name: my-voice
description: Use only when the user explicitly asks to rewrite a document in their own voice, or to capture that voice from writing samples; the document is a spec, README, report, announcement, PR body, or any prose a person reads. Reads ~/VOICE.md and hands the draft to a subagent that rewrites the wording without touching a fact or a section. Never invoke it on your own after producing a document. Trigger on "/my-voice", "make this sound like me", "rewrite this in my voice", "learn my writing style".
disable-model-invocation: true
---

# my-voice

Run `/my-voice` explicitly to capture or apply the user's writing voice.

`~/VOICE.md` records how the user writes, in enough detail that a rewriter can match it.
This skill has two jobs: capture that record from writing samples, and rewrite a finished draft against it.

Run it only when asked.
Never draft a document in the user's voice from the start; write the document normally, and run the pass over it afterward.

## Which job

- `~/VOICE.md` does not exist, the user supplies writing samples, or the user asks to learn, update, or refresh the voice: **capture**.
- Otherwise, with a document in play: **rewrite**.
- `/my-voice capture` forces capture; use it to refresh a profile when no document is in play.
- Asked to rewrite with no `~/VOICE.md` on disk: capture first, then rewrite.

## Scope

The pass runs on prose a person reads: specs, READMEs, reports, announcements, emails, issue and PR bodies.

It does not run on artifacts an agent executes - implementation plans, task briefs, handoff documents, structured findings, `CLAUDE.md`, code comments, or docstrings.
Those are written for precision under a house style, and a voice pass over them trades precision for personality.
Decline such a target and say which rule excluded it.

## Capture

**1. Collect samples.**
Ask for them if the user supplied none: three to five pieces, a few hundred words each, that the user wrote without agent help.
Accept pasted text or file paths.
Ask which register each one is, when it is not obvious - a Slack post and a design doc are different voices, and a profile that averages them matches neither.

**2. Read the samples and extract only what a rewriter can act on.**
Prefer a rule naming the words and constructions themselves ("writes *use*, never *utilize*"; "opens with the conclusion, then the evidence") over an adjective ("conversational", "direct"), which no rewriter can apply.

Keep a rule only if it is **distinctive**.
A rule that describes competent writing in general changes no sentence and costs attention; cut it.
The test: would a draft that violates this rule still read as written by someone else?

Claim nothing the samples do not show.
Where they are too few or too uniform to support an observation, leave it out.

**3. Write `~/VOICE.md`** with these sections.
The lines under each heading say what belongs there; replace them with the user's actual profile.

```markdown
# Voice

## Coverage
Which registers the profile is drawn from, and how many samples back it.

## Register
One paragraph: who the user sounds like, how formal they are, and how close they stand to the reader.

## Sentence and paragraph shape
Typical and longest sentence length, how much length varies, fragments, paragraph length,
when prose gives way to a list.

## Diction
Words and phrasings the user reaches for, quoted. Contractions, jargon tolerance,
how technical terms get introduced.

## Punctuation and mechanics
Dashes, semicolons, parentheticals, Oxford comma, heading capitalization, emphasis,
sentence-per-line habits.

## Moves
Recurring structural habits: how a piece opens, how it closes, whether the conclusion
leads or lands, how the user hedges or refuses to.

## Never
Words and constructions absent from every sample.

## Excerpts
Three to six verbatim passages, two to four sentences each, labeled by register and
copied exactly. These calibrate the rewriter better than any rule above them.
```

**4. Show the user what was captured** and ask whether it reads right.

**Updating an existing profile:** revise the entries the new samples contradict, add the ones they support, and replace excerpts the voice has outgrown.
Do not append a second set of rules beside the first; a profile that argues with itself gives the rewriter no answer.
Update the Coverage section to match.

## Rewrite

**1. Confirm the target.**
Name the file.
Check it against *Scope* above, and stop if it is excluded.
Make sure the draft is final in content; a voice pass over a draft still being edited is thrown away.

**2. Make the original recoverable** before any edit: commit it, or copy it aside if the file is not tracked.
The diff is how both you and the user check the pass.

**3. Hand the rewrite to a subagent**, giving it the target path, `~/VOICE.md`, and the bounds below verbatim.
Do the rewrite inline only when no subagent is available; an author matching a voice profile against their own draft mostly rediscovers their own phrasing.

Ask it to edit the file in place and report what it changed, plus anything it left alone deliberately.

**The bounds:**

- Change wording, sentence structure, rhythm, transitions, paragraph breaks, and heading wording.
- Change no fact: no number, name, path, URL, citation, command, version, or code block.
- Preserve every stated uncertainty. The voice governs how a hedge is worded, never whether the hedge is there.
- Add, remove, reorder, and merge no section. The heading count and order come out unchanged.
- Add no information that is not in the draft, and drop none that is.
- Keep the markdown structure: lists stay lists, tables stay tables, links keep their targets.
- Where voice and correctness conflict, correctness wins; report the conflict rather than resolving it silently.

**4. Read the diff yourself** before showing the user, checking every changed line against the bounds.
Revert anything that crossed one.

**5. Report**: the file, one or two lines on what shifted, and any passage the pass deliberately left in its original voice.

## Notes

- The profile is a description of the user, so the user is the only authority on whether it is right. Do not defend a captured rule they reject; correct it.
- One document per pass. Run a set one at a time rather than rewriting them in a single sweep, so each diff stays reviewable.
