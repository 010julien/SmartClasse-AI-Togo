from src.agents.adaptix import AdaptixAgent
from src.agents.equitix import EquitixAgent
from src.agents.pilotix import PilotixAgent
from src.agents.kulturix import KulturixAgent


def test_kulturix_loads_local_corpus_and_enriches_adaptix_prompt(monkeypatch):
    kulturix = KulturixAgent()
    assert kulturix.corpus_size() >= 50

    adaptix = AdaptixAgent()
    monkeypatch.setattr(adaptix, "_ensure_ollama_client", lambda: None)

    captured = {}

    def fake_call(prompt, fallback=None):
        captured["prompt"] = prompt
        return fallback

    monkeypatch.setattr(adaptix, "_call_gemma4", fake_call)

    exercise = adaptix.generate_exercise("Kossi", "CM1", "math", "fractions", "french")

    assert exercise["title"] == "Fractions avec le sorgho"
    assert exercise["cultural_context"]
    assert "KULTURIX local corpus" in captured["prompt"]
    assert "sorgho" in captured["prompt"].lower()
    assert "marché" in captured["prompt"].lower() or "market" in captured["prompt"].lower()


def test_afissa_dropout_risk_triggers_high_alert_without_network():
    agent = EquitixAgent()

    result = agent.assess_dropout_risk(
        student_id="afissa-001",
        student_name="Afissa",
        signals={
            "attendance_days_missed": 4,
            "lateness_count": 3,
            "missing_assignments": 2,
            "participation_score": 20,
            "language_confidence": 30,
            "fatigue_score": 2,
            "home_support": 0,
        },
    )

    assert result["student_name"] == "Afissa"
    assert result["risk_level"] in {"high", "critical"}
    assert result["teacher_action"]
    assert len(result["signals_detected"]) >= 4


def test_kofi_teacher_dashboard_uses_local_fallback_and_class_summary(monkeypatch):
    adaptix = AdaptixAgent()
    monkeypatch.setattr(adaptix, "_ensure_ollama_client", lambda: None)

    kofi_profile = adaptix.build_student_profile(
        "kofi-001",
        [
            {"skill": "math", "subject": "math", "is_correct": True},
            {"skill": "math", "subject": "math", "is_correct": True},
            {"skill": "reading", "subject": "french", "is_correct": False},
        ],
    )

    fal_profile = adaptix.build_student_profile(
        "fal-001",
        [
            {"skill": "math", "subject": "math", "is_correct": False},
            {"skill": "math", "subject": "math", "is_correct": False},
            {"skill": "reading", "subject": "french", "is_correct": False},
        ],
    )

    adaptix.evaluate_response("kofi-001", "ex-1", "answer", True)
    adaptix.evaluate_response("kofi-001", "ex-2", "answer", True)
    adaptix.evaluate_response("fal-001", "ex-3", "answer", False)

    pilotix = PilotixAgent()
    monkeypatch.setattr(pilotix, "_ensure_ollama_client", lambda: None)
    monkeypatch.setattr(
        pilotix,
        "_generate_audio",
        lambda text, language="french": {"audio_url": None, "audio_path": None, "language": language},
    )

    dashboard = pilotix.build_dashboard(
        teacher_name="Kofi",
        class_name="CE2 A",
        student_ids=["kofi-001", "fal-001"],
        language="french",
    )

    assert dashboard["teacher_name"] == "Kofi"
    assert dashboard["class_overview"]["total_students"] == 2
    assert dashboard["class_overview"]["ready_count"] >= 0
    assert dashboard["lesson_suggestion"]["recommended_lesson"]
    assert dashboard["lesson_suggestion"]["audio"]["language"] == "french"
    assert kofi_profile["student_id"] == "kofi-001"
    assert fal_profile["student_id"] == "fal-001"