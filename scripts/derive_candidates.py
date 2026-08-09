#!/usr/bin/env python3
"""Build a deduplicated derived-question candidate queue from one history-card JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "remotion" / "src" / "card.json"
DEFAULT_REGISTRY = ROOT / "data" / "derivation" / "concept_registry.json"
DEFAULT_QUEUE = ROOT / "data" / "derivation" / "derived_queue.json"


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def normalize_registry(raw: Any) -> dict[str, dict]:
    if isinstance(raw, dict) and "concepts" in raw:
        items = raw["concepts"]
    elif isinstance(raw, list):
        items = raw
    else:
        items = []

    result: dict[str, dict] = {}
    for item in items:
        if isinstance(item, str):
            result[item] = {"conceptId": item, "status": "registered"}
        elif isinstance(item, dict) and item.get("conceptId"):
            result[item["conceptId"]] = item
    return result


def make_candidate(source: dict, choice: dict) -> dict:
    return {
        "sourceCardId": source["id"],
        "sourceQuestion": source["question"],
        "sourceChoiceNumber": choice["number"],
        "sourceChoiceText": choice["text"],
        "conceptId": choice["conceptId"],
        "conceptTitle": choice["conceptTitle"],
        "status": "candidate",
        "questionType": "기출형 5지선다",
        "generationPlan": {
            "targetConcept": choice["conceptTitle"],
            "preserveExamSkill": True,
            "copySourceWording": False,
            "requiredFields": [
                "question",
                "choices",
                "correctChoice",
                "explanation",
                "wrongTraps",
                "memoryScene",
                "memoryTip"
            ],
            "rule": "기출 출제포인트는 유지하되 문제·보기 문장은 자체 작성한다."
        }
    }


def build_queue(source: dict, registry: dict[str, dict], existing_queue: list[dict]) -> dict:
    source_concept = None
    for choice in source.get("choices", []):
        if choice.get("number") == source.get("correctChoice"):
            source_concept = choice.get("conceptId")
            break

    known = set(registry.keys())
    known.update(
        item.get("conceptId")
        for item in existing_queue
        if isinstance(item, dict) and item.get("conceptId")
    )

    candidates: list[dict] = []
    skipped: list[dict] = []

    for choice in source.get("choices", []):
        cid = choice.get("conceptId")
        title = choice.get("conceptTitle")
        if not choice.get("deriveQuestion", False) or not cid or not title:
            continue

        reason = None
        if cid == source_concept:
            reason = "source_correct_concept"
        elif cid in known:
            reason = "already_registered_or_queued"

        if reason:
            skipped.append(
                {
                    "conceptId": cid,
                    "conceptTitle": title,
                    "choiceNumber": choice.get("number"),
                    "reason": reason,
                }
            )
            continue

        candidates.append(make_candidate(source, choice))
        known.add(cid)

    max_count = int(
        source.get("derivationPolicy", {}).get("maxDerivedVideos", 5)
    )
    candidates = candidates[:max_count]

    return {
        "sourceCardId": source["id"],
        "sourceTitle": source.get("title"),
        "policy": source.get("derivationPolicy", {}),
        "summary": {
            "choiceCount": len(source.get("choices", [])),
            "candidateCount": len(candidates),
            "skippedCount": len(skipped),
        },
        "candidates": candidates,
        "skipped": skipped,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--output", default=str(DEFAULT_QUEUE))
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = ROOT / source_path

    registry_path = Path(args.registry)
    if not registry_path.is_absolute():
        registry_path = ROOT / registry_path

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = ROOT / output_path

    source = load_json(source_path)
    registry = normalize_registry(load_json(registry_path, {"concepts": []}))

    previous = load_json(output_path, {"candidates": []})
    previous_candidates = previous.get("candidates", []) if isinstance(previous, dict) else []

    if not source.get("choices"):
        raise SystemExit(
            "card.json에 choices가 없습니다. v2 5지선다 패치를 먼저 적용하세요."
        )

    queue = build_queue(source, registry, previous_candidates)
    save_json(output_path, queue)

    print("=" * 58)
    print(" History Card Factory - Derivation Queue")
    print("=" * 58)
    print(f"source   : {queue['sourceCardId']} / {queue['sourceTitle']}")
    print(f"choices  : {queue['summary']['choiceCount']}")
    print(f"candidates: {queue['summary']['candidateCount']}")
    print(f"skipped  : {queue['summary']['skippedCount']}")
    print()
    for item in queue["candidates"]:
        print(
            f"[ADD] {item['conceptId']} | {item['conceptTitle']} "
            f"(source choice {item['sourceChoiceNumber']})"
        )
    for item in queue["skipped"]:
        print(
            f"[SKIP] {item['conceptId']} | {item['conceptTitle']} "
            f"({item['reason']})"
        )
    print()
    print(f"queue    : {output_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
