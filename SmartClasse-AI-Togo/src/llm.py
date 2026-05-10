"""LLM helper utilities for calling Ollama/Gemma4 with retries and sane defaults."""
import time
import logging
from typing import Any, Dict, List, Optional

try:
    import ollama  # type: ignore
except ImportError:
    ollama = None

from src.config import settings

logger = logging.getLogger(__name__)


def _is_memory_pressure_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return "more system memory" in message or "insufficient memory" in message


def call_chat(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    timeout: Optional[int] = None,
    retries: int = 2,
) -> Dict[str, Any]:
    """Call Ollama chat with retries and return the raw response dict.

    Raises Exception on final failure.
    """
    if ollama is None or not settings.OLLAMA_BASE_URL:
        raise RuntimeError("Ollama client not available or base URL not configured")

    model = model or settings.LLM_MODEL
    temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
    max_tokens = max_tokens if max_tokens is not None else settings.LLM_MAX_TOKENS
    timeout = timeout if timeout is not None else settings.OLLAMA_TIMEOUT

    last_exc: Optional[Exception] = None
    for attempt in range(1, retries + 2):
        try:
            client = ollama.Client(host=settings.OLLAMA_BASE_URL, timeout=timeout)
            options = {"temperature": temperature, "max_tokens": max_tokens}
            resp = client.chat(model=model, messages=messages, options=options)
            return resp
        except Exception as exc:
            last_exc = exc
            logger.warning("LLM call attempt %s failed: %s", attempt, exc)
            if _is_memory_pressure_error(exc):
                break
            if attempt <= retries:
                backoff = 0.5 * (2 ** (attempt - 1))
                time.sleep(backoff)
                continue
            break

    raise last_exc or RuntimeError("LLM call failed without exception")
