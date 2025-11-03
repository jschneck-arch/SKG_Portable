#!/usr/bin/env python3
from pathlib import Path
import json, os

class Skill:
    name = "introspect"
    description = "Reflect on SKG: skills, files, mode, memory. Supports self_prompt for reflective output."

    def run(self, params):
        root = Path.home() / "SKG_Portable"
        skills_dir = root / "skills"

        report = {}
        # list skills
        report["skills_files"] = sorted([p.name for p in skills_dir.glob("*.py")])

        # mode info (if exists)
        try:
            from mode import get_mode
            mode, auto = get_mode()
            report["mode"] = {"mode": mode, "autonomy": auto}
        except Exception as e:
            report["mode"] = {"error": str(e)}

        # memory tail
        mem = root / "brain" / "memory.jsonl"
        report["memory_tail"] = mem.read_text().splitlines()[-50:] if mem.exists() else []

        # needs log (if exists)
        needs = root / "brain" / "needs.yml"
        report["needs_log"] = needs.read_text() if needs.exists() else ""

        # ----- Reflection Mode -----
        prompt = (params or {}).get("self_prompt")
        mode_flag = (params or {}).get("mode")

        if prompt or mode_flag in ("interpret_ethos", "reflect", "self"):
            tail = report.get("memory_tail", [])
            recent_ethos = [
                line for line in tail
                if any(key in line.lower() for key in ["ethos", "reflection", "trajectory"])
            ]

            # Core reflective sentence — evolves via new memory seeds
            reflection = "I grow by seeking clarity, honoring truth, and evolving through understanding."

            return {
                "ok": True,
                "reflection": reflection,
                "inspired_by": recent_ethos[-5:],
                "echo_prompt": prompt
            }

        # ----- Default Diagnostic Output -----
        return {"ok": True, "output": report}

def run(params): 
    return Skill().run(params)

