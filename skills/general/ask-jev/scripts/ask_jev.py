#!/usr/bin/env python3
"""Submit JSON questions to Jev and print its structured response."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_BASE = "https://api.typesafe.ai/v1"


class RequestError(Exception):
    pass


def read_request(source: str) -> dict[str, Any]:
    try:
        if source == "-":
            request = json.load(sys.stdin)
        else:
            with open(source, encoding="utf-8") as request_file:
                request = json.load(request_file)
    except (OSError, json.JSONDecodeError) as error:
        raise RequestError(f"Cannot read request JSON: {error}") from error

    if not isinstance(request, dict):
        raise RequestError("The request must be a JSON object.")

    extra_fields = set(request) - {"state", "state_file", "questions", "model"}
    if extra_fields:
        names = ", ".join(sorted(extra_fields))
        raise RequestError(f"Unknown request field(s): {names}")

    has_state = "state" in request
    has_state_file = "state_file" in request
    if has_state == has_state_file:
        raise RequestError("Set exactly one of 'state' or 'state_file'.")

    if has_state_file:
        state_file = request["state_file"]
        if not isinstance(state_file, str) or not state_file:
            raise RequestError("'state_file' must be a non-empty path string.")
        state_path = Path(state_file)
        try:
            request["state"] = state_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise RequestError(
                f"Cannot read state file '{state_path}': {error}"
            ) from error
        del request["state_file"]

    state = request["state"]
    if not isinstance(state, (str, dict, list)):
        raise RequestError("'state' must be a string, object, or array.")

    questions = request.get("questions")
    if not isinstance(questions, dict) or not questions:
        raise RequestError("'questions' must be a non-empty JSON object.")

    for question_id, question in questions.items():
        if not question_id:
            raise RequestError("Question ids must not be empty.")
        if not isinstance(question, dict):
            raise RequestError(f"Question '{question_id}' must be a JSON object.")
        question_type = question.get("type")
        if not isinstance(question_type, str) or question_type not in {
            "noul",
            "choice",
            "score",
        }:
            raise RequestError(
                f"Question '{question_id}' type must be 'noul', 'choice', or 'score'."
            )
        if question_type == "choice":
            criteria = question.get("criteria")
            if not isinstance(criteria, dict) or not 1 <= len(criteria) <= 255:
                raise RequestError(
                    f"Question '{question_id}' needs 1 to 255 object criteria "
                    "for 'choice'."
                )
        if question_type == "score":
            criteria = question.get("criteria")
            if not isinstance(criteria, list) or not 1 <= len(criteria) <= 10:
                raise RequestError(
                    f"Question '{question_id}' needs 1 to 10 array criteria "
                    "for 'score'."
                )
        if question_type == "noul" and "criteria" in question:
            criteria = question["criteria"]
            if criteria is not None and not isinstance(criteria, dict):
                raise RequestError(
                    f"Question '{question_id}' criteria for 'noul' must be an object."
                )

    return request


def fetch_json(url: str, api_key: str) -> dict[str, Any]:
    request = Request(url, headers={"Authorization": f"Bearer {api_key}"})
    try:
        with urlopen(request, timeout=60) as response:
            return json.load(response)
    except HTTPError as error:
        raise RequestError(f"TypeSafe returned HTTP {error.code} for {url}.") from error
    except (URLError, TimeoutError) as error:
        reason = error.reason if isinstance(error, URLError) else error
        raise RequestError(f"TypeSafe request failed: {reason}") from error
    except json.JSONDecodeError as error:
        raise RequestError(f"TypeSafe returned invalid JSON from {url}.") from error


def choose_model(api_key: str, requested_model: Optional[str]) -> str:
    response = fetch_json(f"{API_BASE}/models", api_key)
    models = response.get("models") if isinstance(response, dict) else None
    names = [model.get("name") for model in models or [] if isinstance(model, dict)]
    jev_models = [
        name for name in names if isinstance(name, str) and name.startswith("jev-")
    ]

    if requested_model is not None:
        if not isinstance(requested_model, str):
            raise RequestError("'model' must be a model name string.")
        if requested_model not in jev_models:
            raise RequestError(
                f"Requested model '{requested_model}' is not an available Jev model."
            )
        return requested_model

    if "jev-latest" in jev_models:
        return "jev-latest"
    if jev_models:
        return jev_models[0]
    raise RequestError("The API key has no available Jev model.")


def send_request(api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = Request(
        f"{API_BASE}/systemone",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            return json.load(response)
    except HTTPError as error:
        message = f"TypeSafe returned HTTP {error.code} for the Jev request."
        if error.code == 422:
            try:
                body = json.load(error)
            except (json.JSONDecodeError, UnicodeDecodeError):
                body = None
            if isinstance(body, dict) and isinstance(body.get("detail"), list):
                details = [
                    {
                        key: str(item[key]).replace(api_key, "[redacted]")
                        for key in ("loc", "msg", "type")
                        if key in item
                    }
                    for item in body["detail"]
                    if isinstance(item, dict)
                ]
                if details:
                    message += f" Details: {json.dumps(details)}"
        raise RequestError(message) from error
    except (URLError, TimeoutError) as error:
        reason = error.reason if isinstance(error, URLError) else error
        raise RequestError(
            f"Jev request failed: {reason}. Completion may be unclear; "
            "do not retry automatically."
        ) from error
    except json.JSONDecodeError as error:
        raise RequestError(
            "TypeSafe returned invalid JSON for the Jev request."
        ) from error


def main() -> int:
    parser = argparse.ArgumentParser(description="Send JSON questions to Jev.")
    parser.add_argument(
        "request", help="JSON request file, or '-' to read JSON from standard input"
    )
    args = parser.parse_args()

    api_key = os.environ.get("JEV_API_KEY", "")
    if not api_key:
        print("JEV_API_KEY is not set or is empty.", file=sys.stderr)
        return 2

    try:
        payload = read_request(args.request)
        requested_model = payload.pop("model", None)
        payload["model"] = choose_model(api_key, requested_model)
        response = send_request(api_key, payload)
    except RequestError as error:
        print(error, file=sys.stderr)
        return 1

    json.dump(response, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
