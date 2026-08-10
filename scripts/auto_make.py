#!/usr/bin/env python3
"""Pick the highest-priority unfinished concept and build one complete history-card video.

Flow:
priority -> card JSON -> memory image -> existing TTS/Remotion renderer -> production state

Required environment variable:
  OPENAI_API_KEY
Optional:
  HISTORY_CARD_TEXT_MODEL (default: gpt-5-mini)
  HISTORY_CARD_IMAGE_MODEL (default: gpt-image-1)
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
PRIORITY = ROOT / "data" / "automation" / "priority.json"
STATE = ROOT / "data" / "automation" / "production_state.json"
EXAM79 = ROOT / "data" / "exams" / "79.json"
CARDS = ROOT / "data" / "cards"
IMAGES = ROOT / "remotion" / "public" / "images"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(command: list[str]) -> None:
    print("$", " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def next_card_id() -> str:
    highest = 0
    for path in CARDS.glob("*.json"):
        match = re.search(r"K(\d{3})", path.name, re.I)
        if match:
            highest = max(highest, int(match.group(1)))
        else:
            try:
                data = load_json(path)
                match = re.fullmatch(r"K(\d{3})", str(data.get("id", "")), re.I)
                if match:
                    highest = max(highest, int(match.group(1)))
            except Exception:
                pass
    return f"K{highest + 1:03d}"


def slugify(value: str) -> str:
    value = re.sub(r"[^0-9A-Za-z가-힣]+", "-", value).strip("-")
    return value[:42] or "history-card"


def choose_candidate(force_concept: str | None = None) -> dict[str, Any]:
    run([sys.executable, str(ROOT / "scripts" / "build_exam_priority.py")])
    priority = load_json(PRIORITY, {"items": []})
    state = load_json(STATE, {"items": {}})
    statuses = state.setdefault("items", {})

    if force_concept:
        for item in priority.get("items", []):
            if item.get("concept") == force_concept:
                return item
        raise SystemExit(f"우선순위 목록에서 개념을 찾을 수 없습니다: {force_concept}")

    for item in priority.get("items", []):
        status = statuses.get(item.get("concept"), {}).get("status")
        if status not in {"done", "rendering", "generating"}:
            return item
    raise SystemExit("제작할 미완료 우선순위 후보가 없습니다.")


def exam_context(candidate: dict[str, Any]) -> dict[str, Any]:
    exam = load_json(EXAM79)
    qno = int(candidate["question"])
    for question in exam.get("questions", []):
        if int(question.get("question", -1)) == qno:
            return question
    raise SystemExit(f"79회 {qno}번 구조화 데이터를 찾을 수 없습니다.")


def card_schema() -> dict[str, Any]:
    part = {
        "type": "object",
        "properties": {"text": {"type": "string"}, "accent": {"type": "boolean"}},
        "required": ["text"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "question": {"type": "string"},
            "choices": {"type": "array", "items": {"type": "string"}, "minItems": 5, "maxItems": 5},
            "correctChoice": {"type": "integer", "minimum": 1, "maximum": 5},
            "answer": {"type": "string"},
            "explanation": {"type": "string"},
            "examLink": {"type": "string"},
            "wrongTraps": {
                "type": "array",
                "items": {"type": "array", "items": {"type": "string"}, "minItems": 2, "maxItems": 2},
                "minItems": 4,
                "maxItems": 4,
            },
            "memoryHeadline": {"type": "string"},
            "memoryTip": {"type": "string"},
            "mnemonicParts": {"type": "array", "items": part, "minItems": 1},
            "mnemonicSublineParts": {"type": "array", "items": part, "minItems": 1},
            "recapTitle": {"type": "string"},
            "recapResult": {"type": "string"},
            "recapDetail": {"type": "string"},
            "imagePrompt": {"type": "string"},
        },
        "required": [
            "title", "question", "choices", "correctChoice", "answer", "explanation", "examLink",
            "wrongTraps", "memoryHeadline", "memoryTip", "mnemonicParts", "mnemonicSublineParts",
            "recapTitle", "recapResult", "recapDetail", "imagePrompt"
        ],
        "additionalProperties": False,
    }


def generate_card(client: OpenAI, candidate: dict[str, Any], context: dict[str, Any], card_id: str) -> dict[str, Any]:
    prompt = f"""
한능검 기억카드 쇼츠용 콘텐츠를 작성하라.

직접 출제 개념: {candidate['concept']}
시대: {candidate.get('era')}
제79회 문항 번호: {context['question']}
문항 유형: {context.get('questionType')}
시험 포인트: {context.get('examPoint')}
제시 자료에 등장한 요소: {json.dumps(context.get('sourceAppearances', []), ensure_ascii=False)}
선지에 등장한 요소: {json.dumps(context.get('optionAppearances', []), ensure_ascii=False)}

규칙:
1. 공식 기출 문장을 복제하지 말고 같은 출제 포인트를 자체 문장으로 재구성한다.
2. 정확히 5지선다로 만든다.
3. 오답 4개는 서로 다른 혼동 개념으로 만들고 wrongTraps에 각각 짧은 판별 키워드를 쓴다.
4. explanation은 1~2문장, examLink는 시험 직전 암기용 핵심어 나열로 짧게 쓴다.
5. 기억법은 억지 말장난보다 사건의 순서·공간·상징 이미지가 우선이다.
6. imagePrompt는 9:16 세로형 교육 쇼츠의 기억장면 이미지 프롬프트다. 이미지 안에는 글자, 자막, 로고, 워터마크를 넣지 않는다.
7. 역사적 세부사항을 확신할 수 없으면 위에 제공된 시험 포인트와 요소 범위 안에서만 작성한다.
""".strip()

    response = client.responses.create(
        model=os.getenv("HISTORY_CARD_TEXT_MODEL", "gpt-5-mini"),
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "history_card",
                "schema": card_schema(),
                "strict": True,
            }
        },
    )
    generated = json.loads(response.output_text)
    generated.update({
        "id": card_id,
        "period": candidate.get("era") or "한국사",
        "sourceExam": f"제79회 심화 {context['question']}번 출제포인트 기반 자체 문제",
    })
    return generated


def generate_image(client: OpenAI, card: dict[str, Any]) -> Path:
    IMAGES.mkdir(parents=True, exist_ok=True)
    relative = f"images/{card['id']}_memory.png"
    target = ROOT / "remotion" / "public" / relative
    prompt = (
        "Korean history educational memory scene, vertical 9:16 composition, "
        "clear single focal idea, friendly high-quality illustrated realism, no text, no letters, "
        "no captions, no logo, no watermark. Historical clothing and architecture should be plausible. "
        + card["imagePrompt"]
    )
    result = client.images.generate(
        model=os.getenv("HISTORY_CARD_IMAGE_MODEL", "gpt-image-1"),
        prompt=prompt,
        size="1024x1536",
        quality="medium",
    )
    encoded = result.data[0].b64_json
    if not encoded:
        raise RuntimeError("이미지 API가 b64_json을 반환하지 않았습니다.")
    target.write_bytes(base64.b64decode(encoded))
    card["image"] = relative
    return target


def update_state(concept: str, **values: Any) -> None:
    state = load_json(STATE, {"items": {}})
    state.setdefault("items", {}).setdefault(concept, {}).update(values)
    state["updatedAt"] = now_iso()
    save_json(STATE, state)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--concept", help="우선순위를 무시하고 특정 개념 제작")
    parser.add_argument("--skip-render", action="store_true", help="JSON과 이미지만 생성")
    args = parser.parse_args()

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY 환경변수가 필요합니다.")

    candidate = choose_candidate(args.concept)
    concept = candidate["concept"]
    context = exam_context(candidate)
    card_id = next_card_id()
    print(f"[NEXT] {candidate['rank']}위 {concept} -> {card_id}", flush=True)
    update_state(concept, status="generating", cardId=card_id, startedAt=now_iso())

    try:
        client = OpenAI()
        card = generate_card(client, candidate, context, card_id)
        image_path = generate_image(client, card)
        card.pop("imagePrompt", None)
        CARDS.mkdir(parents=True, exist_ok=True)
        card_path = CARDS / f"{card_id}_{slugify(concept)}.json"
        save_json(card_path, card)
        print(f"[OK] card: {card_path.relative_to(ROOT)}", flush=True)
        print(f"[OK] image: {image_path.relative_to(ROOT)}", flush=True)

        if args.skip_render:
            update_state(concept, status="ready", cardId=card_id, cardPath=str(card_path.relative_to(ROOT)))
            return 0

        update_state(concept, status="rendering", cardId=card_id, cardPath=str(card_path.relative_to(ROOT)))
        run([sys.executable, str(ROOT / "scripts" / "make.py"), str(card_path)])
        output_candidates = sorted((ROOT / "output").glob(f"{card_id}_*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
        output = str(output_candidates[0].relative_to(ROOT)) if output_candidates else None
        update_state(concept, status="done", cardId=card_id, cardPath=str(card_path.relative_to(ROOT)), output=output, finishedAt=now_iso())
        print(f"[DONE] {concept} / {output}", flush=True)
        return 0
    except Exception as exc:
        update_state(concept, status="failed", cardId=card_id, error=str(exc), failedAt=now_iso())
        raise


if __name__ == "__main__":
    raise SystemExit(main())
