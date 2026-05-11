from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time


@dataclass
class Turn:
    role: str
    content: str
    ts: float = field(default_factory=time.time)


@dataclass
class ConversationContext:
    session_id: str
    active_channel: str = "text"
    user_profile: Dict[str, Any] = field(default_factory=dict)
    short_term_memory: List[Turn] = field(default_factory=list)
    long_term_memory: List[Dict[str, Any]] = field(default_factory=list)
    current_intent: Optional[str] = None
    conversation_state: str = "IDLE"
    language: str = "french"
    preferences: Dict[str, Any] = field(default_factory=dict)
    channel_history: Dict[str, List[Turn]] = field(default_factory=lambda: {"voice": [], "text": []})


class ContextHub:
    """Simple in-memory context hub. Replace with Redis/Chroma for prod."""

    def __init__(self, session_id: str, short_term_turns: int = 20):
        self.ctx = ConversationContext(session_id=session_id)
        self.short_term_turns = short_term_turns

    def add_turn(self, role: str, content: str, channel: str = "text") -> None:
        turn = Turn(role=role, content=content)
        self.ctx.short_term_memory.append(turn)
        self.ctx.channel_history.setdefault(channel, []).append(turn)
        # trim
        if len(self.ctx.short_term_memory) > self.short_term_turns:
            self.ctx.short_term_memory = self.ctx.short_term_memory[-self.short_term_turns:]

    def get_context_for_llm(self) -> Dict[str, Any]:
        return {
            "short_term": [t.content for t in self.ctx.short_term_memory],
            "user_profile": self.ctx.user_profile,
            "language": self.ctx.language,
        }

    def set_user_profile(self, profile: Dict[str, Any]) -> None:
        self.ctx.user_profile.update(profile)
