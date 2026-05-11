"""Micro-benchmark for LINGUIX routing and response latency.

This script uses lightweight stubs by default so it can run without loading Gemma
or Whisper. It measures the end-to-end Python overhead of the routing flow.
"""

from __future__ import annotations

import argparse
import statistics
import time
from dataclasses import dataclass
from typing import Any, Dict, List

from src.agents.linguix import LinguixAgent


@dataclass
class _FakeResponse:
    message: str
    intent: str = "explain"
    confidence: float = 0.91
    quality_score: float = 93.0
    reasoning_chain: Any = None
    reasoning_time_ms: float = 8.0
    total_time_ms: float = 12.0
    used_regeneration: bool = False


def _patch_agent_for_benchmark(agent: LinguixAgent) -> None:
    agent.conversation_manager.process_conversation = lambda **kwargs: _FakeResponse(
        message="Une fraction représente une partie d'un tout."
    )
    agent.asr.transcribe = lambda *args, **kwargs: type(
        "T",
        (),
        {"text": "Explique-moi les fractions", "language": "french"},
    )()
    agent.vad.process = lambda *args, **kwargs: type("V", (), {"speech_detected": True})()
    agent.normalizer.process = lambda *args, **kwargs: {"audio": b"fake"}
    agent.tts.synthesize = lambda text, ssml=False: {
        "status": "ok",
        "audio_path": None,
        "duration_seconds": 0.4,
    }


def bench_chat(agent: LinguixAgent, iterations: int = 10) -> Dict[str, float]:
    samples: List[float] = []
    messages = [{"role": "user", "content": "Explique-moi les fractions"}]

    for _ in range(iterations):
        start = time.perf_counter()
        agent.chat(messages=messages, speak=False, language="french", user_level="CE1", user_id="bench_user", user_name="Kossi")
        samples.append((time.perf_counter() - start) * 1000)

    return {
        "min_ms": min(samples),
        "avg_ms": statistics.mean(samples),
        "p95_ms": statistics.quantiles(samples, n=20)[18] if len(samples) >= 20 else max(samples),
        "max_ms": max(samples),
    }


def bench_voice(agent: LinguixAgent, iterations: int = 10) -> Dict[str, float]:
    samples: List[float] = []

    for _ in range(iterations):
        start = time.perf_counter()
        agent.chat_voice(audio_bytes=b"fake-audio", language_hint="french", user_id="bench_user", user_name="Kossi", speak=False)
        samples.append((time.perf_counter() - start) * 1000)

    return {
        "min_ms": min(samples),
        "avg_ms": statistics.mean(samples),
        "p95_ms": statistics.quantiles(samples, n=20)[18] if len(samples) >= 20 else max(samples),
        "max_ms": max(samples),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark LINGUIX latency")
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument("--mode", choices=["chat", "voice", "both"], default="both")
    args = parser.parse_args()

    agent = LinguixAgent()
    _patch_agent_for_benchmark(agent)

    if args.mode in {"chat", "both"}:
        chat_stats = bench_chat(agent, iterations=args.iterations)
        print("CHAT_LATENCY_MS", chat_stats)

    if args.mode in {"voice", "both"}:
        voice_stats = bench_voice(agent, iterations=args.iterations)
        print("VOICE_LATENCY_MS", voice_stats)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
