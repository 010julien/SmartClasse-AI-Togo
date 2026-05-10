"""ORCHESTRATOR: central composer that aggregates agent contexts and calls Gemma 4.

Provides a single entrypoint to generate personalized exercises using all agents' knowledge.
"""
import logging
from typing import Any, Dict, Optional

from src.config import settings
from src.llm import call_chat
from src.prompting import build_messages, extract_json

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    def __init__(
        self,
        adaptix,
        linguix,
        kulturix,
        diagnostix,
        equitix,
        pilotix,
        parentix,
    ):
        self.adaptix = adaptix
        self.linguix = linguix
        self.kulturix = kulturix
        self.diagnostix = diagnostix
        self.equitix = equitix
        self.pilotix = pilotix
        self.parentix = parentix

    def compose_context(self, student_id: Optional[str], student_name: str, level: str, subject: str, topic: str, language: str) -> Dict[str, Any]:
        """Aggregate local context from multiple agents into a compact dict."""
        query = f"{topic} {subject} {language} {student_name}"
        kultur = self.kulturix.get_context_pack(query)

        progress = None
        try:
            progress = self.adaptix.get_student_progress(student_id) if student_id else {}
        except Exception:
            progress = {}

        diagnostix_analysis = {}
        try:
            diagnostix_analysis = self.diagnostix.analyze_student(student_id, student_name, level, language)
        except Exception:
            diagnostix_analysis = {}

        equitix_assessment = {}
        try:
            equitix_assessment = self.equitix.assess_dropout_risk(student_id, student_name, language)
        except Exception:
            equitix_assessment = {}

        return {
            "kulturix": kultur,
            "progress": progress or {},
            "diagnostix": diagnostix_analysis or {},
            "equitix": equitix_assessment or {},
        }

    def generate_personalized_exercise(self, student_id: Optional[str], student_name: str, level: str, subject: str, topic: str, language: str) -> Dict[str, Any]:
        """Compose a rich prompt using all contexts and call Gemma 4. Falls back to ADAPTIX."""
        context = self.compose_context(student_id, student_name, level, subject, topic, language)

        kultur_snippets = "\n".join([f"- {e['example']}" for e in context.get("kulturix", {}).get("examples", [])])
        progress_summary = context.get("progress", {})
        diag = context.get("diagnostix", {})
        risk = context.get("equitix", {})

        user_prompt = f"""
Generate one personalized exercise for {student_name} (level: {level}) in {language}.

CONTEXT SUMMARY:
- Topic: {topic}
- Subject: {subject}
- KULTURIX:
{kultur_snippets}
- Student progress: {progress_summary}
- Diagnostix summary: {diag}
- Risk signals: {risk}

REQUIREMENTS:
1) Be culturally grounded using KULTURIX examples.
2) Provide a clear question, multiple-choice options, correct answer and explanation.
3) Output ONLY valid JSON with keys: exercise_id, title, instruction, problem, options, correct_answer, explanation, cultural_context, difficulty, estimated_time_minutes

Return only JSON.
""".strip()

        try:
            messages = build_messages(
                agent_name="ORCHESTRATOR",
                role_description="Compose contexts and ask Gemma 4 to generate a personalized educational exercise.",
                user_prompt=user_prompt,
                require_json=True,
            )
            resp = call_chat(messages=messages, model=settings.LLM_MODEL, temperature=0.0, retries=2)
            content = resp.get("message", {}).get("content", "")
            parsed = extract_json(content)
            if parsed:
                return parsed
            logger.warning("ORCHESTRATOR: Gemma returned non-JSON, falling back to ADAPTIX")
        except Exception as exc:
            logger.warning(f"ORCHESTRATOR: Gemma call failed, fallback to ADAPTIX | {exc}")

        # Fallback
        try:
            return self.adaptix.generate_exercise(student_name, level, subject, topic, language)
        except Exception:
            return self.adaptix._fallback_exercise(student_name, level, subject, topic, language, "local context")
