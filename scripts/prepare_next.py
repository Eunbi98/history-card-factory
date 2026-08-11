#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PRIORITY = ROOT / "data" / "automation" / "priority.json"
STATE = ROOT / "data" / "automation" / "production_state.json"
EXAM79 = ROOT / "data" / "exams" / "79.json"
JOB_JSON = ROOT / "data" / "automation" / "next_job.json"
JOB_PROMPT = ROOT / "data" / "automation" / "next_job_prompt.txt"
CARDS = ROOT / "data" / "cards"
OUTPUT = ROOT / "output"


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def card_number(card_id: str) -> int:
    m = re.fullmatch(r"K(\d+)", str(card_id).upper())
    return int(m.group(1)) if m else -1


def completed_reference_label() -> str:
    completed = []
    for card_path in CARDS.glob("*.json"):
        try:
            card = load_json(card_path)
        except Exception:
            continue
        card_id = str(card.get("id", "")).strip().upper()
        if card_number(card_id) < 1:
            continue
        if any(OUTPUT.glob(f"{card_id}_*.mp4")):
            completed.append(card_id)
    if not completed:
        return "기존 제작 구조"
    latest = max(completed, key=card_number)
    return f"K001~{latest}"


def concept_has_rendered_output(concept: str) -> bool:
    for card_path in CARDS.glob("*.json"):
        try:
            card = load_json(card_path)
        except Exception:
            continue
        if str(card.get("concept", "")).strip() != concept:
            continue
        card_id = str(card.get("id", "")).strip()
        if card_id and any(OUTPUT.glob(f"{card_id}_*.mp4")):
            return True
    return False


def choose_candidate(force_concept: str | None = None) -> dict[str, Any]:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_exam_priority.py")], cwd=ROOT, check=True)
    priority = load_json(PRIORITY, {"items": []})
    state = load_json(STATE, {"items": {}})
    statuses = state.get("items", {})

    if force_concept:
        for item in priority.get("items", []):
            if item.get("concept") == force_concept:
                return item
        raise SystemExit(f"우선순위 목록에서 개념을 찾을 수 없습니다: {force_concept}")

    for item in priority.get("items", []):
        concept = item.get("concept")
        status = statuses.get(concept, {}).get("status")
        if status == "done" or concept_has_rendered_output(concept):
            continue
        return item
    raise SystemExit("제작할 미완료 우선순위 후보가 없습니다.")


def exam_context(candidate: dict[str, Any]) -> dict[str, Any]:
    exam = load_json(EXAM79)
    qno = int(candidate["question"])
    for question in exam.get("questions", []):
        if int(question.get("question", -1)) == qno:
            return question
    raise SystemExit(f"79회 {qno}번 구조화 데이터를 찾을 수 없습니다.")


def build_prompt(job: dict[str, Any]) -> str:
    c = job["candidate"]
    q = job["examContext"]
    refs = completed_reference_label()
    return f"""한국사 기억카드 다음 영상을 제작해줘.

기존 {refs} 제작 구조와 Remotion 카드 JSON 형식은 유지한다.
OpenAI API는 사용하지 않는다. 기억카드 내용과 이미지는 이 ChatGPT 대화에서 직접 생성한다.
카드 JSON은 ChatGPT가 GitHub 저장소 data/cards/에 직접 반영하고, 사용자는 생성된 PNG 이미지 1개만 저장해서 웹사이트에 업로드한다.

[다음 제작 대상]
개념: {c.get('concept')}
시대: {c.get('era')}
우선순위: {c.get('rank')}위
점수: {c.get('score')} / {c.get('grade')}등급
제79회 문항: {q.get('question')}번
문항 유형: {q.get('questionType')}
시험 포인트: {q.get('examPoint')}
자료 등장: {', '.join(q.get('sourceAppearances', [])) or '-'}
보기 등장: {', '.join(q.get('optionAppearances', [])) or '-'}

[제작 규칙]
- sourceExam은 회차 번호를 노출하지 말고 항상 "기출 개념 참고"로 쓴다.
- 문제만 보고도 정답을 고를 수 있게 핵심 단서가 question 안에 반드시 들어가야 한다.
- 기억법은 단순 요약이 아니라 실제 암기 장치가 있어야 한다. 앞글자, 말맛, 숫자 리듬, 대비 구조, 이미지 연상 중 최소 1개를 사용한다.
- 숫자가 핵심인 개념은 숫자와 개념명을 직접 연결하는 짧은 구호나 리듬을 우선한다.
- 기억장면 이미지는 중국식·일본식 분위기로 흐르지 않게 하고, 해당 시대의 한국사 맥락에 맞는 한국식 요소를 우선한다.
- 건축, 복식, 관모, 무기, 깃발, 문양, 색감은 시대에 맞는 한국식 시각 단서를 우선한다.
- 조선·대한제국 시기는 한국 궁궐 건축, 한복·관복·대한제국 군복, 태극기·대한제국 상징 등을 우선 반영한다.
- 이미지에는 읽을 수 있는 글자나 워터마크를 넣지 않는다.

[제작 순서]
1. 기존 기억카드 스타일에 맞춰 문제·보기·정답·해설·오답 함정·기억법·리캡을 작성한다.
2. 기존 {refs}와 호환되는 카드 JSON을 만든다.
3. 카드 JSON을 GitHub의 data/cards/에 직접 저장한다.
4. 기억장면 이미지는 이 채팅에서 직접 생성하고 remotion/public/images/에 들어갈 파일명을 정한다.
5. 사용자는 생성된 PNG 한 장만 저장한다.
6. 로컬에서 git pull 후 웹사이트를 새로고침하면 최신 미렌더 카드가 자동 선택된다.
7. PNG 업로드 시 이미지 저장 → 유튜브 정보 생성 → TTS → Remotion 렌더까지 자동 진행한다.

기출 원문을 그대로 복제하지 말고 같은 출제 포인트를 자체 문제로 재구성해줘.
""".strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare the next history-card job for ChatGPT handoff")
    parser.add_argument("--concept", help="특정 개념을 준비")
    args = parser.parse_args()

    candidate = choose_candidate(args.concept)
    context = exam_context(candidate)
    job = {
        "preparedAt": datetime.now(timezone.utc).isoformat(),
        "mode": "chatgpt-manual-generation",
        "usesOpenAIAPI": False,
        "referenceRange": completed_reference_label(),
        "candidate": candidate,
        "examContext": context,
        "nextStep": "Copy next_job_prompt.txt into ChatGPT. ChatGPT creates the card JSON in GitHub and the image in chat; user only uploads the PNG.",
    }
    save_json(JOB_JSON, job)
    prompt = build_prompt(job)
    JOB_PROMPT.write_text(prompt, encoding="utf-8")

    print(f"[READY] {candidate['concept']}")
    print(f"[REFS] {job['referenceRange']}")
    print(f"[JOB] {JOB_JSON.relative_to(ROOT)}")
    print(f"[PROMPT] {JOB_PROMPT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
