"""
conftest.py — stub native/heavy dependencies before any test imports.

The production code imports webrtcvad, whisper, pyttsx3, ollama, torch, etc.
Those are not available in the CI/test environment (native C extensions, GPU
drivers). We inject MagicMock stubs into sys.modules early so that
module-level imports inside src/ succeed without the real packages.
"""
from __future__ import annotations

import os
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

# ── sys.path ─────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── env vars ─────────────────────────────────────────────────────────────────
os.environ.setdefault("PYTHONUTF8", "1")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

# ── Native / heavy module stubs ──────────────────────────────────────────────

def _stub(name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    mod.__spec__ = None  # type: ignore[assignment]
    mod.__path__: list = []
    return mod


def _install(*names: str) -> None:
    for name in names:
        if name not in sys.modules:
            sys.modules[name] = _stub(name)


_install(
    "webrtcvad",
    "whisper",
    "openai",
    "ollama",
    "pyttsx3",
    "sounddevice",
    "librosa",
    "torch",
    "torch.nn",
    "torch.cuda",
    "torchaudio",
    "transformers",
    "africastalking",
    "cryptography",
    "cryptography.fernet",
    "noisereduce",
    "llama_cpp",
)

# Attribute-level stubs for code that accesses attributes at import time
_webrtc = sys.modules["webrtcvad"]
_webrtc.Vad = MagicMock()  # type: ignore[attr-defined]

_whisper = sys.modules["whisper"]
_whisper.load_model = MagicMock(return_value=MagicMock())  # type: ignore[attr-defined]

_pyttsx3 = sys.modules["pyttsx3"]
_pyttsx3.init = MagicMock(return_value=MagicMock())  # type: ignore[attr-defined]

_torch = sys.modules["torch"]
_torch.cuda = MagicMock()  # type: ignore[attr-defined]
_torch.cuda.is_available = MagicMock(return_value=False)