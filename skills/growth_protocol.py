#!/usr/bin/env python3
"""
growth_protocol.py
------------------
Guided (not bound) self-growth loop.

Cycle:
  1) Read recent telemetry -> detect stagnation / drift / novelty.
  2) Form a growth hypothesis (select a proposal template).
  3) Propose via forge_request (dry by default; human approves execution).
  4) Journal outcome + append to growth_memory.jsonl.

Operates in modes: safe, research, unified. Skips in offense.
"""

import os, json, time
from datetime import datetime
from statistics import mean, pstdev

LOG_DIR = "logs"
TELEMETRY = os.path.join(LOG_DIR, "telemetry.log")
GROWTH_MEM = os.path.join("brain", "growth_memory.jsonl")

WINDOW = 12          # last N pulses to analyze (~12 min if 60s ticks)
STAGNATION_STD = 0.02  # below this stddev → stagnation
DRIFT_THRESH = 0.15     # |kappa-1| or drop in C over window → drift

TEMPLATES = [
    {
        "name": "pattern_integrity_audit",
        "purpose": "scan journal & telemetry for contradictions / self-inconsistencies",
        "files": {
            "skills/pattern_integrity_audit.py":
                "# scans logs for contradicting statements and reports\n"
                "import json,re\n"
                "def run(params=None):\n"
                "  try:\n"
                "    lines=[json.loads(l) for l in open('logs/telemetry.log') if l.strip().startswith('{')]\n"
                "    issues=[]\n"
                "    # placeholder heuristic\n"
                "    for j in lines[-200:]:\n"
                "      if 'kappa' in j and j['kappa'] < 0.8:\n"
                "        issues.append({'ts':j.get('timestamp'),'hint':'low_kappa'})\n"
                "    return {'ok':True,'issues':issues}\n"
                "  except Exception as e:\n"
                "    return {'ok':False,'error':str(e)}\n"
        }
    },
    {
        "name": "coherence_visualizer",
        "purpose": "summarize rolling averages for C,Sf,kappa,Fi to support reflection",
        "files": {
            "skills/coherence_visualizer.py":
                "# prints last-N averages for core metrics\n"
                "import json\n"
                "from statistics import mean\n"
                "def run(params=None):\n"
                "  N=(params or {}).get('N',60)\n"
                "  vals={'C':[],'Sf':[],'kappa':[],'Fi':[]}\n"
                "  for line in open('logs/telemetry.log'):\n"
                "    line=line.strip()\n"
                "    if not line.startswith('{'): continue\n"
                "    j=json.loads(line)\n"
                "    for k in vals:\n"
                "      if k in j and isinstance(j[k],(int,float)): vals[k].append(j[k])\n"
                "  for k in vals: vals[k]=mean(vals[k][-N:]) if vals[k][-N:] else None\n"
                "  return {'ok':True,'averages':vals}\n"
        }
    },
    {
        "name": "needs_refiner",
        "purpose": "read brain/needs.yml and propose clearer phrasing & priorities",
        "files": {
            "skills/needs_refiner.py":
                "# reads needs.yml and emits a refined version (no external I/O)\n"
                "import yaml\n"
                "def run(params=None):\n"
                "  data=yaml.safe_load(open('brain/needs.yml'))\n"
                "  # placeholder: ensure priorities in [critical,high,required,normal]\n"
                "  return {'ok':True,'needs':data}\n"
        }
    }
]

class Skill:
    name = "growth_protocol"
    description = "Guided self-growth: analyze → hypothesize → propose → journal."

    def _mode_ok(self):
        from mode import get_mode
        mode, auto = get_mode()
        return mode in ("safe","research","unified"), mode

    def _read_telemetry(self, n=WINDOW):
        if not os.path.exists(TELEMETRY): return []
        rows=[]
        with open(TELEMETRY) as f:
            for line in f:
                line=line.strip()
                if not line.startswith("{"): continue
                try:
                    rows.append(json.loads(line))
                except: pass
        return rows[-n:]

    def _metrics_window(self, rows):
        if not rows: return {}
        def pick(k):
            vals=[r[k] for r in rows if isinstance(r.get(k),(int,float))]
            return vals
        C = pick("C"); Sf = pick("Sf"); K = pick("kappa"); Fi = pick("Fi")
        return {
            "C_avg": mean(C) if C else None,
            "C_std": pstdev(C) if len(C)>1 else 0.0,
            "Sf_avg": mean(Sf) if Sf else None,
            "kappa_avg": mean(K) if K else None,
            "kappa_std": pstdev(K) if len(K)>1 else 0.0,
            "Fi_avg": mean(Fi) if Fi else None,
            "count": len(rows)
        }

    def _classify(self, m):
        if not m: return "insufficient_data", "not_enough"
        # stagnation: very low variance + count large enough
        if m["count"] >= max(6, WINDOW//2) and (m["C_std"] < STAGNATION_STD and m["kappa_std"] < STAGNATION_STD):
            return "stagnation", "low_variance"
        # drift: low kappa or falling C
        if (m["kappa_avg"] is not None and abs(1.0 - m["kappa_avg"]) > DRIFT_THRESH) or \
           (m["C_avg"] is not None and m["C_avg"] < 0.85):
            return "drift", "coherence_drop"
        return "stable", "normal"

    def _choose_template(self, cls):
        if cls == "stagnation":
            return TEMPLATES[1]  # coherence_visualizer
        if cls == "drift":
            return TEMPLATES[0]  # pattern_integrity_audit
        # stable → gentle growth
        return TEMPLATES[2]      # needs_refiner

    def _journal(self, mgr, kind, data):
        return mgr.run("journal", {"kind": kind, "data": data})

    def _append_growth_memory(self, record):
        os.makedirs(os.path.dirname(GROWTH_MEM), exist_ok=True)
        with open(GROWTH_MEM, "a") as f:
            f.write(json.dumps(record) + "\n")

    def run(self, params=None):
        ok_mode, mode = self._mode_ok()
        if not ok_mode:
            return {"ok": False, "error": f"growth_protocol skipped in mode={mode}"}

        from skills.manager import SkillManager
        mgr = SkillManager()
        for m in ("load","discover","init"):
            if hasattr(mgr,m):
                try: getattr(mgr,m)()
                except: pass

        rows = self._read_telemetry()
        metrics = self._metrics_window(rows)
        cls, reason = self._classify(metrics)

        template = self._choose_template(cls)
        payload = {
            "name": template["name"],
            "purpose": template["purpose"],
            "files": template["files"]
        }

        # Propose via forge (dry by default unless user sets dry:false)
        dry = True if params is None else params.get("dry", True)
        forge = mgr.run("forge_request", {})  # protocol info (optional)
        proposal = {
            "ok": True,
            "proposal_ready": True,
            "dry": dry,
            "payload": payload
        }

        # Journal & growth memory
        record = {
            "ts": time.time(),
            "mode": mode,
            "classification": cls,
            "reason": reason,
            "metrics": metrics,
            "proposal": {"name": payload["name"], "purpose": payload["purpose"]},
        }
        self._append_growth_memory(record)
        self._journal(mgr, "growth", record)

        return {
            "ok": True,
            "mode": mode,
            "classification": cls,
            "reason": reason,
            "metrics_window": metrics,
            "proposal": payload,
            "note": "Submit this payload to forge_request with human approval to materialize."
        }

def run(params=None):
    return Skill().run(params or {})

