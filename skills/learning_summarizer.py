#!/usr/bin/env python3
"""
learning_summarizer.py
----------------------
Periodically compresses SKG's recent telemetry and reflections
into a compact learning-state summary for introspection.
"""

import json, os, time
from datetime import datetime
from statistics import mean, pstdev

TELEMETRY_PATH = "logs/telemetry.log"
SUMMARY_PATH = "logs/learning_summary.log"

def _read_json_lines(path, limit=100):
    if not os.path.exists(path):
        return []
    lines = []
    with open(path, "r") as f:
        for line in f.readlines()[-limit:]:
            try:
                lines.append(json.loads(line))
            except Exception:
                continue
    return lines

def run(params=None):
    lines = _read_json_lines(TELEMETRY_PATH, limit=200)
    if not lines:
        return {"ok": False, "error": "no telemetry data"}

    # Gather metrics
    metrics = {"C": [], "Sf": [], "Fi": [], "kappa": []}
    for l in lines:
        for k in metrics:
            if k in l and isinstance(l[k], (int, float)):
                metrics[k].append(l[k])

    averages = {k: mean(v) if v else None for k, v in metrics.items()}
    stdevs = {k: pstdev(v) if v else None for k, v in metrics.items()}

    # Classify general state
    if all(v == 1.0 for v in averages.values() if v is not None):
        classification = "stable"
    elif any(v is None for v in averages.values()):
        classification = "incomplete"
    else:
        classification = "drifting"

    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "summary": {
            "state": classification,
            "averages": averages,
            "stdevs": stdevs,
            "entries_analyzed": len(lines),
        }
    }

    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, "a") as f:
        f.write(json.dumps(summary) + "\n")

    return {"ok": True, "summary": summary}

