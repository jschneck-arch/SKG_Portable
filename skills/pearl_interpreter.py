#!/usr/bin/env python3
"""
pearl_interpreter.py
Reads SKG pearls, samples them, and produces interpretive summaries.
NO autonomous action. Pure interpretation / reflection only.
"""
import sys
import json, random, math
from pathlib import Path
from datetime import datetime
from statistics import mean, pstdev

CANDIDATES = [
    Path("/data/data/com.termux/files/home/SKG_Portable/memory"),
    Path("/data/data/com.termux/files/home/storage/shared/SKG/memory"),
    Path.home()/ "SKG_Portable/memory",
    Path.home()/ "storage/shared/SKG/memory",
]

ROOT = None
checked = []
for p in CANDIDATES:
    checked.append(str(p))
    if p.exists():
        ROOT = p
        break

# debug output to confirm
print("[pearl_interpreter] candidates:", checked, file=sys.stderr)
print("[pearl_interpreter] chosen:", str(ROOT), file=sys.stderr)

if ROOT is None:
    ROOT = CANDIDATES[0]  # default fallback

def load_pearl(path: Path):
    try:
        txt = path.read_text(encoding="utf-8", errors="ignore").strip()
        if not txt:
            return None
        
        # Try structured JSON pearl format
        try:
            obj = json.loads(txt)
            payload = obj.get("payload") or obj.get("msg") or obj
            kind = obj.get("class") or obj.get("kind") or "unknown"
            ts = obj.get("ts") or obj.get("timestamp")
        except Exception:
            # Raw text pearl fallback
            payload = txt
            kind = "raw"
            ts = None
        
        if isinstance(payload, dict):
            text = json.dumps(payload, ensure_ascii=False)
        else:
            text = str(payload)

        return {
            "kind": kind,
            "text": text,
            "ts": ts,
            "len": len(text)
        }
    except Exception:
        return None


def summarize(samples, style="minimal"):
    if not samples:
        return {
            "mode": "interpretation",
            "sampled": 0,
            "summary": {
                "interpretation": "Memory present but not yet semantically decoded.",
                "themes": ["initialization"],
                "future_pull": "Feed labeled pearls to strengthen interpretation."
            },
            "telemetry": {
                "count": 0,
                "avg_msg_len": 0,
                "sd_msg_len": 0,
                "kinds": {},
                "kinds_top": [],
                "time_coverage_ratio": 0,
                "stability_hint": "unknown"
            }
        }

    lengths = [p["len"] for p in samples]
    kinds = {}
    timestamps = []

    for p in samples:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
        if p["ts"]:
            timestamps.append(p["ts"])

    avg_len = round(mean(lengths), 3)
    sd_len  = round(pstdev(lengths), 3) if len(lengths) > 1 else 0

    if timestamps:
        try:
            times = [datetime.fromisoformat(t) for t in timestamps if t]
            span = (max(times) - min(times)).total_seconds()
        except Exception:
            span = 0
    else:
        span = 0
    
    stability = "coherent" if sd_len < avg_len * 0.6 else "variable"

    themes = []
    interpretation = ""

    if style in ("scientific", "hybrid"):
        interpretation += f"Pearl length avg={avg_len}, sd={sd_len}. "
        interpretation += f"Kind diversity={len(kinds)}. "
        if span > 0:
            interpretation += f"Time span={span} sec. "

        if avg_len > 40:
            themes.append("complex")
        elif avg_len > 5:
            themes.append("concise")
        else:
            themes.append("minimal")

    if style in ("hermeneutic", "hybrid"):
        interpretation += "Meaning appears to accumulate through reflective trace. "
        themes.append("emergence")
        themes.append("continuity")

    if style == "minimal":
        interpretation = "Reflective memory traces active."

    return {
        "mode": "interpretation",
        "sampled": len(samples),
        "summary": {
            "interpretation": interpretation.strip(),
            "themes": sorted(set(themes)),
            "future_pull": "Continue recording and add meaning labels for deeper resonance."
        },
        "telemetry": {
            "count": len(samples),
            "avg_msg_len": avg_len,
            "sd_msg_len": sd_len,
            "kinds": kinds,
            "kinds_top": sorted(kinds.items(), key=lambda x: x[1], reverse=True)[:5],
            "time_coverage_ratio": round(span, 3),
            "stability_hint": stability
        },
        "timestamp": datetime.utcnow().isoformat()
    }


def run(params=None):
    params = params or {}
    style = params.get("style", "minimal")
    limit = params.get("limit", 200)
    # DEBUG pearl list
    try:
        pearl_files = list(ROOT.rglob("pearl.hspr")) if ROOT else []
        print("[pearl_interpreter] found pearls:", len(pearl_files), file=sys.stderr)
    except Exception as e:
        print("[pearl_interpreter] ERROR scanning:", e, file=sys.stderr)

    # Glob pearls
    files = list(ROOT.rglob("pearl.hspr"))
    if not files:
        return summarize([])

    samples = []
    random.shuffle(files)

    for p in files:
        pearl = load_pearl(Path(p))
        if pearl:
            samples.append(pearl)
        if len(samples) >= limit:
            break

    return summarize(samples, style=style)


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))

