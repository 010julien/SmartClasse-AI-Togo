from dataclasses import dataclass
import webrtcvad
from typing import Optional


@dataclass
class VADResult:
    speech_detected: bool
    speech_start: Optional[float]
    speech_end: Optional[float]


class VADModule:
    """Simple wrapper around WebRTC VAD for short audio chunks.

    Usage:
        vad = VADModule(mode=3)
        res = vad.process(audio_chunk_bytes, sample_rate=16000)
    """

    def __init__(self, mode: int = 3, frame_duration_ms: int = 30):
        self.vad = webrtcvad.Vad(mode)
        self.frame_duration_ms = frame_duration_ms

    def _frame_generator(self, frame_bytes: bytes, sample_rate: int):
        n = int(sample_rate * (self.frame_duration_ms / 1000.0) * 2)
        for i in range(0, len(frame_bytes), n):
            yield frame_bytes[i:i + n]

    def process(self, audio_chunk: bytes, sample_rate: int = 16000) -> VADResult:
        """Process raw PCM16LE bytes and return speech boundaries (approx).

        This function is meant for streaming: feed it recent audio buffer.
        It returns whether speech was detected inside the chunk and approximate
        start/end offsets in seconds relative to the chunk.
        """
        frames = list(self._frame_generator(audio_chunk, sample_rate))
        speech_frames = [self.vad.is_speech(f, sample_rate) for f in frames if len(f) > 0]
        if any(speech_frames):
            # approximate start/end
            first = speech_frames.index(True)
            last = len(speech_frames) - 1 - speech_frames[::-1].index(True)
            start = (first * self.frame_duration_ms) / 1000.0
            end = ((last + 1) * self.frame_duration_ms) / 1000.0
            return VADResult(True, start, end)
        return VADResult(False, None, None)
