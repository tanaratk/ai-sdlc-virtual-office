import json
import logging
import math

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def embed(text: str, timeout: float = 60.0) -> list[float]:
    """Call Ollama /api/embeddings and return the embedding vector."""
    url = f"{settings.ollama_base_url}/api/embeddings"
    model = settings.ollama_embed_model
    payload = {"model": model, "prompt": text}

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, json=payload)
    except httpx.ConnectError:
        raise RuntimeError(
            f"Cannot connect to Ollama at {settings.ollama_base_url}. "
            "Make sure Ollama is running, then pull the embedding model with: "
            f"ollama pull {model}"
        )
    except httpx.TimeoutException:
        raise RuntimeError(
            f"Ollama timed out after {timeout}s while generating embeddings. "
            "The model may still be loading — try again in a moment."
        )

    if response.status_code == 404:
        raise RuntimeError(
            f"Embedding model '{model}' not found in Ollama. "
            f"Run: ollama pull {model}"
        )

    response.raise_for_status()
    return response.json()["embedding"]


def serialize(vector: list[float]) -> str:
    return json.dumps(vector)


def deserialize(text: str) -> list[float]:
    return json.loads(text)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError(
            f"Vector dimension mismatch: {len(a)} vs {len(b)}. "
            "Re-ingest documents if the embedding model was changed."
        )
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0.0 or mag_b == 0.0:
        return 0.0
    return dot / (mag_a * mag_b)
