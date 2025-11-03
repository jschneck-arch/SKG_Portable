#!/usr/bin/env python3
# skills/hello_skg.py
class Skill:
    name = "hello_skg"
    description = "sanity test"
    def run(self, params):
        return {"ok": True, "output": "skill hello_skg (template) executed"}
def run(params): return Skill().run(params)
