#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import mimetypes
import re
import subprocess
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
STATE = ROOT / "data" / "automation" / "production_state.json"
JOB_PROMPT = ROOT / "data" / "automation" / "next_job_prompt.txt"
CARDS = ROOT / "data" / "cards"
YOUTUBE = ROOT / "data" / "youtube"
OUTPUT = ROOT / "output"


def safe_path(base: Path, relative: str) -> Path | None:
    target = (base / relative).resolve()
    try:
        target.relative_to(base.resolve())
    except ValueError:
        return None
    return target


def read_json(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def find_card(card_id: str) -> Path | None:
    key = card_id.upper()
    for path in CARDS.glob("*.json"):
        try:
            if str(read_json(path).get("id", "")).upper() == key:
                return path
        except Exception:
            continue
    return None


def output_for(card_id: str) -> Path | None:
    matches = sorted(OUTPUT.glob(f"{card_id}_*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def card_summary(path: Path) -> dict:
    card = read_json(path)
    image_rel = card.get("image", "")
    image_path = ROOT / "remotion" / "public" / image_rel if image_rel else None
    card_id = str(card.get("id", path.stem))
    out = output_for(card_id)
    meta_path = YOUTUBE / f"{card_id}.json"
    meta = read_json(meta_path, None) if meta_path.exists() else None
    return {
        "id": card_id,
        "title": card.get("title", ""),
        "concept": card.get("concept", ""),
        "period": card.get("period", ""),
        "image": image_rel,
        "imageExists": bool(image_path and image_path.exists()),
        "output": str(out.relative_to(ROOT)).replace("\\", "/") if out else None,
        "outputExists": bool(out),
        "youtube": meta,
    }


def merged_state() -> dict:
    state = read_json(STATE, {"items": {}})
    items = state.setdefault("items", {})
    if CARDS.exists():
        for card_path in CARDS.glob("*.json"):
            try:
                card = read_json(card_path, {})
                card_id = str(card.get("id", "")).strip()
                concept = str(card.get("concept", "")).strip()
                if not card_id or not concept:
                    continue
                out = output_for(card_id)
                if out:
                    items.setdefault(concept, {})
                    items[concept].update({
                        "status": "done",
                        "cardId": card_id,
                        "cardPath": str(card_path.relative_to(ROOT)).replace("\\", "/"),
                        "output": str(out.relative_to(ROOT)).replace("\\", "/"),
                        "inferredFromOutput": True,
                    })
            except Exception:
                continue
    return state


def set_state(concept: str, **values) -> None:
    if not concept:
        return
    state = read_json(STATE, {"items": {}})
    state.setdefault("items", {}).setdefault(concept, {}).update(values)
    state["updatedAt"] = datetime.now(timezone.utc).isoformat()
    write_json(STATE, state)


class Handler(BaseHTTPRequestHandler):
    server_version = "HistoryCardFactory/0.4"

    def send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(404)
            return
        data = path.read_bytes()
        content_type, _ = mimetypes.guess_type(path.name)
        self.send_response(200)
        self.send_header("Content-Type", content_type or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def read_payload(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if not length:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:
        path = unquote(urlparse(self.path).path)
        if path == "/api/status":
            self.send_json(merged_state())
            return
        if path == "/api/cards":
            cards = []
            for card_path in sorted(CARDS.glob("*.json")):
                try:
                    cards.append(card_summary(card_path))
                except Exception:
                    continue
            self.send_json({"cards": cards})
            return
        if path == "/":
            self.send_file(WEB / "index.html")
            return
        if path.startswith("/data/") or path.startswith("/output/") or path.startswith("/remotion/public/"):
            target = safe_path(ROOT, path.lstrip("/"))
            if target is None:
                self.send_error(403)
            else:
                self.send_file(target)
            return
        target = safe_path(WEB, path.lstrip("/"))
        if target is None:
            self.send_error(403)
        else:
            self.send_file(target)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/prepare-next":
            self.handle_prepare()
            return
        if path == "/api/upload-render":
            self.handle_upload_render()
            return
        if path == "/api/build-youtube":
            self.handle_build_youtube()
            return
        self.send_error(404)

    def handle_prepare(self) -> None:
        try:
            payload = self.read_payload()
        except Exception:
            payload = {}
        command = [sys.executable, str(ROOT / "scripts" / "prepare_next.py")]
        concept = payload.get("concept")
        if concept:
            command += ["--concept", str(concept)]
        try:
            result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
            prompt = JOB_PROMPT.read_text(encoding="utf-8") if result.returncode == 0 and JOB_PROMPT.exists() else ""
            self.send_json({"ok": result.returncode == 0, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr, "prompt": prompt}, 200 if result.returncode == 0 else 500)
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, 500)

    def handle_build_youtube(self) -> None:
        try:
            payload = self.read_payload()
            card_id = str(payload.get("cardId", ""))
            card_path = find_card(card_id)
            if not card_path:
                self.send_json({"ok": False, "error": f"카드 없음: {card_id}"}, 404)
                return
            result = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_youtube_meta.py"), str(card_path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode != 0:
                self.send_json({"ok": False, "error": result.stderr or result.stdout}, 500)
                return
            meta = read_json(YOUTUBE / f"{card_id}.json")
            self.send_json({"ok": True, "youtube": meta})
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, 500)

    def handle_upload_render(self) -> None:
        try:
            payload = self.read_payload()
            card_id = str(payload.get("cardId", "")).upper()
            image_data = str(payload.get("imageData", ""))
            card_path = find_card(card_id)
            if not card_path:
                self.send_json({"ok": False, "error": f"카드 JSON을 찾을 수 없습니다: {card_id}"}, 404)
                return
            if not image_data.startswith("data:image/png;base64,"):
                self.send_json({"ok": False, "error": "PNG 이미지만 업로드할 수 있습니다."}, 400)
                return
            encoded = image_data.split(",", 1)[1]
            raw = base64.b64decode(encoded, validate=True)
            if len(raw) > 20 * 1024 * 1024:
                self.send_json({"ok": False, "error": "이미지는 20MB 이하로 업로드하세요."}, 400)
                return

            card = read_json(card_path)
            image_rel = str(card.get("image", ""))
            if not re.fullmatch(r"images/[A-Za-z0-9_-]+\.png", image_rel):
                self.send_json({"ok": False, "error": f"안전하지 않은 이미지 경로: {image_rel}"}, 400)
                return
            image_path = ROOT / "remotion" / "public" / image_rel
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image_path.write_bytes(raw)

            concept = str(card.get("concept", ""))
            set_state(concept, status="rendering", cardId=card_id, cardPath=str(card_path.relative_to(ROOT)))

            meta_result = subprocess.run([sys.executable, str(ROOT / "scripts" / "build_youtube_meta.py"), str(card_path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if meta_result.returncode != 0:
                raise RuntimeError(meta_result.stderr or meta_result.stdout)

            result = subprocess.run([sys.executable, str(ROOT / "scripts" / "make.py"), str(card_path)], cwd=ROOT, text=True, capture_output=True, check=False)
            if result.returncode != 0:
                set_state(concept, status="failed", cardId=card_id, error=result.stderr or result.stdout)
                self.send_json({"ok": False, "error": result.stderr or result.stdout, "stdout": result.stdout}, 500)
                return

            out = output_for(card_id)
            meta = read_json(YOUTUBE / f"{card_id}.json")
            set_state(concept, status="done", cardId=card_id, cardPath=str(card_path.relative_to(ROOT)), output=str(out.relative_to(ROOT)) if out else None)
            self.send_json({
                "ok": True,
                "card": card_summary(card_path),
                "youtube": meta,
                "output": "/" + str(out.relative_to(ROOT)).replace("\\", "/") if out else None,
                "stdout": result.stdout,
            })
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, 500)

    def log_message(self, fmt: str, *args) -> None:
        print("[WEB]", fmt % args)


def main() -> int:
    host = "127.0.0.1"
    port = 8000
    print(f"History Card Factory: http://{host}:{port}")
    print("OpenAI API는 사용하지 않습니다. 기존 렌더 결과도 자동으로 완료 상태에 반영합니다.")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
