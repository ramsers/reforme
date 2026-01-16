from django.conf import settings
from huggingface_hub import InferenceClient


def hf_chat(system_prompt: str, user_prompt: str) -> str:
    if not settings.HF_API_TOKEN:
        raise RuntimeError('HF API token not set.')

    client = InferenceClient(model=settings.HF_MODEL, token=settings.HF_API_TOKEN)

    resp = client.chat_completion(messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=1500,
        temperature=0.4,
        top_p=0.9
    )

    print('response:=========', resp.choices[0].message.content.strip(), flush=True)

    return resp.choices[0].message.content