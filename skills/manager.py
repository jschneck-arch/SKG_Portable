#!/usr/bin/env python3
# skills/manager.py

import os, importlib, inspect

class SkillManager:
    def __init__(self):
        self.skills = {}  # name -> run function
        self.load_skills()

    def load_skills(self):
        skills_dir = os.path.dirname(__file__)
        print("[SKG:loader] scanning skills directory:", skills_dir)

        for file in os.listdir(skills_dir):
            if not file.endswith(".py") or file in ("__init__.py", "manager.py"):
                continue

            print(f"[SKG:loader] trying: {file}")
            module_name = file[:-3]

            try:
                module = importlib.import_module(f"skills.{module_name}")
                loaded = False

                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and hasattr(obj, "name") and hasattr(obj, "run"):
                        instance = obj()
                        self.skills[instance.name] = instance.run
                        print(f"[SKG:loader] ✅ class skill loaded: {instance.name}")
                        loaded = True

                    elif callable(obj) and name == "run":
                        self.skills[module_name] = obj
                        print(f"[SKG:loader] ✅ function skill loaded: {module_name}")
                        loaded = True

                if not loaded:
                    print(f"[SKG:loader] ⚠️ no skill entry found in {file}")

            except Exception as e:
                print(f"[SKG:loader] ❌ ERROR loading {file}: {e}")

        print(f"[SKG:loader] finished. Skills loaded:", list(self.skills.keys()))

    def run(self, name, params):
        if name not in self.skills:
            return {"ok": False, "error": "unknown_skill", "skill": name}

        try:
            return self.skills[name](params)
        except Exception as e:
            return {"ok": False, "error": str(e), "skill": name}

    def available(self):
        return list(self.skills.keys())

