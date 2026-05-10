"""PILOTIX: real-time teacher dashboard and adaptive lesson suggestions."""

import hashlib
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    import ollama  # type: ignore
except ImportError:
    ollama = None

from src.llm import call_chat

from src.config import settings
from src.db import load_student_progress

logger = logging.getLogger(__name__)


class PilotixAgent:
    """Build a live view of class readiness and suggest the next lesson."""

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

    def _generate_audio(self, text: str, language: str = "french") -> Dict[str, Any]:
        try:
            import pyttsx3  # type: ignore

            audio_dir = os.path.join("data", "audio")
            os.makedirs(audio_dir, exist_ok=True)
            audio_name = f"pilotix_{hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]}.wav"
            audio_path = os.path.join(audio_dir, audio_name)

            engine = pyttsx3.init()
            engine.setProperty("rate", 155)
            engine.save_to_file(text, audio_path)
            engine.runAndWait()

            return {
                "audio_url": f"/audio/{audio_name}",
                "audio_path": audio_path,
                "language": language,
            }
        except Exception as exc:
            logger.warning(f"PILOTIX: audio generation unavailable | {exc}")
            return {"audio_url": None, "audio_path": None, "language": language}

    def _student_snapshot(self, student_id: str) -> Dict[str, Any]:
        progress = load_student_progress(student_id)
        profile = progress.get("profile") or {}
        stats = progress.get("statistics") or {}

        success_rate = float(stats.get("success_rate_percent", 0.0))
        total = int(stats.get("total_exercises", 0))
        activity_factor = min(total / 10.0, 1.0)
        readiness = round(min(100.0, success_rate * 0.8 + activity_factor * 20.0), 2)

        competencies = profile.get("competencies") or {}
        weakest_skill = None
        weakest_score = 1.0
        for skill, payload in competencies.items():
            if skill == "overall" or not isinstance(payload, dict):
                continue
            score = float(payload.get("confidence", 1.0))
            if score < weakest_score:
                weakest_score = score
                weakest_skill = skill

        if readiness >= 75:
            state = "ready"
            color = "green"
        elif readiness >= 50:
            state = "watch"
            color = "amber"
        else:
            state = "support"
            color = "red"

        return {
            "student_id": student_id,
            "student_name": profile.get("student_name") or student_id,
            "readiness_score": readiness,
            "success_rate_percent": round(success_rate, 2),
            "state": state,
            "color": color,
            "weakest_skill": weakest_skill or "math",
            "recent_exercises": total,
            "language": profile.get("language", "french"),
        }

    def _build_prompt(self, teacher_name: str, class_name: str, snapshot: List[Dict[str, Any]], language: str) -> str:
        ready_count = sum(1 for item in snapshot if item["state"] == "ready")
        support_count = sum(1 for item in snapshot if item["state"] != "ready")
        avg_readiness = round(sum(item["readiness_score"] for item in snapshot) / len(snapshot), 2) if snapshot else 0.0

        return f"""
You are PILOTIX, a real-time classroom pilot for teachers in Togo.

Teacher: {teacher_name}
Class: {class_name}
Language: {language}
Class snapshot: {snapshot}

Write a short adaptive lesson suggestion in {language}.
Mention how many students are ready, how many need support, and give one vocal instruction the teacher can say now.
Return only JSON with keys:
- class_message
- teacher_voice_prompt
- recommended_lesson
- pace
- ready_count
- support_count
- average_readiness
""".strip()

    def build_dashboard(
        self,
        teacher_name: str,
        class_name: str,
        student_ids: List[str],
        language: str = "french",
    ) -> Dict[str, Any]:
        snapshot = [self._student_snapshot(student_id) for student_id in student_ids]
        if not snapshot:
            snapshot = []

        if snapshot:
            class_readiness = round(sum(item["readiness_score"] for item in snapshot) / len(snapshot), 2)
        else:
            class_readiness = 0.0

        ready_count = sum(1 for item in snapshot if item["state"] == "ready")
        support_count = sum(1 for item in snapshot if item["state"] == "support")
        watch_count = sum(1 for item in snapshot if item["state"] == "watch")

        prompt = self._build_prompt(teacher_name, class_name, snapshot, language)
        lesson_payload: Dict[str, Any] = {}
        try:
            messages = build_messages(
                agent_name="PILOTIX",
                role_description="Real-time classroom pilot for teachers in Togo.",
                user_prompt=prompt,
                require_json=True,
            )
            response = call_chat(messages=messages, model=settings.LLM_MODEL, temperature=settings.LLM_TEMPERATURE, retries=1)
            lesson_payload = extract_json(response.get("message", {}).get("content", "")) or self._safe_json_loads(response.get("message", {}).get("content", "")) or {}
        except Exception as exc:
            logger.warning(f"PILOTIX: Gemma call failed, using fallback | {exc}")

        if not lesson_payload:
            lesson_payload = {
                "class_message": f"{ready_count} élèves sont prêts, {support_count + watch_count} ont besoin d'un appui ciblé.",
                "teacher_voice_prompt": "Ajustez le rythme et lancez une activité en deux groupes.",
                "recommended_lesson": "Cours différencié avec groupe autonome et groupe de remédiation.",
                "pace": "differentiated",
                "ready_count": ready_count,
                "support_count": support_count + watch_count,
                "average_readiness": class_readiness,
            }

        class_message = lesson_payload.get("class_message") or f"{ready_count} élèves sont prêts, {support_count + watch_count} ont besoin d'un appui ciblé."
        voice = lesson_payload.get("teacher_voice_prompt") or class_message
        voice_audio = self._generate_audio(voice, language)

        heatmap = []
        for item in snapshot:
            heatmap.append(
                {
                    "student_id": item["student_id"],
                    "student_name": item["student_name"],
                    "heat": item["readiness_score"],
                    "color": item["color"],
                    "state": item["state"],
                    "weakest_skill": item["weakest_skill"],
                }
            )

        return {
            "teacher_name": teacher_name,
            "class_name": class_name,
            "generated_at": datetime.utcnow().isoformat(),
            "class_overview": {
                "average_readiness": class_readiness,
                "ready_count": ready_count,
                "support_count": support_count,
                "watch_count": watch_count,
                "total_students": len(snapshot),
            },
            "heatmap": heatmap,
            "lesson_suggestion": {
                "class_message": class_message,
                "teacher_voice_prompt": voice,
                "recommended_lesson": lesson_payload.get("recommended_lesson"),
                "pace": lesson_payload.get("pace", "differentiated"),
                "audio": voice_audio,
            },
        }
