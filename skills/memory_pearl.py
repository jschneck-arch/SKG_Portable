#!/usr/bin/env python3
# skills/memory_pearl.py
"""
Writes an HSPR "pearl" (Hybrid Spherical Pearl Record) to:
  A) Local:  ~/SKG_Portable/memory/YYYY/MM/DD/sphere_<hash>/pearl.hspr
  B) Shared: ~/storage/shared/SKG/memory/YYYY/MM/DD/sphere_<hash>/pearl.hspr  (best-effort mirror)

Never mutates state beyond writing files.
"""

import os, json, time, hashlib
from pathlib import Path
from datetime import datetime

HOME = Path("/data/data/com.termux/files/home")
ROOT_LOCAL  = HOME / "SKG_Portable"
ROOT_SHARED = HOME / "storage" / "shared" / "SKG"

MEM_LOCAL   = ROOT_LOCAL  / "memory"
MEM_SHARED  = ROOT_SHARED / "memory"

def _safe_mkdir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def _ts():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def _mk_hash(payload: str) -> str:
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]

def _pearl_paths(hash12: str):
    today = datetime.utcnow()
    rel = Path(str(today.year)) / f"{today.month:02d}" / f"{today.day:02d}" / f"sphere_{hash12}"
    return (MEM_LOCAL / rel / "pearl.hspr", MEM_SHARED / rel / "pearl.hspr", rel)

def _build_hspr(meta: dict, tml: str, jmini: dict) -> str:
    """
    HSPR = XML-ish wrapper + TML core + JSON mini
    """
    # Minimal XML-ish header (not strict XML — readable and robust)
    header = []
    header.append("<pearl>")
    header.append("  .meta {")
    for k, v in meta.items():
        header.append(f"    {k}: {v}")
    header.append("  }")
    header.append("  ~thought")
    # TML (one indent)
    for line in tml.strip().splitlines():
        header.append(f"   {line}")
    header.append("  ~")
    header.append("  { " + json.dumps(jmini, ensure_ascii=False)[1:-1] + " }")
    header.append("</pearl>")
    return "\n".join(header) + "\n"

def write_pearl(kind: str, msg: str, context: str = "", truth_anchor: bool = True, extras: dict = None):
    # Construct TML payload (SKG-internal symbolic block)
    tml = f'msg:"{msg}"\ncontext:"{context}"\nkind:"{kind}"'
    if extras:
        for k, v in extras.items():
            tml += f'\n{k}:"{v}"'

    # Meta & JSON mini
    now = _ts()
    core = f"{now}|{kind}|{msg}|{context}|{json.dumps(extras or {}, ensure_ascii=False)}"
    h = _mk_hash(core)
    meta = {
        "ts": now,
        "id": f"{now.replace(':','').replace('-','')}_{h}",
        "class": kind,
        "state": "stable",
        "hash": f"sha1:{h}",
    }
    jmini = {"truth_anchor": bool(truth_anchor), "kind": kind, "msg": msg, "context": context}

    # Build record
    body = _build_hspr(meta, tml, jmini)
    # Resolve paths
    p_local, p_shared, rel = _pearl_paths(h)
    _safe_mkdir(p_local.parent)

    # Always write local
    with open(p_local, "w", encoding="utf-8") as f:
        f.write(body)

    # Best-effort mirror to shared; on failure, queue a retry file
    mirror_ok = False
    try:
        _safe_mkdir(p_shared.parent)
        with open(p_shared, "w", encoding="utf-8") as f:
            f.write(body)
        mirror_ok = True
    except Exception:
        # Queue for later
        outbox = ROOT_LOCAL / "memory_mirror_queue"
        _safe_mkdir(outbox)
        q = outbox / f"mirror_{meta['id']}.hspr"
        with open(q, "w", encoding="utf-8") as f:
            f.write(body)

    return {
        "ok": True,
        "meta": meta,
        "local_path": str(p_local),
        "shared_path": str(p_shared),
        "shared_mirror": "ok" if mirror_ok else "queued",
        "rel": str(rel),
    }

class Skill:
    name = "memory_pearl"
    description = "Create a Hybrid Spherical Pearl Record (HSPR) and mirror to shared storage."

    def run(self, params):
        params = params or {}
        kind = params.get("kind", "note")
        msg  = params.get("msg", "")
        ctx  = params.get("context", "")
        truth = bool(params.get("truth_anchor", True))
        extras = params.get("extras", {})
        return write_pearl(kind, msg, ctx, truth, extras)

def run(params):
    return Skill().run(params)

