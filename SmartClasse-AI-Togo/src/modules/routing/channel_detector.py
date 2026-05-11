from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ChannelDecision:
    channel: str
    confidence: float
    reason: str
    language_hint: Optional[str] = None
    audio_expected: bool = False


class ChannelDetector:
    """Heuristic detector that chooses the active channel for LINGUIX.

    It prefers explicit signals first (audio payload, explicit channel) and falls back
    to lightweight text heuristics for typed messages.
    """

    VOICE_HINTS = (
        "audio",
        "voix",
        "parle",
        "spoken",
        "listen",
        "écoute",
        "ecoute",
        "m'entends",
        "transcris",
        "transcribe",
    )

    TEXT_HINTS = (
        "résume",
        "resume",
        "écris",
        "ecris",
        "affiche",
        "montre",
        "markdown",
        "table",
        "copie",
    )

    def detect(
        self,
        *,
        messages: Optional[List[Dict[str, str]]] = None,
        text: Optional[str] = None,
        audio_present: bool = False,
        explicit_channel: Optional[str] = None,
        speak: bool = False,
        language_hint: Optional[str] = None,
    ) -> ChannelDecision:
        if explicit_channel in {"voice", "text"}:
            return ChannelDecision(
                channel=explicit_channel,
                confidence=1.0,
                reason="explicit_channel",
                language_hint=language_hint,
                audio_expected=explicit_channel == "voice",
            )

        if audio_present:
            return ChannelDecision(
                channel="voice",
                confidence=0.98,
                reason="audio_payload_present",
                language_hint=language_hint,
                audio_expected=True,
            )

        candidate_text = text or self._extract_last_user_message(messages) or ""
        lowered = candidate_text.lower().strip()

        if any(hint in lowered for hint in self.VOICE_HINTS):
            return ChannelDecision(
                channel="voice",
                confidence=0.82,
                reason="voice_keywords",
                language_hint=language_hint,
                audio_expected=True or speak,
            )

        if any(hint in lowered for hint in self.TEXT_HINTS):
            return ChannelDecision(
                channel="text",
                confidence=0.80,
                reason="text_keywords",
                language_hint=language_hint,
                audio_expected=False,
            )

        if speak:
            return ChannelDecision(
                channel="voice",
                confidence=0.70,
                reason="speak_requested",
                language_hint=language_hint,
                audio_expected=True,
            )

        return ChannelDecision(
            channel="text",
            confidence=0.55,
            reason="default_text",
            language_hint=language_hint,
            audio_expected=False,
        )

    @staticmethod
    def _extract_last_user_message(messages: Optional[List[Dict[str, str]]]) -> Optional[str]:
        if not messages:
            return None
        for message in reversed(messages):
            if message.get("role") == "user":
                return (message.get("content") or "").strip()
        return None
