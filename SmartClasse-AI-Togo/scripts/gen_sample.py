import os
import wave
import struct
import math

os.makedirs('samples', exist_ok=True)
path = os.path.join('samples', 'sample.wav')
framerate = 16000
duration = 1.0
amplitude = 0.2
frequency = 220.0
n_samples = int(framerate * duration)
with wave.open(path, 'w') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(framerate)
    for i in range(n_samples):
        t = i / framerate
        val = int(amplitude * 32767.0 * math.sin(2.0 * math.pi * frequency * t))
        wf.writeframes(struct.pack('<h', val))
print('WAV generated:', path)