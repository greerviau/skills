# Teaching skills survey

Survey of existing teaching skills for coding agents, as input to a `/teach` skill for this repo.
Sources were read on 2026-10-19 from the GitHub repositories named in each row.
Star counts and push dates come from the GitHub API on that date.
The recommendation at the end is implemented in `skills/general/teach` and has not been run against a real topic.

## Findings

- Matt Pocock's `teach` is the only surveyed skill that grounds teaching in a recorded mission and vetted sources, and it keeps learning records across sessions (`sigma` also persists state, but not sources).
  Its repo docs list four open gaps: no knowledge assessment, no spaced-repetition scheduling, no exit criteria, and a quiz answer that lands in the first position every time.
- Every other skill falls into one of three designs: a Socratic questioner that withholds answers, a quiz loop over a finished work session, or a mastery tutor with a learner model.
- One surveyed skill (`socratic-inquiry`) cites research that unguided discovery fails for novices and uses contingent scaffolding.
  `socrates-skill` and `sigma` forbid direct answers outright.
- In Anthropic's randomized trial, retention varied by interaction pattern.
  The three high-scoring patterns all kept the developer asking conceptual questions or checking their own understanding.

## Survey

| Skill | Design | State kept | Stars | Last push |
| --- | --- | --- | --- | --- |
| [mattpocock/skills `teach`](https://github.com/mattpocock/skills/tree/main/skills/productivity/teach) | Multi-session course in a workspace directory; HTML lessons | `MISSION.md`, `RESOURCES.md`, `learning-records/`, `lessons/`, `reference/`, `assets/`, `NOTES.md` | 297,197 (whole repo) | 2026-10-19 |
| [dashed/claude-marketplace `teach`](https://github.com/dashed/claude-marketplace/tree/main/plugins/teach) | Quiz loop over a past Claude Code session, PR, or transcript | One dated checklist file per session, committed | 25 (whole repo) | 2026-10-14 |
| [sanyuan0704/sanyuan-skills `sigma`](https://github.com/sanyuan0704/sanyuan-skills/tree/main/skills/sigma) | 1-on-1 mastery tutor, Socratic, advance at about 80% | `learner-profile.md` across topics, per-topic `session.md` with scores and review schedule | 3,955 (whole repo) | 2026-05-11 |
| [RoundTable02/socrates-skill](https://github.com/RoundTable02/socrates-skill) | Socratic questioner over a codebase or document; never states the answer | None | 340 | 2026-04-02 |
| [UderMoreiraDeAssis/socrates `socratic-inquiry`](https://github.com/UderMoreiraDeAssis/socrates) | Socratic protocol with contingent scaffolding, grounded in cited learning science | None found | 0 | 2026-07-09 |
| [wangyuxinwhy/learn-with-claude](https://github.com/wangyuxinwhy/learn-with-claude) | Short Socratic prompt; saves notes to a repo at session end | Markdown notes per topic | 0 | 2026-02-06 |
| [anthropics/claude-code `learning-output-style`](https://github.com/anthropics/claude-code/tree/main/plugins/learning-output-style) | Session-start hook that makes Claude leave 5-10 line `TODO(human)` slots in code and add explanatory insights | None | 152,487 (whole repo) | 2026-10-18 |

Also found and not read in full: Claude.ai's "Learning" style (Socratic, per [press coverage](https://engadget.com/ai/anthropic-brings-claudes-learning-mode-to-regular-users-and-devs-170018471.html)), the `explanatory-output-style` plugin in the same Anthropic repo, `Jellypod-Inc/school-skills-for-claude-code` (listed by a registry; the repo URL returned 404), and a compound-engineering plan to put a "New concepts" teaching section in generated PR descriptions ([plan](https://github.com/EveryInc/compound-engineering-plugin/blob/main/docs/plans/2026-07-07-001-feat-pr-concept-teaching-plan.md)).

## Pocock's `teach`

**Mechanism.**
The skill treats the current directory as a teaching workspace and reads state from files at each invocation.
`MISSION.md` holds the concrete reason for learning and grounds every lesson.
If it is empty, the first action is an interview.
`RESOURCES.md` lists vetted sources split into Knowledge and Wisdom (communities).
The skill says "Never trust your parametric knowledge" and requires citations inside lessons.
`learning-records/NNNN-slug.md` files are short ADR-style notes written when the user shows understanding, discloses prior knowledge, has a misconception corrected, or shifts the mission.
Coverage alone does not qualify.
The skill reads these records to pick the next topic inside the zone of proximal development.

**Teaching model.**
Knowledge, skills, and wisdom are taught differently.
Knowledge lessons minimize difficulty to protect working memory.
Skill lessons add difficulty through retrieval practice, spacing, and interleaving, with immediate feedback.
Each lesson is one self-contained HTML file that fits one sitting and ends in one tangible win.
Shared components in `assets/` (a stylesheet first) keep lessons consistent.
Quiz answers must have equal word counts, and the correct answer's position must vary.

**Reported failures** (from the skill's own [docs page](https://github.com/mattpocock/skills/blob/main/docs/productivity/teach.md); I did not open the linked issues):

- The correct answer is the first option in all 33 of 33 quizzes one contributor tested, across Sonnet, Opus, and GLM.
  The docs recommend a shuffling quiz component and call instruction-level fixes ineffective.
- No assessment step exists.
  Session one has no learning records, so the skill guesses the learner's level and uses undefined jargon.
- Nothing schedules a review, and the skill does not propose switching from new material to review or practice.
- One user learning a 2x2 Rubik's cube received invented move sequences.
  The docs rate procedural domains with precise notation as highest risk.
- `GLOSSARY-FORMAT.md` ships but `SKILL.md` does not link it.

**Fit for this repo.**
The HTML lesson and `assets/` component pipeline is a large instruction surface for a prompt that loads on every invocation.
The state files (`MISSION.md`, `RESOURCES.md`, `learning-records/`) transfer without it.

## Other designs

**Quiz over finished work (`dashed` `teach`).**
Origin is a public gist by ThariqS titled "Learn Quiz", credited to Suzanne at Anthropic.
The gist and the original port carry no license, so the text cannot be copied into this repo.
Behavior: the human restates their understanding first, then the agent quizzes one concept at a time against a checklist (problem, solution, broader context), drills into "why", and does not end the session until every item is confirmed.
The checklist file is the only state.
This design fits the case where an agent just did work the human must be able to defend, such as a PR.
It has no model of prior knowledge beyond the opening restatement.

**Mastery tutor (`sigma`).**
Diagnoses first, builds a concept roadmap of 5 to 15 atoms, requires about 80% demonstrated mastery to advance, interleaves every 3 to 4 questions, and runs spaced-repetition review on `--resume`.
It writes a cross-topic `learner-profile.md`.
It also forbids direct answers and generates HTML dashboards, Excalidraw maps, and images, which is a large output surface for a chat tutor.

**Pure Socratic (`socrates-skill`, `learn-with-claude`).**
Both are under 150 lines.
`socrates-skill` forbids answers "even if the user begs" and lists "giving up and providing the answer after a few failed attempts" as an anti-pattern.
Neither keeps state between sessions beyond optional notes.

**Evidence-grounded Socratic (`socratic-inquiry`).**
Cites Chi and Wylie (ICAP), Kirschner, Sweller and Clark (unguided discovery fails for novices), Wood, Bruner and Ross (scaffolding), Kalyuga (expertise reversal), and Roediger and Karpicke (testing effect).
I did not verify those citations.
Its protocol starts with a diagnostic question, classifies the learner as novice, intermediate, or advanced, and raises support (up to worked examples) when the learner stalls.
It has no persistent state.

**Output style (`learning-output-style`).**
Changes the working session itself and does not teach a topic.
It asks the human to write the 5 to 10 lines that carry a design decision and skips boilerplate.
Anthropic's docs state that both built-in styles produce longer responses than Default.

## Evidence on AI use and learning

Anthropic's [study](https://www.anthropic.com/research/AI-assistance-coding-skills) (Shen and Tamkin, [arXiv 2601.20245](https://www.arxiv.org/pdf/2601.20245), January 2026) is a randomized trial of developers learning the Trio async library.

- The AI group scored 50% on a follow-up quiz and the hand-coding group 67% (Cohen's d = 0.738, p = 0.01).
  The AI group finished about two minutes faster, which was not statistically significant.
- The largest gap was on debugging questions.
- The authors identify six interaction patterns.
  Delegation, progressive reliance (questions first, then full delegation), and iterative AI debugging scored low.
  Conceptual inquiry (n = 7, only conceptual questions), hybrid code-and-explanation (n = 3), and generation followed by comprehension questions scored high.
- Limits stated by the authors: small sample, short horizon, one library.
  The per-pattern groups have 3 to 7 participants.

Confidence that the pattern ranking generalizes: low.
Confidence that delegating without engaging reduces retention in this setting: moderate.

## Gaps across the field

- Only `sigma` and Pocock's `teach` keep learner state across sessions.
  `sigma` diagnoses before teaching.
  Pocock's `teach` does not, and the docs list an assessment step as a feature request.
- No skill defends against the model teaching wrong facts beyond requiring citations.
  Pocock's is the only one that requires sources, and it relies on the model to find and judge them.
- The `dashed` skill and the original gist also tell the agent to vary the correct answer's position.
  Only Pocock's docs report that this fails, and none of the skills ships a mechanical fix.
- None defines when to stop teaching and move to practice.

## Counterargument to building `/teach`

Claude Code already ships a Learning output style, Pocock's `teach` is installable with `npx skills@latest add mattpocock/skills`, and any of the Socratic skills can be adopted with one command.
A repo skill adds maintenance and one more description in every session's context.
The case for a new skill rests on two things the surveyed skills lack together: grounding in vetted sources and a per-session diagnostic that does not depend on prior records.
If neither matters for the intended use, install Pocock's `teach` and stop.

## Recommendation

Build one user-invoked `/teach` skill with a narrow job: teach one topic in the chat, grounded in sources, and persist what the user demonstrated.
Behavior of `skills/general/teach`:

1. Interview for the mission when `MISSION.md` is absent, then run a three-question diagnostic before any lesson.
   Record stated prior knowledge as the first learning record.
2. Fetch and record sources in `RESOURCES.md` before teaching, and cite them in each explanation.
   Mark any claim without a source as unverified.
3. Scaffold contingently.
   Ask first, explain directly after two failed attempts, and use a worked example when the learner still stalls.
4. Quiz with retrieval practice in chat.
   Choose the correct answer's position by running `awk 'BEGIN{srand(); print int(rand()*4)+1}'` and place it there, because instruction-level variation failed in Pocock's tests.
5. On each invocation, read `learning-records/` and open with one retrieval question on the oldest record not reviewed in 7 days.
   This is the minimal spacing mechanism and needs no scheduler.
6. Stop teaching new material and propose real practice when the last three quiz answers were correct without hints.
7. Write plain markdown lessons by default.
   Leave HTML to an explicit user request.

Items 4, 5, and 6 are untested.
A prototype with a small topic would show whether the `awk` placement removes the position bias and whether the 7-day and three-correct thresholds fit.

## Sources

- [mattpocock/skills `teach` SKILL.md and format files](https://github.com/mattpocock/skills/tree/main/skills/productivity/teach)
- [mattpocock/skills `teach` docs page](https://github.com/mattpocock/skills/blob/main/docs/productivity/teach.md)
- [dashed/claude-marketplace `teach`](https://github.com/dashed/claude-marketplace/tree/main/plugins/teach)
- [Learn Quiz gist by ThariqS](https://gist.github.com/ThariqS/1389dcdff9eba4789887a2211370f06b) (linked from the `dashed` skill; not opened)
- [sanyuan0704/sanyuan-skills `sigma`](https://github.com/sanyuan0704/sanyuan-skills/tree/main/skills/sigma)
- [RoundTable02/socrates-skill](https://github.com/RoundTable02/socrates-skill)
- [UderMoreiraDeAssis/socrates](https://github.com/UderMoreiraDeAssis/socrates)
- [wangyuxinwhy/learn-with-claude](https://github.com/wangyuxinwhy/learn-with-claude)
- [anthropics/claude-code `learning-output-style`](https://github.com/anthropics/claude-code/tree/main/plugins/learning-output-style)
- [Claude Code output styles docs](https://code.claude.com/docs/en/output-styles)
- [Anthropic: AI assistance and coding skills](https://www.anthropic.com/research/AI-assistance-coding-skills)
- [arXiv 2601.20245](https://www.arxiv.org/pdf/2601.20245)
