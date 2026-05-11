from typing import List, Dict, Any, Optional
from src import llm as llm_util
from src.config import settings
import logging

logger = logging.getLogger(__name__)


class GemmaEngine:
    """Thin wrapper to call Gemma 4 via existing llm utilities.

    Provides a channel-adaptive prompt helper and a simple generate() method.
    """

    def __init__(self, model: Optional[str] = None):
        self.model = model or settings.LLM_MODEL

    def adapt_system_prompt(self, channel: str) -> str:
        if channel == "voice":
            return "You are an expressive voice assistant. Keep answers short and conversational."
        if channel == "text":
            return "You are a precise text assistant. Use markdown when helpful."
        return "You are a helpful assistant."

    def generate(self, messages: List[Dict[str, str]], channel: str = "text", max_tokens: int = 256, temperature: float = 0.4) -> Dict[str, Any]:
        system = self.adapt_system_prompt(channel)
        llm_messages = [
            {"role": "system", "content": system},
            *messages,
        ]
        resp = llm_util.call_chat(messages=llm_messages, model=self.model, temperature=temperature, max_tokens=max_tokens)
        return resp
