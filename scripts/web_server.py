#!/usr/bin/env python3
from __future__ import annotations

import json
import mimetypes
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
STATE = ROOT / "data" / "automation" / "production_state.json"
JOB_PROMPT = ROOT / "data" / "automation" / "next_job_prompt.txt"


def safe_path(base: Path, relative: str) -> Path | None:
    target = (base / relative).resolve()
    try:
        target.relative_to(base.resolve())
    except ValueError:
        return None
    return target


class Handler(BaseHTTPRequestHandler):
    server_version = "HistoryCardFactory/0.2"

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

    def do_GET(self) -> None:
        path = unquote(urlparse(self.path).path)
        if path == "/api/status":
            if STATE.exists():
                self.send_json(json.loads(STATE.read_text(encoding="utf-8")))
            else:
                self.send_json({"items": {}})
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
        if path != "/api/prepare-next":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0") or 0)
        payload = {}
        if length:
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
            except Exception:
                payload = {}

        command = [sys.executable, str(ROOT / "scripts" / "prepare_next.py")]
        concept = payload.get("concept")
        if concept:
            command += ["--concept", str(concept)]

        try:
            result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
            prompt = JOB_PROMPT.read_text(encoding="utf-8") if result.returncode == 0 and JOB_PROMPT.exists() else ""
            self.send_json({
                "ok": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "prompt": prompt,
            }, 200 if result.returncode == 0 else 500)
        except Exception as exc:
            self.send_json({"ok": False, "error": str(exc)}, 500)

    def log_message(self, fmt: str, *args) -> None:
        print("[WEB]", fmt % args)


def main() -> int:
    host = "127.0.0.1"
    port = 8000
    print(f"History Card Factory: http://{host}:{port}")
    print("OpenAI API는 사용하지 않습니다. 다음 제작 대상을 준비한 뒤 ChatGPT 대화에서 카드와 이미지를 생성합니다.")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
