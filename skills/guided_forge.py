#!/usr/bin/env python3
"""
guided_forge.py
---------------
Allows SKG to materialize new modules when in 'stable' or 'improving' learning states.
- Reads from the latest learning_summary.log
- If stability is confirmed, it activates a forge request
- Requires human confirmation to commit actual writes (dry=True by default)
"""

import os, json
from datetime import datetime
from skills.manager import SkillManager

SUMMARY_PATH = "logs/learning_summary.log"

def _read_latest_summary():
    if not os.path.exists(SUMMARY_PATH):
        return None
    with open(SUMMARY_PATH, "r") as f:
        lines = f.readlines()
    if not lines:
        return None
    try:
        return json.loads(lines[-1])
    except Exception:
        return None

def run(params=None):
    mgr = SkillManager()
    params = params or {}

    summary = _read_latest_summary()
    if not summary:
        return {"ok": False, "error": "no_summary"}

    state = summary["summary"]["state"]
    averages = summary["summary"]["averages"]
    stability_ok = state in ("stable", "improving")

    if not stability_ok:
        return {
            "ok": False,
            "state": state,
            "note": "Not forging; system not stable or improving."
        }

    # Example self-proposal template
    proposed_name = params.get("name", "self_state_reporter")
    proposal = {
        "name": proposed_name,
        "purpose": "Generate JSON snapshot of SKG's latest coherence and summaries.",
        "files": {
            f"skills/{proposed_name}.py": f"""#!/usr/bin/env python3
import json
from datetime import datetime
def run(params=None):
    try:
        from skills.learning_summarizer import _read_json_lines
        data = _read_json_lines('logs/learning_summary.log', 5)
        latest = data[-1] if data else {{}}
        return {{
            'ok': True,
            'timestamp': datetime.utcnow().isoformat(),
            'latest_summary': latest
        }}
    except Exception as e:
        return {{'ok': False, 'error': str(e)}}
"""
        }
    }

    # dry mode default unless explicitly overridden
    dry = params.get("dry", True)
    if dry:
        return {
            "ok": True,
            "dry": True,
            "state": state,
            "proposal": proposal,
            "note": "Ready for human confirmation via forge_request."
        }

    # If explicitly allowed to write (rare)
    resp = mgr.run("forge_request", proposal)
    return {"ok": True, "state": state, "forged": resp}

