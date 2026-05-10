"""KULTURIX: local Togolese cultural knowledge retrieval for prompt enrichment."""

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from src.config import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class KulturixEntry:
    theme: str
    language: str
    example: str
    prompt_seed: str
    tags: List[str]


class KulturixAgent:
    """Load and retrieve local cultural examples for ADAPTIX prompts."""

    def __init__(self, corpus_path: str | None = None):
        self.corpus_path = Path(corpus_path or settings.CULTURAL_CORPUS_PATH or "./data/cultural_corpus.json")
        self._entries: List[KulturixEntry] = self._load_corpus()

    def _load_corpus(self) -> List[KulturixEntry]:
        if not self.corpus_path.exists():
            logger.warning("KULTURIX corpus missing at %s", self.corpus_path)
            return []

        raw = json.loads(self.corpus_path.read_text(encoding="utf-8"))
        entries: List[KulturixEntry] = []
        for item in raw.get("entries", []):
            entries.append(
                KulturixEntry(
                    theme=item["theme"],
                    language=item.get("language", "french"),
                    example=item["example"],
                    prompt_seed=item.get("prompt_seed", item["example"]),
                    tags=item.get("tags", []),
                )
            )
        return entries

    def corpus_size(self) -> int:
        return len(self._entries)

    def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        lowered = query.lower()
        scored: List[tuple[int, KulturixEntry]] = []

        for entry in self._entries:
            haystack = " ".join([entry.theme, entry.language, entry.example, entry.prompt_seed, " ".join(entry.tags)]).lower()
            score = sum(1 for token in lowered.split() if token and token in haystack)
            if score > 0:
                scored.append((score, entry))

        if not scored:
            scored = [(0, entry) for entry in self._entries[:limit]]

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                "theme": entry.theme,
                "language": entry.language,
                "example": entry.example,
                "prompt_seed": entry.prompt_seed,
                "tags": entry.tags,
            }
            for _, entry in scored[:limit]
        ]

    def enrich_prompt(self, base_prompt: str, query: str, limit: int = 3) -> str:
        examples = self.search(query, limit=limit)
        snippets = "\n".join(f"- {item['example']}" for item in examples)
        return (
            f"{base_prompt}\n\n"
            f"KULTURIX local corpus ({len(examples)} references from {self.corpus_size()} entries):\n"
            f"{snippets}\n"
            "Use these local examples naturally and keep the cultural context authentic."
        )

    def get_context_pack(self, query: str, limit: int = 5) -> Dict[str, Any]:
        examples = self.search(query, limit=limit)
        return {
            "query": query,
            "corpus_size": self.corpus_size(),
            "examples": examples,
        }