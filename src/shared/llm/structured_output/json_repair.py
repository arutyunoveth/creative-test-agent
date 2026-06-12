import json
import re


def repair_json(raw_text: str) -> dict:
    if not raw_text or not raw_text.strip():
        return {"repaired": False, "error": "empty_input", "data": None}

    text = raw_text.strip()
    steps: list[str] = []

    # Step 1: remove markdown fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
        text = text.strip()
        steps.append("removed_markdown_fence")

    # Step 2: try parse
    try:
        parsed = json.loads(text)
        if isinstance(parsed, (dict, list)):
            return {"repaired": len(steps) > 0, "repair_steps": steps, "data": parsed}
    except json.JSONDecodeError:
        pass

    # Step 3: trim text before first { and after last }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace > first_brace:
        trimmed = text[first_brace : last_brace + 1]
        if trimmed != text:
            steps.append("trimmed_outer_text")
            text = trimmed

    try:
        parsed = json.loads(text)
        if isinstance(parsed, (dict, list)):
            return {"repaired": True, "repair_steps": steps, "data": parsed}
    except json.JSONDecodeError:
        pass

    # Step 4: remove trailing commas in objects and arrays
    text_no_trailing = re.sub(r",\s*}", "}", text)
    text_no_trailing = re.sub(r",\s*]", "]", text_no_trailing)
    if text_no_trailing != text:
        steps.append("removed_trailing_commas")
        text = text_no_trailing

    try:
        parsed = json.loads(text)
        if isinstance(parsed, (dict, list)):
            return {"repaired": True, "repair_steps": steps, "data": parsed}
    except json.JSONDecodeError:
        pass

    return {"repaired": False, "error": "json_parse_failed", "data": None}
