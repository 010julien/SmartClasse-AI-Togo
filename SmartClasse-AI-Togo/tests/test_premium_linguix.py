"""Test suite for LINGUIX Premium: Advanced conversational AI system."""

import pytest
from unittest.mock import patch, MagicMock

from src.advanced.nlu_engine import NLUEngine, IntentType, EntityExtractor, IntentClassifier
from src.advanced.reasoning_engine import ReasoningEngine
from src.advanced.memory_manager import MemoryManager, ConversationMemoryManager, UserProfileManager
from src.advanced.quality_validator import QualityValidator, QualityScore
from src.advanced.prompts import AdvancedPromptEngineering
from src.advanced.conversation_manager import ConversationManager


class TestNLUEngine:
    """Test Natural Language Understanding."""

    def test_entity_extraction_subject(self):
        """Test extraction of subject from text."""
        extractor = EntityExtractor()
        entities = extractor.extract("Je veux apprendre les fractions en math")
        assert entities.get("subject") == "math"

    def test_entity_extraction_level(self):
        """Test extraction of educational level."""
        extractor = EntityExtractor()
        entities = extractor.extract("Je suis en CE1 et je ne comprends pas")
        assert entities.get("level") == "CE1"

    def test_entity_extraction_language(self):
        """Test extraction of language preference."""
        extractor = EntityExtractor()
        entities = extractor.extract("Traduit en kabyie sil'te plait")
        assert entities.get("language") == "kabyie"

    def test_intent_classification_explain(self):
        """Test classification of explanation intent."""
        classifier = IntentClassifier()
        intent = classifier.classify("Explique-moi les fractions", {})
        assert intent.type == IntentType.EXPLAIN
        assert intent.confidence > 0.5

    def test_intent_classification_exercise(self):
        """Test classification of exercise intent."""
        classifier = IntentClassifier()
        intent = classifier.classify("Donne-moi un exercice de math", {})
        assert intent.type == IntentType.EXERCISE
        assert intent.confidence > 0.5

    def test_nlu_full_pipeline(self):
        """Test full NLU pipeline."""
        engine = NLUEngine()
        result = engine.analyze("Bonjour, je suis en CE1 et je veux apprendre les fractions")

        assert result["intent"].type in [IntentType.LEARN, IntentType.SOCIALIZE]
        assert "level" in result["entities"] or result["entities"]
        assert result["analysis_confidence"] >= 0.0


class TestReasoningEngine:
    """Test reasoning engine with CoT."""

    def test_math_reasoning(self):
        """Test math reasoning pipeline."""
        engine = ReasoningEngine()
        chain = engine.reason("2 + 2 = ?", problem_type="math")

        assert len(chain.steps) >= 3
        assert chain.reasoning_confidence > 0.0
        assert chain.final_conclusion is not None

    def test_explanation_reasoning(self):
        """Test explanation reasoning."""
        engine = ReasoningEngine()
        chain = engine.reason("Qu'est-ce qu'une fraction?", problem_type="explanation", context={"educational_level": "CE1"})

        assert len(chain.steps) >= 3
        assert "CE1" in chain.steps[1].analysis or chain.steps[1].description

    def test_exercise_generation_reasoning(self):
        """Test exercise generation reasoning."""
        engine = ReasoningEngine()
        chain = engine.reason("Genère un exercice sur les fractions", problem_type="exercise_generation")

        assert len(chain.steps) >= 3
        assert any("exercice" in step.description.lower() for step in chain.steps)


class TestMemoryManager:
    """Test memory management system."""

    def test_conversation_memory_creation(self):
        """Test conversation memory session creation."""
        manager = ConversationMemoryManager()
        session = manager.create_session("test_session_1")

        assert session.session_id == "test_session_1"
        assert len(session.messages) == 0

    def test_conversation_memory_add_message(self):
        """Test adding messages to memory."""
        manager = ConversationMemoryManager()
        manager.create_session("test_session_1")
        manager.add_message("test_session_1", "user", "Bonjour")
        manager.add_message("test_session_1", "assistant", "Salut!")

        context = manager.get_session_context("test_session_1")
        assert context["message_count"] == 2

    def test_user_profile_creation(self):
        """Test user profile creation."""
        profile_manager = UserProfileManager()
        profile = profile_manager.create_profile("user_001", "Kossi", language="french", level="CE1")

        assert profile.user_id == "user_001"
        assert profile.name == "Kossi"
        assert profile.preferred_language == "french"

    def test_user_profile_update(self):
        """Test updating user profile."""
        profile_manager = UserProfileManager()
        profile_manager.create_profile("user_001", "Kossi")
        updated = profile_manager.update_profile("user_001", {"strengths": ["math", "reading"]})

        assert "math" in updated.strengths
        assert "reading" in updated.strengths

    def test_memory_manager_integration(self):
        """Test full memory manager integration."""
        manager = MemoryManager()
        session = manager.initialize_session("session_1", "user_001", "Kossi")

        assert session["session_id"] == "session_1"
        assert session["user_id"] == "user_001"
        assert session["user_profile"] is not None


class TestQualityValidator:
    """Test quality validation system."""

    def test_quality_score_relevance(self):
        """Test relevance scoring."""
        validator = QualityValidator()
        score = validator.validate("2 + 2 = 4", "Qu'est-ce que 2 + 2?")

        assert score.overall_score >= 0.0
        assert score.overall_score <= 100.0
        assert QualityScore.scores_by_dimension

    def test_quality_score_clarity(self):
        """Test clarity assessment."""
        validator = QualityValidator()

        # Long complex sentence should score lower on clarity
        long_sentence = "Une fraction est une representation mathematique d'une portion d'un ensemble " \
                       "qui peut etre decomposee en parties egales selon un certain nombre denomine." * 3
        score = validator.validate(long_sentence, "Qu'est-ce qu'une fraction?")

        assert "long" in " ".join(score.issues).lower() or score.scores_by_dimension["clarity"] < 85

    def test_quality_threshold(self):
        """Test quality threshold."""
        validator = QualityValidator()
        score = validator.validate("Oui", "C'est correct?")

        assert not score.passes_threshold  # Too short
        assert score.needs_regeneration


class TestAdvancedPromptEngineering:
    """Test advanced prompt engineering."""

    def test_system_prompt_explain(self):
        """Test system prompt generation for explanations."""
        from src.advanced.nlu_engine import Intent

        intent = Intent(
            type=IntentType.EXPLAIN,
            confidence=0.95,
            entities={"subject": "math"},
            raw_tokens=["explique", "fractions"],
        )

        user_context = {
            "user_name": "Kossi",
            "educational_level": "CE1",
            "preferred_language": "french",
        }

        prompt = AdvancedPromptEngineering.build_system_prompt(intent, user_context)

        assert "Explique" in prompt or "explique" in prompt.lower()
        assert "Kossi" in prompt or "CE1" in prompt

    def test_quality_check_prompt(self):
        """Test quality check prompt generation."""
        prompt = AdvancedPromptEngineering.build_quality_check_prompt(
            "Une fraction est...",
            "Qu'est-ce qu'une fraction?",
            "CE1",
        )

        assert "Pertinence" in prompt or "pertinence" in prompt.lower()
        assert "CE1" in prompt


class TestConversationManager:
    """Test full conversation manager."""

    @patch("src.advanced.conversation_manager.call_chat")
    def test_process_conversation_basic(self, mock_call_chat):
        """Test basic conversation processing."""
        mock_response = {
            "message": {"content": "Une fraction est une partie d'un tout."}
        }
        mock_call_chat.return_value = mock_response

        manager = ConversationManager()
        messages = [{"role": "user", "content": "Explique les fractions"}]

        response = manager.process_conversation(
            session_id="test_1",
            user_id="user_1",
            user_name="Kossi",
            messages=messages,
            user_level="CE1",
        )

        assert response.message is not None
        assert response.intent is not None
        assert response.total_time_ms > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
