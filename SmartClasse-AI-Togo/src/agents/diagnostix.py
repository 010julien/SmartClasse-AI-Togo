"""DIAGNOSTIX: precise gap detection and retroactive remediation."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import ollama  # type: ignore
except ImportError:
    ollama = None

from src.llm import call_chat

from src.config import settings
from src.db import load_student_attempts, load_student_profile, load_student_progress

logger = logging.getLogger(__name__)


class DiagnostixAgent:
    """Detect the blocking prerequisite gap that prevents progress."""

    LEVEL_ORDER = ["cp1", "cp2", "ce1", "ce2", "cm1", "cm2"]

    def __init__(self):
        self.ollama_client = None

    def _ensure_ollama_client(self):
        if ollama is None or not settings.OLLAMA_BASE_URL:
            return None
        if self.ollama_client is None:
            self.ollama_client = ollama.Client(
                host=settings.OLLAMA_BASE_URL,
                timeout=min(settings.OLLAMA_TIMEOUT, 5),
            )
        return self.ollama_client

    def _safe_json_loads(self, content: str) -> Optional[Dict[str, Any]]:
        text = content.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if "\n" in text:
                text = text.split("\n", 1)[1]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None

    def _level_index(self, level: Optional[str]) -> int:
        if not level:
            return 1
        lowered = level.lower()
        for index, item in enumerate(self.LEVEL_ORDER):
            if item == lowered:
                return index
        return 1

    def _infer_level_from_score(self, score: float) -> str:
        if score >= 0.85:
            return "cm1"
        if score >= 0.65:
            return "ce2"
        if score >= 0.40:
            return "ce1"
        if score >= 0.20:
            return "cp2"
        return "cp1"

    def _score_by_subject(self, attempts: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        if not attempts:
            return {}

        grouped: Dict[str, List[bool]] = {}
        for attempt in attempts:
            subject = (attempt.get("subject") or attempt.get("skill") or "math").lower()
            grouped.setdefault(subject, []).append(bool(attempt.get("is_correct", False)))

        scores: Dict[str, Dict[str, Any]] = {}
        for subject, answers in grouped.items():
            score = sum(1 for answer in answers if answer) / len(answers)
            scores[subject] = {
                "success_rate": round(score, 2),
                "level": self._infer_level_from_score(score),
                "attempts": len(answers),
            }
        return scores

    def _build_prompt(
        self,
        student_name: str,
        overall_level: str,
        blocking_gap: Dict[str, Any],
        language: str,
    ) -> str:
        return f"""
You are DIAGNOSTIX, an expert in learning gap detection for Togolese students.

Student: {student_name}
Current level: {overall_level}
Language: {language}
Blocking gap: {blocking_gap}

Return ONLY valid JSON with:
- teacher_message: short sentence in {language}
- blocking_gap: precise blocking skill and level
- retroactive_level: prerequisite level to revisit
- retroactive_exercise: one short exercise using sorghum, karité or market context
- next_action: concrete intervention for the teacher
""".strip()

    def _fallback_response(
        self,
        student_name: str,
        overall_level: str,
        blocking_gap: Dict[str, Any],
        language: str,
    ) -> Dict[str, Any]:
        retro_level = blocking_gap.get("retroactive_level", "ce1")
        skill = blocking_gap.get("skill", "math")
        focus = blocking_gap.get("focus", "fractions")
        teacher_message = (
            f"{student_name} bloque en {overall_level.upper()} car une lacune {retro_level.upper()} n'est pas encore comblée sur {focus}."
        )
        return {
            "teacher_message": teacher_message,
            "blocking_gap": blocking_gap,
            "retroactive_level": retro_level,
            "retroactive_exercise": {
                "title": f"Rattrapage {focus}",
                "instruction": "Reviens sur la base avant de continuer.",
                "problem": f"{student_name} partage 8 sacs de sorgho. S'il en garde 3, combien partent au marché ?",
                "options": ["A: 3", "B: 5", "C: 6", "D: 8"],
                "correct_answer": "B",
                "explanation": "Il reste 5 sacs pour le marché, donc la base doit être reprise avant le niveau actuel.",
                "cultural_context": "sorgho, marché, famille",
                "difficulty": retro_level,
            },
            "next_action": f"Faire une remédiation ciblée de niveau {retro_level.upper()} sur {focus}.",
            "language": language,
            "skill": skill,
        }

    def analyze_student(
        self,
        student_id: str,
        student_name: Optional[str] = None,
        level: Optional[str] = None,
        language: str = "french",
    ) -> Dict[str, Any]:
        if not student_id:
            raise ValueError("student_id is required")

        progress = load_student_progress(student_id)
        profile = progress.get("profile") or load_student_profile(student_id) or {}
        attempts = load_student_attempts(student_id, limit=12)
        name = student_name or profile.get("student_name") or student_id

        competencies = profile.get("competencies") or {}
        overall_level = (level or competencies.get("overall", {}).get("level") or "ce1").lower()
        subject_scores = self._score_by_subject(attempts)

        if not attempts:
            neutral_gap = {
                "skill": "math",
                "current_level": overall_level,
                "retroactive_level": overall_level,
                "focus": "diagnostic_initial",
                "reason": "Aucune réponse enregistrée pour le moment. Le premier diagnostic servira de point de départ.",
                "success_rate": 0.0,
            }
            fallback = self._fallback_response(name, overall_level, neutral_gap, language)
            fallback.update(
                {
                    "student_id": student_id,
                    "student_name": name,
                    "created_at": datetime.utcnow().isoformat(),
                    "progress": progress,
                    "recent_attempts": attempts[:5],
                    "subject_scores": subject_scores,
                    "note": "insufficient_history_for_precise_gap_detection",
                }
            )
            return fallback

        weakest_subject = None
        weakest_score = 1.0
        for subject, score_data in subject_scores.items():
            if score_data["success_rate"] < weakest_score:
                weakest_subject = subject
                weakest_score = score_data["success_rate"]

        weakest_level = subject_scores.get(weakest_subject, {}).get("level", "ce1") if weakest_subject else "ce1"
        retroactive_index = min(self._level_index(weakest_level), self._level_index(overall_level) - 1)
        retroactive_index = max(0, retroactive_index)
        retroactive_level = self.LEVEL_ORDER[retroactive_index] if self.LEVEL_ORDER else "ce1"

        blocking_gap = {
            "skill": weakest_subject or "math",
            "current_level": overall_level,
            "retroactive_level": retroactive_level,
            "focus": "fractions" if weakest_subject == "math" else weakest_subject or "math",
            "reason": f"Le niveau moyen de {weakest_subject or 'la compétence'} reste inférieur au niveau actuel.",
            "success_rate": round(weakest_score, 2),
        }

        prompt = self._build_prompt(name, overall_level, blocking_gap, language)
        try:
            messages = build_messages(
                agent_name="DIAGNOSTIX",
                role_description="Expert in learning gap detection for Togolese students.",
                user_prompt=prompt,
                require_json=True,
            )
            response = call_chat(messages=messages, model=settings.LLM_MODEL, temperature=settings.LLM_TEMPERATURE, retries=1)
            content = response.get("message", {}).get("content", "")
            parsed = extract_json(content) or self._safe_json_loads(content)
            if parsed:
                parsed.setdefault("blocking_gap", blocking_gap)
                parsed.setdefault("retroactive_level", retroactive_level)
                parsed.setdefault("student_id", student_id)
                parsed.setdefault("student_name", name)
                parsed.setdefault("created_at", datetime.utcnow().isoformat())
                return parsed
        except Exception as exc:
            logger.warning(f"DIAGNOSTIX: Gemma call failed, using fallback | {exc}")

        fallback = self._fallback_response(name, overall_level, blocking_gap, language)
        fallback.update(
            {
                "student_id": student_id,
                "student_name": name,
                "created_at": datetime.utcnow().isoformat(),
                "progress": progress,
                "recent_attempts": attempts[:5],
                "subject_scores": subject_scores,
            }
        )
        return fallback
