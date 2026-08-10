#!/usr/bin/env python3
from __future__ import annotations

import math
import struct
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def make_tone(path: Path, frequency: float, seconds: float, volume: float = 0.25) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rate = 44100
    frames = int(seconds * rate)
    with wave.open(str(path), 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        for i in range(frames):
            envelope = max(0.0, min(1.0, i / 500, (frames - i) / 500))
            sample = int(32767 * volume * envelope * math.sin(2 * math.pi * frequency * i / rate))
            f.writeframes(struct.pack('<h', sample))


def main() -> None:
    sounds = ROOT / 'remotion' / 'public' / 'sounds'
    make_tone(sounds / 'countdown.wav', 720, 0.16, 0.2)
    make_tone(sounds / 'correct.wav', 1040, 0.28, 0.22)

    print('Explanation TTS disabled: core explanation is displayed as text only.')
    print('Generated WAV effects: countdown.wav, correct.wav')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python scripts/generate_tts.py data/cards/K001_euljimundeok.json')
    main()
