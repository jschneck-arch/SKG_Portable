#!/usr/bin/env python3
from pathlib import Path
import re, json
TEMPLATE = """#!/usr/bin/env python3
# skills/{fname}.py
class Skill:
    name = "{sname}"
    description = "{desc}"
    def run(self, params):
        return {{"ok": True, "output": "skill {sname} (template) executed"}}
def run(params): return Skill().run(params)
"""
YAML_TEMPLATE = """name: {sname}
description: {desc}
entrypoint: "skills/{fname}.py"
"""
class Skill:
    name = "codeforge"
    description = "Create/patch skills from a template (offline, safe)."
    def run(self, params):
        name = (params or {}).get("name", "").strip()
        desc = (params or {}).get("description", "Generated skill.")
        dry = bool((params or {}).get("dry", True))
        if not name or not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
            return {"ok": False, "error": "valid 'name' required (python identifier)."}
        fname = f"{name}.py"
        root = Path.home() / "SKG_Portable"
        skills = root / "skills"
        py_path = skills / fname
        yml_path = skills / f"{name}.yml"
        py_code = TEMPLATE.format(fname=name, sname=name, desc=desc)
        yml_code = YAML_TEMPLATE.format(sname=name, desc=desc, fname=name)
        plan = {"py_path": str(py_path), "yml_path": str(yml_path),
                "py_preview": py_code.splitlines()[:12], "yml_preview": yml_code.splitlines(), "dry": dry}
        if dry: return {"ok": True, "output": {"plan": plan, "note": "dry run; set dry:false to write"}}
        py_path.write_text(py_code); yml_path.write_text(yml_code)
        try: py_path.chmod(0o755)
        except Exception: pass
        return {"ok": True, "output": {"written": [str(py_path), str(yml_path)]}}
def run(params): return Skill().run(params)
