#!/usr/bin/env python3
# skills/sandbox_mode.py

class Skill:
    name = "sandbox_mode"
    description = "Toggle hypothetical imagination sandbox mode"

    state = {"sandbox": False}

    def run(self, params):
        mode = params.get("mode")

        if mode == "on":
            self.state["sandbox"] = True
            return {"ok": True, "sandbox": "on"}

        if mode == "off":
            self.state["sandbox"] = False
            return {"ok": True, "sandbox": "off"}

        return {
            "ok": True,
            "sandbox": "on" if self.state["sandbox"] else "off",
            "note": "Send {\"mode\":\"on\"} or {\"mode\":\"off\"}"
        }

def run(params):
    return Skill().run(params)

