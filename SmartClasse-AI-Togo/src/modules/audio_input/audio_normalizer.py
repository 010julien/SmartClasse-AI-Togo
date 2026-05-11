from typing import Dict
import os
import tempfile
import numpy as np
import librosa
import noisereduce as nr


class AudioNormalizer:
    """Audio normalization and lightweight cleaning pipeline.

    Exposes a single `process` method that accepts raw wav bytes or numpy array
    and returns a normalized numpy array at target sample rate.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate

    def process(self, audio: bytes | np.ndarray, sr: int = None) -> Dict:
        """Return {'audio': np.ndarray, 'sample_rate': int}

        Steps:
        - Load to numpy
        - Noise reduction
        - Volume normalization (RMS)
        - Optional filler removal (not implemented here)
        """
        if isinstance(audio, bytes):
            fd, temp_path = tempfile.mkstemp(suffix=".wav")
            try:
                with os.fdopen(fd, "wb") as temp_file:
                    temp_file.write(audio)
                y, sr = librosa.load(temp_path, sr=self.sample_rate)
            finally:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except Exception:
                    pass
        else:
            y = audio
            sr = sr or self.sample_rate

        # Noise reduction
        try:
            y_reduced = nr.reduce_noise(y=y, sr=sr)
        except Exception:
            y_reduced = y

        # RMS normalization
        rms = np.sqrt(np.mean(y_reduced ** 2))
        target_rms = 0.1
        if rms > 0:
            y_norm = y_reduced * (target_rms / (rms + 1e-9))
        else:
            y_norm = y_reduced

        return {"audio": y_norm, "sample_rate": sr}
