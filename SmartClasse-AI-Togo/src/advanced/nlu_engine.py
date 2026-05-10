"""Advanced NLU Engine: Intent Detection, Entity Extraction, Context Analysis."""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Core intent types for educational conversations."""
    EXPLAIN = "explain"  # Demande d'explication
    EXERCISE = "exercise"  # Demande d'exercice
    CORRECT = "correct"  # Demande de correction
    TRANSLATE = "translate"  # Demande de traduction
    LEARN = "learn"  # Apprentissage général
    EVALUATE = "evaluate"  # Auto-évaluation
    SOCIALIZE = "socialize"  # Interaction sociale/motivation
    CLARIFY = "clarify"  # Demande de clarification
    HELP = "help"  # Aide générale
    UNKNOWN = "unknown"  # Non classifié


@dataclass
class Intent:
    """Structured intent representation."""
    type: IntentType
    confidence: float  # 0.0 to 1.0
    entities: Dict[str, Any]  # Extracted entities: subject, level, language, etc.
    raw_tokens: List[str]
    primary_subject: Optional[str] = None  # math, french, history, etc.
    educational_level: Optional[str] = None  # CE1, CE2, CM1, CM2, etc.
    action_type: Optional[str] = None  # detailed action: generate, explain_step, etc.


class EntityExtractor:
    """Extract educational entities from user input."""

    SUBJECTS = {
        "math": ["math", "mathematic", "fraction", "geometrie", "calcul", "addition", "soustraction", "multiplication"],
        "french": ["francais", "french", "grammaire", "conjugaison", "orthographe", "vocabulaire", "lecture"],
        "history": ["histoire", "history", "civilisation", "geographie", "culture"],
        "science": ["science", "physique", "chimie", "biologie", "nature"],
        "civic": ["civique", "civic", "droits", "devoir", "citoyen"],
    }

    LEVELS = {
        "CE1": ["ce1", "cours", "elementary", "primaire"],
        "CE2": ["ce2", "cours", "elementary"],
        "CM1": ["cm1", "course", "intermediate"],
        "CM2": ["cm2", "course", "intermediate"],
        "6e": ["6e", "sixth", "college"],
        "5e": ["5e", "fifth"],
        "4e": ["4e", "fourth"],
        "3e": ["3e", "third", "brevet"],
    }

    LANGUAGES = {
        "french": ["francais", "french"],
        "kabyie": ["kabyie", "kabiye"],
        "ewe": ["ewe", "ewé"],
        "haoussa": ["haoussa", "haussa"],
        "mina": ["mina", "minà"],
        "tem": ["tem", "tém"],
    }

    @staticmethod
    def extract(text: str) -> Dict[str, Any]:
        """Extract entities from text."""
        entities = {}
        lowered = text.lower()

        # Extract subject
        for subject, keywords in EntityExtractor.SUBJECTS.items():
            if any(kw in lowered for kw in keywords):
                entities["subject"] = subject
                break

        # Extract level
        for level, keywords in EntityExtractor.LEVELS.items():
            if any(kw in lowered for kw in keywords):
                entities["level"] = level
                break

        # Extract language
        for lang, keywords in EntityExtractor.LANGUAGES.items():
            if any(kw in lowered for kw in keywords):
                entities["language"] = lang
                break

        # Extract action type
        if any(kw in lowered for kw in ["corrige", "corrige", "correction"]):
            entities["action"] = "correct"
        elif any(kw in lowered for kw in ["exemple", "explique", "comment", "c'est quoi"]):
            entities["action"] = "explain"
        elif any(kw in lowered for kw in ["exo", "exercice", "probleme", "test"]):
            entities["action"] = "exercise"

        return entities


class IntentClassifier:
    """Classify user intent using heuristic + keyword matching."""

    KEYWORDS = {
        IntentType.EXPLAIN: ["explique", "comment", "c'est quoi", "c est quoi", "definition", "aide moi comprendre", "pourquoi", "exemple", "clarifier"],
        IntentType.EXERCISE: ["exercice", "exo", "probleme", "test", "donnez", "donne moi", "faites", "propose", "test moi", "verifier"],
        IntentType.CORRECT: ["corriger", "correction", "corrige", "verify", "check", "is correct", "juste", "faux"],
        IntentType.TRANSLATE: ["traduction", "traduit", "translate", "en", "traduire"],
        IntentType.LEARN: ["apprendre", "enseigner", "lecon", "cours", "comprendre", "understand"],
        IntentType.EVALUATE: ["evaluer", "evaluation", "score", "progress", "resultat", "performance"],
        IntentType.SOCIALIZE: ["bonjour", "hello", "ça va", "comment ca va", "salut", "thanks", "merci", "merci beaucoup"],
        IntentType.CLARIFY: ["je ne comprends", "c'est pas clair", "plus simple", "encore", "plutot", "rephrase"],
        IntentType.HELP: ["aide", "help", "assistance", "support", "probleme", "stuck"],
    }

    @staticmethod
    def classify(text: str, entities: Dict[str, Any]) -> Intent:
        """Classify intent from text and entities."""
        lowered = text.lower()
        scores: Dict[IntentType, float] = {}

        # Score each intent based on keyword matches
        for intent_type, keywords in IntentClassifier.KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in lowered)
            scores[intent_type] = matches / len(keywords) if keywords else 0.0

        # Fallback to SOCIALIZE or LEARN if no strong signal
        best_intent = max(scores, key=scores.get) if scores else IntentType.LEARN
        confidence = scores.get(best_intent, 0.0)

        # Boost confidence if entities support it
        if best_intent == IntentType.EXERCISE and "action" in entities and entities["action"] == "exercise":
            confidence = min(1.0, confidence + 0.2)

        if confidence < 0.15:
            best_intent = IntentType.LEARN

        return Intent(
            type=best_intent,
            confidence=min(1.0, confidence),
            entities=entities,
            raw_tokens=text.split(),
            primary_subject=entities.get("subject"),
            educational_level=entities.get("level"),
            action_type=entities.get("action"),
        )


class ContextAnalyzer:
    """Analyze multi-turn conversation context."""

    @staticmethod
    def extract_context(messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extract context from message history."""
        context = {
            "turn_count": len(messages),
            "last_user_message": "",
            "conversation_topic": None,
            "user_language": "french",
            "user_level": None,
            "mentioned_subjects": [],
            "conversation_history_summary": "",
        }

        # Find last user message
        for msg in reversed(messages):
            if msg.get("role") == "user":
                context["last_user_message"] = msg.get("content", "").strip()
                break

        # Extract topics from entire conversation
        all_text = " ".join([m.get("content", "") for m in messages]).lower()
        entities = EntityExtractor.extract(all_text)

        context["user_level"] = entities.get("level")
        context["user_language"] = entities.get("language", "french")

        # Subject detection across multiple messages
        if "subject" in entities:
            context["mentioned_subjects"].append(entities["subject"])
            context["conversation_topic"] = entities["subject"]

        # Detect if user is repeating a question (indicates misunderstanding)
        user_messages = [m.get("content", "").lower() for m in messages if m.get("role") == "user"]
        if len(user_messages) >= 2:
            last_two = user_messages[-2:]
            similarity = sum(1 for word in last_two[0].split() if word in last_two[1]) / max(1, len(last_two[0].split()))
            if similarity > 0.6:
                context["user_confused"] = True

        return context


class NLUEngine:
    """Main NLU Engine: orchestrates intent, entity, and context analysis."""

    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.intent_classifier = IntentClassifier()
        self.context_analyzer = ContextAnalyzer()

    def analyze(self, text: str, messages: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Full NLU pipeline: extract → classify → contextualize."""
        # 1. Entity extraction
        entities = self.entity_extractor.extract(text)

        # 2. Intent classification
        intent = self.intent_classifier.classify(text, entities)

        # 3. Context analysis (if message history available)
        context = {}
        if messages:
            context = self.context_analyzer.extract_context(messages + [{"role": "user", "content": text}])

        return {
            "intent": intent,
            "entities": entities,
            "context": context,
            "raw_text": text,
            "analysis_confidence": intent.confidence,
        }
