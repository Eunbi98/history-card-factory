#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
        status = statuses.get(item.get("concept"), {}).get("status")
        if status != "done":
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
    return f"""한국사 기억카드 다음 영상을 제작해줘.

기존 K001~K005 제작 구조와 Remotion 카드 JSON 형식은 유지한다.
OpenAI API는 사용하지 않는다. 기억카드 내용과 이미지는 이 ChatGPT 대화에서 직접 생성한다.

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
- 문제만 보고도 정답을 고를 수 있게 핵심 단서가 question 안에 반드시 들어가야 한다. 단순히 "어떤 나라일까요?"처럼 단서 없는 질문은 만들지 않는다.
- 기억법은 단순 요약이 아니라 실제 암기 장치가 있어야 한다. 앞글자, 말맛, 숫자 리듬, 대비 구조, 이미지 연상 중 최소 1개를 사용한다.
- 숫자가 핵심인 개념은 숫자와 개념명을 직접 연결하는 짧은 구호나 리듬을 우선한다.

[제작 순서]
1. 기존 기억카드 스타일에 맞춰 문제·보기·정답·해설·오답 함정·기억법·리캡을 작성한다.
2. 기존 data/cards K001~K005와 호환되는 카드 JSON을 만든다.
3. 기억장면 이미지는 API가 아니라 이 채팅에서 직접 생성한다.
4. 생성 이미지가 remotion/public/images/에 들어갈 파일명을 정한다.
5. JSON과 이미지가 준비되면 기존 scripts/make.py → TTS → Remotion 렌더 구조를 사용한다.

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
        "candidate": candidate,
        "examContext": context,
        "nextStep": "Copy next_job_prompt.txt into the current ChatGPT conversation and generate the card JSON and image there.",
    }
    save_json(JOB_JSON, job)
    prompt = build_prompt(job)
    JOB_PROMPT.write_text(prompt, encoding="utf-8")

    print(f"[READY] {candidate['concept']}")
    print(f"[JOB] {JOB_JSON.relative_to(ROOT)}")
    print(f"[PROMPT] {JOB_PROMPT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
