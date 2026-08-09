#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS_DIR = ROOT / "data" / "cards"
ACTIVE_CARD = ROOT / "remotion" / "src" / "card.json"
PUBLIC_DIR = ROOT / "remotion" / "public"
OUTPUT_DIR = ROOT / "output"


def resolve_card(value: str) -> Path:
    direct = Path(value)
    if direct.exists():
        return direct.resolve()

    if not direct.is_absolute() and (ROOT / direct).exists():
        return (ROOT / direct).resolve()

    key = value.lower().replace(".json", "")
    matches = [p for p in CARDS_DIR.glob("*.json") if key in p.stem.lower()]
    if len(matches) == 1:
        return matches[0].resolve()
    if not matches:
        raise SystemExit(f"카드를 찾을 수 없습니다: {value}")
    raise SystemExit("카드가 여러 개 검색되었습니다:\n" + "\n".join(f"- {p.name}" for p in matches))


def validate(card: dict, card_path: Path) -> None:
    required = ["id", "title", "question", "choices", "correctChoice", "answer", "explanation", "image"]
    missing = [key for key in required if not card.get(key)]
    if missing:
        raise SystemExit(f"{card_path.name}: 필수 필드 누락: {', '.join(missing)}")

    choices = card["choices"]
    if not isinstance(choices, list) or len(choices) < 2:
        raise SystemExit("choices는 2개 이상의 배열이어야 합니다.")

    correct = int(card["correctChoice"])
    if correct < 1 or correct > len(choices):
        raise SystemExit("correctChoice가 choices 범위를 벗어났습니다.")

    image_path = PUBLIC_DIR / card["image"]
    if not image_path.exists():
        raise SystemExit(
            f"기억장면 이미지가 없습니다: {image_path}\n"
            "ChatGPT에서 9:16 이미지를 만든 뒤 이 경로에 저장하고 다시 실행하세요."
        )


def run(command: list[str]) -> None:
    print("$", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def npm_executable() -> str:
    return shutil.which("npm.cmd") or shutil.which("npm") or "npm"


def main() -> None:
    parser = argparse.ArgumentParser(description="History Card Factory one-command renderer")
    parser.add_argument("card", help="예: K002 또는 data/cards/K002_ganggamchan.json")
    parser.add_argument("--skip-tts", action="store_true", help="기존 TTS를 그대로 사용")
    parser.add_argument("--preview", action="store_true", help="렌더 대신 Remotion Studio 실행")
    args = parser.parse_args()

    card_path = resolve_card(args.card)
    card = json.loads(card_path.read_text(encoding="utf-8-sig"))
    validate(card, card_path)

    ACTIVE_CARD.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] active card: {card['id']} / {card['title']}")

    if not args.skip_tts:
        run([sys.executable, str(ROOT / "scripts" / "generate_tts.py"), str(card_path)])

    npm = npm_executable()
    if args.preview:
        run([npm, "--prefix", "remotion", "run", "preview"])
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"{card['id']}_{card_path.stem.split('_', 1)[-1]}.mp4"
    run([npm, "--prefix", "remotion", "run", "render", "--", str(output)])
    print(f"[DONE] {output}")


if __name__ == "__main__":
    main()
