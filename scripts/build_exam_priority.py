#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "exams" / "79.json"
OUTPUT = ROOT / "data" / "automation" / "priority.json"

BASELINE = {
    "발해 핵심 제도와 왕 계보": [3, 97], "광무개혁": [2, 96],
    "조선어학회": [2, 96], "한국광복군": [2, 97], "제주 4·3 사건": [2, 95],
    "6·10 만세 운동": [2, 90], "위화도 회군": [1, 99], "6월 민주 항쟁": [1, 98],
    "영조": [1, 97], "임오군란": [1, 96], "국가총동원법과 공출": [1, 96],
    "러일전쟁과 독도 불법 편입": [1, 95], "삼국사기 vs 삼국유사": [1, 95],
    "묘청의 서경 천도 운동": [1, 93], "김구의 통일정부 노력": [1, 93],
    "세도 정치와 홍경래의 난": [1, 92], "대한광복회": [1, 87],
    "임진왜란 이후 조일관계": [1, 86], "1920년대 사회상": [1, 85],
    "일제강점기 대중문화": [1, 82]
}

ALIASES = {
    "구석기 시대 생활": ["구석기", "뗀석기"],
    "부여·동예 풍속 비교": ["부여", "동예"],
    "발해 핵심 제도와 왕 계보": ["발해"],
    "고려 전기 거란 대응": ["거란", "귀주대첩", "현종"],
    "삼국사기 vs 삼국유사": ["삼국사기", "삼국유사"],
    "원 간섭기 권문세족": ["원 간섭기", "권문세족"],
    "세도 정치와 홍경래의 난": ["홍경래", "세도정치"],
    "러일전쟁과 독도 불법 편입": ["러일전쟁"],
    "민족 말살 통치": ["황국신민", "창씨개명", "민족 말살"],
    "국가총동원법과 공출": ["국가총동원법", "공출"],
    "김구의 통일정부 노력": ["김구", "남북협상"],
    "노태우 정부 남북관계": ["남북기본합의서", "유엔 동시가입", "비핵화"],
    "군사 제도 비교": ["9서당", "2군6위", "훈련도감", "5군영"]
}


def grade(score: int) -> str:
    return "S" if score >= 95 else "A" if score >= 88 else "B" if score >= 80 else "C"


def appears(question: dict, field: str, aliases: list[str]) -> bool:
    text = " ".join(question.get(field, []))
    return any(alias in text for alias in aliases)


def main() -> int:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    questions = data["questions"]
    items = []
    for q in questions:
        name = q["directConcept"]
        previous_count, previous_score = BASELINE.get(name, [0, 80])
        aliases = ALIASES.get(name, [name])
        source_count = sum(1 for item in questions if appears(item, "sourceAppearances", aliases))
        option_count = sum(1 for item in questions if appears(item, "optionAppearances", aliases))
        score = min(100, previous_score + 5 + source_count * 2 + option_count)
        items.append({
            "concept": name, "conceptId": q.get("conceptId"), "era": q.get("era"),
            "question": q["question"], "previousDirectCount": previous_count,
            "direct79": 1, "source79": source_count, "option79": option_count,
            "previousScore": previous_score, "score": score, "grade": grade(score),
            "reason": f"79회 직접 출제 · 자료 {source_count} · 보기 {option_count}"
        })
    items.sort(key=lambda x: (-x["score"], -x["previousDirectCount"], x["concept"]))
    for rank, item in enumerate(items, 1):
        item["rank"] = rank
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({
        "latestExam": 79,
        "scoringRule": "기존 우선점수 + 79 직접 5 + 자료 등장 2/회 + 보기 등장 1/회, 최대 100",
        "items": items
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"saved: {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
