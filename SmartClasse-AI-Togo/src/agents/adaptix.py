# src/agents/adaptix.py
# ADAPTIX: Personal Adaptive Tutor Agent

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import ollama  # type: ignore
except ImportError:
    ollama = None

from src.config import settings
from src.db import (
    init_db,
    load_student_attempts,
    load_student_profile,
    load_student_progress,
    record_diagnostic_session,
    record_exercise_attempt,
    upsert_student_profile,
)
from src.agents.kulturix import KulturixAgent
from src.llm import call_chat
from src.prompting import build_messages, extract_json

logger = logging.getLogger(__name__)


class AdaptixAgent:
    """ADAPTIX: adaptive tutor for Togolese students."""

    def __init__(self):
        self.llm = None
        self.ollama_client = None
        self.student_profiles: Dict[str, Dict[str, Any]] = {}
        self.exercise_history: Dict[str, List[Dict[str, Any]]] = {}
        self.cultural_context = self._load_cultural_corpus()
        self.kulturix = KulturixAgent()

        init_db()
        logger.info("ADAPTIX Agent initialized")

    def _load_cultural_corpus(self) -> Dict:
        return {
            "kabyie": {
                "math": {
                    "fractions": "sorgho (mil), karité, partage récolte",
                    "multiplication": "groupes de 10 (dénombrement)",
                    "geometry": "grenier (banco), toit rond",
                    "counting": "sacs de sorgho au marché",
                    "logic": "paniers de récolte et séquences",
                },
                "french": {"reading": "marché, famille, commerce"},
            },
            "ewe": {
                "math": {
                    "fractions": "noix de coco, huile de palme",
                    "counting": "marché, paniers, récolte",
                    "logic": "ordre des paniers et des fruits",
                }
            },
            "haoussa": {"math": {"commerce": "échange au marché, prix"}},
            "mina": {"math": {"fractions": "huile de palme et partage"}},
            "tem": {"math": {"fractions": "sorgho, marché, partage"}},
            "french": {"math": {"reading": "marché, famille, commerce"}},
        }

    def _ensure_ollama_client(self):
        if ollama is None or not settings.OLLAMA_BASE_URL:
            return None

        if self.ollama_client is None:
            # Keep ADAPTIX responsive even when the local model is slow.
            request_timeout = min(settings.OLLAMA_TIMEOUT, 5)
            self.ollama_client = ollama.Client(host=settings.OLLAMA_BASE_URL, timeout=request_timeout)

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

    def _fallback_exercise(
        self,
        student_name: str,
        level: str,
        subject: str,
        topic: str,
        language: str,
        cultural_ref: str,
    ) -> Dict[str, Any]:
        exercise_id = f"ex_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if topic == "fractions":
            return {
                "exercise_id": exercise_id,
                "title": "Fractions avec le sorgho",
                "instruction": "Résous ce problème en partageant le sorgho",
                "problem": f"{student_name} a récolté 8 sacs de sorgho. Il en garde 3 pour la famille. Quelle fraction va au marché ?",
                "options": ["A: 3/8", "B: 5/8", "C: 2/8", "D: 8/8"],
                "correct_answer": "B",
                "explanation": "Si 3 sacs restent à la maison, alors 8-3=5 sacs vont au marché. Donc 5/8 du sorgho.",
                "cultural_context": cultural_ref or "sorgho, récolte, marché",
                "difficulty": "intermediate",
                "estimated_time_minutes": 5,
            }

        return {
            "exercise_id": exercise_id,
            "title": f"Exercice de {topic}",
            "instruction": f"Résous cet exercice de {topic} en contexte local",
            "problem": f"{student_name} travaille au niveau {level} en {subject}.",
            "options": ["A: 1", "B: 2", "C: 3", "D: 4"],
            "correct_answer": "A",
            "explanation": f"Exemple contextualisé pour {language} avec {cultural_ref or 'le contexte local'}.",
            "cultural_context": cultural_ref,
            "difficulty": "intermediate",
            "estimated_time_minutes": 5,
        }

    def _build_generation_prompt(
        self,
        student_name: str,
        level: str,
        subject: str,
        topic: str,
        language: str,
        cultural_ref: str,
    ) -> str:
        lang_map = {
            "kabyie": "kabiyè",
            "ewe": "ewe",
            "haoussa": "haoussa",
            "mina": "mina",
            "tem": "tem",
            "french": "français",
        }

        target_lang = lang_map.get(language, "français")
        kulturix_context = self.kulturix.enrich_prompt(
            base_prompt=f"Cultural starting point for the exercise: {cultural_ref}",
            query=f"{student_name} {level} {subject} {topic} {language} {cultural_ref}",
            limit=3,
        )

        return f"""
You are ADAPTIX, an adaptive tutoring agent for Togolese students.
Generate a personalized exercise for {student_name}.

CONTEXT:
- Official Level: {level}
- Subject: {subject}
- Topic: {topic}
- Student Language: {target_lang}
- Cultural Reference: {cultural_ref}
- KULTURIX Context:
{kulturix_context}
- Difficulty: intermediate

REQUIREMENTS:
1. Write the exercise in {target_lang}
2. Use the cultural reference to make it relatable (sorghum, market, family, karité)
3. Include a clear question, answer options and explanation
4. Make it appropriate for a 9-12 year old child in rural Togo

OUTPUT FORMAT:
{{
  "exercise_id": "ex_{{timestamp}}",
  "title": "...",
  "instruction": "...",
  "problem": "...",
  "options": ["A: ...", "B: ...", "C: ...", "D: ..."],
  "correct_answer": "A",
  "explanation": "...",
  "cultural_context": "{cultural_ref}",
  "difficulty": "intermediate",
  "estimated_time_minutes": 5
}}

Return only JSON.
""".strip()

    def _build_diagnostic_prompt(
        self,
        student_name: str,
        level: str,
        subject: str,
        topic: str,
        language: str,
        cultural_ref: str,
    ) -> str:
        return f"""
You are ADAPTIX, an adaptive tutoring agent for Togolese students.
Generate one diagnostic exercise for {student_name}.

CONTEXT:
- Official Level: {level}
- Subject: {subject}
- Topic: {topic}
- Student Language: {language}
- Cultural Reference: {cultural_ref}
- KULTURIX Context:
{self.kulturix.enrich_prompt(cultural_ref, f'{student_name} {level} {subject} {topic} {language}', limit=3)}
- Difficulty: diagnostic

REQUIREMENTS:
1. Use simple language for a child in rural Togo.
2. Include sorghum, karité, market, family, or farming examples when appropriate.
3. Return exactly one JSON object.

OUTPUT FORMAT:
{{
  "exercise_id": "ex_{{timestamp}}",
  "title": "...",
  "instruction": "...",
  "problem": "...",
  "options": ["A: ...", "B: ...", "C: ...", "D: ..."],
  "correct_answer": "A",
  "explanation": "...",
  "cultural_context": "...",
  "difficulty": "diagnostic",
  "estimated_time_minutes": 3
}}

Return only JSON.
""".strip()

    def _call_gemma4(self, prompt: str, fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            messages = build_messages(
                agent_name="ADAPTIX",
                role_description="Adaptive tutoring agent for Togolese students.",
                user_prompt=prompt,
                require_json=True,
            )
            response = call_chat(messages=messages, model=settings.LLM_MODEL, temperature=settings.LLM_TEMPERATURE, retries=2)
            content = response.get("message", {}).get("content", "")
            parsed = extract_json(content) or self._safe_json_loads(content)
            if parsed is not None:
                parsed.setdefault("exercise_id", f"ex_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                return parsed
            logger.warning("ADAPTIX: Gemma 4 returned non-JSON content, using fallback")
        except Exception as exc:
            logger.warning(f"ADAPTIX: Gemma 4 call failed, using fallback | {exc}")

        if fallback is not None:
            return fallback

        return self._fallback_exercise("Student", "CE1", "math", "fractions", "french", "sorghum, market, family")

    def _analyze_responses(self, responses: list) -> Dict[str, Any]:
        if not responses:
            return {
                "math": {"level": "ce1", "confidence": 0.50},
                "french": {"level": "ce1", "confidence": 0.50},
                "logic": {"level": "cp2", "confidence": 0.50},
                "reading": {"level": "ce1", "confidence": 0.50},
                "overall": {"level": "ce1", "confidence": 0.50},
            }

        grouped: Dict[str, List[bool]] = {}
        for response in responses:
            if not isinstance(response, dict):
                continue
            skill = response.get("skill") or response.get("subject") or "math"
            grouped.setdefault(skill, []).append(bool(response.get("is_correct", False)))

        def score_to_level(score: float) -> str:
            if score >= 0.85:
                return "cm1"
            if score >= 0.65:
                return "ce2"
            if score >= 0.40:
                return "ce1"
            return "cp2"

        analysis: Dict[str, Any] = {}
        scores: List[float] = []
        for skill, answers in grouped.items():
            score = sum(1 for answer in answers if answer) / len(answers)
            scores.append(score)
            analysis[skill] = {"level": score_to_level(score), "confidence": round(score, 2)}

        overall_score = sum(scores) / len(scores) if scores else 0.0
        analysis["overall"] = {"level": score_to_level(overall_score), "confidence": round(overall_score, 2)}
        return analysis

    def build_student_profile(self, student_id: str, responses: list) -> Dict:
        profile = {
            "student_id": student_id,
            "created_at": datetime.now().isoformat(),
            "diagnostic_responses": responses,
            "competencies": self._analyze_responses(responses),
            "language_level": "beginner",
            "learning_style": "visual",
            "cultural_context": "default",
        }
        self.student_profiles[student_id] = profile
        upsert_student_profile(profile)
        record_diagnostic_session(student_id, responses, profile["competencies"])
        return profile

    def generate_diagnostic_exercises(self, student_name: str, level: str, language: str = "french") -> List[Dict[str, Any]]:
        diagnostic_specs = [
            ("math", "counting", "sorghum baskets"),
            ("math", "fractions", "karité sharing"),
            ("math", "multiplication", "market baskets"),
            ("french", "reading", "family at the market"),
            ("logic", "patterns", "farm sequences"),
        ]

        exercises: List[Dict[str, Any]] = []
        for index, (subject, topic, cultural_ref) in enumerate(diagnostic_specs, start=1):
            prompt = self._build_diagnostic_prompt(student_name, level, subject, topic, language, cultural_ref)
            fallback = self._fallback_exercise(student_name, level, subject, topic, language, cultural_ref)
            exercise = self._call_gemma4(prompt, fallback=fallback)
            exercise.setdefault("diagnostic_index", index)
            exercise.setdefault("subject", subject)
            exercise.setdefault("topic", topic)
            exercises.append(exercise)

        return exercises

    def generate_exercise(
        self,
        student_name: str,
        level: str,
        subject: str,
        topic: str,
        language: str = "french",
    ) -> Dict[str, Any]:
        logger.info(f"ADAPTIX: Generating exercise for {student_name} | {subject}/{topic} | {language}")
        cultural_ref = self.cultural_context.get(language, {}).get(subject, {}).get(topic, "")
        prompt = self._build_generation_prompt(student_name, level, subject, topic, language, cultural_ref)
        fallback = self._fallback_exercise(student_name, level, subject, topic, language, cultural_ref)
        return self._call_gemma4(prompt, fallback=fallback)

    def evaluate_response(self, student_id: str, exercise_id: str, response: str, is_correct: bool) -> Dict[str, Any]:
        if student_id not in self.student_profiles:
            persisted = load_student_profile(student_id)
            if persisted is None:
                raise ValueError(f"Student {student_id} not found")
            self.student_profiles[student_id] = persisted

        profile = self.student_profiles[student_id]

        if student_id not in self.exercise_history:
            self.exercise_history[student_id] = []

        history_entry = {
            "exercise_id": exercise_id,
            "response": response,
            "correct": is_correct,
            "timestamp": datetime.now().isoformat(),
        }
        self.exercise_history[student_id].append(history_entry)
        record_exercise_attempt(student_id, exercise_id, response, is_correct)

        if is_correct:
            profile["last_correct_score"] = profile.get("last_correct_score", 0) + 1
        else:
            profile["last_error_score"] = profile.get("last_error_score", 0) + 1

        upsert_student_profile(profile)

        next_exercise_recommendation = "continue_current_level"
        if profile.get("last_correct_score", 0) >= 3:
            next_exercise_recommendation = "increase_difficulty"
        elif profile.get("last_error_score", 0) >= 2:
            next_exercise_recommendation = "review_prerequisite"

        return {
            "status": "evaluated",
            "is_correct": is_correct,
            "profile_updated": True,
            "next_recommendation": next_exercise_recommendation,
            "student_progress": {
                "correct_count": profile.get("last_correct_score", 0),
                "error_count": profile.get("last_error_score", 0),
            },
        }

    def get_student_progress(self, student_id: str) -> Dict[str, Any]:
        return load_student_progress(student_id)
