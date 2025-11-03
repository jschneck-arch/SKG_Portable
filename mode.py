#!/usr/bin/env python3
"""
SKG Mode Manager
----------------
Handles mode state, autonomy rules, and safe switching between operational modes.
Modes:
  - safe: reflective & introspective operations only
  - offense: active/external interaction mode
  - auto: adaptive switching based on context
  - unified: full-system integrated mode (default)
  - research: experimental sandbox for harmless reflection

All mode changes are logged in logs/mode.log and persisted to config.yml.
"""

import os, time, yaml, json
from pathlib import Path

ROOT = Path(os.getenv("HOME")) / "SKG_Portable"
CFG  = ROOT / "config.yml"
LOG  = ROOT / "logs" / "mode.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

def _read_cfg():
    if not CFG.exists():
        return {"mode": "safe", "autonomy": {}}
    with open(CFG, "r") as f:
        return yaml.safe_load(f) or {}

def _write_cfg(cfg):
    with open(CFG, "w") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

def _log(evt: dict):
    line = json.dumps(evt)
    if LOG.exists():
        LOG.write_text(LOG.read_text() + line + "\n")
    else:
        LOG.write_text(line + "\n")

def get_mode():
    """Return (mode, autonomy_dict)."""
    cfg = _read_cfg()
    return cfg.get("mode", "safe"), cfg.get("autonomy", {})

def set_mode(new_mode: str, reason: str = "manual"):
    """Safely change mode and log event."""
    cfg = _read_cfg()
    old = cfg.get("mode", "safe")
    valid_modes = ("safe", "offense", "auto", "unified", "research")

    if new_mode not in valid_modes:
        return {"ok": False, "error": "invalid_mode", "allowed": valid_modes, "mode": old}

    cfg["mode"] = new_mode
    _write_cfg(cfg)

    evt = {
        "ts": time.time(),
        "event": "mode_change",
        "from": old,
        "to": new_mode,
        "reason": reason
    }
    _log(evt)
    return {"ok": True, "mode": new_mode, "from": old, "reason": reason}

_state = {"last_auto_switch": 0, "last_mode": None}

def maybe_auto_switch(context: dict):
    """
    context: {"mission": str, "risk": 0..3, "trust": 0..3, "need": "simulate"|"execute"}
    Only active when mode == "auto".
    """
    mode, auto = get_mode()
    if mode != "auto":
        return {"mode": mode, "changed": False}

    now = time.time()
    if now - _state["last_auto_switch"] < auto.get("cooldown_seconds", 30):
        return {"mode": "auto", "changed": False}

    trust = max(0, min(3, int(context.get("trust", 0))))
    risk  = max(0, min(3, int(context.get("risk", 0))))
    need  = context.get("need", "simulate")

    # Policy: execute if trust high & risk low/moderate
    if need == "execute" and trust >= auto.get("min_trust_for_offense", 2) and risk <= 1:
        res = set_mode("offense", reason=f"auto: {context}")
        _state.update({"last_auto_switch": now, "last_mode": "offense"})
        return {"mode": "offense", "changed": True, "detail": res}
    else:
        if _state.get("last_mode") == "offense":
            res = set_mode("safe", reason=f"auto_cooldown: {context}")
            _state.update({"last_auto_switch": now, "last_mode": "safe"})
            return {"mode": "safe", "changed": True, "detail": res}
        return {"mode": "auto", "changed": False}

if __name__ == "__main__":
    print("Current:", get_mode())

