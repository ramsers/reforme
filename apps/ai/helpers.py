import json
import re

def extract_json(text: str) -> dict:
    if not text:
        raise ValueError("Empty AI response")

    t = text.strip()

    # Remove code fences: ```json ... ```
    t = re.sub(r"^```json\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"^```\s*", "", t)
    t = re.sub(r"\s*```$", "", t)

    # Try parse as-is first
    try:
        return json.loads(t)
    except Exception:
        pass

    # Fallback: parse the first {...} object
    start = t.find("{")
    end = t.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("Could not find JSON object boundaries")

    return json.loads(t[start:end+1])
