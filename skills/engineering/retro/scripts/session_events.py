"""List the user prompts, interruptions, failed tool calls, and oversized results in a session log.

Usage: python3 session_events.py <session-log.jsonl>
Each line of output starts with the log line number, so a finding can cite it.
"""
import json
import sys

for number, line in enumerate(open(sys.argv[1]), 1):
    record = json.loads(line)
    content = (record.get("message") or {}).get("content") or []
    blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content
    for block in blocks:
        text = block.get("text", "")
        if record.get("type") == "user" and text and not record.get("isMeta"):
            if text.startswith("[Request interrupted"):
                print(f"{number} interrupted")
            elif not text.startswith(("<local-command", "<command-", "<task-notification")):
                print(f"{number} prompt: {text[:200]!r}")
        if block.get("type") == "tool_result":
            result = str(block.get("content"))
            if block.get("is_error"):
                print(f"{number} tool error: {result[:200]!r}")
            elif "<persisted-output>" in result:
                print(f"{number} oversized result: {result.splitlines()[1][:120]!r}")
