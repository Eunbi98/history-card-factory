#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "youtube"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_card(value: str) -> Path:
    p = Path(value)
    if p.exists():
        return p.resolve()
    if not p.is_absolute() and (ROOT / p).exists():
        return (ROOT / p).resolve()
    key = value.lower().replace(".json", "")
    matches = [x for x in (ROOT / "data" / "cards").glob("*.json") if key in x.stem.lower()]
    if len(matches) != 1:
        raise SystemExit(f"카드를 찾을 수 없거나 여러 개입니다: {value}")
    return matches[0]


def clean_tag(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣]", "", text)


def short_question(card: dict) -> str:
    explicit = str(card.get("youtubeTitleQuestion", "")).strip()
    if explicit:
        return explicit.rstrip("?") + "?"
    answer = str(card.get("answer") or card.get("title") or "한국사").strip()
    return f"{answer}의 핵심은?"


def build(card: dict) -> dict:
    title = card.get("title", "한국사 기억카드")
    answer = card.get("answer", title)
    exam = card.get("sourceExam", "한능검 핵심 개념")
    memory = card.get("memoryTip", "")
    explanation = card.get("explanation", "")
    exam_link = card.get("examLink", "")

    exam_round = card.get("examRound")
    exam_question = card.get("examQuestion")
    title_question = short_question(card)

    if exam_round and exam_question:
        youtube_title = f"[#한능검 {exam_round}회 {exam_question}번] #{title_question} #쇼츠 #shorts"
    else:
        youtube_title = f"[#한능검] #{title_question} #쇼츠 #shorts"
    youtube_title = youtube_title[:100]

    description = (
        f"한능검에서 자주 헷갈리는 ‘{answer}’ 핵심을 기억카드로 정리했습니다.\n\n"
        f"핵심 해설\n{explanation}\n\n"
        f"시험 직전 기억하기\n{memory}\n\n"
        f"출제 기준: {exam}\n"
        "※ 기출 원문을 그대로 복제하지 않고 출제 포인트를 바탕으로 재구성한 학습 콘텐츠입니다."
    )

    fixed_comment = (
        f"{answer}에서 가장 먼저 떠올려야 할 키워드는 무엇인가요?\n"
        f"정답 확인: {exam_link or memory}\n"
        "다음 기억카드에서 다뤘으면 하는 한국사 개념도 댓글로 남겨주세요."
    )

    tags = [
        "한능검", "한국사능력검정시험", "한국사", "한능검심화", "한국사공부",
        "한국사암기", "기억카드", clean_tag(answer), clean_tag(title),
    ]
    for token in re.split(r"[·→, /]+", exam_link):
        token = clean_tag(token)
        if token and token not in tags:
            tags.append(token)

    return {
        "cardId": card.get("id"),
        "title": youtube_title,
        "description": description,
        "fixedComment": fixed_comment,
        "tags": tags,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("card")
    args = parser.parse_args()
    card_path = resolve_card(args.card)
    card = load(card_path)
    meta = build(card)
    card_id = card.get("id") or card_path.stem
    target = OUT_DIR / f"{card_id}.json"
    save(target, meta)
    print(target.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
