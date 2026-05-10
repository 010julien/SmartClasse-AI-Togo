"""PARENTIX: weekly parent SMS generation and optional Africa's Talking delivery."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from urllib import parse, request as urlrequest

try:
    import ollama  # type: ignore
except ImportError:
    ollama = None

from src.llm import call_chat

from src.config import settings
from src.db import load_student_progress

logger = logging.getLogger(__name__)


class ParentixAgent:
    """Generate weekly parent messages and send them through SMS when configured."""

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

    def _translate_or_adapt(self, text: str, target_language: str) -> str:
        if target_language.lower() == "french":
            return text

        try:
            messages = build_messages(
                agent_name="PARENTIX",
                role_description="Parent message generator and translator for weekly SMS.",
                user_prompt=f"Translate this SMS into {target_language}: {text}",
                require_json=False,
            )
            response = call_chat(messages=messages, model=settings.LLM_MODEL, temperature=settings.LLM_TEMPERATURE, retries=1)
            translated = response.get("message", {}).get("content", "").strip()
            if translated:
                return translated[:160]
        except Exception as exc:
            logger.warning(f"PARENTIX: translation failed, using fallback | {exc}")

        return text

    def build_weekly_message(
        self,
        student_id: str,
        student_name: Optional[str] = None,
        language: str = "french",
    ) -> Dict[str, Any]:
        progress = load_student_progress(student_id)
        profile = progress.get("profile") or {}
        stats = progress.get("statistics") or {}
        name = student_name or profile.get("student_name") or student_id

        total = int(stats.get("total_exercises", 0))
        correct = int(stats.get("correct_answers", 0))
        success_rate = float(stats.get("success_rate_percent", 0.0))

        base_sms = (
            f"SmartClasse: {name} a fait {total} exercices cette semaine, avec {correct} bonnes réponses. "
            f"Taux de réussite: {success_rate:.1f}%. Continuons les efforts à la maison."
        )
        adapted_sms = self._translate_or_adapt(base_sms, language)
        return {
            "student_id": student_id,
            "student_name": name,
            "generated_at": datetime.utcnow().isoformat(),
            "language": language,
            "sms_text": adapted_sms,
            "progress": progress,
        }

    def _send_africastalking_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        if not settings.AFRICASTALKING_USERNAME or not settings.AFRICASTALKING_API_KEY:
            return {
                "status": "dry_run",
                "provider": "africastalking",
                "reason": "credentials_missing",
                "phone_number": phone_number,
                "message": message,
            }

        payload = parse.urlencode(
            {
                "username": settings.AFRICASTALKING_USERNAME,
                "to": phone_number,
                "message": message,
                "from": settings.AFRICASTALKING_SENDER_ID or "SmartClasse",
            }
        ).encode("utf-8")

        req = urlrequest.Request(
            "https://api.africastalking.com/version1/messaging",
            data=payload,
            method="POST",
            headers={
                "apiKey": settings.AFRICASTALKING_API_KEY,
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

        with urlrequest.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8")
            return {
                "status": "sent",
                "provider": "africastalking",
                "response": json.loads(body) if body else {},
            }

    def send_weekly_message(
        self,
        student_id: str,
        phone_number: Optional[str],
        student_name: Optional[str] = None,
        language: str = "french",
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        weekly = self.build_weekly_message(student_id, student_name, language)
        phone = phone_number or ""

        if dry_run or not phone:
            return {
                "status": "dry_run",
                "provider": settings.SMS_PROVIDER,
                "phone_number": phone,
                "weekly_message": weekly,
            }

        if settings.SMS_PROVIDER.lower() == "africastalking":
            send_result = self._send_africastalking_sms(phone, weekly["sms_text"])
        else:
            send_result = {
                "status": "dry_run",
                "provider": settings.SMS_PROVIDER,
                "phone_number": phone,
                "message": weekly["sms_text"],
            }

        return {
            "status": send_result.get("status", "dry_run"),
            "provider": send_result.get("provider", settings.SMS_PROVIDER),
            "phone_number": phone,
            "weekly_message": weekly,
            "delivery": send_result,
        }
