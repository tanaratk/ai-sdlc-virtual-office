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
    response_format: str | None = "json",
) -> str:
    """Call Ollama /api/chat and return the assistant message content.

    Pass response_format=None for free-form text output (code generation).
    Default is "json" to preserve existing behaviour for document agents.
    """
    model = model or settings.ollama_model
    url = f"{settings.ollama_base_url}/api/chat"

    payload: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }
    if response_format:
        payload["format"] = response_format

    logger.info("LLM call → Ollama model=%s format=%s url=%s", model, response_format, url)
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
    # Strip <think>...</think> blocks emitted by reasoning models (e.g. qwen3)
    text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
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


def strip_code_fences(text: str) -> str:
    """Remove markdown code fences from LLM code output."""
    text = text.strip()
    # Strip <think>...</think> blocks emitted by reasoning models (e.g. qwen3)
    text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
    match = re.match(r"^```[\w]*\n([\s\S]+?)\n```$", text)
    if match:
        return match.group(1)
    return text
