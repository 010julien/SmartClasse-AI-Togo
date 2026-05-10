"""EQUITIX: dropout risk detection for girls and concrete teacher actions."""

import hashlib
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.db import load_student_attempts, load_student_progress

logger = logging.getLogger(__name__)


class EquitixAgent:
    """Detect disengagement signals and propose a practical teacher intervention."""

    SIGNAL_LABELS = {
        "absences_recurrentes": "Absences récurrentes",
        "retard_persistant": "Retard persistant",
        "baisse_des_resultats": "Baisse des résultats",
        "devoirs_non_rendus": "Devoirs non rendus",
        "faible_participation": "Faible participation",
        "perte_de_confiance_langue": "Perte de confiance linguistique",
        "isolement_ou_fatigue": "Isolement ou fatigue",
    }

    def _generate_audio(self, text: str, language: str = "french") -> Dict[str, Any]:
        try:
            import pyttsx3  # type: ignore

            audio_dir = os.path.join("data", "audio")
            os.makedirs(audio_dir, exist_ok=True)
            audio_name = f"equitix_{hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]}.wav"
            audio_path = os.path.join(audio_dir, audio_name)

            engine = pyttsx3.init()
            engine.setProperty("rate", 150)
            engine.save_to_file(text, audio_path)
            engine.runAndWait()

            return {"audio_url": f"/audio/{audio_name}", "audio_path": audio_path, "language": language}
        except Exception as exc:
            logger.warning(f"EQUITIX: audio generation unavailable | {exc}")
            return {"audio_url": None, "audio_path": None, "language": language}

    def _score_signal(self, detected: bool, severity: int, evidence: str) -> Dict[str, Any]:
        return {
            "detected": detected,
            "severity": severity if detected else 0,
            "evidence": evidence,
        }

    def _recent_performance_trend(self, attempts: List[Dict[str, Any]]) -> float:
        if not attempts:
            return 0.0
        recent = attempts[:3]
        older = attempts[3:6]
        recent_rate = sum(1 for attempt in recent if attempt["is_correct"]) / len(recent)
        older_rate = sum(1 for attempt in older if attempt["is_correct"]) / len(older) if older else recent_rate
        return round(recent_rate - older_rate, 2)

    def assess_dropout_risk(
        self,
        student_id: str,
        student_name: Optional[str] = None,
        language: str = "french",
        signals: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not student_id:
            raise ValueError("student_id is required")

        signals = signals or {}
        progress = load_student_progress(student_id)
        profile = progress.get("profile") or {}
        attempts = load_student_attempts(student_id, limit=12)
        stats = progress.get("statistics") or {}
        name = student_name or profile.get("student_name") or student_id

        success_rate = float(stats.get("success_rate_percent", 0.0))
        trend = self._recent_performance_trend(attempts)
        total_exercises = int(stats.get("total_exercises", 0))

        detected_signals = {
            "absences_recurrentes": self._score_signal(
                bool(signals.get("attendance_days_missed", 0) >= 3 or total_exercises < 2),
                3,
                "Peu d'activités récentes ou plusieurs jours sans trace d'exercice.",
            ),
            "retard_persistant": self._score_signal(
                bool(signals.get("lateness_count", 0) >= 3),
                2,
                "Retards répétés signalés par l'enseignant.",
            ),
            "baisse_des_resultats": self._score_signal(
                bool(trend < -0.2 or success_rate < 45),
                3,
                f"Tendance récente: {trend}; taux de réussite: {success_rate}%.",
            ),
            "devoirs_non_rendus": self._score_signal(
                bool(signals.get("missing_assignments", 0) >= 2 or total_exercises == 0),
                2,
                "Exercices non rendus ou activité insuffisante.",
            ),
            "faible_participation": self._score_signal(
                bool(signals.get("participation_score", 100) < 45),
                2,
                "Participation en classe faible.",
            ),
            "perte_de_confiance_langue": self._score_signal(
                bool(signals.get("language_confidence", 100) < 45 or profile.get("language_level") == "beginner"),
                2,
                "Difficulté d'expression ou baisse de confiance linguistique.",
            ),
            "isolement_ou_fatigue": self._score_signal(
                bool(signals.get("fatigue_score", 0) >= 2 or signals.get("home_support", 1) == 0),
                2,
                "Fatigue ou faible soutien à la maison.",
            ),
        }

        risk_points = sum(item["severity"] for item in detected_signals.values())
        if risk_points >= 11:
            risk_level = "critical"
        elif risk_points >= 7:
            risk_level = "high"
        elif risk_points >= 4:
            risk_level = "moderate"
        else:
            risk_level = "low"

        detected_list = [
            {
                "signal": key,
                "label": self.SIGNAL_LABELS[key],
                **value,
            }
            for key, value in detected_signals.items()
            if value["detected"]
        ]

        teacher_action = {
            "low": "Maintenir un suivi hebdomadaire et valoriser les progrès visibles.",
            "moderate": "Prévoir un entretien rapide avec l'élève et une activité de soutien ciblée.",
            "high": "Appeler la famille, adapter la charge de travail et proposer un mentorat immédiat.",
            "critical": "Déclencher un suivi urgent avec la famille, l'enseignant et l'équipe de direction.",
        }[risk_level]

        voice_alert = self._generate_audio(
            f"Alerte {name}. Niveau de risque {risk_level}. {teacher_action}",
            language,
        )

        return {
            "student_id": student_id,
            "student_name": name,
            "generated_at": datetime.utcnow().isoformat(),
            "risk_level": risk_level,
            "risk_points": risk_points,
            "signals_detected": detected_list,
            "teacher_action": teacher_action,
            "voice_alert": voice_alert,
            "progress": progress,
            "trend": trend,
        }
