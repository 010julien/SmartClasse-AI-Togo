from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class RoutedOutput:
    channel: str
    text: str
    audio: Optional[Dict[str, Any]] = None
    stream: bool = False
    metadata: Optional[Dict[str, Any]] = None


class OutputRouter:
    """Map an assistant response to the correct output shape.

    This keeps the agent response logic compact while supporting text-only, voice,
    and streaming audio outputs.
    """

    def route_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> RoutedOutput:
        return RoutedOutput(channel="text", text=text, metadata=metadata or {})

    def route_voice(self, text: str, audio: Optional[Dict[str, Any]] = None, metadata: Optional[Dict[str, Any]] = None) -> RoutedOutput:
        return RoutedOutput(channel="voice", text=text, audio=audio, stream=False, metadata=metadata or {})

    def route_voice_stream(
        self,
        text: str,
        audio: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RoutedOutput:
        return RoutedOutput(channel="voice", text=text, audio=audio, stream=True, metadata=metadata or {})

    def as_dict(self, routed: RoutedOutput) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "channel": routed.channel,
            "text": routed.text,
            "stream": routed.stream,
        }
        if routed.audio is not None:
            payload["audio"] = routed.audio
        if routed.metadata is not None:
            payload["metadata"] = routed.metadata
        return payload
