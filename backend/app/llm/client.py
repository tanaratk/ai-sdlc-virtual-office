import json
import logging
import re

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Model families that use extended thinking tokens.
# These need special handling when format=json is requested because thinking
# tokens consume the context window and leave no room for actual JSON output.
_THINKING_MODEL_PREFIXES = ("qwen3", "qwq", "deepseek-r1", "deepseek-r2", "marco-o1")


def _is_thinking_model(model: str) -> bool:
    m = model.lower()
    return any(p in m for p in _THINKING_MODEL_PREFIXES)


def _build_payload(
    model: str,
    system_prompt: str,
    user_prompt: str,
    response_format: str | None,
    force_no_think: bool = False,
) -> dict:
    """Build Ollama request payload with model-appropriate settings.

    Thinking models (qwen3, qwq, deepseek-r1, …) generate a reasoning chain
    before the answer.  When format=json is also active this causes empty
    responses because the model exhausts its context on thinking tokens.
    We suppress thinking via two complementary mechanisms:
      - /no_think appended to the user turn (prompt-level, all Ollama versions)
      - options.think=false  (API-level, Ollama ≥ 0.9)
    """
    is_thinking = _is_thinking_model(model)
    suppress = (is_thinking or force_no_think) and response_format

    effective_user = user_prompt
    options: dict = {}

    if suppress:
        effective_user = user_prompt + "\n/no_think"
        options["think"] = False

    payload: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": effective_user},
        ],
        "stream": False,
    }
    if options:
        payload["options"] = options
    if response_format:
        payload["format"] = response_format

    return payload


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

    Automatically handles per-model-family quirks:
    - Thinking models (qwen3, qwq, deepseek-r1 …): suppresses thinking chain
      for JSON calls so the context window is not wasted.
    - Standard models (llama3, mistral, phi3 …): no modifications.

    If the first call returns an empty string the function retries once with
    thinking suppression forced on, which recovers cases where the model
    ignored the /no_think hint on first attempt.
    """
    model = model or settings.ollama_model
    url = f"{settings.ollama_base_url}/api/chat"

    payload = _build_payload(model, system_prompt, user_prompt, response_format)
    logger.info(
        "LLM call → Ollama model=%s format=%s thinking_model=%s url=%s",
        model, response_format, _is_thinking_model(model), url,
    )

    with httpx.Client(timeout=timeout) as http:
        resp = http.post(url, json=payload)
        resp.raise_for_status()

    content: str = resp.json()["message"]["content"]
    logger.info("LLM call complete, response length=%d chars", len(content))

    # Retry once if empty — the thinking chain consumed all context tokens.
    # Force suppress on retry regardless of model family (catches miscategorised models).
    if not content.strip() and response_format:
        logger.warning(
            "Empty response from model=%s; retrying with forced thinking suppression", model
        )
        retry_payload = _build_payload(
            model, system_prompt, user_prompt, response_format, force_no_think=True
        )
        with httpx.Client(timeout=timeout) as http:
            resp = http.post(url, json=retry_payload)
            resp.raise_for_status()
        content = resp.json()["message"]["content"]
        logger.info("Retry complete, response length=%d chars", len(content))

    return content


def extract_json(text: str) -> dict:
    """Parse JSON from LLM output.

    Handles:
    - Direct JSON output
    - Markdown code-fenced JSON (``` or ```json)
    - Residual <think>…</think> blocks from reasoning models
    - Bare JSON buried in surrounding prose
    """
    original = text
    text = text.strip()
    # Remove closed thinking blocks (deepseek-r1, qwen3 with partial suppression)
    text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
    # Remove unclosed thinking block (truncated response)
    text = re.sub(r"<think>[\s\S]*", "", text).strip()

    logger.debug("extract_json input (first 500): %s", original[:500])

    # 1. Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning(
            "json.loads failed pos=%d col=%d: %s | context=%r",
            e.pos, e.colno, e.msg,
            text[max(0, e.pos - 30): e.pos + 30],
        )

    # 2. Markdown code fence
    m = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Outermost { … } — handles prose before/after the JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        try:
            return json.loads(text[start: end + 1])
        except json.JSONDecodeError as e:
            logger.warning("brace-extract failed pos=%d: %s", e.pos, e.msg)

    logger.error("extract_json giving up. Full text (%d chars): %s", len(original), original)
    raise ValueError(f"Cannot parse JSON from LLM output. First 300 chars: {original[:300]}")


def strip_code_fences(text: str) -> str:
    """Remove markdown code fences and thinking blocks from LLM code output."""
    text = text.strip()
    text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
    text = re.sub(r"<think>[\s\S]*", "", text).strip()
    m = re.match(r"^```[\w]*\n([\s\S]+?)\n```$", text)
    if m:
        return m.group(1)
    return text
