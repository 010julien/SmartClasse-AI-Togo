"""Tests d'intégration pour les endpoints FastAPI de SmartClasse.

Tous les agents et appels Ollama/Whisper sont mockés — aucun service externe requis.
"""
from __future__ import annotations

import io
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _exercise():
    return {"title": "Exercice test", "problem": "2 + 2 = ?", "answer": "4"}


def _make_adaptix():
    m = MagicMock()
    m.generate_exercise.return_value = _exercise()
    m.generate_diagnostic_exercises.return_value = [_exercise()]
    m.build_student_profile.return_value = {"level": "CE1", "student_id": "s1"}
    m.evaluate_response.return_value = {"updated": True}
    return m


def _make_linguix():
    m = MagicMock()
    m.transcribe.return_value = {"text": "Bonjour", "language": "french"}
    m.chat.return_value = {"assistant_text": "Réponse IA", "audio_url": None}
    m.chat_voice.return_value = {"assistant_text": "Réponse vocale", "audio_url": None}
    m.translate_instruction.return_value = [{"lang": "kabyie", "translated_instruction": "..."}]
    m.voice_pipeline.return_value = {
        "transcription": {"text": "Test"},
        "translations": [],
    }
    m.tts = MagicMock()
    m.tts.synthesize_stream.return_value = iter([b"RIFF\x00\x00\x00\x00WAVE"])
    return m


def _make_kulturix():
    m = MagicMock()
    m.get_context_pack.return_value = {"sorgho": "karité marché famille"}
    return m


def _make_diagnostix():
    m = MagicMock()
    m.analyze_student.return_value = {
        "teacher_message": "Akouvi progresse",
        "next_action": "Exercice de remédiation",
        "retroactive_exercise": _exercise(),
    }
    return m


def _make_pilotix():
    m = MagicMock()
    m.build_dashboard.return_value = {
        "class_overview": {"ready_count": 20, "support_count": 5},
        "lesson_suggestion": {"class_message": "Cours en cours"},
    }
    return m


def _make_equitix():
    m = MagicMock()
    m.assess_dropout_risk.return_value = {
        "risk_level": "low",
        "teacher_action": "Continuer le suivi",
        "voice_alert": {"audio_url": None},
    }
    return m


def _make_parentix():
    m = MagicMock()
    m.send_weekly_message.return_value = {
        "status": "dry_run",
        "weekly_message": {"sms_text": "Akouvi progresse bien."},
    }
    return m


def _make_orchestrator():
    m = MagicMock()
    m.generate_personalized_exercise.return_value = _exercise()
    return m


# ---------------------------------------------------------------------------
# Fixture principale : client avec tous les agents mockés
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    mock_adaptix = _make_adaptix()
    mock_linguix = _make_linguix()
    mock_kulturix = _make_kulturix()
    mock_diagnostix = _make_diagnostix()
    mock_pilotix = _make_pilotix()
    mock_equitix = _make_equitix()
    mock_parentix = _make_parentix()
    mock_orch = _make_orchestrator()

    patches = [
        patch("src.agents.adaptix.AdaptixAgent", return_value=mock_adaptix),
        patch("src.agents.diagnostix.DiagnostixAgent", return_value=mock_diagnostix),
        patch("src.agents.pilotix.PilotixAgent", return_value=mock_pilotix),
        patch("src.agents.equitix.EquitixAgent", return_value=mock_equitix),
        patch("src.agents.parentix.ParentixAgent", return_value=mock_parentix),
        patch("src.agents.linguix.LinguixAgent", return_value=mock_linguix),
        patch("src.agents.kulturix.KulturixAgent", return_value=mock_kulturix),
        patch("src.agents.orchestrator.OrchestratorAgent", return_value=mock_orch),
        patch("src.db.init_db"),
        patch("src.db.load_student_profile", return_value={"level": "CE1", "student_id": "s1"}),
    ]

    for p in patches:
        p.start()

    # Forcer le rechargement de src.main pour qu'il utilise les mocks
    for key in list(sys.modules.keys()):
        if "src.main" in key:
            del sys.modules[key]

    from src.main import app
    with TestClient(app) as c:
        yield c

    for p in patches:
        p.stop()


# ---------------------------------------------------------------------------
# Tests endpoints
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "online"
        assert "version" in data

    def test_root_lists_endpoints(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "endpoints" in r.json()


class TestAdaptix:
    def test_generate_exercise(self, client):
        r = client.post("/agents/adaptix/generate", json={
            "student_name": "Akouvi",
            "level": "CE1",
            "subject": "math",
            "topic": "fractions",
        })
        assert r.status_code == 200
        assert r.json()["status"] == "success"
        assert "exercise" in r.json()

    def test_generate_exercise_missing_field_returns_422(self, client):
        # student_name est requis
        r = client.post("/agents/adaptix/generate", json={
            "level": "CE1",
            "subject": "math",
            "topic": "fractions",
        })
        assert r.status_code == 422

    def test_generate_exercise_default_language(self, client):
        r = client.post("/agents/adaptix/generate", json={
            "student_name": "Kossi",
            "level": "CM1",
            "subject": "math",
            "topic": "multiplication",
        })
        assert r.status_code == 200

    def test_diagnostic(self, client):
        r = client.post("/agents/adaptix/diagnostic", json={
            "student_name": "Akouvi",
            "level": "CE1",
        })
        assert r.status_code == 200
        assert "diagnostic_exercises" in r.json()

    def test_build_profile(self, client):
        r = client.post("/agents/adaptix/profile", json={
            "student_id": "s1",
            "responses": [],
        })
        assert r.status_code == 200
        assert "profile" in r.json()

    def test_build_profile_missing_student_id_422(self, client):
        r = client.post("/agents/adaptix/profile", json={"responses": []})
        assert r.status_code == 422

    def test_get_profile(self, client):
        r = client.get("/agents/adaptix/profile/s1")
        assert r.status_code == 200
        assert "profile" in r.json()

    def test_evaluate(self, client):
        r = client.post("/agents/adaptix/evaluate", json={
            "student_id": "s1",
            "exercise_id": "ex-1",
            "response": "4",
            "is_correct": True,
        })
        assert r.status_code == 200
        assert r.json()["status"] == "success"


class TestLinguix:
    def test_translate_instruction(self, client):
        r = client.post("/agents/linguix/translate_instruction", json={
            "instruction": "Ouvrez vos livres à la page 12",
            "source_language": "french",
            "target_languages": ["kabyie", "ewe"],
        })
        assert r.status_code == 200
        assert "translations" in r.json()

    def test_translate_missing_instruction_422(self, client):
        r = client.post("/agents/linguix/translate_instruction", json={
            "source_language": "french",
        })
        assert r.status_code == 422

    def test_tts_stream_ok(self, client):
        r = client.post("/agents/linguix/tts_stream", json={
            "text": "Bonjour les enfants",
            "language": "french",
        })
        assert r.status_code == 200
        assert r.headers["content-type"] == "audio/wav"

    def test_tts_stream_empty_text_400(self, client):
        r = client.post("/agents/linguix/tts_stream", json={"text": "   "})
        assert r.status_code == 400

    def test_chat_json(self, client):
        r = client.post("/agents/linguix/chat", json={
            "messages": [{"role": "user", "content": "Bonjour"}],
            "speak": False,
            "language": "french",
        })
        assert r.status_code == 200
        assert "result" in r.json()

    def test_transcribe_audio(self, client):
        fake_audio = io.BytesIO(b"RIFF\x00\x00\x00\x00WAVEfmt ")
        r = client.post(
            "/agents/linguix/transcribe",
            files={"file": ("test.wav", fake_audio, "audio/wav")},
            data={"language_hint": "french"},
        )
        assert r.status_code == 200
        assert "transcription" in r.json()

    def test_voice_pipeline(self, client):
        fake_audio = io.BytesIO(b"RIFF\x00\x00\x00\x00WAVEfmt ")
        r = client.post(
            "/agents/linguix/voice_pipeline",
            files={"file": ("test.wav", fake_audio, "audio/wav")},
            data={"source_language_hint": "french", "target_languages": "ewe,kabyie"},
        )
        assert r.status_code == 200
        assert "pipeline" in r.json()


class TestDiagnostix:
    def test_analyze(self, client):
        r = client.post("/agents/diagnostix/analyze", json={
            "student_id": "s1",
            "student_name": "Akouvi",
            "level": "CM1",
        })
        assert r.status_code == 200
        assert "analysis" in r.json()

    def test_analyze_missing_student_id_422(self, client):
        r = client.post("/agents/diagnostix/analyze", json={
            "student_name": "Akouvi",
            "level": "CM1",
        })
        assert r.status_code == 422


class TestPilotix:
    def test_dashboard(self, client):
        r = client.post("/agents/pilotix/dashboard", json={
            "teacher_name": "Kossi",
            "class_name": "CM1 A",
            "student_ids": ["s1", "s2"],
        })
        assert r.status_code == 200
        assert "dashboard" in r.json()


class TestEquitix:
    def test_risk_assessment(self, client):
        r = client.post("/agents/equitix/risk_assessment", json={
            "student_id": "s1",
            "student_name": "Akouvi",
            "signals": {
                "attendance_days_missed": 4,
                "participation_score": 30,
            },
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "success"
        assert "assessment" in data

    def test_risk_assessment_missing_fields_422(self, client):
        r = client.post("/agents/equitix/risk_assessment", json={
            "signals": {},
        })
        assert r.status_code == 422


class TestParentix:
    def test_send_sms_dry_run(self, client):
        r = client.post("/agents/parentix/send_sms", json={
            "student_id": "s1",
            "student_name": "Akouvi",
            "phone_number": "+22890000000",
            "language": "french",
            "dry_run": True,
        })
        assert r.status_code == 200
        assert r.json()["status"] == "success"

    def test_send_sms_missing_phone_422(self, client):
        r = client.post("/agents/parentix/send_sms", json={
            "student_id": "s1",
            "student_name": "Akouvi",
        })
        assert r.status_code == 422


class TestOrchestrator:
    def test_generate(self, client):
        r = client.post("/agents/orchestrator/generate", json={
            "student_id": "s1",
            "student_name": "Akouvi",
            "level": "CE1",
            "subject": "math",
            "topic": "fractions",
            "language": "french",
        })
        assert r.status_code == 200
        assert "exercise" in r.json()

    def test_generate_uses_defaults(self, client):
        r = client.post("/agents/orchestrator/generate", json={})
        assert r.status_code == 200


class TestKulturix:
    def test_context(self, client):
        r = client.get("/agents/kulturix/context", params={"query": "sorgho marché"})
        assert r.status_code == 200
        assert "context" in r.json()
