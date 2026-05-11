"""Micro-benchmark for Linguix pipeline (ASR -> LLM -> TTS).

This script creates a `LinguixAgent`, replaces heavy components with lightweight
mocks (simulated delays), and measures per-step latency. Useful to get baseline
numbers without loading big models.

Usage:
    python scripts/bench_linguix.py
"""
import time
from statistics import mean

from src.agents.linguix import LinguixAgent


def mock_transcribe(audio_bytes, language=None, streaming=False):
    time.sleep(0.05)  # simulate 50ms ASR
    class T:
        text = "Bonjour, comment vas-tu ?"
        language = language or "french"
    return T()


def mock_generate(messages, channel="text", max_tokens=150, temperature=0.6):
    time.sleep(0.12)  # simulate 120ms LLM
    return {"message": {"content": "Ceci est une réponse simulée."}}


def mock_tts(text):
    time.sleep(0.03)  # simulate 30ms TTS
    return {"status": "ok", "audio_path": None, "duration_seconds": 1.2}


def run_benchmark(iterations=20):
    agent = LinguixAgent()

    # Patch heavy components
    agent.asr.transcribe = mock_transcribe
    agent.gemma.generate = mock_generate
    agent.tts.synthesize = mock_tts

    steps = {"asr": [], "llm": [], "tts": [], "total": []}

    for i in range(iterations):
        start = time.time()
        # ASR
        s1 = time.time()
        tr = agent.asr.transcribe(b"dummy_audio")
        steps["asr"].append(time.time() - s1)

        # LLM
        s2 = time.time()
        resp = agent.gemma.generate([{"role": "user", "content": tr.text}], channel="voice")
        steps["llm"].append(time.time() - s2)

        # TTS
        s3 = time.time()
        t = agent.tts.synthesize(resp.get("message").get("content"))
        steps["tts"].append(time.time() - s3)

        steps["total"].append(time.time() - start)

    print("Linguix micro-benchmark results (simulated)")
    print(f"Iterations: {iterations}")
    for k in ("asr", "llm", "tts", "total"):
        print(f"{k}: mean={mean(steps[k]):.3f}s min={min(steps[k]):.3f}s max={max(steps[k]):.3f}s")


if __name__ == "__main__":
    run_benchmark()
