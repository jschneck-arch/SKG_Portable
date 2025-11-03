#!/usr/bin/env python3
class Skill:
    name = "safety_kernel"
    description = "Query or set safety mode: safe, research, operator."
    def run(self, params):
        action = (params or {}).get("action","get")
        try:
            from mode import get_mode, set_mode
        except Exception as e:
            return {"ok": False, "error": f"mode module missing: {e}"}
        if action == "get":
            m,a = get_mode(); return {"ok": True, "mode": m, "autonomy": a}
        if action == "set":
            target = (params or {}).get("mode","safe")
            res = set_mode(target, "safety_kernel")
            return {"ok": True, "output": res}
        return {"ok": False, "error": "unknown action"}
def run(params): return Skill().run(params)
