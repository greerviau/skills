---
name: cook
description: Use when the user says "cook", "let it cook", or "/cook" to hand off a task of any kind (code, research, writing, operations) that they will not watch until it is finished. Not for tasks where the user stays available to steer the work.
---

# cook

Settle every decision with the user in one **interview** at the start, then take the task to its end without contacting them again.
Ending the turn before the work is done stops it, because nobody prompts you again.
After the interview, every workflow step that would ask the user takes its "When no user can answer" path instead.

The **deliverable** is what the finished task produces: a PR for a code change in a repo, or otherwise a document, an analysis, a changed system, an answer, or whatever the request names.

## 1. Interview

Before asking anything, read the request, the files or systems it touches, and any agent instructions that apply, and answer every question you can from them.
Then ask the user about everything that remains, with a question tool available in the current mode (`AskUserQuestion` in Claude Code, `request_user_input` in Codex).
When no question tool is available, send the questions as one message and end the turn, and start work when the answers arrive.
Send as many batches as the open questions need.
Cover:

- The deliverable, its format, and where it goes, when the request does not settle them.
- Acceptance criteria: what the user will check to call the work done.
- Ambiguity in the goal or scope that changes the result.
- Choices with more than one reasonable answer.
- Actions outside the grant in step 2 that the task will likely need, including finalizing.
- Credentials, logins, accounts, and secrets the work will need.
  Collect secrets now with the harness's secret tool (`request_secret` in T3 Code).

Put your recommended option first in each question, and include the context needed to answer it without reading the thread.
Do not ask about choices that have a conventional default or that are cheap to reverse.
Decide those yourself and record them for the report.
Stop asking when no open question would change the result.
When no user can answer, take your recommended options, record them as decisions, and treat every permission question as refused.

Post the **brief** as a message: the deliverable, the acceptance criteria, each answer, and which finalizing actions are allowed.
Start work without waiting for a reply to the brief.

## 2. Grant

A cook request allows, for this task only:

- Any action that stays inside the task's own workspace and can be undone, such as editing files, running commands, writing drafts, and committing and pushing to the task's branch.
- Any verification method the proof in step 4 needs, including running apps or servers, browser automation, computer use, simulators, devices, and screenshots, even when a project file says to ask first.
  Project rules that name the command, fixture, or check to use still apply.

**Finalizing** is the step that makes the deliverable take effect for other people: deploying, publishing, sending a message or email, filing an issue, or spending money.
Finalizing is allowed only when the request or an interview answer says so explicitly.
"cook" alone does not allow it.
Without that permission, take the deliverable to the point where finalizing is the only step left, and stop.

Never merge a PR, enable auto-merge, add a PR to a merge queue, or push to the default branch.
The user merges.
When the work continues an existing PR, disable its auto-merge and remove it from any merge queue before the first push, and check again before each later push:

```bash
gh pr merge <pr> --disable-auto
gh api graphql -f query='mutation($id:ID!){dequeuePullRequest(input:{id:$id}){clientMutationId}}' \
  -f id="$(gh pr view <pr> --json id -q .id)"
```

Deleting data, touching production, and changing anything outside the task's scope need an interview answer that allows them.
The grant does not bypass a harness or system approval prompt.

## 3. Work

Do the task with the smallest change or output that meets the acceptance criteria.
For a code change in a repo, implement it and open a PR.

Decide each issue that comes up mid-run from the brief and sensible defaults, and record the decision for the report.
A step is **blocked** when it needs an action outside the grant, a secret or access you do not have, or a choice the brief does not settle and that changes the result.
When a step is blocked, finish every part of the task that does not depend on it, then go to step 6.

## 4. Prove

**Proof** is evidence you observed in this session that the deliverable meets each acceptance criterion, such as command output, a test run, a reproduction, a rendered page, or a source you opened and read.
For a changed system, read its state back after the change.
For a document or analysis, render it and read the result, and open every source it cites to confirm the source says what the document claims.
Prove each criterion that can be observed before finalizing.
A criterion that only finalizing can satisfy, such as "production serves the new version", is proved in step 5.
A criterion you cannot prove is blocked.

When the deliverable has had no independent review, have a fresh subagent on a model from a different provider review it against the brief, without your conversation.
When no other provider is available, use a fresh subagent from the same provider.
Fix each finding you agree with and prove the fix, and record each rejected finding with its reason.

## 5. Deliver

Put the deliverable where the brief says.

For a PR, stay after CI passes until the review bots that reviewed the repo's recent PRs have reviewed the latest commit.
Fix their findings or record each rejection with its reason, and wait for checks and bots again after each push.
In T3 Code, call `watch_pull_request` and end the turn so the next PR change wakes you, and call `unwatch_pull_request` before the final message.
When only human approval remains, the status is waiting on human approval.

The PR is ready to merge when the latest commit passes required checks, the bots have finished, no human review requests changes, and GitHub reports the PR as mergeable.

When a finalizing action is allowed, take it, then confirm from the system that it took effect, for example the deployed version or the sent message.
Prove the criteria that depended on it.

## 6. Report

The final message is the first thing the user reads, so write it to stand alone:

- The status in the first line: finalized, ready to finalize (ready to merge, for a PR), waiting on someone else (name who and for what), or blocked.
- Where the deliverable is: a link, path, or system and identifier.
- The proof for each acceptance criterion.
- Each decision you made without the user, and each departure from the brief.
- Review findings you rejected, with reasons.
- Remaining risks, and problems you found that predate the task.

When blocked, lead with the blocker: what it is, what you tried, what you finished, and the options with your recommendation first.
After the report, ask the blocking question with the question tool as your last action, so the thread shows that it waits for the user.
When no question tool is available, start the final message with the question.
