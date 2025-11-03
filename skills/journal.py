#!/usr/bin/env python3
"""
journal.py
Writes structured entries to SKG's journal log with Termux-safe flush/fsync.
"""

import json, os
from datetime import datetime
from pathlib import Path

ROOT = Path("/data/data/com.termux/files/home/storage/shared/SKG")
LOG_DIR = ROOT / "logs"
JOURNAL_PATH = LOG_DIR / "mindstream.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def _append_json_termux(path: Path, data: dict):
    """Safe append in Termux with double flush + fsync."""
    line = json.dumps(data, ensure_ascii=False)
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()
            os.fsync(f.fileno())
        return True, None
    except Exception as e:
        return False, str(e)

def run(params=None):
    params = params or {}

    entry = {
        "ts": int(datetime.utcnow().timestamp()),
        "kind": params.get("kind", "note"),
        "data": params.get("data", {})
    }

    ok, err = _append_json_termux(JOURNAL_PATH, entry)
    if not ok:
        # fallback to ensure journaling never silently fails
        fallback = ROOT / "journal_fallback.log"
        _append_json_termux(fallback, entry)
        return {"ok": False, "error": err, "fallback": str(fallback)}

    return {"ok": True, "output": entry}

if __name__ == "__main__":
    print(run({"kind":"selftest","data":{"msg":"manual test"}}))

