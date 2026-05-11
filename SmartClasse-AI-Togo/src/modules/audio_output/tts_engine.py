from typing import Optional, Dict, Any
import logging
import tempfile
import os
from pathlib import Path
from typing import Iterator
import threading
import time
import wave
import contextlib

logger = logging.getLogger(__name__)


class TTSEngine:
    """Simple TTS engine wrapper using pyttsx3 for offline fallback.

    For production, swap to Coqui, Edge-TTS, Piper, or a streaming-capable engine.
    """

    def __init__(self, voice: Optional[str] = None, sample_rate: int = 22050):
        self.voice = voice
        self.sample_rate = sample_rate
        self.engine = None
        self._last_temp_file: Optional[str] = None
        self._stop_flag = threading.Event()
        self._lock = threading.Lock()
        # engine is initialized lazily in _ensure_engine()

    def _ensure_engine(self) -> bool:
        if self.engine is not None:
            return True

        try:
            self.engine = pyttsx3.init()
            return True
        except Exception as exc:
            logger.warning(f"TTS engine unavailable: {exc}")
            return False

    def synthesize(self, text: str, ssml: bool = False) -> Dict[str, Any]:
        """Synthesize synchronously to a temporary file path and return metadata.

        Note: For streaming, integrate a streaming backend instead.
        """
        try:
            if not self._ensure_engine():
                return {"status": "error", "error": "tts_unavailable"}

            # Save to temporary WAV using engine drivers
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tf:
                temp_path = tf.name

            # pyttsx3 supports save_to_file on many drivers
            with self._lock:
                self._stop_flag.clear()
                self.engine.save_to_file(text, temp_path)
                self.engine.runAndWait()

            self._last_temp_file = temp_path

            # Ensure persistent audio directory exists and copy temp file there
            try:
                dest_dir = os.path.join(os.getcwd(), "data", "audio")
                os.makedirs(dest_dir, exist_ok=True)
                dest_name = f"tts_{int(time.time()*1000)}_{os.path.basename(temp_path)}"
                dest_path = os.path.join(dest_dir, dest_name)
                # copy to persistent location
                try:
                    with open(temp_path, 'rb') as src, open(dest_path, 'wb') as dst:
                        dst.write(src.read())
                except Exception:
                    # fallback to move if copy fails
                    try:
                        os.replace(temp_path, dest_path)
                        temp_path = dest_path
                    except Exception:
                        dest_path = temp_path

                audio_path = dest_path
                # create a simple static audio URL path that the backend can serve from /audio/
                audio_url = f"/audio/{os.path.basename(audio_path)}"
            except Exception:
                audio_path = temp_path
                audio_url = None

            # Try to compute duration
            duration = None
            try:
                with contextlib.closing(wave.open(audio_path, 'r')) as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    duration = frames / float(rate)
            except Exception:
                duration = None

            return {"status": "ok", "audio_path": audio_path, "audio_url": audio_url, "duration_seconds": duration}
        except Exception as e:
            logger.error(f"TTS synth failed: {e}")
            return {"status": "error", "error": str(e)}

    def synthesize_stream(self, text: str, chunk_size: int = 4096) -> Iterator[bytes]:
        """Synthesize to a temp WAV file then yield chunks for streaming.

        Note: This is a pragmatic streaming proxy (writes full WAV then streams). It
        supports barge-in via `stop()` which will interrupt chunk generation.
        """
        meta = self.synthesize(text)
        if meta.get("status") != "ok":
            return iter(())

        path = meta.get("audio_path")

        def _gen() -> Iterator[bytes]:
            try:
                with open(path, 'rb') as f:
                    while not self._stop_flag.is_set():
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        yield chunk
                        # small sleep to yield control and allow stop flag to be set
                        time.sleep(0.001)
            finally:
                # cleanup temp file
                try:
                    if path and os.path.exists(path):
                        os.remove(path)
                except Exception:
                    pass

        return _gen()

    def stop(self):
        """Request immediate stop of current TTS playback/synthesis (best-effort)."""
        try:
            self._stop_flag.set()
            if self.engine is None:
                return
            with self._lock:
                try:
                    self.engine.stop()
                except Exception:
                    pass
        except Exception:
            pass
