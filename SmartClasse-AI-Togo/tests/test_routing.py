from src.modules.routing.channel_detector import ChannelDetector
from src.modules.routing.output_router import OutputRouter


def test_channel_detector_prefers_audio_payload():
    detector = ChannelDetector()
    decision = detector.detect(audio_present=True, language_hint="french")

    assert decision.channel == "voice"
    assert decision.audio_expected is True
    assert decision.confidence >= 0.9


def test_channel_detector_uses_text_hint():
    detector = ChannelDetector()
    decision = detector.detect(text="Affiche en tableau et résume", language_hint="french")

    assert decision.channel == "text"
    assert decision.confidence >= 0.75


def test_output_router_serializes_voice_payload():
    router = OutputRouter()
    routed = router.route_voice("Bonjour", {"audio_path": "/tmp/test.wav"}, {"channel": "voice"})
    payload = router.as_dict(routed)

    assert payload["channel"] == "voice"
    assert payload["text"] == "Bonjour"
    assert payload["audio"]["audio_path"] == "/tmp/test.wav"
