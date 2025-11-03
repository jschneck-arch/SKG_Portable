#!/usr/bin/env python3
"""
approval_reflector.py
Records, audits, and summarizes SKG's human-approved decisions.
Creates both approval_history.log (decision ledger)
and journal.log (reflective trace).
"""

import json
import os
from datetime import datetime
from pathlib import Path
from statistics import mean

# === ABSOLUTE PATHS =======================================================
ROOT = Path("/data/data/com.termux/files/home/SKG_Portable")
LOG_DIR = ROOT / "logs"
LOG_PATH = LOG_DIR / "approval_history.log"
JOURNAL_PATH = LOG_DIR / "journal.log"
LOG_DIR.mkdir(parents=True, exist_ok=True)


# === UTILITIES ===========================================================

def _append_json(path: Path, data: dict):
    """Append JSON with flush & sync to guarantee persistence in Termux."""
    line = json.dumps(data, ensure_ascii=False)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
        os.fsync(f.fileno())


def _read_json_lines(path: Path, max_lines: int = 200):
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()[-max_lines:]
    out = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


# === MAIN RUN FUNCTION ===================================================

def run(params=None):
    params = params or {}
    mode = params.get("mode", "record")

    # ------------------------------------------------------------------
    # SUMMARY MODE
    # ------------------------------------------------------------------
    if mode == "summary":
        entries = _read_json_lines(LOG_PATH, 500)
        if not entries:
            return {"ok": True, "summary": {"note": "no approvals yet"}}

        approved = [e for e in entries if e.get("decision") == "approved"]
        rejected = [e for e in entries if e.get("decision") == "rejected"]
        deferred = [e for e in entries if e.get("decision") == "deferred"]
        total = len(entries)

        ratio = len(approved) / total if total else None

        return {
            "ok": True,
            "summary": {
                "total": total,
                "approved": len(approved),
                "rejected": len(rejected),
                "deferred": len(deferred),
                "approval_ratio": ratio,
                "recent_5": entries[-5:]
            }
        }

    # ------------------------------------------------------------------
    # RECORD MODE
    # ------------------------------------------------------------------
    proposal = params.get("proposal")
    decision = params.get("decision")
    reason = params.get("reason", "unspecified")

    if not proposal or not decision:
        return {"ok": False, "error": "missing proposal or decision"}

    record = {
        "proposal": proposal,
        "decision": decision,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Record into approval history
    _append_json(LOG_PATH, record)

    # Create corresponding journal entry
    journal_entry = {
        "kind": "approval_reflection",
        "data": record
    }

    # Explicitly ensure file is created even if absent
    try:
        _append_json(JOURNAL_PATH, journal_entry)
    except Exception as e:
        # fallback: try direct absolute write
        alt_path = Path("/data/data/com.termux/files/home/SKG_Portable/logs/journal.log")
        try:
            _append_json(alt_path, journal_entry)
        except Exception as inner:
            return {"ok": False, "error": f"journal write failed: {inner}"}

    return {"ok": True, "recorded": record}


# === ENTRYPOINT ==========================================================
if __name__ == "__main__":
    print(json.dumps(run(), indent=2))

