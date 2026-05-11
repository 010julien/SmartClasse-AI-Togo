from unittest.mock import patch

from src.modules.audio_output.tts_engine import TTSEngine


def test_tts_engine_fails_soft_when_driver_missing():
    with patch("src.modules.audio_output.tts_engine.pyttsx3.init", side_effect=OSError("libespeak.so.1 missing")):
        engine = TTSEngine()

        assert engine.engine is None

        meta = engine.synthesize("Bonjour")

        assert meta["status"] == "error"
        assert meta["error"] == "tts_unavailable"