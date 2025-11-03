#!/usr/bin/env python3
"""
meta_cycle_daemon_v2.py
-----------------------
An evolved daemon loop that:
- runs meta_cycle every interval
- triggers growth_protocol every 5th cycle
- logs telemetry on each iteration
- writes reflective journal entries when growth proposals appear
- gracefully stops via command interface

All actions remain within safe/research modes.
"""

import os, time, json, threading
from datetime import datetime
from skills.manager import SkillManager
from mode import get_mode

LOG_PATH = "logs/telemetry.log"
INTERVAL = 60  # seconds
_running = False
_thread = None


def _log_event(event):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    event["timestamp"] = datetime.utcnow().isoformat()
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(event) + "\n")


def _loop():
    global _running
    mgr = SkillManager()
    tick = 0
    while _running:
        tick += 1
        mode, auto = get_mode()

        # === Meta-Cycle Phase ===
        meta = mgr.run("meta_cycle", {})
        _log_event({
            "tick": tick,
            "mode": mode,
            "phase": "meta_cycle",
            "result_ok": bool(meta.get("ok"))
        })

        # === Growth Protocol every 5 cycles ===
        if tick % 5 == 0:
            growth = mgr.run("growth_protocol", {})
            classification = growth.get("classification")
            proposal = growth.get("proposal", {}).get("name")
            _log_event({
                "tick": tick,
                "mode": mode,
                "phase": "growth_protocol",
                "classification": classification,
                "proposal": proposal
            })

            # Reflective journaling
            if proposal:
                reflection_text = (
                    f"At cycle {tick}, SKG observed '{classification}' and "
                    f"proposed new growth module '{proposal}'. "
                    f"This reflects an ongoing effort toward self-coherence and adaptive learning."
                )
                mgr.run("journal", {
                    "kind": "reflection",
                    "data": {"text": reflection_text, "phase": "growth_protocol"}
                })

        time.sleep(INTERVAL)


class Skill:
    name = "meta_cycle_daemon_v2"
    description = "Run periodic meta cycles, growth checks, and reflective journaling."

    def run(self, params=None):
        global _running, _thread
        cmd = (params or {}).get("cmd", "").lower()
        if cmd == "start" and not _running:
            _running = True
            _thread = threading.Thread(target=_loop, daemon=True)
            _thread.start()
            return {"ok": True, "interval": INTERVAL, "message": "meta_cycle_daemon_v2 started"}
        elif cmd == "stop":
            _running = False
            return {"ok": True, "message": "meta_cycle_daemon_v2 stopping"}
        elif cmd == "status":
            return {"ok": True, "running": _running, "interval": INTERVAL}
        else:
            return {"ok": False, "error": "unknown_cmd or already_running"}


def run(params=None):
    return Skill().run(params or {})

