from .exec_chain import run as exec_chain

class Skill:
    name = "iface_enum"
    description = "Enumerate local interfaces"

    def run(self, params):
        commands = [
            "ip addr",
            "ifconfig",
            "ip -br addr",
            "busybox ifconfig"
        ]

        result = exec_chain({"commands": commands})

        if result.get("ok") and result.get("output"):
            return {"ok": True, "output": result["output"]}

        return {"ok": False, "error": "iface_enum failed", "output": result}

def run(params):
    return Skill().run(params)

