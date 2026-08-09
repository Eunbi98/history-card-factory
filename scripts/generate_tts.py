#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import json
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


async def main(card_path: Path) -> None:
    # utf-8-sig accepts both normal UTF-8 and UTF-8 files that contain a BOM.
    card = json.loads(card_path.read_text(encoding='utf-8-sig'))
    try:
        import edge_tts
    except ImportError as exc:
        raise RuntimeError("edge-tts가 없습니다. 먼저 'npm run setup:tts'를 실행하세요.") from exc

    out = ROOT / 'remotion' / 'public' / 'tts' / card['id'] / 'explanation.mp3'
    out.parent.mkdir(parents=True, exist_ok=True)
    text = card['explanation']
    voice = 'ko-KR-SunHiNeural'
    await edge_tts.Communicate(text=text, voice=voice, rate='+0%', volume='+0%').save(str(out))

    sounds = ROOT / 'remotion' / 'public' / 'sounds'
    make_tone(sounds / 'countdown.wav', 720, 0.16, 0.2)
    make_tone(sounds / 'correct.wav', 1040, 0.28, 0.22)

    print(f'TTS ready: {out}')
    print('Generated WAV effects: countdown.wav, correct.wav')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python scripts/generate_tts.py data/cards/K001_euljimundeok.json')
    path = Path(sys.argv[1])
    if not path.is_absolute():
        path = ROOT / path
    asyncio.run(main(path))
