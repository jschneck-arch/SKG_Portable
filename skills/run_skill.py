#!/usr/bin/env python3
# skills/run_skill.py

import importlib
from skills.manager import SkillManager

class Skill:
    name = "run_skill"
    description = "Execute another skill by name (proxy)"

    def run(self, params):
        skill = params.get("skill")
        args = params.get("params", {})

        if not skill:
            return {"ok": False, "error": "missing skill name"}

        mgr = SkillManager()
        return mgr.run(skill, args)

def run(params):
    return Skill().run(params)

