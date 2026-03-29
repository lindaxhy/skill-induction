"""Shared OpenRouter LLM client for all strategy scripts."""

import os
from openai import OpenAI

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Models: use sonnet for induction (quality), haiku for bulk evaluation (cost)
INDUCTION_MODEL = "anthropic/claude-3.5-sonnet"
EVAL_MODEL = "anthropic/claude-sonnet-4-6"


def get_client() -> OpenAI:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY environment variable not set")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
    )


def chat(system: str, user: str, model: str = INDUCTION_MODEL, temperature: float = 0.3) -> str:
    """Single chat call. Returns the assistant message content."""
    client = get_client()
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.choices[0].message.content
