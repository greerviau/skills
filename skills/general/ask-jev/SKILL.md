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
To ask about a file without loading its contents into the conversation, have Python read the file into the request's `state` field.
Do not send credentials, unrelated files, or secrets.
Before sending sensitive project content to TypeSafe, tell the user what will be sent and ask for confirmation.
When no user can answer, exclude that material and continue only if the remaining state supports the question.

## Send the request

List models available to the key:

```bash
curl --fail --silent --show-error \
  https://api.typesafe.ai/v1/models \
  -H "Authorization: Bearer $JEV_API_KEY"
```

Use a Jev model name from that response, for example `jev-latest` when listed. The model field is required.

Create the request file with Python's standard `json` module so it preserves escaping.
Keep the API key out of the file:

```bash
request_file=$(mktemp)
trap 'rm -f "$request_file"' EXIT
python3 - "$request_file" <<'PY'
import json
import sys
from pathlib import Path

request = {
    "model": "jev-latest",
    "state": Path("path/to/file").read_text(encoding="utf-8"),
    "questions": {
        "has_tests": {
            "type": "noul",
            "instructions": "Does this change include tests for the behavior it adds?",
        }
    },
}
with open(sys.argv[1], "w", encoding="utf-8") as output:
    json.dump(request, output)
PY
curl --fail-with-body --silent --show-error \
  https://api.typesafe.ai/v1/systemone \
  -H "Authorization: Bearer $JEV_API_KEY" \
  -H "Content-Type: application/json" \
  --data-binary @"$request_file"
```

Replace the example file, model, and question with the requested state and decision.
The request reports billable input tokens in `usage.input_tokens`.
If a timeout leaves completion unclear, ask before resending because a retry can run and incur another charge.
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
