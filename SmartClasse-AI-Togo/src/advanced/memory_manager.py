"""Memory Manager: Short-term and Long-term memory for conversation context and user profiles."""

import json
import logging
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class ConversationMemory:
    """Short-term conversation memory (current session)."""
    session_id: str
    messages: List[Dict[str, str]]
    context: Dict[str, Any]
    last_update: datetime
    session_metadata: Dict[str, Any]  # topic, user_level, language, etc.


@dataclass
class UserProfile:
    """Long-term user profile memory."""
    user_id: str
    name: str
    preferred_language: str
    educational_level: str
    subjects_history: Dict[str, int]  # subject -> interaction_count
    learning_preferences: Dict[str, Any]  # pacing, format, etc.
    previous_misconceptions: List[str]
    strengths: List[str]
    weaknesses: List[str]
    last_interaction: datetime
    created_at: datetime


class ConversationMemoryManager:
    """Manages short-term conversation memory."""

    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.sessions: Dict[str, ConversationMemory] = {}
        self.session_timeout = timedelta(hours=2)

    def create_session(self, session_id: str, metadata: Optional[Dict] = None) -> ConversationMemory:
        """Create new conversation session."""
        session = ConversationMemory(
            session_id=session_id,
            messages=[],
            context={},
            last_update=datetime.now(),
            session_metadata=metadata or {},
        )
        self.sessions[session_id] = session
        logger.info(f"New session created: {session_id}")
        return session

    def add_message(self, session_id: str, role: str, content: str) -> None:
        """Add message to session memory."""
        if session_id not in self.sessions:
            self.create_session(session_id)

        session = self.sessions[session_id]
        session.messages.append({"role": role, "content": content, "timestamp": datetime.now().isoformat()})
        session.last_update = datetime.now()

        # Keep only recent messages in memory (avoid overflow)
        if len(session.messages) > self.max_history:
            session.messages = session.messages[-self.max_history:]

        logger.debug(f"Message added to {session_id}: {role} ({len(content)} chars)")

    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get current session context."""
        if session_id not in self.sessions:
            return {}

        session = self.sessions[session_id]

        # Check if session expired
        if datetime.now() - session.last_update > self.session_timeout:
            del self.sessions[session_id]
            logger.info(f"Session {session_id} expired and removed")
            return {}

        return {
            "session_id": session_id,
            "message_count": len(session.messages),
            "recent_messages": session.messages[-5:],  # Last 5 messages
            "session_metadata": session.session_metadata,
            "session_age": (datetime.now() - session.last_update).total_seconds(),
        }

    def update_session_metadata(self, session_id: str, metadata: Dict[str, Any]) -> None:
        """Update session metadata (topic, level discovered, etc.)."""
        if session_id not in self.sessions:
            self.create_session(session_id, metadata)
        else:
            self.sessions[session_id].session_metadata.update(metadata)

    def get_conversation_summary(self, session_id: str, max_turns: int = 10) -> str:
        """Get a summary of the conversation for context injection."""
        if session_id not in self.sessions:
            return ""

        session = self.sessions[session_id]
        recent = session.messages[-max_turns:]

        summary_parts = []
        for msg in recent:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:100]  # Truncate
            summary_parts.append(f"{role}: {content}")

        return "\n".join(summary_parts)


class UserProfileManager:
    """Manages long-term user profiles (persistent)."""

    def __init__(self, db_path: str = "sqlite:///./smartclasse_profiles.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize user profile database."""
        # This would connect to actual DB (SQLite or other)
        # For now, we'll use in-memory cache
        self.profiles: Dict[str, UserProfile] = {}
        logger.info("User Profile Manager initialized")

    def create_profile(self, user_id: str, name: str, language: str = "french", level: str = "CE1") -> UserProfile:
        """Create new user profile."""
        profile = UserProfile(
            user_id=user_id,
            name=name,
            preferred_language=language,
            educational_level=level,
            subjects_history={},
            learning_preferences={},
            previous_misconceptions=[],
            strengths=[],
            weaknesses=[],
            last_interaction=datetime.now(),
            created_at=datetime.now(),
        )
        self.profiles[user_id] = profile
        logger.info(f"Profile created for {user_id}")
        return profile

    def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Retrieve user profile."""
        if user_id not in self.profiles:
            # Could fetch from DB here
            return None
        return self.profiles[user_id]

    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> Optional[UserProfile]:
        """Update user profile with new information."""
        profile = self.get_profile(user_id)
        if not profile:
            return None

        # Update profile attributes
        for key, value in updates.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        profile.last_interaction = datetime.now()
        logger.info(f"Profile updated for {user_id}")
        return profile

    def record_interaction(self, user_id: str, subject: str, interaction_type: str, success: bool) -> None:
        """Record a learning interaction."""
        profile = self.get_profile(user_id)
        if not profile:
            return

        # Update subject history
        if subject not in profile.subjects_history:
            profile.subjects_history[subject] = 0
        profile.subjects_history[subject] += 1

        # Record learning outcomes (could feed into diagnostix)
        logger.info(f"Interaction recorded: {user_id} | {subject} | {interaction_type} | success={success}")

    def add_misconception(self, user_id: str, misconception: str) -> None:
        """Record a common misconception for the user."""
        profile = self.get_profile(user_id)
        if not profile:
            return

        if misconception not in profile.previous_misconceptions:
            profile.previous_misconceptions.append(misconception)
            logger.info(f"Misconception recorded for {user_id}: {misconception}")

    def add_strength(self, user_id: str, strength: str) -> None:
        """Record user strength area."""
        profile = self.get_profile(user_id)
        if not profile:
            return

        if strength not in profile.strengths:
            profile.strengths.append(strength)

    def add_weakness(self, user_id: str, weakness: str) -> None:
        """Record user weakness area."""
        profile = self.get_profile(user_id)
        if not profile:
            return

        if weakness not in profile.weaknesses:
            profile.weaknesses.append(weakness)

    def get_user_context_for_response(self, user_id: str) -> Dict[str, Any]:
        """Get user context to inject into system prompt."""
        profile = self.get_profile(user_id)
        if not profile:
            return {}

        return {
            "user_name": profile.name,
            "educational_level": profile.educational_level,
            "preferred_language": profile.preferred_language,
            "strengths": profile.strengths[:3],  # Top 3
            "weaknesses": profile.weaknesses[:3],
            "misconceptions_to_avoid": profile.previous_misconceptions[:5],
            "favorite_subjects": sorted(profile.subjects_history.items(), key=lambda x: x[1], reverse=True)[:3],
        }


class MemoryManager:
    """Master memory manager orchestrating conversation + user memories."""

    def __init__(self):
        self.conversation_memory = ConversationMemoryManager()
        self.user_profiles = UserProfileManager()

    def initialize_session(self, session_id: str, user_id: str, user_name: str = "Student") -> Dict[str, Any]:
        """Initialize a new conversation session."""
        # Create conversation session
        conv_session = self.conversation_memory.create_session(session_id)

        # Load or create user profile
        user_profile = self.user_profiles.get_profile(user_id)
        if not user_profile:
            user_profile = self.user_profiles.create_profile(user_id, user_name)

        return {
            "session_id": session_id,
            "user_id": user_id,
            "user_profile": user_profile,
            "conversation_session": conv_session,
        }

    def add_turn(self, session_id: str, user_id: str, user_message: str, assistant_message: str) -> None:
        """Add a conversation turn to memory."""
        self.conversation_memory.add_message(session_id, "user", user_message)
        self.conversation_memory.add_message(session_id, "assistant", assistant_message)

    def get_context_for_response(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Get all relevant context for generating next response."""
        conv_context = self.conversation_memory.get_session_context(session_id)
        user_context = self.user_profiles.get_user_context_for_response(user_id)

        return {
            "conversation": conv_context,
            "user": user_context,
            "conversation_summary": self.conversation_memory.get_conversation_summary(session_id),
        }
