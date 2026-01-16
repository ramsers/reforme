import json

def build_inactive_clients_prompt(studio_name: str, window_days: int, rows: list[dict]) -> str:
    payload = {
        "studio_name": studio_name,
        "window_days": window_days,
        "clients": rows,
    }

    system_prompt = (
        "You are a retention assistant for a Pilates studio admin.\n"
        "Rules:\n"
        "- Use ONLY the provided JSON facts. Do NOT invent purchases, credits, reasons, or attendance.\n"
        "- You may make soft inferences but label them as 'possible'.\n"
        "- No medical claims.\n"
        "- Return STRICT JSON only.\n"
    )

    user_prompt = f"""
    Task:
    Given the inactive client list (inactive for {window_days}+ days), produce:
    1) summary: 3–6 sentences about what's happening.
    2) segments: 3–5 groups with name, description, client_ids.
    3) priorities: ranked list of up to 10 client_ids with reasons grounded in data.
    4) messages: 2 SMS drafts and 1 email draft, matched broadly to the segments, with placeholders like {{name}}.

    Return STRICT JSON with this structure:
    {{
      "summary": "...",
      "segments": [{{"name":"...", "description":"...", "client_ids":[...]}}],
      "priorities": [{{"client_id":"...", "reason":"..."}}],
      "messages": {{
        "sms": ["...", "..."],
        "email": ["..."]
      }}
    }}

    Input JSON:
    {json.dumps(payload)}
    """.strip()

    return system_prompt, user_prompt