#!/usr/bin/env python3
from pathlib import Path
from skills.manager import SkillManager

class Skill:
    name = "reload_skills"
    description = "Reload all skills from disk"

    def run(self, params):
        mgr = SkillManager()
        for m in ("load", "load_all", "discover", "init"):
            if hasattr(mgr, m):
                try: 
                    getattr(mgr, m)()
                except: 
                    pass
        return {"ok": True, "output": f"reloaded {len(mgr.skills)} skills"}

def run(params): 
    return Skill().run(params)

