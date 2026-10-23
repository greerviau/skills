---
name: ask-jev
description: Use Jev's decision API to classify, score, or estimate whether a statement applies to supplied state. Invoke when a second decision signal can help review work, inspect files, or answer a focused question. Requires JEV_API_KEY.
---

# ask-jev

Ask Jev structured questions about a state through TypeSafe's API.

## Check access

Before preparing a request, check that `JEV_API_KEY` is set and non-empty:

```bash
test -n "${JEV_API_KEY:-}"
```

If it is missing, stop.
Tell the user to create a TypeSafe API key in the [TypeSafe console](https://console.typesafe.ai/) and export it as `JEV_API_KEY`, then ask them to invoke the skill again.
Do not search files, shell history, or other environment variables for a key.

## Form the request

Represent the material as `state` and ask one decision per question. Choose a question type:

- `noul` returns the probability that a yes/no statement applies. Add `criteria` only when needed to define what yes and no mean.
- `choice` selects one label from a `criteria` object. Map each label to a short description.
- `score` places the state on an ordered `criteria` array, from lowest to highest.

Ask several focused questions about one state in one request.
Do not ask Jev to explain its answer or produce prose.

Use only the file text or context needed to answer the questions.
Put file paths in `state_file` so the script reads them without adding their contents to the conversation.
Do not send credentials, unrelated files, or secrets.
Before sending sensitive project content to TypeSafe, tell the user what will be sent and ask for confirmation.
When no user can answer, exclude that material and continue only if the remaining state supports the question.

## Send the request

Pass a JSON object with `questions` and exactly one of `state` or `state_file` to `scripts/ask_jev.py`.
The script reads `JEV_API_KEY`, selects `jev-latest` when the API key can use it, validates the request, sends it to TypeSafe, and prints the JSON response.
Set `model` only when you need a specific available Jev model.
The script writes the response to standard output and errors to standard error.

```bash
cat <<'JSON' | uv run --no-project skills/general/ask-jev/scripts/ask_jev.py -
{
  "state_file": "README.md",
  "questions": {
    "has_install_instructions": {
      "type": "noul",
      "instructions": "Does this file explain how to install the project?"
    }
  }
}
JSON
```

Run the command from the repository root and replace `README.md` and the example question with the requested file and decision.
When this skill is installed outside this repository, use the installed skill's path to `scripts/ask_jev.py`.
Relative `state_file` paths resolve from the current working directory.
The response reports billable input tokens in `usage.input_tokens`.
If a timeout leaves completion unclear, do not retry automatically because a retry can run and incur another charge.
When no user can answer, report the timeout as unresolved and do not retry.

## Use the result

Read the `answers` entry for each question id.
Report the returned values and probabilities, and keep probabilities distinct from certainty.
For `noul`, values near `0.5` are uncertain.
For `choice` and `score`, use the returned probability distribution to describe ambiguity.
Treat Jev's result as an additional signal.
Verify consequential claims against the source material and other available evidence.

If the request fails, report the HTTP or transport error and do not invent an answer.
For `401`, ask the user to check that the environment contains a valid TypeSafe API key.
Do not print or repeat the key.
