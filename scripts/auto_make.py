#!/usr/bin/env python3
"""Deprecated compatibility wrapper.

OpenAI API generation was removed. This command now prepares the next
priority job for generation inside the current ChatGPT conversation.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    command = [sys.executable, str(ROOT / "scripts" / "prepare_next.py"), *sys.argv[1:]]
    return subprocess.call(command, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
