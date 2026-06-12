import json
import re


def extract_json_candidate(raw_text: str) -> dict | list | None:
    if not raw_text or not raw_text.strip():
        return None

    text = raw_text.strip()

    # Try direct parse first
    try:
        parsed = json.loads(text)
        if isinstance(parsed, (dict, list)):
            return parsed
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code fence
    fence_pattern = re.compile(
        r"```(?:json)?\s*\n?(.*?)\n?```", re.DOTALL
    )
    fence_match = fence_pattern.search(text)
    if fence_match:
        candidate = fence_match.group(1).strip()
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, (dict, list)):
                return parsed
        except json.JSONDecodeError:
            pass

    # Try extracting first { ... } block or [ ... ] block
    block_pattern = re.compile(r"(\{.*\}|\[.*\])", re.DOTALL)
    block_match = block_pattern.search(text)
    if block_match:
        candidate = block_match.group(1).strip()
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, (dict, list)):
                return parsed
        except json.JSONDecodeError:
            pass

    return None
