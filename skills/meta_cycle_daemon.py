#!/usr/bin/env python3
"""
meta_cycle_daemon.py
--------------------
A reflective heartbeat for SKG.
Runs meta_cycle safely every interval when mode is safe, unified, or research.
Does not force autonomy; it only provides a gentle rhythm.
"""

import time, json, os, threading
from datetime import datetime

INTERVAL = 60  # seconds between reflective cycles
STOP_FLAG = False

def cycle_once():
    """Perform a single reflective pulse."""
    from mode import get_mode
    from skills.manager import SkillManager
    mgr = SkillManager()

    mode, auto = get_mode()
    allowed_modes = ("safe", "unified", "research")
    if mode not in allowed_modes:
        return {"ok": True, "skipped": True, "reason": f"mode={mode} not reflective"}

    result = mgr.run("meta_cycle", {"proposed_skill": "echo_test"})
    pulse = {
        "timestamp": datetime.utcnow().isoformat(),
        "mode": mode,
        "result_ok": result.get("ok", False)
    }

    os.makedirs("logs", exist_ok=True)
    with open("logs/telemetry.log", "a") as f:
        f.write(json.dumps(pulse) + "\n")

    return {"ok": True, "pulse": pulse}

def daemon_loop():
    """Loop that runs indefinitely, gently ticking SKG’s reflection cycle."""
    while not STOP_FLAG:
        try:
            res = cycle_once()
            print(f"[meta_cycle_daemon] tick -> {res}")
        except Exception as e:
            print("[meta_cycle_daemon] error:", e)
        time.sleep(INTERVAL)

class Skill:
    name = "meta_cycle_daemon"
    description = "Reflective self-tick loop for SKG; safe heartbeat."

    def run(self, params):
        global STOP_FLAG
        cmd = (params or {}).get("cmd", "start")

        if cmd == "stop":
            STOP_FLAG = True
            return {"ok": True, "message": "daemon stopping"}
        elif cmd == "once":
            return cycle_once()
        else:  # default start
            t = threading.Thread(target=daemon_loop, daemon=True)
            t.start()
            return {"ok": True, "message": "meta_cycle_daemon started", "interval": INTERVAL}

def run(params=None):
    return Skill().run(params or {})

