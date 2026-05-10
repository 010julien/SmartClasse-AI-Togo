from src.main import orchestrator


def test_orchestrator_generate_direct():
    result = orchestrator.generate_personalized_exercise(
        student_id="test-1",
        student_name="Test",
        level="CE1",
        subject="math",
        topic="fractions",
        language="french",
    )

    assert isinstance(result, dict)
    # Should contain at least these keys from fallback or Gemma output
    for key in [
        "exercise_id",
        "title",
        "problem",
        "options",
        "correct_answer",
    ]:
        assert key in result
