"""LLM client — routes to Ollama, OpenAI, or Anthropic based on model name.

Model name prefix routing:
  gpt-*, o1-*, o3-*, o4-*   → OpenAI
  claude-*                   → Anthropic
  (anything else)            → Ollama (local)

Thinking-model suppression (Ollama only):
  qwen3/qwq/deepseek-r1/…   → /no_think directive + options.think=false
"""
import json
import logging
import re

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# ── Model family detection ────────────────────────────────────────────────────

_OPENAI_PREFIXES = ("gpt-", "o1", "o3", "o4")
_ANTHROPIC_PREFIX = "claude-"
_THINKING_PREFIXES = ("qwen3", "qwq", "deepseek-r1", "deepseek-r2", "marco-o1")


def _provider(model: str) -> str:
    m = model.lower()
    if any(m.startswith(p) for p in _OPENAI_PREFIXES):
        return "openai"
    if m.startswith(_ANTHROPIC_PREFIX):
        return "anthropic"
    return "ollama"


def _is_thinking_model(model: str) -> bool:
    m = model.lower()
    return any(p in m for p in _THINKING_PREFIXES)


# ── Ollama ────────────────────────────────────────────────────────────────────

def _build_ollama_payload(
    model: str,
    system_prompt: str,
    user_prompt: str,
    response_format: str | None,
    no_think: bool = False,
    no_grammar: bool = False,
) -> dict:
    """Build Ollama request payload.

    no_think=True  → append /no_think + options.think=false (qwen3/qwq/deepseek)
    no_grammar=True → skip format=json (used on retry when grammar+thinking conflicts)
    """
    apply_no_think = (no_think or _is_thinking_model(model)) and bool(response_format)
    effective_user = (user_prompt + "\n/no_think") if apply_no_think else user_prompt
    effective_format = None if no_grammar else response_format

    payload: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": effective_user},
        ],
        "stream": False,
    }
    if apply_no_think:
        payload["options"] = {"think": False}
    if effective_format:
        payload["format"] = effective_format
    return payload


def _ollama_post(url: str, payload: dict, timeout: float) -> str:
    with httpx.Client(timeout=timeout) as http:
        resp = http.post(url, json=payload)
        resp.raise_for_status()
    return resp.json()["message"]["content"]


def _call_ollama(
    system_prompt: str,
    user_prompt: str,
    model: str,
    timeout: float,
    response_format: str | None,
) -> str:
    url = f"{settings.ollama_base_url}/api/chat"

    # Attempt 1 — standard (with format=json, thinking suppressed for known models)
    payload = _build_ollama_payload(model, system_prompt, user_prompt, response_format)
    content = _ollama_post(url, payload, timeout)
    logger.info("Ollama attempt 1 model=%s response=%d chars", model, len(content))

    if content.strip():
        return content

    if not response_format:
        return content  # free-form call, empty is the final answer

    # Attempt 2 — force no_think + keep format=json
    logger.warning("Ollama model=%s: empty on attempt 1, retry with forced no_think", model)
    payload2 = _build_ollama_payload(
        model, system_prompt, user_prompt, response_format, no_think=True
    )
    content = _ollama_post(url, payload2, timeout)
    logger.info("Ollama attempt 2 model=%s response=%d chars", model, len(content))

    if content.strip():
        return content

    # Attempt 3 — drop format=json entirely; rely on prompt instructions + extract_json
    # Fixes: thinking models where grammar-constrained JSON + thinking tokens exhaust context
    logger.warning(
        "Ollama model=%s: still empty, retrying WITHOUT format=json (grammar conflict)", model
    )
    payload3 = _build_ollama_payload(
        model, system_prompt, user_prompt, response_format, no_think=True, no_grammar=True
    )
    content = _ollama_post(url, payload3, timeout)
    logger.info("Ollama attempt 3 model=%s response=%d chars", model, len(content))
    return content


# ── OpenAI ────────────────────────────────────────────────────────────────────

def _call_openai(
    system_prompt: str,
    user_prompt: str,
    model: str,
    timeout: float,
    response_format: str | None,
) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai package not installed. Run: pip install openai")

    api_key = settings.openai_api_key
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to your .env file or Docker Compose environment."
        )

    client = OpenAI(api_key=api_key, timeout=timeout)

    kwargs: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    if response_format == "json":
        kwargs["response_format"] = {"type": "json_object"}

    resp = client.chat.completions.create(**kwargs)
    return resp.choices[0].message.content or ""


# ── Anthropic / Claude ────────────────────────────────────────────────────────

def _call_anthropic(
    system_prompt: str,
    user_prompt: str,
    model: str,
    timeout: float,
    response_format: str | None,
) -> str:
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

    api_key = settings.anthropic_api_key
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to your .env file or Docker Compose environment."
        )

    client = anthropic.Anthropic(api_key=api_key, timeout=timeout)

    # Claude uses prompt-level JSON instructions (no native format=json param).
    # System prompt already says "Return ONLY valid JSON" so no extra change needed.
    message = client.messages.create(
        model=model,
        max_tokens=8192,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text if message.content else ""


# ── Public API ────────────────────────────────────────────────────────────────

def call_ollama(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    timeout: float = 120.0,
    response_format: str | None = "json",
) -> str:
    """Call the appropriate LLM provider based on the model name.

    Routes automatically:
      gpt-*, o1-*, o3-*, o4-*  → OpenAI API
      claude-*                  → Anthropic API
      (everything else)         → Ollama (local)

    Pass response_format=None for free-form output (code generation).
    Default is "json" for structured document agents.
    """
    model = model or settings.ollama_model
    provider = _provider(model)

    logger.info("LLM call → provider=%s model=%s format=%s", provider, model, response_format)

    if provider == "openai":
        content = _call_openai(system_prompt, user_prompt, model, timeout, response_format)
    elif provider == "anthropic":
        content = _call_anthropic(system_prompt, user_prompt, model, timeout, response_format)
    else:
        content = _call_ollama(system_prompt, user_prompt, model, timeout, response_format)

    logger.info("LLM call complete, provider=%s response length=%d chars", provider, len(content))
    return content


# ── JSON / code extraction helpers ───────────────────────────────────────────

def extract_json(text: str) -> dict:
    """Parse JSON from LLM output.

    Handles: direct JSON, markdown code fences, residual <think> blocks,
    and bare JSON buried in surrounding prose.
    """
    original = text
    text = text.strip()
    text = re.sub(r"<think>[\s\S]*?</think>", "", text).strip()
    text = re.sub(r"<think>[\s\S]*", "", text).strip()

    logger.debug("extract_json input (first 500): %s", original[:500])

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        logger.warning(
            "json.loads failed pos=%d col=%d: %s | context=%r",
            e.pos, e.colno, e.msg,
            text[max(0, e.pos - 30): e.pos + 30],
        )

    m = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass

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
    return m.group(1) if m else text
