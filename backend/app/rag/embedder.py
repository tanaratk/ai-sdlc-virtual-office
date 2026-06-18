import json
import logging
import math

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def embed(text: str, timeout: float = 60.0) -> list[float]:
    """Call Ollama /api/embeddings and return the embedding vector."""
    url = f"{settings.ollama_base_url}/api/embeddings"
    payload = {"model": settings.ollama_embed_model, "prompt": text}

    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, json=payload)
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
