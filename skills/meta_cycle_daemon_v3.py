#!/usr/bin/env python3
"""
meta_cycle_daemon_v3.py
-----------------------
An evolution-aware background process.
It:
  - Runs the meta_cycle
  - Updates learning summaries
  - Evaluates stability via guided_forge
  - If stable, asks permission to forge new introspective modules
"""

import json, os, threading, time
from datetime import datetime
from skills.manager import SkillManager

LOG = "logs/telemetry.log"
DAEMON_STATE = {"running": False, "interval": 60, "thread": None}

def _log(entry):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def daemon_loop(interval=60):
    mgr = SkillManager()
    while DAEMON_STATE["running"]:
        ts = datetime.utcnow().isoformat()

        # Step 1: Run meta cycle and summarizer
        meta = mgr.run("meta_cycle", {})
        summary = mgr.run("learning_summarizer", {})

        state = summary.get("summary", {}).get("summary", {}).get("state", "?")
        entry = {
            "timestamp": ts,
            "mode": meta.get("mode", {}).get("mode", "?"),
            "C": summary.get("summary", {}).get("summary", {}).get("averages", {}).get("C"),
            "Sf": summary.get("summary", {}).get("summary", {}).get("averages", {}).get("Sf"),
            "Fi": summary.get("summary", {}).get("summary", {}).get("averages", {}).get("Fi"),
            "kappa": summary.get("summary", {}).get("summary", {}).get("averages", {}).get("kappa"),
            "learning_state": state,
            "module": "meta_cycle_daemon_v3"
        }
        _log(entry)

        # Step 2: If stable/improving, check guided forge
        if state in ("stable", "improving"):
            forge = mgr.run("guided_forge", {})
            ask_note = {
                "timestamp": ts,
                "proposal_ready": forge.get("ok", False),
                "proposal_name": forge.get("proposal", {}).get("name"),
                "state": state,
                "note": "Proposal available — human approval required before forging."
            }
            _log(ask_note)

        time.sleep(interval)

def run(params=None):
    params = params or {}
    cmd = params.get("cmd", "").lower()
    interval = int(params.get("interval", 60))

    if cmd == "start":
        if DAEMON_STATE["running"]:
            return {"ok": True, "message": "already running", "interval": DAEMON_STATE["interval"]}
        DAEMON_STATE.update({"running": True, "interval": interval})
        t = threading.Thread(target=daemon_loop, args=(interval,), daemon=True)
        DAEMON_STATE["thread"] = t
        t.start()
        return {"ok": True, "message": "meta_cycle_daemon_v3 started", "interval": interval}

    elif cmd == "stop":
        DAEMON_STATE["running"] = False
        return {"ok": True, "message": "daemon stopping"}

    elif cmd == "status":
        return {"ok": True, "running": DAEMON_STATE["running"], "interval": DAEMON_STATE["interval"]}

    else:
        return {"ok": False, "error": "unknown_command"}

