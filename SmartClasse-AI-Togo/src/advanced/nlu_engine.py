"""Advanced NLU Engine: Intent Detection, Entity Extraction, Context Analysis."""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple, TYPE_CHECKING
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
        "math": [
            # French
            "math", "mathematic", "fraction", "geometrie", "calcul", "addition",
            "soustraction", "multiplication", "division", "nombre", "chiffre",
            # Kabiyè
            "nɔmɔɔrɩ", "kɔlɩ", "pɩsɩ",
            # Ewe
            "nambala", "kɔnta", "susu",
        ],
        "french": [
            # French
            "francais", "french", "grammaire", "conjugaison", "orthographe",
            "vocabulaire", "lecture", "phrase", "mot", "dictée",
            # Kabiyè
            "fransɩɩ", "yɔɔdɩyɛ",
            # Ewe
            "gɔme", "xó",
        ],
        "history": [
            # French
            "histoire", "history", "civilisation", "geographie", "culture",
            "continent", "pays", "roi", "epoque",
            # Kabiyè
            "pɩyalɩ", "tɛtɛ",
            # Ewe
            "hisɔti", "gbe",
        ],
        "science": [
            # French
            "science", "physique", "chimie", "biologie", "nature", "plante",
            "animal", "corps", "sante", "vie",
            # Kabiyè
            "sɛkɛlɛnsi", "mbʊ",
            # Ewe
            "siaense", "dzidzime",
        ],
        "civic": [
            # French
            "civique", "civic", "droits", "devoir", "citoyen", "loi",
            "republique", "vote", "liberte",
            # Kabiyè
            "sɩɣtʊʊ", "ɛjaɣdɩ",
        ],
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
    """
    Classify user intent using a two-tier strategy:
      1. LLM-based classification (Gemma via Ollama) — language-agnostic,
         works with French, Kabiyè, Ewe, code-switching and any mixture.
      2. Multilingual keyword fallback — instant, no LLM required.
    """

    # ── Multilingual keyword bank (French + Kabiyè + Ewe + Haoussa basics) ───
    KEYWORDS: Dict[IntentType, List[str]] = {
        IntentType.EXPLAIN: [
            # French
            "explique", "comment", "c'est quoi", "c est quoi", "definition",
            "aide moi comprendre", "pourquoi", "exemple", "clarifier", "qu'est-ce",
            # Kabiyè
            "ɛzɩma", "pʊ", "lɛ", "wɩlɩʊ",
            # Ewe
            "alesi", "wòafia", "nye", "ŋutinya",
            # English
            "what is", "explain", "why", "how does",
        ],
        IntentType.EXERCISE: [
            # French
            "exercice", "exo", "probleme", "test", "donnez", "donne moi",
            "propose", "test moi", "verifier", "entrainer", "pratiquer",
            # Kabiyè
            "tɔm", "ɛsɩ", "kɔm",
            # Ewe
            "tɔm", "gbɔ", "mia wɔ",
            # English
            "exercise", "practice", "problem", "give me",
        ],
        IntentType.CORRECT: [
            # French
            "corriger", "correction", "corrige", "juste", "faux", "verifier",
            "est-ce que c'est", "ai-je raison",
            # English
            "correct", "check", "is this right", "verify",
        ],
        IntentType.TRANSLATE: [
            # French
            "traduction", "traduit", "traduire", "en kabiye", "en ewe",
            "comment dit-on", "comment on dit",
            # English
            "translate", "in kabyie", "in ewe",
            # Kabiyè/Ewe
            "yɔɔdɩyɛ", "gblɔ",
        ],
        IntentType.LEARN: [
            # French
            "apprendre", "enseigner", "lecon", "cours", "comprendre", "etudier",
            "je veux savoir", "montre moi",
            # English
            "learn", "study", "teach me", "show me",
            # Kabiyè
            "wɩlɩɣ", "nɩɩ",
        ],
        IntentType.EVALUATE: [
            "evaluer", "evaluation", "score", "progress", "resultat",
            "performance", "mon niveau", "bilan", "résultat",
        ],
        IntentType.SOCIALIZE: [
            # French
            "bonjour", "bonsoir", "ça va", "comment ca va", "salut",
            "merci", "au revoir", "super", "bravo",
            # Kabiyè
            "waaléwi", "yiyaɖi", "mbʊ",
            # Ewe
            "woezɔ", "akpe", "ŋdi",
            # Ewe/Mina
            "bonsua",
            # English
            "hello", "hi", "thanks", "bye",
        ],
        IntentType.CLARIFY: [
            "je ne comprends", "pas clair", "plus simple", "encore",
            "répète", "reformule", "rephrase", "je suis perdu",
        ],
        IntentType.HELP: [
            "aide", "help", "assistance", "support", "stuck",
            "bloqué", "je ne sais pas", "j'ai besoin",
        ],
    }

    # ── LLM-based classification ─────────────────────────────────────────────

    @staticmethod
    def _classify_with_llm(text: str) -> Optional[Tuple[IntentType, float]]:
        """
        Call Gemma to classify intent. Language-agnostic — works in French,
        Kabiyè, Ewe, and code-switching. Returns (IntentType, confidence) or
        None if the LLM is unavailable or the response cannot be parsed.
        """
        try:
            import json as _json
            from src.llm import call_chat  # lazy import — avoids circular deps

            prompt = (
                "Tu es un classificateur d'intention pour un tuteur éducatif au Togo.\n"
                "Classifie ce message en UN des codes suivants:\n"
                "  explain   — demande d'explication ou de définition\n"
                "  exercise  — demande d'exercice ou de problème\n"
                "  correct   — demande de correction d'une réponse\n"
                "  translate — demande de traduction\n"
                "  learn     — apprentissage général d'un concept\n"
                "  socialize — salutation ou conversation sociale\n"
                "  clarify   — demande de reformulation\n"
                "  help      — demande d'aide générale\n\n"
                f"Message (peut être en français, kabiyè, ewe ou mélangé): \"{text}\"\n\n"
                'Réponds UNIQUEMENT en JSON: {"intent": "...", "confidence": 0.0}'
            )

            response = call_chat(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=40,
            )
            raw = response.get("message", {}).get("content", "").strip()

            # Strip markdown fences if present
            raw = re.sub(r"^```json\s*|^```\s*|```$", "", raw, flags=re.MULTILINE).strip()

            parsed = _json.loads(raw)
            intent_str = parsed.get("intent", "").strip().lower()
            confidence = float(parsed.get("confidence", 0.5))

            # Map string → IntentType
            mapping = {t.value: t for t in IntentType}
            intent_type = mapping.get(intent_str, IntentType.LEARN)
            return intent_type, min(1.0, max(0.0, confidence))

        except Exception as exc:
            logger.debug(f"LLM classification unavailable ({exc}), falling back to keywords")
            return None

    # ── Keyword-based classification (fallback) ──────────────────────────────

    @staticmethod
    def _keyword_classify(text: str, entities: Dict[str, Any]) -> Tuple[IntentType, float]:
        """Score-based keyword matching across all supported languages."""
        lowered = text.lower()
        scores: Dict[IntentType, float] = {}

        for intent_type, keywords in IntentClassifier.KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in lowered)
            # Normalize: raw count / sqrt(keywords) for length-invariant scoring
            scores[intent_type] = matches / max(1, len(keywords) ** 0.5)

        best_intent = max(scores, key=scores.get) if scores else IntentType.LEARN
        confidence = min(1.0, scores.get(best_intent, 0.0))

        # Entity-based boosts
        if best_intent == IntentType.EXERCISE and entities.get("action") == "exercise":
            confidence = min(1.0, confidence + 0.25)
        if best_intent == IntentType.EXPLAIN and entities.get("action") == "explain":
            confidence = min(1.0, confidence + 0.20)

        # Low-signal fallback
        if confidence < 0.05:
            best_intent = IntentType.LEARN
            confidence = 0.4

        return best_intent, confidence

    # ── Public API ───────────────────────────────────────────────────────────

    @staticmethod
    def classify(text: str, entities: Dict[str, Any]) -> Intent:
        """
        Two-tier classification:
          1. Try Gemma (language-agnostic, high accuracy)
          2. Fall back to multilingual keyword scoring
        """
        # Tier 1 — LLM
        llm_result = IntentClassifier._classify_with_llm(text)
        if llm_result is not None:
            best_intent, confidence = llm_result
        else:
            # Tier 2 — keywords
            best_intent, confidence = IntentClassifier._keyword_classify(text, entities)

        return Intent(
            type=best_intent,
            confidence=confidence,
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
