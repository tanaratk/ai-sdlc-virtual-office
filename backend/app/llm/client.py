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
        # Disable thinking mode for qwen3 family — thinking tokens consume context
        # and cause empty responses when combined with format=json constraint
        "options": {"think": False},
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
    original = text
    text = text.strip()
    # Strip closed <think>...</think> blocks (qwen3 reasoning mode)
    text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
    # Strip unclosed <think> block (truncated LLM response)
    text = re.sub(r"<think>[\s\S]*", "", text).strip()

    logger.debug("extract_json raw (first 500): %s", original[:500])

    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning("json.loads failed (pos=%d col=%d): %s | text[%d:%d]=%r",
                       e.pos, e.colno, e.msg,
                       max(0, e.pos - 30), e.pos + 30,
                       text[max(0, e.pos - 30): e.pos + 30])

    # Markdown code fence ```json ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Last resort: find outermost { ... } in the text
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError as e:
            logger.warning("brace-extract also failed (pos=%d): %s", e.pos, e.msg)

    logger.error("extract_json giving up. Full text (%d chars): %s", len(original), original)
    raise ValueError(f"Cannot parse JSON from LLM output. First 300 chars: {original[:300]}")


def strip_code_fences(text: str) -> str:
    """Remove markdown code fences from LLM code output."""
    text = text.strip()
    text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
    text = re.sub(r"<think>[\s\S]*", "", text).strip()
    match = re.match(r"^```[\w]*\n([\s\S]+?)\n```$", text)
    if match:
        return match.group(1)
    return text
