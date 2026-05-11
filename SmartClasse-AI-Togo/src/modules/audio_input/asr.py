from dataclasses import dataclass
import os
import tempfile
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class Transcription:
    text: str
    language: Optional[str]
    confidence: float
    word_timestamps: Optional[List[Dict[str, Any]]]


class ASRModule:
    """ASR wrapper built around openai-whisper by default.

    Methods implemented focus on streaming-friendly API (placeholder).
    """

    def __init__(self, engine: str = "openai-whisper", model_size: str = "base", device: str = "cpu"):
        self.engine = engine
        self.model_size = model_size
        self.device = device
        # Lazy init to avoid heavy import on startup
        self.model = None

    def _ensure_model(self):
        if self.model is not None:
            return
        try:
            import whisper

            self.model = whisper.load_model(self.model_size)
            logger.info("Loaded openai-whisper model")
        except Exception as e:
            logger.warning(f"ASR model load failed: {e}")
            self.model = None

    @staticmethod
    def _write_temp_audio_file(audio_segment: bytes) -> str:
        fd, temp_path = tempfile.mkstemp(suffix=".wav")
        try:
            with os.fdopen(fd, "wb") as temp_file:
                temp_file.write(audio_segment)
        except Exception:
            os.close(fd)
            raise
        return temp_path

    def transcribe(self, audio_segment: bytes, language: str = "auto", streaming: bool = True) -> Transcription:
        """Transcribe raw PCM bytes or wav bytes. Returns Transcription dataclass.

        This is a synchronous convenience wrapper; for production use a streaming
        transcription pipeline should be implemented.
        """
        self._ensure_model()
        if self.model is None:
            return Transcription(text="", language=None, confidence=0.0, word_timestamps=None)

        # Placeholder: try a quick synchronous call
        try:
            temp_path = None
            if isinstance(audio_segment, (bytes, bytearray)):
                temp_path = self._write_temp_audio_file(bytes(audio_segment))
                input_audio: Any = temp_path
            else:
                input_audio = audio_segment

            result = self.model.transcribe(input_audio, language=None if language == "auto" else language)
            text = result.get("text", "") if isinstance(result, dict) else ""
            detected_language = result.get("language") if isinstance(result, dict) else None
            return Transcription(text=text, language=detected_language, confidence=0.85, word_timestamps=None)
        except Exception as e:
            logger.error(f"ASR transcription failed: {e}")
            return Transcription(text="", language=None, confidence=0.0, word_timestamps=None)
        finally:
            if 'temp_path' in locals() and temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
