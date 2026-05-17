"""Conversation Manager: Orchestrates NLU, Reasoning, Memory, and Quality Validation."""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from src.advanced.nlu_engine import NLUEngine, IntentType
from src.advanced.reasoning_engine import ReasoningEngine
from src.advanced.memory_manager import MemoryManager
from src.advanced.quality_validator import QualityValidator
from src.advanced.prompts import AdvancedPromptEngineering
from src.llm import call_chat

logger = logging.getLogger(__name__)


@dataclass
class ConversationResponse:
    """Complete response with metadata."""
    message: str
    intent: str
    confidence: float
    reasoning_chain: Optional[Dict[str, Any]] = None
    quality_score: Optional[float] = None
    reasoning_time_ms: float = 0.0
    total_time_ms: float = 0.0
    used_regeneration: bool = False
    memory_context: Optional[Dict[str, Any]] = None


class ConversationManager:
    """Premium conversation orchestrator combining all advanced components."""

    def __init__(self):
        self.nlu_engine = NLUEngine()
        self.reasoning_engine = ReasoningEngine()
        self.memory_manager = MemoryManager()
        self.quality_validator = QualityValidator()
        self.prompt_engineer = AdvancedPromptEngineering()

        logger.info("ConversationManager initialized with premium components")

    def process_conversation(
        self,
        session_id: str,
        user_id: str,
        user_name: str,
        messages: List[Dict[str, str]],
        language: str = "french",
        user_level: str = "CE1",
        max_retries_on_quality: int = 0,
    ) -> ConversationResponse:
        """Process a conversation turn with full pipeline."""

        total_start = time.time()

        # Get the latest user message
        last_user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "").strip()
                break

        if not last_user_message:
            return ConversationResponse(
                message="Je n'ai pas reçu de message valide.",
                intent="unknown",
                confidence=0.0,
                total_time_ms=(time.time() - total_start) * 1000,
            )

        logger.info(f"Processing: {user_name} | Level: {user_level} | Message: {last_user_message[:50]}...")

        # ============= PHASE 1: MEMORY INITIALIZATION =============
        session_init = self.memory_manager.initialize_session(session_id, user_id, user_name)
        user_profile = session_init["user_profile"]

        # ============= PHASE 2: NLU ANALYSIS =============
        nlu_result = self.nlu_engine.analyze(last_user_message, messages)
        intent = nlu_result["intent"]
        entities = nlu_result["entities"]
        nlu_confidence = nlu_result["analysis_confidence"]

        logger.info(f"NLU Result: {intent.type.value} (confidence: {nlu_confidence:.2f})")

        # ============= PHASE 3: REASONING PIPELINE =============
        reasoning_start = time.time()
        reasoning_chain = self.reasoning_engine.reason(
            problem=last_user_message,
            problem_type=intent.type.value,
            context={"educational_level": user_level, "language": language},
        )
        reasoning_time_ms = (time.time() - reasoning_start) * 1000

        logger.info(f"Reasoning: {len(reasoning_chain.steps)} steps | Time: {reasoning_time_ms:.1f}ms")

        # ============= PHASE 4: GET CONTEXT FOR RESPONSE =============
        memory_context = self.memory_manager.get_context_for_response(session_id, user_id)
        user_context = memory_context.get("user", {})
        user_context.update({
            "user_name": user_name,
            "educational_level": user_level,
            "preferred_language": language,
        })

        # ============= PHASE 5: BUILD SOPHISTICATED PROMPT =============
        system_prompt = self.prompt_engineer.build_system_prompt(intent, user_context, memory_context.get("conversation"))

        # Build user message with context
        user_message_with_context = self.prompt_engineer.build_user_message_with_context(
            last_user_message,
            intent,
            user_context,
            memory_context.get("conversation_summary"),
        )

        # ============= PHASE 6: CALL LLM WITH RETRIES FOR QUALITY =============
        response_text = None
        final_quality_score = 0.0
        used_regeneration = False

        for attempt in range(max_retries_on_quality + 1):
            logger.info(f"LLM call attempt {attempt + 1}/{max_retries_on_quality + 1}")

            try:
                # Build messages for LLM
                llm_messages = [
                    {"role": "system", "content": system_prompt},
                    *messages[:-1],  # Previous conversation (exclude current user message as it's in context)
                    {"role": "user", "content": user_message_with_context},
                ]

                response = call_chat(
                    messages=llm_messages,
                    model=None,  # Use default from config
                    temperature=0.3,  # Moderate temperature for consistency
                    max_tokens=256,
                    retries=2,
                )

                response_text = response.get("message", {}).get("content", "").strip()

                if not response_text:
                    logger.warning("Empty response from LLM")
                    continue

                # ============= PHASE 7: QUALITY VALIDATION =============
                quality_result = self.quality_validator.validate(
                    response=response_text,
                    original_question=last_user_message,
                    user_level=user_level,
                    context={"intent": intent.type.value},
                )

                final_quality_score = quality_result.overall_score

                logger.info(f"Quality Score: {final_quality_score:.1f}/100 | Passes: {quality_result.passes_threshold}")

                if quality_result.passes_threshold:
                    logger.info("✓ Response passed quality check")
                    break  # Exit retry loop
                else:
                    logger.warning(f"✗ Quality issues: {quality_result.issues[:2]}")
                    if attempt < max_retries_on_quality:
                        # Build regeneration prompt
                        regen_prompt = f"""La réponse précédente n'a pas atteint la qualité requise.
Issues: {', '.join(quality_result.issues[:2])}
Recommendations: {', '.join(quality_result.recommendations[:2])}

Génère une meilleure réponse qui :
- Adresse directement la question
- Est plus claire et engageante
- Inclut des exemples locaux
- Est adaptée au niveau {user_level}

Question originale: {last_user_message}"""

                        llm_messages[-1] = {"role": "user", "content": regen_prompt}
                        used_regeneration = True
                        continue  # Retry with regeneration

            except Exception as exc:
                logger.error(f"LLM error on attempt {attempt + 1}: {exc}")
                if attempt == max_retries_on_quality:
                    response_text = self._get_fallback_response(intent.type, last_user_message, user_level)
                continue

        if not response_text:
            response_text = self._get_fallback_response(intent.type, last_user_message, user_level)

        # ============= PHASE 8: MEMORY UPDATE =============
        self.memory_manager.add_turn(session_id, user_id, last_user_message, response_text)

        # Update user profile based on interaction
        self._update_user_profile(user_id, intent.type, entities, success=True)

        # ============= PHASE 9: PACKAGE RESPONSE =============
        total_time_ms = (time.time() - total_start) * 1000

        response = ConversationResponse(
            message=response_text,
            intent=intent.type.value,
            confidence=nlu_confidence,
            reasoning_chain={
                "steps": len(reasoning_chain.steps),
                "problem_type": reasoning_chain.problem_type,
                "confidence": reasoning_chain.reasoning_confidence,
                "time_ms": reasoning_time_ms,
            },
            quality_score=final_quality_score,
            reasoning_time_ms=reasoning_time_ms,
            total_time_ms=total_time_ms,
            used_regeneration=used_regeneration,
            memory_context={
                "session_id": session_id,
                "turn_count": memory_context.get("conversation", {}).get("message_count", 1),
            },
        )

        logger.info(f"Response complete | Total: {total_time_ms:.0f}ms | Quality: {final_quality_score:.1f}")

        return response

    def _update_user_profile(self, user_id: str, intent_type: IntentType, entities: Dict, success: bool) -> None:
        """Update user profile based on interaction."""
        subject = entities.get("subject", "general")
        interaction_type = intent_type.value

        # Record the interaction
        self.memory_manager.user_profiles.record_interaction(
            user_id,
            subject=subject,
            interaction_type=interaction_type,
            success=success,
        )

        # Could add more logic for misconception detection, etc.

    @staticmethod
    def _get_fallback_response(intent_type: IntentType, question: str, level: str) -> str:
        """Fallback response when LLM unavailable."""

        if intent_type == IntentType.EXPLAIN:
            return f"""Je comprends que tu veux une explication. 

En {level}, voici l'idée principale:
- Les concepts s'apprennent pas à pas
- Utilise toujours des exemples concrets
- Demande à ton enseignant pour plus de détails

Peux-tu me donner plus de détails sur ce que tu veux savoir?"""

        elif intent_type == IntentType.EXERCISE:
            return f"""Voici un exercice pour toi:

Énoncé: À partir de ce que tu viens d'apprendre, comment appliquerais-tu ce concept?

Conseil: Prends ton temps, écris tes étapes, et vérifie ton travail.

Besoin d'aide? Dis-moi!"""

        elif intent_type == IntentType.SOCIALIZE:
            return f"""Bonjour! 👋

Je suis heureux(euse) de te voir! Comment ça va?

Je peux t'aider avec:
- Des explications en classe
- Des exercices à pratiquer  
- Des corrections détaillées

Qu'est-ce que tu veux faire aujourd'hui?"""

        else:
            return f"""Salut {level}! 

Je suis ici pour t'aider à apprendre et à progresser.

Que puis-je faire pour toi?
- Expliquer un concept
- Proposer un exercice
- Corriger ton travail"""
