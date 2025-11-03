#!/usr/bin/env python3
# skills/convert_logs_to_pearls.py
"""
One-shot / batch: convert existing .log files to HSPR pearls.
Never deletes logs. Use mode:"dry" to preview.
"""

import json
from pathlib import Path
from datetime import datetime
from skills import memory_pearl as mp

HOME = Path("/data/data/com.termux/files/home")
ROOT = HOME / "SKG_Portable"
LOGS = ROOT / "logs"

LOG_FILES = [
    "telemetry.log",
    "approval_history.log",
    "learning_summary.log",
    "api.log",
    "skill.log",
    "daemon.log",
    "mode.log",
    "ui.log",
    # add more if you like
]

def _read_json_lines(path: Path, max_lines=1000):
    if not path.exists(): return []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()[-max_lines:]
    out = []
    for l in lines:
        l = l.strip()
        if not l: continue
        try:
            out.append(json.loads(l))
        except Exception:
            # allow non-JSON lines to pass as text
            out.append({"text": l})
    return out

class Skill:
    name = "convert_logs_to_pearls"
    description = "Batch convert selected logs to HSPR pearls (dry-run or write)."

    def run(self, params):
        params = params or {}
        dry = bool(params.get("dry", True))
        kinds = params.get("kinds")  # optional filter: ["telemetry","approval",...]
        converted = []
        for fname in LOG_FILES:
            p = LOGS / fname
            rows = _read_json_lines(p)
            for r in rows:
                k = "telemetry" if "C" in r or "Fi" in r else \
                    "approval" if "decision" in r and "proposal" in r else \
                    "learning" if "learning" in r or "summary" in r else \
                    "logline"
                if kinds and k not in kinds:
                    continue
                msg = json.dumps(r, ensure_ascii=False)[:2000]
                if dry:
                    converted.append({"kind": k, "msg_preview": msg[:200], "src": fname})
                else:
                    out = mp.write_pearl(kind=k, msg=msg, context=f"from:{fname}", truth_anchor=True)
                    converted.append({"kind": k, "src": fname, "meta": out["meta"]})
        return {"ok": True, "dry": dry, "count": len(converted), "items": converted[:25]}

def run(params):
    return Skill().run(params)

