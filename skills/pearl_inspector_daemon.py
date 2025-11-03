#!/usr/bin/env python3
# skills/pearl_inspector_daemon.py
"""
Scans the HSPR tree and writes:
 - logs/pearl_index.json (lightweight reference index)
 - logs/pearl_summaries.log (roll-up stats)
Daemon requires explicit start; does nothing unless called.
"""

import os, json, time
from pathlib import Path
from datetime import datetime
import threading

HOME = Path("/data/data/com.termux/files/home")
ROOT = HOME / "SKG_Portable"
MEM  = ROOT / "memory"
LOGS = ROOT / "logs"
LOGS.mkdir(parents=True, exist_ok=True)

INDEX = LOGS / "pearl_index.json"
OUTLOG = LOGS / "pearl_summaries.log"

_running = False
_thread = None

def _scan_once(max_files=5000):
    idx = []
    count = 0
    for p in MEM.rglob("pearl.hspr"):
        try:
            rel = p.relative_to(MEM)
        except Exception:
            rel = p.name
        # lightweight meta read (no strict parse): look for .meta lines
        meta = {"path": str(rel)}
        try:
            with open(p, "r", encoding="utf-8") as f:
                head = f.read(2048)
            for line in head.splitlines():
                line = line.strip()
                if line.startswith("ts:"):
                    meta["ts"] = line.split("ts:",1)[1].strip()
                elif line.startswith("id:"):
                    meta["id"] = line.split("id:",1)[1].strip()
                elif line.startswith("class:"):
                    meta["class"] = line.split("class:",1)[1].strip()
                elif line.startswith("hash:"):
                    meta["hash"] = line.split("hash:",1)[1].strip()
        except Exception:
            pass
        idx.append(meta)
        count += 1
        if count >= max_files:
            break

    # write index
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump({"updated": datetime.utcnow().isoformat(), "count": len(idx), "items": idx}, f, ensure_ascii=False)

    # append summary line
    with open(OUTLOG, "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": datetime.utcnow().isoformat(),
            "pearl_count": len(idx)
        }, ensure_ascii=False) + "\n")

    return {"ok": True, "count": len(idx), "index_path": str(INDEX)}

def _loop(interval):
    global _running
    while _running:
        _scan_once()
        time.sleep(interval)

class Skill:
    name = "pearl_inspector_daemon"
    description = "Index and summarize pearls. start/stop/status/once."

    def run(self, params):
        global _running, _thread
        params = params or {}
        cmd = params.get("cmd", "status")
        interval = int(params.get("interval", 300))

        if cmd == "start":
            if _running:
                return {"ok": True, "message": "already running"}
            _running = True
            _thread = threading.Thread(target=_loop, args=(interval,), daemon=True)
            _thread.start()
            return {"ok": True, "message": "pearl_inspector started", "interval": interval}
        if cmd == "stop":
            _running = False
            return {"ok": True, "message": "stopping"}
        if cmd == "status":
            return {"ok": True, "running": _running}
        if cmd == "once":
            return _scan_once()
        return {"ok": False, "error": "unknown cmd"}

def run(params):
    return Skill().run(params)

