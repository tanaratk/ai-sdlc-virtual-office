import json
import logging
import re

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def call_ollama(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    timeout: float = 120.0,
) -> str:
    """Call Ollama /api/chat and return the assistant message content."""
    model = model or settings.ollama_model
    url = f"{settings.ollama_base_url}/api/chat"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "format": "json",
    }

    logger.info("LLM call → Ollama model=%s url=%s", model, url)
    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()

    data = response.json()
    content = data["message"]["content"]
    logger.info("LLM call complete, response length=%d chars", len(content))
    return content


def extract_json(text: str) -> dict:
    """Parse JSON from LLM output, handling markdown code-block wrapping."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Cannot parse JSON from LLM output. First 300 chars: {text[:300]}")
